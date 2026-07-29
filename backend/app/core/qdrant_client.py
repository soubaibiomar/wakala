import logging
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from app.core.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

class VectorDBClient:
    def __init__(self, host, port, collection_name):
        self.collection_name = collection_name
        try:
            self.client = QdrantClient(host=host, port=port)
            logger.info("Connected to Qdrant successfully")
            
            # Check if collection exists, if not create it
            # The ollama model `bge-m3:latest` has dimension 1024
            dim = 1024 
            if not self.client.collection_exists(collection_name=self.collection_name):
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {self.collection_name} with dim {dim}")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {e}")
            self.client = None

# Create singleton instance
qdrant_client = VectorDBClient(
    host=settings.QDRANT_HOST, 
    port=settings.QDRANT_PORT, 
    collection_name=settings.QDRANT_COLLECTION
)

def get_qdrant_client():
    return qdrant_client.client
