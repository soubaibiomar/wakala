from pydantic import BaseModel, Field
from typing import Optional

class SearchRequest(BaseModel):
    query: str = Field(..., description="Texte de recherche libre")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    user_id: Optional[str] = Field(None, description="ID de l'utilisateur (pour le filtrage collaboratif)")
    quiz_answers: Optional[dict] = Field(None, description="Réponses optionnelles au quiz Matchmaker")

class RankedResult(BaseModel):
    vehicle_id: str
    match_score: float
    badges: list[str]
    content_score: float
    collaborative_score: float
