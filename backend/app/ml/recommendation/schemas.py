from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class RecommendationFilters(BaseModel):
    brand: Optional[str] = None
    city: Optional[str] = None
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    fuel_type: Optional[str] = None
    body_type: Optional[str] = None
    year_min: Optional[int] = Field(None, ge=1950)
    year_max: Optional[int] = Field(None, le=2030)
    mileage_max: Optional[int] = Field(None, ge=0)


class RecommendationRequest(BaseModel):
    query: Optional[str] = Field(
        None,
        description="Texte libre décrivant le véhicule recherché",
        examples=["SUV diesel entre 200 000 et 300 000 MAD à Casablanca"],
    )
    filters: RecommendationFilters = Field(default_factory=RecommendationFilters)
    user_id: Optional[str] = Field(
        None,
        description="UUID utilisateur (active le collaboratif si fourni)",
    )
    page: int = Field(1, ge=1, description="Numéro de page")
    page_size: int = Field(20, ge=1, le=100, description="Éléments par page")


class ScoreBreakdown(BaseModel):
    content: float = Field(..., ge=0, le=1)
    collaborative: float = Field(..., ge=0, le=1)


class RecommendationResult(BaseModel):
    vehicle_id: str
    match_score: float = Field(..., ge=0, le=100)
    score_breakdown: ScoreBreakdown


class RecommendationResponse(BaseModel):
    cold_start: bool = Field(
        False,
        description="True lorsqu'aucun historique utilisateur exploitable n'est disponible",
    )
    items: list[RecommendationResult]
    total: int
    page: int
    page_size: int
    method: str = Field(
        ...,
        description="Méthode utilisée : 'content-based', 'hybrid', ou 'cold-start'",
    )
