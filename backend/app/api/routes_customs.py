from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import numpy as np

from app.services.customs_service import calculate_customs
from app.rag.customs_chain import customs_chain
from app.ml.pricing.price_predictor import price_predictor

router = APIRouter(prefix="/customs", tags=["Dédouanement"])

class CustomsRequest(BaseModel):
    brand: str = Field(..., description="Marque du véhicule")
    model: str = Field(..., description="Modèle du véhicule")
    year: int = Field(..., description="Année de première mise en circulation")
    fuel_type: str = Field(..., description="Type de carburant (Diesel, Essence, Hybride)")
    fiscal_power: int = Field(..., description="Puissance fiscale (CV)")
    origin_eu: bool = Field(True, description="Vrai si origine UE (accord libre échange)")
    purchase_price_origin: float = Field(..., description="Prix d'achat dans le pays d'origine (en MAD)")

class CustomsResponse(BaseModel):
    financial_breakdown: dict
    local_market_price: float
    ai_verdict: str

@router.post("/calculate", response_model=CustomsResponse, summary="Calculer la douane et la rentabilité")
async def calculate_customs_endpoint(request: CustomsRequest):
    """
    Calcule les droits de douane et interroge l'IA pour évaluer la rentabilité 
    de l'importation par rapport au marché local.
    """
    # 1. Calcul des frais de douane
    financial_breakdown = calculate_customs(
        purchase_price=request.purchase_price_origin,
        age_years=2024 - request.year, # Approximation de l'âge
        fuel_type=request.fuel_type,
        fiscal_power=request.fiscal_power,
        origin_eu=request.origin_eu
    )
    
    # 2. Estimation Argus Local (Mock features base)
    # L'Argus Intelligent a besoin de : ['year', 'mileage', 'brand_encode', 'fuel_encode', 'transmission_encode', 'condition_score', 'month']
    # Pour ce calculateur, on va simuler ou appeler le predictor de base
    # (En production, un matching plus complexe est requis)
    try:
        # Valeurs mockées pour l'exemple (kilométrage 50000)
        local_market_price = price_predictor.predict_price(
            brand=request.brand,
            fuel_type=request.fuel_type,
            transmission="Manuelle", # fallback
            year=request.year,
            mileage=50000,
            condition_score=85
        )
    except Exception as e:
        local_market_price = request.purchase_price_origin * 1.5 # Fallback approximatif
        
    # 3. Verdict IA de rentabilité
    ai_verdict = await customs_chain.generate_verdict(
        vehicle_data={
            "brand": request.brand,
            "model": request.model,
            "year": request.year,
            "fuel_type": request.fuel_type,
            "fiscal_power": request.fiscal_power
        },
        financial_data=financial_breakdown,
        local_market_price=local_market_price
    )
    
    return {
        "financial_breakdown": financial_breakdown,
        "local_market_price": round(local_market_price, 2),
        "ai_verdict": ai_verdict
    }
