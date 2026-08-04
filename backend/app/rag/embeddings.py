"""
Embeddings — Génération et gestion des embeddings véhicules.
"""

from langchain_community.embeddings import OllamaEmbeddings
from app.core.config import settings

class EmbeddingService:
    """Génère des embeddings pour les descriptions de véhicules via Ollama (bge-m3)."""

    def __init__(self):
        self._model = None

    @property
    def model(self) -> OllamaEmbeddings:
        if self._model is None:
            _ollama_base = settings.OLLAMA_BASE_URL.replace("/v1", "") if settings.OLLAMA_BASE_URL else "http://localhost:11434"
            self._model = OllamaEmbeddings(
                base_url=_ollama_base,
                model="bge-m3"
            )
        return self._model

    def embed_text(self, text: str) -> list[float]:
        """Encode un texte en vecteur d'embedding."""
        return self.model.embed_query(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Encode un batch de textes."""
        return self.model.embed_documents(texts)

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
