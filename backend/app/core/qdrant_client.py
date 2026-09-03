import logging
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorDBClient:
    def __init__(self, host=None, port=6333, collection_name=None, url=None, api_key=None):
        self.collection_name = collection_name or settings.QDRANT_COLLECTION
        if not url and not host:
            logger.info("Qdrant host/url not configured; vector store features will be disabled.")
            self.client = None
            return
        try:
            self.client = (
                QdrantClient(url=url, api_key=api_key or None)
                if url
                else QdrantClient(host=host, port=port, api_key=api_key or None)
            )
            logger.info("Connected to Qdrant successfully")
            
            # Check if collection exists, if not create it
            dim = 1024 
            if not self.client.collection_exists(collection_name=self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {self.collection_name} with dim {dim}")
        except Exception as e:
            logger.warning(f"Failed to initialize Qdrant at startup (continuing gracefully): {e}")
            self.client = None

# Create singleton instance
qdrant_client = VectorDBClient(
    host=settings.QDRANT_HOST or None, 
    port=settings.QDRANT_PORT or 6333, 
    collection_name=settings.QDRANT_COLLECTION,
    url=settings.QDRANT_URL or None,
    api_key=settings.QDRANT_API_KEY or None,
)

def get_qdrant_client():
    return qdrant_client.client
