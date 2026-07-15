import base64
import io
import logging

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import numpy as np
import cv2

from app.ml.vision.plate_blur import PlateBlur
from app.ml.vision.yolo_detector import yolo_detector

router = APIRouter(prefix="/vision", tags=["Computer Vision"])
logger = logging.getLogger(__name__)

plate_blurrer = PlateBlur()

class VisionAnalysisResponse(BaseModel):
    condition_score: float
    fraud_detected: bool
    blur_variance: float
    anomalies_count: int
    image_base64: str  # L'image floutée renvoyée au frontend

@router.post("/analyze", response_model=VisionAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Reçoit une image de véhicule.
    1. Vérifie si elle est lisible.
    2. Applique le floutage de plaque (loi 09-08).
    3. Passe l'image floutée dans YOLOv8 (ou heuristique).
    4. Retourne l'image traitée en base64 et le score de condition.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image.")

    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Image invalide ou corrompue.")

        # 1. Floutage de la plaque
        blurred_img = plate_blurrer.blur_plate(img)

        # 2. Analyse YOLOv8 (Score d'état)
        score, metadata = yolo_detector.analyze_image(blurred_img)
        
        # 3. Préparer l'image encodée pour le retour (Silver Layer simulation)
        _, buffer = cv2.imencode('.jpg', blurred_img)
        img_b64 = base64.b64encode(buffer).decode('utf-8')

        return VisionAnalysisResponse(
            condition_score=score,
            fraud_detected=metadata.get("fraud_detected", False),
            blur_variance=metadata.get("blur_variance", 100.0),
            anomalies_count=len(metadata.get("anomalies", [])),
            image_base64=f"data:image/jpeg;base64,{img_b64}"
        )

    except Exception as e:
        logger.error(f"Erreur lors de l'analyse d'image: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne de traitement d'image.")
