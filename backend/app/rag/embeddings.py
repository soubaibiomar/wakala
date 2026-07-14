"""
Embeddings — Génération et gestion des embeddings véhicules.
"""

from sentence_transformers import SentenceTransformer
from app.core.config import settings


class EmbeddingService:
    """Génère des embeddings pour les descriptions de véhicules."""

    def __init__(self):
        self._model = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        return self._model

    def embed_text(self, text: str) -> list[float]:
        """Encode un texte en vecteur d'embedding."""
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Encode un batch de textes."""
        return self.model.encode(texts).tolist()

    def embed_vehicle(self, vehicle: dict) -> list[float]:
        """
        Crée un embedding enrichi pour un véhicule en concaténant
        ses attributs clés en texte structuré.
        """
        text = (
            f"{vehicle.get('brand', '')} {vehicle.get('model', '')} "
            f"{vehicle.get('year', '')} {vehicle.get('fuel_type', '')} "
            f"{vehicle.get('body_type', '')} {vehicle.get('description', '')}"
        )
        return self.embed_text(text.strip())


embedding_service = EmbeddingService()
