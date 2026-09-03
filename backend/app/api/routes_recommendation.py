from typing import Annotated, Optional
import hashlib
import json
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.ml.recommendation.collaborative import compute_collaborative_scores
from app.ml.recommendation.content_based import compute_content_scores
from app.ml.recommendation.feature_extraction import (
    extract_filters_from_query,
    semantic_search,
)
from app.ml.recommendation.hybrid_engine import HybridEngine
from app.ml.recommendation.schemas import (
    EightDimensionScoreRequest,
    EightDimensionScoreResult,
    RecommendationRequest,
    RecommendationResponse,
)
from app.ml.recommendation.eight_dimension_scorer import score_vehicle_8d
from app.ml.recommendation.dynamic_weighting import compute_dynamic_weights_from_query
from app.ml.matching.schemas import SearchRequest
from app.ml.matching.matching_engine import matching_engine
from app.ml.scoring.criteria_ranker import criteria_ranker
from app.ml.scoring.top3_aggregator import Top3Response
from app.models.vehicle import Vehicle
from app.core.limiter import limiter
from app.core.security import get_current_user_optional
from app.models.user import User

router = APIRouter()
engine = HybridEngine(alpha=0.6)
_RECOMMENDATION_CACHE: dict[str, tuple[float, RecommendationResponse]] = {}
_RECOMMENDATION_CACHE_TTL = 120
_RECOMMENDATION_CACHE_MAX = 128


@router.post("/", response_model=RecommendationResponse)
@limiter.limit("15/minute")
async def get_recommendations(
    request: Request,
    payload: RecommendationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    if payload.user_id:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentification requise pour l'historique utilisateur.")
        if str(current_user.id) != str(payload.user_id):
            raise HTTPException(status_code=403, detail="Accès refusé à cet historique utilisateur.")

    # Anonymous catalogue searches are deterministic for a short period. Do
    # not cache signed-in requests because collaborative scores are personal.
    cache_key = None
    if not current_user and not payload.user_id:
        cache_key = hashlib.sha256(json.dumps(
            payload.model_dump(exclude_none=True), sort_keys=True, ensure_ascii=False
        ).encode("utf-8")).hexdigest()
        cached = _RECOMMENDATION_CACHE.get(cache_key)
        if cached and time.monotonic() - cached[0] < _RECOMMENDATION_CACHE_TTL:
            return cached[1]

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
        ).where(
            # Recommendations may only use verified vehicles from the active
            # Moroccan catalogue. This is the deterministic compliance gate
            # described in the Wakala architecture document.
            Vehicle.status == "available",
            Vehicle.condition == "new",
            Vehicle.mileage == 0,
            Vehicle.price.isnot(None),
            Vehicle.price > 0,
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

    effective_user_id = str(current_user.id) if current_user else None
    if effective_user_id:
        collaborative_scores, cold_start = await compute_collaborative_scores(
            db=db,
            target_user_id=effective_user_id,
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
        user_id=effective_user_id,
        diversity_types=(
            {str(v.id): str(v.body_type or "").lower() for v in all_vehicles}
            if merged_filters.get("body_type_in") else None
        ),
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

    if cache_key:
        _RECOMMENDATION_CACHE[cache_key] = (time.monotonic(), response)
        if len(_RECOMMENDATION_CACHE) > _RECOMMENDATION_CACHE_MAX:
            oldest_key = min(_RECOMMENDATION_CACHE, key=lambda key: _RECOMMENDATION_CACHE[key][0])
            _RECOMMENDATION_CACHE.pop(oldest_key, None)
    return response


@router.post("/score-8d", response_model=list[EightDimensionScoreResult])
@limiter.limit("30/minute")
async def score_recommendation_shortlist(
    request: Request,
    payload: EightDimensionScoreRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Return the authoritative 8D breakdown for a final shortlist."""
    result = await db.execute(
        select(Vehicle)
        .options(selectinload(Vehicle.wakala_scores))
        .where(Vehicle.id.in_(payload.vehicle_ids))
    )
    vehicles_by_id = {str(vehicle.id): vehicle for vehicle in result.scalars().all()}
    weights = compute_dynamic_weights_from_query(payload.profile)
    response: list[EightDimensionScoreResult] = []

    for vehicle_id in payload.vehicle_ids:
        vehicle = vehicles_by_id.get(str(vehicle_id))
        if vehicle is None:
            continue
        scored = score_vehicle_8d(vehicle)
        scores = scored.scores.model_dump()
        weighted_total = round(sum(weights.get(key, 0.0) * value for key, value in scores.items()), 3)
        response.append(EightDimensionScoreResult(
            vehicle_id=str(vehicle.id),
            scores=scores,
            weighted_total=weighted_total,
            weighted_total_percent=round(weighted_total * 20, 1),
            source=scored.source,
        ))

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
