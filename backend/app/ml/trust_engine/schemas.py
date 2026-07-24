from pydantic import BaseModel, Field
from typing import Optional

class TrustScoreResult(BaseModel):
    vehicle_id: str
    trust_score: float = Field(..., description="Score global de 0 à 100")
    price_anomaly_score: Optional[float] = Field(None, description="Score d'anomalie de prix (0-100)")
    seller_pattern_score: Optional[float] = Field(None, description="Score du vendeur (0-100)")
    photo_damage_score: Optional[float] = Field(None, description="Score des photos (0-100)")
    confidence: str = Field(..., description="high, medium, low selon les signaux disponibles")
