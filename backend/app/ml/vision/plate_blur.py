"""
ml/vision/plate_blur.py — Floutage de plaques d'immatriculation.
Format marocain : XXXXX-X-XX (5 chiffres - 1 lettre - 2 chiffres)
Détection par heuristique de contours (pas de modèle ML lourd).
"""

import io
from typing import Optional

import cv2
import numpy as np
from PIL import Image

MOROCCAN_PLATE_PATTERN = (
    r"\d{5}[\s-]?[A-Za-z][\s-]?\d{2}"
)


class PlateBlur:
    """Détection et floutage de plaque d'immatriculation marocaine.

    Utilise OpenCV (contours + ratio d'aspect) pour localiser
    la plaque dans une image, puis applique un flou gaussien.
    """

    MIN_AREA = 1500
    MAX_AREA = 30000
    ASPECT_RATIO_MIN = 2.0
    ASPECT_RATIO_MAX = 6.0

    def __init__(self, kernel_size: tuple = (51, 51)):
        self._kernel_size = kernel_size

    def _find_plate_contour(self, gray: np.ndarray) -> Optional[np.ndarray]:
        """Trouve le contour correspondant probablement à une plaque marocaine."""
        blurred = cv2.bilateralFilter(gray, 11, 17, 17)
        edges = cv2.Canny(blurred, 30, 200)

        contours, _ = cv2.findContours(
            edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.MIN_AREA or area > self.MAX_AREA:
                continue
            rect = cv2.minAreaRect(cnt)
            w, h = rect[1]
            if w == 0 or h == 0:
                continue
            aspect = max(w, h) / min(w, h)
            if self.ASPECT_RATIO_MIN <= aspect <= self.ASPECT_RATIO_MAX:
                return cv2.boxPoints(rect)

        return None

    def blur_plate(self, image: np.ndarray) -> np.ndarray:
        """Détecte et floute une plaque. Retourne l'image modifiée."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        contour = self._find_plate_contour(gray)

        if contour is not None:
            contour = np.int32(contour)
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(mask, [contour], -1, 255, -1)
            roi = cv2.bitwise_and(image, image, mask=mask)
            blurred_roi = cv2.GaussianBlur(roi, self._kernel_size, 0)
            result = np.where(mask[..., None] > 0, blurred_roi, image)
            return result

        return image

    def blur_plate_bytes(self, image_bytes: bytes) -> bytes:
        """Variante acceptant des bytes (PIL compatible)."""
        pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        numpy_img = np.array(pil)
        bgr = cv2.cvtColor(numpy_img, cv2.COLOR_RGB2BGR)
        result_bgr = self.blur_plate(bgr)
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        out_pil = Image.fromarray(result_rgb)
        buf = io.BytesIO()
        out_pil.save(buf, format="PNG")
        return buf.getvalue()
