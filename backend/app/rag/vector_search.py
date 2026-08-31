from typing import Optional

REVIEW_COLLECTION = "review_embeddings"
SIMILARITY_THRESHOLD = 0.35


def _get_vector_store():
    from app.rag.vector_store import vector_store
    return vector_store


def _get_embedding_service():
    from app.rag.embeddings import embedding_service
    return embedding_service


def compute_query_embedding(query: str) -> list[float]:
    """Compute the embedding for a query string once, to reuse across searches."""
    emb = _get_embedding_service()
    return emb.embed_text(query)


def search_vehicles(
    query: str,
    limit: int = 5,
    threshold: float = SIMILARITY_THRESHOLD,
    precomputed_embedding: Optional[list[float]] = None,
) -> list[dict]:
    try:
        vs = _get_vector_store()
        embedding = precomputed_embedding or compute_query_embedding(query)
        results = vs.search(embedding, limit=limit)
        return [
            {
                "vehicle_id": r["vehicle_id"],
                "score": r["score"],
                "metadata": r.get("metadata", {}),
            }
            for r in results
            if r.get("score", 0) >= threshold and r.get("vehicle_id")
        ]
    except Exception:
        return []


def search_reviews(
    query: str,
    limit: int = 3,
    threshold: float = SIMILARITY_THRESHOLD,
    precomputed_embedding: Optional[list[float]] = None,
) -> list[dict]:
    try:
        vs = _get_vector_store()
        embedding = precomputed_embedding or compute_query_embedding(query)
        review_store = vs.client
        collections = [c.name for c in review_store.get_collections().collections]
        if REVIEW_COLLECTION not in collections:
            return []
        results = review_store.search(
            collection_name=REVIEW_COLLECTION,
            query_vector=embedding,
            limit=limit,
        )
        return [
            {
                "review_id": str(hit.id),
                "vehicle_id": hit.payload.get("vehicle_id", ""),
                "text": hit.payload.get("comment", ""),
                "rating": hit.payload.get("rating", 0),
                "score": hit.score,
            }
            for hit in results
            if hit.score >= threshold
        ]
    except Exception:
        return []
