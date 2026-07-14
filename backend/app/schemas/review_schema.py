"""
schemas/review_schema.py — Schémas Pydantic pour les avis.
"""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user_schema import UserReadBrief


ReviewTargetType = Literal["vehicle", "seller"]


# ─── Création ──────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    """Schéma de création d'un avis."""
    target_type: ReviewTargetType
    vehicle_id: Optional[UUID] = None
    seller_id: Optional[UUID] = None
    rating: int = Field(..., ge=1, le=5, examples=[4])
    title: Optional[str] = Field(None, max_length=200, examples=["Très bon véhicule"])
    comment: str = Field(..., min_length=10, max_length=5000, examples=["Véhicule en excellent état..."])


# ─── Lecture ───────────────────────────────────────────────────

class ReviewRead(BaseModel):
    """Schéma de lecture d'un avis."""
    id: UUID
    author_id: UUID
    target_type: str
    vehicle_id: Optional[UUID] = None
    seller_id: Optional[UUID] = None
    rating: int
    title: Optional[str] = None
    comment: str

    # NLP (nullable — rempli par le module NLP)
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    key_phrases: Optional[list[str]] = None

    # Modération
    is_approved: bool
    is_flagged: bool

    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewReadWithAuthor(ReviewRead):
    """Avis avec les infos de l'auteur."""
    author: Optional[UserReadBrief] = None


# ─── Mise à jour ──────────────────────────────────────────────

class ReviewUpdate(BaseModel):
    """Mise à jour partielle d'un avis (par l'auteur)."""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=200)
    comment: Optional[str] = Field(None, min_length=10, max_length=5000)
