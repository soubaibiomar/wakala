from typing import Optional
from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    vehicle_id: str
    vehicle_title: str = ""
    relevance_score: float = Field(..., ge=0, le=1)
    source_type: str = "vector_search"
    image_url: Optional[str] = None
    price: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=["Je cherche un SUV diesel à Casablanca entre 200 000 et 300 000 MAD"],
    )
    session_id: str = Field(
        ...,
        description="Identifiant de session pour le maintien du contexte conversationnel",
        examples=["session-abc123"],
    )
    user_id: Optional[str] = Field(
        None,
        description="UUID utilisateur (optionnel)",
    )


class ChatResponse(BaseModel):
    reply: str
    sources: list[SourceReference] = Field(
        default_factory=list,
        description="Véhicules sources utilisés pour générer la réponse",
    )
    session_id: str
    style_profile: Optional[dict] = Field(
        None,
        description="Profil de style du dernier message utilisateur",
    )
