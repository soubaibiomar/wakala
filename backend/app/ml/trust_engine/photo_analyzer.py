import httpx
from typing import Optional
from app.ml.vision.damage_detector import damage_detector

import cv2
import numpy as np

async def analyze_photos(image_urls: list[str]) -> Optional[float]:
    if not image_urls:
        return None
        
    scores = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for url in image_urls[:3]: # Max 3 photos
            try:
                if url.startswith("http"):
                    resp = await client.get(url)
                    resp.raise_for_status()
                    img_array = np.asarray(bytearray(resp.content), dtype=np.uint8)
                    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                else:
                    img = cv2.imread(url)
                    
                if img is not None:
                    score = damage_detector.evaluate_condition(img)
                    scores.append(score)
            except Exception:
                continue
                
    if not scores:
        return None
    
    return sum(scores) / len(scores)
