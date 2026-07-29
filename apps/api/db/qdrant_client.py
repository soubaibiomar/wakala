"""
apps/api/db/qdrant_client.py
Client Qdrant pour la recherche vectorielle (contenu).

Collection : annonces_vecteurs
  - Distance : Cosinus
  - Dimension : 1024 (bge-m3 standard via Ollama)
  - HNSW natif Qdrant : m=16, ef_construct=100

Formule de similarité (calculée par Qdrant, pas par nous) :
  Cos(θ) = Σ(A_i × B_i) / (√Σ(A_i²) × √Σ(B_i²))
  où A = vecteur utilisateur, B = vecteur annonce, i parcourt chaque dimension.
"""
import os
import logging
from apps.api.config import EMBEDDING_DIMENSION, HNSW_M, HNSW_EF_CONSTRUCT

logger = logging.getLogger("wakala.db.qdrant")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = "annonces_vecteurs"


class QdrantVectorClient:
    """
    Client Qdrant pour Wakala.
    Gère la création de collection, l'upsert de vecteurs,
    et la recherche cosinus filtrée par IDs.

    Les imports qdrant-client sont différés pour permettre
    l'exécution des tests avec des mocks sans dépendance installée.
    """

    def __init__(self, host: str | None = None, port: int | None = None):
        self._host = host or QDRANT_HOST
        self._port = port or QDRANT_PORT
        self._client = None

    def _get_client(self):
        if self._client is None:
            from qdrant_client import QdrantClient
            self._client = QdrantClient(host=self._host, port=self._port)
        return self._client

    def create_collection(self, collection_name: str = COLLECTION_NAME):
        """
        Crée (ou recrée) la collection avec les paramètres HNSW configurés.
        Ne pas implémenter HNSW manuellement — Qdrant le gère nativement.
        """
        from qdrant_client.models import VectorParams, Distance, HnswConfigDiff

        self._get_client().recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,  # 1024 pour bge-m3
                distance=Distance.COSINE,
            ),
            hnsw_config=HnswConfigDiff(
                m=HNSW_M,               # 16
                ef_construct=HNSW_EF_CONSTRUCT,  # 100
            ),
        )
        logger.info(
            f"Collection '{collection_name}' créée : "
            f"dim={EMBEDDING_DIMENSION}, distance=COSINE, m={HNSW_M}, ef={HNSW_EF_CONSTRUCT}"
        )

    def upsert_vectors(
        self,
        car_ids: list[str],
        vectors: list[list[float]],
        collection_name: str = COLLECTION_NAME,
    ):
        """Insère ou met à jour les vecteurs d'annonces dans Qdrant."""
        from qdrant_client.models import PointStruct

        points = [
            PointStruct(
                id=i,
                vector=vec,
                payload={"car_id": car_id},
            )
            for i, (car_id, vec) in enumerate(zip(car_ids, vectors))
        ]
        self._get_client().upsert(collection_name=collection_name, points=points)

    def search(
        self,
        collection_name: str,
        query_vector: list[float],
        filter_ids: list[str],
        top_k: int = 20,
    ) -> dict[str, float]:
        """
        Recherche cosinus dans Qdrant, restreinte aux IDs pré-filtrés
        par les hard_filters SQL (filtre natif Qdrant, pas de post-traitement Python).

        Formule (calculée nativement par Qdrant) :
        Cos(θ) = Σ(A_i × B_i) / (√Σ(A_i²) × √Σ(B_i²))
        où A = vecteur utilisateur (query), B = vecteur annonce, i = dimension embedding.

        Args:
            collection_name: nom de la collection Qdrant
            query_vector: vecteur d'embedding de la requête utilisateur
            filter_ids: IDs autorisés (résultat du filtrage SQL)
            top_k: nombre maximal de résultats

        Returns:
            {car_id: similarity_score} trié par score descendant
        """
        from qdrant_client.models import Filter, FieldCondition, MatchAny, SearchParams

        # Filtre natif Qdrant : restreint la recherche aux IDs autorisés
        qdrant_filter = Filter(
            must=[
                FieldCondition(
                    key="car_id",
                    match=MatchAny(any=filter_ids),
                )
            ]
        )

        results = self._get_client().search(
            collection_name=collection_name,
            query_vector=query_vector,
            query_filter=qdrant_filter,
            limit=top_k,
            search_params=SearchParams(exact=False),  # Utilise HNSW
        )

        return {
            hit.payload["car_id"]: hit.score
            for hit in results
        }
