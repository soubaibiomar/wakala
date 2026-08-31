from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class EquipmentFeatureInput(BaseModel):
    category: str = Field(..., description="Sécurité, Confort, Multimédia, Extérieur")
    name: str = Field(..., description="Nom de l'équipement")
    status: str = Field("SERIE", description="SERIE, OPTION, NON_DISPO")
    option_price_mad: Optional[float] = 0.0


class ColorOption(BaseModel):
    name: str
    hex: str
    price_mad: Optional[float] = 0.0


class PowertrainInput(BaseModel):
    name: str = Field(..., description="e.g. 1.5 dCi 115, 1.2 PureTech 130")
    fuel_type: str = Field(..., description="DIESEL, ESSENCE, HYBRIDE, ELECTRIQUE, GPL")
    fiscal_power_cv: int = Field(..., ge=1, le=50, description="Puissance fiscale CV")
    engine_power_hp: Optional[int] = Field(None, ge=30, le=1500)
    torque_nm: Optional[int] = None
    transmission: str = Field("MANUELLE", description="MANUELLE, AUTOMATIQUE, EDC, E-CVT, BVA8")
    drivetrain: Optional[str] = "FWD"
    consumption_l_100: Optional[float] = None
    co2_emissions_g_km: Optional[int] = None
    battery_capacity_kwh: Optional[float] = None
    electric_range_km: Optional[int] = None


class NormalizedTrimContract(BaseModel):
    brand_name: str
    brand_origin: Optional[str] = None
    brand_logo_url: Optional[str] = None
    
    model_name: str
    body_type: str = Field(..., description="SUV, Citadine, Berline, Break, Utilitaire")
    year_start: Optional[int] = 2024
    
    trim_name: str
    powertrain: PowertrainInput
    
    price_new_mad: float = Field(..., gt=50000, lt=10000000)
    promo_price_mad: Optional[float] = None
    is_promo: bool = False
    
    warranty_years: Optional[int] = 3
    warranty_km: Optional[int] = 100000
    trunk_capacity_l: Optional[int] = None
    euro_ncap_stars: Optional[int] = None
    image_url: Optional[str] = None
    gallery_urls: Optional[List[str]] = Field(default_factory=list)
    available_colors: Optional[List[ColorOption]] = Field(default_factory=list)
    equipment: Optional[List[EquipmentFeatureInput]] = Field(default_factory=list)

    @field_validator("brand_name", "model_name", "trim_name")
    def strip_strings(cls, v: str) -> str:
        return v.strip()
