import numpy as np
from sklearn.cluster import KMeans
import joblib
from pathlib import Path

class BuyerSegmenter:
    """
    Segmentation des acheteurs (K-Means) basée sur :
    - Budget moyen
    - Fréquence de visite
    - Types de véhicules consultés (ex: proportion de SUV)
    """
    
    MODEL_PATH = Path(__file__).parent / "model" / "kmeans_model.joblib"
    
    def __init__(self, n_clusters: int = 4):
        self.n_clusters = n_clusters
        self.model = None
        self.cluster_labels = {
            0: "Budget Eco",
            1: "Famille / SUV",
            2: "Premium / Luxe",
            3: "Citadin régulier"
        }

    def load(self):
        if self.MODEL_PATH.exists():
            self.model = joblib.load(self.MODEL_PATH)
            
    def train(self, X: np.ndarray):
        """Entraîne le modèle K-Means."""
        self.model = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.model.fit(X)
        self.save()

    def predict_segment(self, features: np.ndarray) -> str:
        """
        Assigne un segment à un utilisateur donné ses features
        (budget, freq, prop_suv, etc.).
        """
        if self.model is None:
            self.load()
            if self.model is None:
                return "Nouveau"
        
        try:
            cluster_id = self.model.predict(features.reshape(1, -1))[0]
            return self.cluster_labels.get(cluster_id, "Inconnu")
        except Exception:
            return "Nouveau"

    def save(self):
        self.MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.MODEL_PATH)

buyer_segmenter = BuyerSegmenter()
