"""
schemas/vehicle_schema.py — Schémas Pydantic pour les véhicules.
"""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.user_schema import UserReadBrief


# ─── Types ─────────────────────────────────────────────────────

FuelType = Literal[
    "essence", "diesel", "hybride", "hybride_rechargeable",
    "electrique", "gpl", "hydrogene",
]
BodyType = Literal[
    "citadine", "berline", "suv", "break", "coupe",
    "cabriolet", "monospace", "utilitaire", "pick_up",
]
TransmissionType = Literal["manuelle", "automatique", "semi_auto"]


# ─── Création ──────────────────────────────────────────────────

class VehicleCreate(BaseModel):
    """Schéma de création d'un véhicule (seller authentifié)."""
    brand: str = Field(..., min_length=1, max_length=100, examples=["Peugeot"])
    model: str = Field(..., min_length=1, max_length=100, examples=["3008"])
    version: Optional[str] = Field(None, max_length=200, examples=["GT Line 1.6 BlueHDi 130"])
    year: int = Field(..., ge=1950, le=2030, examples=[2022])
    mileage: int = Field(..., ge=0, examples=[45000])
    fuel_type: FuelType = Field(..., examples=["diesel"])
    body_type: BodyType = Field(..., examples=["suv"])
    transmission: TransmissionType = Field("manuelle", examples=["manuelle"])
    engine_power_hp: Optional[int] = Field(None, ge=1, examples=[130])
    color: Optional[str] = Field(None, max_length=50, examples=["Gris Artense"])
    doors: int = Field(5, ge=2, le=7)
    seats: int = Field(5, ge=1, le=9)
    city: str = Field(..., min_length=1, max_length=150, examples=["Paris"])
    postal_code: Optional[str] = Field(None, max_length=10, examples=["75001"])
    price: float = Field(..., gt=0, examples=[28500.00])
    description: Optional[str] = Field(None, examples=["SUV familial, très bon état"])


# ─── Lecture ───────────────────────────────────────────────────

class VehicleRead(BaseModel):
    """Schéma de lecture complet d'un véhicule."""
    id: UUID
    seller_id: UUID
    brand: str
    model: str
    version: Optional[str] = None
    year: int
    mileage: int
    fuel_type: str
    body_type: str
    transmission: str
    engine_power_hp: Optional[int] = None
    color: Optional[str] = None
    doors: int
    seats: int
    city: str
    postal_code: Optional[str] = None
    price: float
    description: Optional[str] = None

    # Scores IA (nullable — remplis par les modules ML)
    predicted_price: Optional[float] = None
    price_confidence: Optional[float] = None
    condition_score: Optional[float] = None
    popularity_score: Optional[float] = None

    images: Optional[list[dict]] = None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VehicleReadWithSeller(VehicleRead):
    """Véhicule avec les informations vendeur imbriquées."""
    seller: Optional[UserReadBrief] = None


class VehicleReadBrief(BaseModel):
    """Version allégée pour les listes et les cartes catalogue."""
    id: UUID
    brand: str
    model: str
    year: int
    mileage: int
    fuel_type: str
    body_type: str
    city: str
    price: float
    condition_score: Optional[float] = None
    popularity_score: Optional[float] = None
    images: Optional[list[dict]] = None

    model_config = {"from_attributes": True}


# ─── Mise à jour ──────────────────────────────────────────────

class VehicleUpdate(BaseModel):
    """Schéma de mise à jour partielle d'un véhicule."""
    version: Optional[str] = None
    mileage: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, gt=0)
    city: Optional[str] = Field(None, max_length=150)
    postal_code: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    engine_power_hp: Optional[int] = None


# ─── Réponse paginée ──────────────────────────────────────────

class VehicleListResponse(BaseModel):
    """Réponse paginée pour la liste de véhicules."""
    items: list[VehicleRead]
    total: int
    page: int
    page_size: int
    pages: int
