from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.recommendation.hybrid_engine import HybridEngine
from app.ml.recommendation.content_based import compute_content_scores
from app.ml.recommendation.collaborative import compute_collaborative_scores
from app.ml.recommendation.feature_extraction import semantic_search
from app.ml.nlp_pipeline.llm_extractor import extract_search_criteria
from app.ml.matching.schemas import SearchRequest, RankedResult
from app.models.vehicle import Vehicle

USAGE_TO_BODY_TYPE = {
    "familial": ["suv", "monospace", "break"],
    "urbain": ["citadine", "berline"],
    "longue_distance": ["berline", "suv", "break"],
    "professionnel": ["utilitaire", "pick_up", "berline"],
    "loisir": ["coupe", "cabriolet", "suv", "pick_up"]
}

class MatchingEngine:
    def __init__(self):
        self.hybrid_engine = HybridEngine(alpha=0.6)

    async def search_with_persona(self, request: SearchRequest, db: AsyncSession) -> list[RankedResult]:
        # 1. Extraction NLP
        extracted = await extract_search_criteria(request.query)
        
        filters = {}
        
        # Override with quiz if provided
        if request.quiz_answers:
            if request.quiz_answers.get("budget"):
                extracted.budget = request.quiz_answers["budget"]
            if request.quiz_answers.get("usage_prevu"):
                extracted.usage_prevu = request.quiz_answers["usage_prevu"]
            if request.quiz_answers.get("priorites"):
                extracted.priorites = request.quiz_answers["priorites"]
                
        if extracted.budget:
            filters["price_max"] = extracted.budget
        
        if extracted.usage_prevu and extracted.usage_prevu in USAGE_TO_BODY_TYPE:
            filters["body_type_in"] = USAGE_TO_BODY_TYPE[extracted.usage_prevu]
                
        # 2. Semantic Search in Qdrant
        semantic_ids = semantic_search(request.query, limit=50)
        
        # Query database for candidates
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
                other_vehicles = [v for v in all_vehicles if str(v.id) not in semantic_set]
                all_vehicles = ranked + other_vehicles

        # 3. Content scores
        content_scores = compute_content_scores(all_vehicles, filters)
        all_vids = [cs["vehicle_id"] for cs in content_scores]

        # 4. Collaborative scores via Neo4j
        if request.user_id:
            collaborative_scores, cold_start = await compute_collaborative_scores(
                db=db,
                target_user_id=request.user_id,
                all_vehicle_ids=all_vids,
            )
        else:
            collaborative_scores = [
                {"vehicle_id": vid, "collaborative_score": 0.0} for vid in all_vids
            ]
            cold_start = True

        # 5. Hybrid combine
        response = self.hybrid_engine.combine(
            content_scores=content_scores,
            collaborative_scores=collaborative_scores,
            page=request.page,
            page_size=request.page_size,
            cold_start=cold_start,
            user_id=request.user_id,
        )
        
        # Map back to RankedResult with badges
        results = []
        for item in response.items:
            badges = []
            if extracted.usage_prevu == "familial":
                badges.append("Idéal Famille")
            if "économique" in extracted.priorites:
                badges.append("Économique")
            if extracted.profil_passagers == "jeune_conducteur":
                badges.append("Premier Achat")
                
            results.append(
                RankedResult(
                    vehicle_id=item.vehicle_id,
                    match_score=item.match_score,
                    content_score=item.score_breakdown.content,
                    collaborative_score=item.score_breakdown.collaborative,
                    badges=badges
                )
            )
            
        return results

matching_engine = MatchingEngine()
