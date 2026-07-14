"""
Module NLP — Analyse de sentiment et recherche sémantique.
Utilise sentence-transformers pour les embeddings.
"""

from sentence_transformers import SentenceTransformer
from app.core.config import settings


class NLPService:
    """Service NLP pour embeddings et analyse de texte."""

    def __init__(self):
        self.model = None

    def load_model(self):
        """Charge le modèle d'embeddings (lazy loading)."""
        if self.model is None:
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def encode(self, texts: list[str]) -> list[list[float]]:
        """Encode une liste de textes en vecteurs d'embeddings."""
        self.load_model()
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def analyze_query(self, query: str) -> dict:
        """
        Analyse une requête en langage naturel pour en extraire :
        - L'intention (achat, comparaison, information)
        - Les critères détectés (budget, carburant, usage, etc.)
        """
        # TODO: NER + classification d'intention
        return {
            "intent": "search",
            "extracted_criteria": {},
            "embedding": self.encode([query])[0],
        }


nlp_service = NLPService()
