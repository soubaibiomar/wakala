"""
schemas/vehicle_option_schema.py — Schémas Pydantic pour les options, couleurs et configurateur.
"""

from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class VehicleOptionRead(BaseModel):
    """Schéma d'une option ou d'un accessoire d'un véhicule."""
    id: UUID
    vehicle_id: UUID
    category: str = Field(..., description="accessoire | couleur | jante | sellerie | pack")
    name: str
    price_delta: float = Field(..., description="Supplément en MAD ou 0 si inclus")
    is_default: bool
    image_reference: Optional[str] = Field(None, description="Nom de fichier ou identifiant 3D")

    model_config = {"from_attributes": True}


class VehicleColorRead(BaseModel):
    """Schéma d'un coloris disponible pour un véhicule."""
    id: UUID
    vehicle_id: UUID
    color_name: str
    hex_code: str
    price_delta: float = Field(0.0, description="Supplément couleur en MAD ou 0 si de série")
    is_default: bool

    model_config = {"from_attributes": True}


class VehicleWakalaScoreRead(BaseModel):
    """Schéma des notes d'évaluation et scores Wakala (1-5)."""
    space_score: Optional[float] = None
    safety_score: Optional[float] = None
    real_cost_score: Optional[float] = None
    access_price_score: Optional[float] = None
    city_practicality_score: Optional[float] = None
    performance_score: Optional[float] = None
    ecology_score: Optional[float] = None
    offroad_score: Optional[float] = None
    overall_score: Optional[float] = None
    data_reliability: Optional[str] = None
    observations: Optional[str] = None
    source_note: Optional[str] = None

    model_config = {"from_attributes": True}


class VehicleConfiguratorOptionsResponse(BaseModel):
    """Réponse complète pour le configurateur : couleurs et options par catégorie."""
    vehicle_id: UUID
    brand: str
    model: str
    version: Optional[str] = None
    base_price: float
    colors: List[VehicleColorRead] = []
    options: List[VehicleOptionRead] = []
    options_by_category: Dict[str, List[VehicleOptionRead]] = {}
    wakala_scores: Optional[VehicleWakalaScoreRead] = None

    model_config = {"from_attributes": True}
