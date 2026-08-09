from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.recommendation.hybrid_engine import HybridEngine
from app.ml.recommendation.content_based import compute_content_scores
from app.ml.recommendation.collaborative import compute_collaborative_scores
from app.ml.recommendation.feature_extraction import semantic_search
from app.ml.nlp_pipeline.llm_extractor import extract_search_criteria
from app.ml.matching.schemas import SearchRequest, RankedResult
from app.ml.scoring.wakala_scorer import wakala_scorer
from app.ml.scoring.top3_aggregator import top3_aggregator, Top3Response
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
        self.scorer = wakala_scorer
        self.aggregator = top3_aggregator

    async def search_with_persona(self, request: SearchRequest, db: AsyncSession) -> list[RankedResult]:
        # 1. Extraction NLP
        extracted = await extract_search_criteria(request.query)
        
        # Override with quiz if provided
        if request.quiz_answers:
            if request.quiz_answers.get("budget"):
                extracted.budget = request.quiz_answers["budget"]
            if request.quiz_answers.get("usage_prevu"):
                extracted.usage_prevu = request.quiz_answers["usage_prevu"]
            if request.quiz_answers.get("priorites"):
                extracted.priorites = request.quiz_answers["priorites"]
                
        # 2. Semantic Search in Qdrant / Embeddings
        semantic_ids = semantic_search(request.query, limit=50)
        
        # Query database for candidates
        result = await db.execute(select(Vehicle))
        all_vehicles: list[Vehicle] = list(result.scalars().all())
        vehicles_by_id = {str(v.id): v for v in all_vehicles}

        # 3. Application des filtres durs avec cascade de relâchement Wakala
        body_filter = USAGE_TO_BODY_TYPE.get(extracted.usage_prevu) if extracted.usage_prevu else None
        filtered_vehicles, relaxed_filter = self.scorer.filter_and_cascade(
            vehicles=all_vehicles,
            budget_max=extracted.budget,
            body_type=body_filter,
        )

        # 4. Calcul des poids personnalisés Wakala (57/25/18 + redistribution honnête)
        user_weights = self.scorer.compute_user_weights(
            usage=extracted.usage_prevu,
            priorites=extracted.priorites,
            profil_passagers=extracted.profil_passagers,
        )

        # 5. Calcul des scores Wakala pour chaque véhicule
        scored_data = {}
        content_scores = []
        for v in filtered_vehicles:
            scored = self.scorer.score_single_vehicle(
                vehicle=v,
                user_weights=user_weights,
                budget_max=extracted.budget,
                usage=extracted.usage_prevu,
            )
            vid = str(v.id)
            scored_data[vid] = scored
            # Normalisation du score de contenu pour l'HybridEngine (entre 0.0 et 1.0)
            content_scores.append({
                "vehicle_id": vid,
                "content_score": scored["final_score"] / 100.0,
            })

        all_vids = [cs["vehicle_id"] for cs in content_scores]

        # 6. Collaborative scores via Neo4j
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

        # 7. Hybrid combine
        response = self.hybrid_engine.combine(
            content_scores=content_scores,
            collaborative_scores=collaborative_scores,
            page=request.page,
            page_size=request.page_size,
            cold_start=cold_start,
            user_id=request.user_id,
        )
        
        # 8. Map back to RankedResult avec badges et justifications Wakala
        results = []
        for item in response.items:
            vid = item.vehicle_id
            scored = scored_data.get(vid, {})
            v_obj = vehicles_by_id.get(vid)

            badges = []
            if extracted.usage_prevu == "familial":
                badges.append("Idéal Famille")
            if "économique" in (extracted.priorites or []):
                badges.append("Économique")
            if extracted.profil_passagers == "jeune_conducteur":
                badges.append("Premier Achat")
            
            # Badges issus des faits tangibles
            key_facts = scored.get("key_facts", [])
            for fact in key_facts:
                if len(badges) < 3 and fact not in badges:
                    badges.append(fact)
                
            version_name = getattr(v_obj, "version", None) if v_obj else None

            results.append(
                RankedResult(
                    vehicle_id=item.vehicle_id,
                    match_score=item.match_score,
                    content_score=item.score_breakdown.content,
                    collaborative_score=item.score_breakdown.collaborative,
                    badges=badges,
                    score_breakdown=scored.get("score_breakdown"),
                    key_facts=key_facts,
                    budget_margin=scored.get("budget_margin"),
                    best_version_name=version_name,
                    relaxed_filter=relaxed_filter,
                )
            )
            
        return results

    async def search_top3(self, request: SearchRequest, db: AsyncSession) -> Top3Response:
        """Endpoint dédié pour la restitution du Top 3 selon le livrable Wakala."""
        # 1. Extraction NLP
        extracted = await extract_search_criteria(request.query)
        if request.quiz_answers:
            if request.quiz_answers.get("budget"):
                extracted.budget = request.quiz_answers["budget"]
            if request.quiz_answers.get("usage_prevu"):
                extracted.usage_prevu = request.quiz_answers["usage_prevu"]
            if request.quiz_answers.get("priorites"):
                extracted.priorites = request.quiz_answers["priorites"]

        # 2. Candidats
        result = await db.execute(select(Vehicle))
        all_vehicles: list[Vehicle] = list(result.scalars().all())
        vehicles_by_id = {str(v.id): v for v in all_vehicles}

        # 3. Filtres durs + cascade
        body_filter = USAGE_TO_BODY_TYPE.get(extracted.usage_prevu) if extracted.usage_prevu else None
        filtered_vehicles, relaxed_filter = self.scorer.filter_and_cascade(
            vehicles=all_vehicles,
            budget_max=extracted.budget,
            body_type=body_filter,
        )

        # 4. Poids
        user_weights = self.scorer.compute_user_weights(
            usage=extracted.usage_prevu,
            priorites=extracted.priorites,
            profil_passagers=extracted.profil_passagers,
        )

        # 5. Scoring
        scored_list = []
        for v in filtered_vehicles:
            scored = self.scorer.score_single_vehicle(
                vehicle=v,
                user_weights=user_weights,
                budget_max=extracted.budget,
                usage=extracted.usage_prevu,
            )
            scored_list.append(scored)

        # 6. Agrégation Top 3 (1/modèle, 1/marque)
        return self.aggregator.aggregate_top3(
            scored_vehicles=scored_list,
            vehicles_map=vehicles_by_id,
            relaxed_filter=relaxed_filter,
            limit=3,
        )

matching_engine = MatchingEngine()
