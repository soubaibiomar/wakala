"""
routes_pricing.py — Price prediction endpoints.

POST /api/vehicles/predict-price   → predict price for one vehicle
POST /api/vehicles/predict-price/batch → predict for multiple vehicles
GET  /api/vehicles/predict-price/model-info  → model metadata
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.ml.pricing.price_model import price_model

router = APIRouter(prefix="/vehicles", tags=["Prédiction de prix"])


class PricePredictionInput(BaseModel):
    brand: str = Field(..., example="Renault", description="Marque du véhicule")
    model: str = Field(..., example="Clio", description="Modèle")
    year: int = Field(..., ge=1990, le=2030, example=2020)
    # PIVOT: mileage removed (new vehicles only)
    fuel_type: str = Field(..., example="diesel")
    body_type: str = Field(..., example="berline")
    transmission: str = Field("manuelle", example="manuelle")
    engine_power_hp: Optional[int] = Field(None, example=90)
    doors: int = Field(5, ge=1, le=9)
    seats: int = Field(5, ge=1, le=9)
    city: str = Field(..., example="Casablanca")
    # PIVOT: condition_score removed (new vehicles only)
    month: Optional[int] = Field(None, ge=1, le=12, description="Mois de mise en vente (pour la saisonnalité)")


class ConfidenceInterval(BaseModel):
    low: float
    high: float


class PricePredictionResponse(BaseModel):
    predicted_price: float
    confidence_interval: ConfidenceInterval
    method: str
    features_importance: dict[str, float]
    market_trend: str = Field("Stable", description="Indicateur de tendance du marché (ex: Stable, À la hausse, À la baisse)")


class BatchPredictionRequest(BaseModel):
    vehicles: list[PricePredictionInput]


class BatchPredictionItem(BaseModel):
    input: PricePredictionInput
    prediction: PricePredictionResponse


class BatchPredictionResponse(BaseModel):
    items: list[BatchPredictionItem]
    total: int


class ModelInfoResponse(BaseModel):
    trained: bool
    n_features: int
    features: list[str]


# Alias for the new requirement POST /api/v1/pricing/estimate
@router.post("/estimate", response_model=PricePredictionResponse)
@router.post("/predict-price", response_model=PricePredictionResponse)
async def predict_price(input_data: PricePredictionInput):
    try:
        result = price_model.predict(input_data.model_dump())
        
        # PIVOT: Simplified trend logic for new cars (no mileage)
        trend = "Stable"
        current_year = 2026
        age = current_year - input_data.year
        if age == 0:
            trend = "Très demandé"
        elif age <= 1:
            trend = "Demandé"

        return PricePredictionResponse(
            predicted_price=result["predicted_price"],
            confidence_interval=ConfidenceInterval(
                low=result["confidence_interval"][0],
                high=result["confidence_interval"][1],
            ),
            method=result["method"],
            features_importance=result["features_importance"],
            market_trend=trend
        )
    except Exception as e:
        import logging
        logging.error(f"Erreur prédiction: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne lors de la prédiction de prix")


@router.post("/predict-price/batch", response_model=BatchPredictionResponse)
async def batch_predict_price(request: BatchPredictionRequest):
    items = []
    for v in request.vehicles:
        result = price_model.predict(v.model_dump())
        items.append(
            BatchPredictionItem(
                input=v,
                prediction=PricePredictionResponse(
                    predicted_price=result["predicted_price"],
                    confidence_interval=ConfidenceInterval(
                        low=result["confidence_interval"][0],
                        high=result["confidence_interval"][1],
                    ),
                    method=result["method"],
                    features_importance=result["features_importance"],
                    market_trend="Stable",
                ),
            )
        )
    return BatchPredictionResponse(items=items, total=len(items))


@router.get("/predict-price/model-info", response_model=ModelInfoResponse)
async def model_info():
    return ModelInfoResponse(
        trained=price_model.model is not None,
        n_features=len(price_model.feature_columns),
        features=price_model.feature_columns or [],
    )
