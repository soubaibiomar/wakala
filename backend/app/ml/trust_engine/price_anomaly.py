from app.ml.pricing.price_model import price_model
from typing import Optional

async def detect_price_anomaly(vehicle_dict: dict) -> Optional[float]:
    """
    Returns a score 0-100 where 100 is perfectly normal price,
    and lower scores mean suspicious (anomalously low or too high).
    """
    try:
        prediction = price_model.predict(vehicle_dict)
        pred_price = prediction.get("predicted_price")
        if not pred_price:
            return None
            
        actual_price = vehicle_dict.get("price")
        if not actual_price:
            return None
            
        diff_ratio = (actual_price - pred_price) / pred_price
        
        # If actual price is > 30% cheaper than predicted, it's very suspicious
        if diff_ratio < -0.30:
            return max(0.0, 100.0 + (diff_ratio * 200)) # e.g. -0.4 -> 20
        elif diff_ratio > 0.30:
            return 80.0 # Just expensive, not necessarily a scam, but less trusted
            
        return 100.0 - abs(diff_ratio * 100)
    except Exception:
        return None
