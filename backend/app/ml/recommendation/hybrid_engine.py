from typing import Optional

from app.ml.recommendation.schemas import (
    RecommendationFilters,
    RecommendationResponse,
    RecommendationResult,
    ScoreBreakdown,
)


class HybridEngine:
    def __init__(self, alpha: float = 0.6):
        self.alpha = alpha

    def combine(
        self,
        content_scores: list[dict],
        collaborative_scores: list[dict],
        page: int = 1,
        page_size: int = 20,
        cold_start: bool = False,
        user_id: Optional[str] = None,
        diversity_types: Optional[dict[str, str]] = None,
    ) -> RecommendationResponse:
        score_map: dict[str, dict] = {}

        # A/B Testing Bucketing
        # Variant A: alpha = 0.8 (Content dominant)
        # Variant B: alpha = 0.2 (Collaborative dominant)
        # Fallback to init alpha if no user_id
        current_alpha = self.alpha
        ab_variant = "none"
        
        if user_id:
            import hashlib
            # Simple hash mod 2 for bucketing
            bucket = int(hashlib.md5(user_id.encode('utf-8')).hexdigest(), 16) % 2
            if bucket == 0:
                current_alpha = 0.8
                ab_variant = "A"
            else:
                current_alpha = 0.2
                ab_variant = "B"

        for cs in content_scores:
            vid = cs["vehicle_id"]
            score_map[vid] = {
                "vehicle_id": vid,
                "content": cs["content_score"],
                "collaborative": 0.0,
            }

        for cs in collaborative_scores:
            vid = cs["vehicle_id"]
            if vid in score_map:
                score_map[vid]["collaborative"] = cs["collaborative_score"]
            else:
                score_map[vid] = {
                    "vehicle_id": vid,
                    "content": 0.0,
                    "collaborative": cs["collaborative_score"],
                }

        if cold_start:
            method = "cold-start"
        elif current_alpha < 1.0 and any(
            s["collaborative"] > 0 for s in score_map.values()
        ):
            method = "hybrid"
        else:
            method = "content-based"

        results = []
        for vid, scores in score_map.items():
            if cold_start:
                final_score = scores["content"]
            else:
                final_score = (
                    current_alpha * scores["content"]
                    + (1 - current_alpha) * scores["collaborative"]
                )

            match_score = round(final_score * 100, 1)

            results.append(
                RecommendationResult(
                    vehicle_id=vid,
                    match_score=match_score,
                    score_breakdown=ScoreBreakdown(
                        content=round(scores["content"], 4),
                        collaborative=round(scores["collaborative"], 4),
                    ),
                )
            )

        results.sort(key=lambda x: x.match_score, reverse=True)

        # A family recommendation should not be monopolized by the most
        # common body style in the catalogue (currently SUVs). Promote the
        # strongest candidate from each practical family shape first, then
        # preserve the normal score order for the remaining vehicles.
        if diversity_types:
            preferred_types = ["monospace", "suv", "break", "berline", "citadine"]
            selected_ids: set[str] = set()
            diversified: list[RecommendationResult] = []
            for body_type in preferred_types:
                for result in results:
                    if result.vehicle_id in selected_ids:
                        continue
                    if (diversity_types.get(result.vehicle_id) or "").lower() == body_type:
                        diversified.append(result)
                        selected_ids.add(result.vehicle_id)
                        break
            diversified.extend(result for result in results if result.vehicle_id not in selected_ids)
            results = diversified

        total = len(results)
        start = (page - 1) * page_size
        end = start + page_size
        paginated = results[start:end]

        return RecommendationResponse(
            items=paginated,
            total=total,
            page=page,
            page_size=page_size,
            method=method,
            cold_start=cold_start,
        )
