from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.core.config import settings
from typing import Optional
import uuid


class VectorStore:
    def __init__(self):
        self._client: Optional[QdrantClient] = None
        self.collection_name = settings.QDRANT_COLLECTION

    @property
    def client(self) -> Optional[QdrantClient]:
        if self._client is None:
            if not settings.QDRANT_URL and not settings.QDRANT_HOST:
                return None
            try:
                self._client = (
                    QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY or None)
                    if settings.QDRANT_URL
                    else QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT or 6333, api_key=settings.QDRANT_API_KEY or None)
                )
            except Exception as e:
                self._client = None
        return self._client

    def ensure_collection(self, vector_size: int = 384):
        if not self.client:
            return
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if self.collection_name not in collections:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
        except Exception:
            pass

    def upsert(self, vehicle_id: str, embedding: list[float], metadata: dict):
        if not self.client:
            return
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=str(uuid.uuid5(uuid.NAMESPACE_DNS, vehicle_id)),
                        vector=embedding,
                        payload={"vehicle_id": vehicle_id, **metadata},
                    )
                ],
            )
        except Exception:
            pass

    def search(self, query_vector: list[float], limit: int = 10, filters: Optional[dict] = None) -> list[dict]:
        if not self.client:
            return []
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
            )
            return [
                {
                    "vehicle_id": hit.payload.get("id") or hit.payload.get("vehicle_id"),
                    "score": hit.score,
                    "metadata": hit.payload,
                }
                for hit in results
            ]
        except Exception:
            return []


vector_store = VectorStore()
