import cv2
import numpy as np

class DamageDetector:
    """
    Détecteur basique de dommages (rayures/bosses) sur les véhicules.
    Pour un projet académique, utilise une heuristique de traitement
    d'image (Edge detection + contour analysis) plutôt qu'un modèle lourd.
    """

    def __init__(self):
        pass

    def evaluate_condition(self, image: np.ndarray) -> float:
        """
        Évalue la condition du véhicule (0-100).
        - Plus il y a de 'bruit' ou de contours irréguliers sur la carrosserie,
          plus le score baisse.
        """
        if image is None or image.size == 0:
            return 100.0
            
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Appliquer un flou pour réduire le bruit normal
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Détection de contours avec Canny
            edges = cv2.Canny(blurred, 50, 150)
            
            # Calcul de la densité des contours (approximation des défauts)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Un véhicule "propre" a peu de contours internes (sauf les portières, phares, etc.)
            # On suppose qu'une densité > 5% indique beaucoup de dommages/saleté
            # C'est une heuristique très simple.
            
            penalty = min(50.0, edge_density * 1000) # Ex: 0.02 (2%) -> 20 pts pénalité
            
            condition_score = 100.0 - penalty
            return round(max(50.0, condition_score), 1) # Score min à 50
        except Exception:
            return 85.0 # Score par défaut si erreur

damage_detector = DamageDetector()
