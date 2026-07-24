import asyncio
from typing import Optional
from app.ml.trust_engine.schemas import TrustScoreResult
from app.ml.trust_engine.photo_analyzer import analyze_photos
from app.ml.trust_engine.price_anomaly import detect_price_anomaly
from app.ml.trust_engine.seller_pattern import detect_seller_pattern
from app.models.vehicle import Vehicle

async def compute_trust_score(vehicle: Vehicle) -> TrustScoreResult:
    # 1. Prepare data
    vehicle_dict = {
        "price": vehicle.price,
        "year": vehicle.year,
        "mileage": vehicle.mileage,
        "engine_power_hp": vehicle.engine_power_hp,
        "doors": vehicle.doors,
        "seats": vehicle.seats,
        "condition_score": vehicle.condition_score,
        "brand": vehicle.brand,
        "model": vehicle.model,
        "fuel_type": vehicle.fuel_type,
        "body_type": vehicle.body_type,
        "transmission": vehicle.transmission,
        "city": vehicle.city,
    }
    
    images = []
    if getattr(vehicle, "images", None):
        images = [img.file_path for img in vehicle.images]
        
    user_id = str(getattr(vehicle, "user_id", ""))
    
    # 2. Run analyses in parallel
    photo_task = analyze_photos(images)
    price_task = detect_price_anomaly(vehicle_dict)
    seller_task = detect_seller_pattern(user_id)
    
    photo_score, price_score, seller_score = await asyncio.gather(
        photo_task, price_task, seller_task, return_exceptions=True
    )
    
    # Handle exceptions
    if isinstance(photo_score, Exception): photo_score = None
    if isinstance(price_score, Exception): price_score = None
    if isinstance(seller_score, Exception): seller_score = None
    
    # 3. Combine scores
    weights = {
        "price": 0.4,
        "seller": 0.4,
        "photo": 0.2
    }
    
    total_weight = 0.0
    total_score = 0.0
    
    if price_score is not None:
        total_score += price_score * weights["price"]
        total_weight += weights["price"]
    
    if seller_score is not None:
        total_score += seller_score * weights["seller"]
        total_weight += weights["seller"]
        
    if photo_score is not None:
        total_score += photo_score * weights["photo"]
        total_weight += weights["photo"]
        
    if total_weight == 0:
        final_score = 80.0 # Default fallback
        confidence = "low"
    else:
        final_score = total_score / total_weight
        if total_weight == 1.0:
            confidence = "high"
        elif total_weight >= 0.6:
            confidence = "medium"
        else:
            confidence = "low"
            
    return TrustScoreResult(
        vehicle_id=str(vehicle.id),
        trust_score=round(final_score, 1),
        price_anomaly_score=round(price_score, 1) if price_score is not None else None,
        seller_pattern_score=round(seller_score, 1) if seller_score is not None else None,
        photo_damage_score=round(photo_score, 1) if photo_score is not None else None,
        confidence=confidence
    )
