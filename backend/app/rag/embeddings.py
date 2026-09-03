"""
Embeddings — Génération et gestion des embeddings véhicules.
"""

import hashlib

EMBEDDING_DIMENSION = 1024

class EmbeddingService:
    """Generate dependency-free vectors for the catalogue text."""

    def __init__(self):
        self._model = None

    def embed_text(self, text: str) -> list[float]:
        """Encode un texte en vecteur normalisé de dimension fixe."""
        vector = [0.0] * EMBEDDING_DIMENSION
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIMENSION
            vector[index] += 1.0 if digest[4] % 2 else -1.0
        norm = sum(value * value for value in vector) ** 0.5 or 1.0
        return [value / norm for value in vector]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Encode un batch de textes."""
        return [self.embed_text(text) for text in texts]

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
