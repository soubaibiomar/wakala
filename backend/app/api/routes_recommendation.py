from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.ml.recommendation.collaborative import compute_collaborative_scores
from app.ml.recommendation.content_based import compute_content_scores
from app.ml.recommendation.feature_extraction import (
    extract_filters_from_query,
    semantic_search,
)
from app.ml.recommendation.hybrid_engine import HybridEngine
from app.ml.recommendation.schemas import (
    RecommendationRequest,
    RecommendationResponse,
)
from app.ml.matching.schemas import SearchRequest
from app.ml.matching.matching_engine import matching_engine
from app.ml.scoring.criteria_ranker import criteria_ranker
from app.ml.scoring.top3_aggregator import Top3Response
from app.models.vehicle import Vehicle
from app.core.limiter import limiter

router = APIRouter()
engine = HybridEngine(alpha=0.6)


@router.post("/", response_model=RecommendationResponse)
@limiter.limit("15/minute")
async def get_recommendations(
    request: Request,
    payload: RecommendationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    merged_filters = payload.filters.model_dump(exclude_none=True)

    if payload.query:
        extracted = extract_filters_from_query(payload.query)
        for key, value in extracted.items():
            if key not in merged_filters or merged_filters[key] is None:
                merged_filters[key] = value

        semantic_ids = semantic_search(payload.query, limit=50)
    else:
        semantic_ids = []

    from sqlalchemy.orm import noload
    
    result = await db.execute(
        select(Vehicle).options(
            noload('*'),
        )
    )
    all_vehicles: list[Vehicle] = list(result.scalars().all())
    vehicles_by_id = {str(v.id): v for v in all_vehicles}

    if semantic_ids:
        semantic_set = set(semantic_ids)
        semantic_vehicles = [v for v in all_vehicles if str(v.id) in semantic_set]
        if semantic_vehicles:
            ranked = sorted(
                semantic_vehicles,
                key=lambda v: (
                    semantic_ids.index(str(v.id))
                    if str(v.id) in semantic_ids
                    else len(semantic_ids)
                ),
            )
            other_vehicles = [
                v for v in all_vehicles if str(v.id) not in semantic_set
            ]
            all_vehicles = ranked + other_vehicles

    content_scores = compute_content_scores(all_vehicles, merged_filters)

    all_vids = [cs["vehicle_id"] for cs in content_scores]

    if payload.user_id:
        collaborative_scores, cold_start = await compute_collaborative_scores(
            db=db,
            target_user_id=payload.user_id,
            all_vehicle_ids=all_vids,
        )
    else:
        collaborative_scores = [
            {"vehicle_id": vid, "collaborative_score": 0.0} for vid in all_vids
        ]
        cold_start = True

    response = engine.combine(
        content_scores=content_scores,
        collaborative_scores=collaborative_scores,
        page=payload.page,
        page_size=payload.page_size,
        cold_start=cold_start,
        user_id=payload.user_id,
    )

    # Enrichir les items avec les faits clés et critères Wakala
    budget_max = merged_filters.get("price_max")
    for item in response.items:
        v_obj = vehicles_by_id.get(item.vehicle_id)
        if v_obj:
            crit_scores = criteria_ranker.compute_criteria_scores(v_obj)
            item.key_facts = criteria_ranker.extract_key_facts(v_obj, crit_scores)
            item.best_version_name = getattr(v_obj, "version", None) or f"{v_obj.brand} {v_obj.model}"
            if budget_max and v_obj.price:
                item.budget_margin = float(budget_max) - float(v_obj.price)
            item.wakala_score_breakdown = crit_scores

    return response


@router.post("/top3", response_model=Top3Response)
@limiter.limit("15/minute")
async def get_top3_recommendations(
    request: Request,
    payload: SearchRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Restitue le Top 3 Wakala avec meilleure version par modèle et diversité de marque."""
    return await matching_engine.search_top3(payload, db)

