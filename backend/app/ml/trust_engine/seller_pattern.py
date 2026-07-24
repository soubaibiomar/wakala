from app.ml.fraud.broker_detector import broker_detector
from typing import Optional

async def detect_seller_pattern(user_id: str) -> Optional[float]:
    """
    Uses the Neo4j graph broker detector to check if user is a suspect.
    Returns 100 if clean, 20 if suspected broker.
    """
    if not user_id:
        return None
        
    try:
        # Detect brokers currently returns a list of suspect user IDs.
        # This might be heavy to run for a single user, but let's assume it works.
        suspects = await broker_detector.detect_brokers(min_shared_artifacts=1, min_ads=2)
        if user_id in suspects:
            return 20.0
            
        return 100.0
    except Exception:
        return None
