"""
Détection d'anomalies — Isolation Forest.
Détecte les annonces frauduleuses ou les vendeurs suspects.
"""

from sklearn.ensemble import IsolationForest
import numpy as np


class AnomalyDetector:
    """Détecteur d'anomalies basé sur Isolation Forest."""

    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42,
        )
        self.is_fitted = False

    def fit(self, X: np.ndarray):
        """Entraîne le détecteur sur les données normales."""
        self.model.fit(X)
        self.is_fitted = True

    def predict(self, X: np.ndarray) -> list[dict]:
        """
        Prédit les anomalies.

        Returns:
            Liste de {index, is_anomaly, anomaly_score}
        """
        if not self.is_fitted:
            return []

        predictions = self.model.predict(X)
        scores = self.model.decision_function(X)

        return [
            {
                "index": i,
                "is_anomaly": bool(pred == -1),
                "anomaly_score": float(score),
            }
            for i, (pred, score) in enumerate(zip(predictions, scores))
        ]

    def compute_trust_score(self, features: np.ndarray) -> float:
        """
        Calcule un score de confiance (0-100) pour un vendeur/annonce.
        Basé sur le decision_function d'Isolation Forest.
        """
        if not self.is_fitted:
            return 50.0  # Score neutre par défaut

        score = self.model.decision_function(features.reshape(1, -1))[0]
        # Normalise le score IF [-0.5, 0.5] vers [0, 100]
        trust = max(0, min(100, (score + 0.5) * 100))
        return round(trust, 1)


anomaly_detector = AnomalyDetector()
