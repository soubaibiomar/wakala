"""
schemas/listing_schema.py — Schémas Pydantic pour les annonces.
"""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.vehicle_schema import VehicleReadBrief


ListingStatus = Literal["draft", "active", "sold", "expired", "flagged"]


# ─── Création ──────────────────────────────────────────────────

class ListingCreate(BaseModel):
    """Schéma de création d'une annonce."""
    vehicle_id: UUID
    images_urls: list[str] = Field(default_factory=list, max_length=20)
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    status: ListingStatus = Field("draft")


# ─── Lecture ───────────────────────────────────────────────────

class ListingRead(BaseModel):
    """Schéma de lecture complet d'une annonce."""
    id: UUID
    vehicle_id: UUID
    status: str
    published_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    # Anti-fraude (nullable)
    fraud_score: Optional[float] = None
    fraud_flags: list = []
    is_manually_reviewed: bool = False

    # Média
    images_urls: list[str] = []
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None

    # Stats
    view_count: int = 0
    contact_count: int = 0
    favorite_count: int = 0

    # Promotion
    is_boosted: bool = False
    boost_expires_at: Optional[datetime] = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ListingReadWithVehicle(ListingRead):
    """Annonce avec les infos véhicule imbriquées."""
    vehicle: Optional[VehicleReadBrief] = None


# ─── Mise à jour ──────────────────────────────────────────────

class ListingUpdate(BaseModel):
    """Mise à jour partielle d'une annonce."""
    status: Optional[ListingStatus] = None
    images_urls: Optional[list[str]] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    expires_at: Optional[datetime] = None
