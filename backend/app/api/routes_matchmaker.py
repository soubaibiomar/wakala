from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List, Optional

from app.ml.recommendation.matchmaker import matchmaker_nlp
from app.ml.recommendation.hybrid_engine import HybridEngine
# Assuming a vehicle search or DB service exists to fetch content_scores, but we'll mock the integration for now 
# as hybrid_engine expects pre-calculated content and collaborative scores.

router = APIRouter(prefix="/matchmaker", tags=["Matchmaker"])

class MatchmakerRequest(BaseModel):
    user_id: str
    free_text_query: str

class MatchmakerResponse(BaseModel):
    extracted_criteria: dict
    recommendations: dict

@router.post("/recommend", response_model=MatchmakerResponse)
async def get_matchmaker_recommendations(request: MatchmakerRequest):
    """
    Extrait les critères de style de vie à partir de texte libre
    et utilise le moteur hybride pour proposer des véhicules.
    """
    # 1. Extraction NLP des critères
    criteria = matchmaker_nlp.extract_criteria(request.free_text_query)
    
    # 2. Appel au moteur hybride (Mock des scores pour cet audit)
    # Dans la réalité, on ferait une requête DB (Elastic/Vector) avec ces critères 
    # pour obtenir les content_scores, puis on appellerait HybridEngine.
    engine = HybridEngine(alpha=0.8)
    
    # Mock content scores based on criteria
    mock_content_scores = [
        {"vehicle_id": "v1", "content_score": 0.95},
        {"vehicle_id": "v2", "content_score": 0.85}
    ]
    mock_collab_scores = [
        {"vehicle_id": "v1", "collaborative_score": 0.4},
        {"vehicle_id": "v3", "collaborative_score": 0.9}
    ]
    
    # On force le cold_start si l'utilisateur est nouveau
    recs = engine.combine(
        content_scores=mock_content_scores,
        collaborative_scores=mock_collab_scores,
        cold_start=False
    )
    
    return MatchmakerResponse(
        extracted_criteria=criteria,
        recommendations=recs.dict()
    )
