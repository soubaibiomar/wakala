import logging
import cv2
import numpy as np
from typing import Tuple, Dict, Any

from app.ml.vision.damage_detector import damage_detector

logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
    _has_yolo = True
except ImportError:
    _has_yolo = False
    logger.warning("ultralytics n'est pas installé. Fallback vers l'heuristique de dommages.")

class YoloDamageDetector:
    """
    Détecteur de dommages basé sur YOLOv8.
    Calcule le Score d'état (condition_score) en fonction des détections.
    """
    def __init__(self, model_path: str = "yolov8n.pt"):
        self.model = None
        self._model_path = model_path
        self._model_loaded = False
        self.use_fallback = not _has_yolo

    def _ensure_model(self):
        """Lazy-load the YOLO model on first use instead of at import time."""
        if self._model_loaded:
            return
        self._model_loaded = True
        if _has_yolo:
            try:
                self.model = YOLO(self._model_path)
                logger.info("Modèle YOLO chargé avec succès.")
            except Exception as e:
                logger.error(f"Erreur chargement YOLO ({e}). Fallback activé.")
                self.use_fallback = True

    def analyze_image(self, image: np.ndarray) -> Tuple[float, Dict[str, Any]]:
        """
        Analyse l'image et retourne un score d'état (0-100) ainsi que les métadonnées.
        """
        self._ensure_model()
        if image is None or image.size == 0:
            return 100.0, {"error": "Image vide"}

        # Vérification basique d'intégrité (Simulation Fraude : ex si l'image est trop petite)
        height, width = image.shape[:2]
        is_manipulated = False
        if width < 300 or height < 300:
            is_manipulated = True

        if self.use_fallback or self.model is None:
            # Fallback vers l'heuristique existante (Canny Edge detection)
            score = damage_detector.evaluate_condition(image)
            return score, {
                "method": "heuristic",
                "fraud_detected": is_manipulated,
                "anomalies": []
            }

        # --- Inférence YOLOv8 ---
        try:
            results = self.model(image, verbose=False)
            anomalies = []
            penalty = 0.0
            
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if conf > 0.5:
                    penalty += 5.0
                    anomalies.append({"class_id": cls_id, "confidence": conf})
            
            score = 100.0 - penalty
            score = max(20.0, min(100.0, score))

            # Ajustement si l'image est très floue (variance du Laplacien)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur_val = cv2.Laplacian(gray, cv2.CV_64F).var()
            if blur_val < 50:
                score = 0.0 # Rejet car trop flou
            
            return round(score, 1), {
                "method": "yolov8",
                "fraud_detected": is_manipulated,
                "anomalies": anomalies,
                "blur_variance": blur_val
            }
        except Exception as e:
            logger.error(f"Erreur d'inférence YOLO: {e}")
            score = damage_detector.evaluate_condition(image)
            return score, {"method": "heuristic_fallback", "fraud_detected": is_manipulated}

yolo_detector = YoloDamageDetector()
