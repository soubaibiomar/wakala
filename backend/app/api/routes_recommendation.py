from typing import Annotated

from fastapi import APIRouter, Depends
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
from app.models.vehicle import Vehicle

router = APIRouter()
engine = HybridEngine(alpha=0.6)


@router.post("/", response_model=RecommendationResponse)
async def get_recommendations(
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

    result = await db.execute(select(Vehicle))
    all_vehicles: list[Vehicle] = list(result.scalars().all())

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

    return response
