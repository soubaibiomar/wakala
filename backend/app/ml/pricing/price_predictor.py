"""
Prédiction de prix — XGBoost.
Entraîné sur les données Gold layer (features véhicule → prix).
Plages attendues pour le marché marocain (MAD) :
  - Véhicules d'occasion : 40 000 – 400 000 MAD
  - Entrées/sorties bas de gamme : 40 000 – 100 000 MAD
  - Citadines/familiales : 80 000 – 250 000 MAD
  - SUV/premium : 180 000 – 400 000+MAD
"""

import xgboost as xgb
import numpy as np
import joblib
from pathlib import Path


class PricePredictor:
    """Prédicteur de prix XGBoost."""

    MODEL_PATH = Path(__file__).parent / "model" / "price_model.joblib"

    def __init__(self):
        self.model = None

    def load(self):
        """Charge le modèle pré-entraîné."""
        if self.MODEL_PATH.exists():
            self.model = joblib.load(self.MODEL_PATH)

    def train(self, X: np.ndarray, y: np.ndarray):
        """Entraîne le modèle XGBoost."""
        self.model = xgb.XGBRegressor(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )
        self.model.fit(X, y)

    def predict(self, features: np.ndarray) -> dict:
        """
        Prédit le prix et retourne un intervalle de confiance.

        Returns:
            {predicted_price, confidence_interval, features_importance}
        """
        if self.model is None:
            self.load()
            if self.model is None:
                return {"predicted_price": 0.0, "confidence_interval": (0.0, 0.0), "features_importance": {}}

        pred = self.model.predict(features.reshape(1, -1))[0]
        # Estimation de l'intervalle de confiance (±10% simplifié)
        margin = pred * 0.10
        importance = dict(zip(
            [f"feature_{i}" for i in range(features.shape[0])],
            self.model.feature_importances_.tolist() if hasattr(self.model, 'feature_importances_') else [],
        ))
        return {
            "predicted_price": float(pred),
            "confidence_interval": (float(pred - margin), float(pred + margin)),
            "features_importance": importance,
        }

    def save(self):
        """Sauvegarde le modèle entraîné."""
        self.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.MODEL_PATH)


price_predictor = PricePredictor()
