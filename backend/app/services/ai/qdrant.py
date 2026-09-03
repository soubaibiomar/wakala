try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.http import models as qmodels
    QDRANT_AVAILABLE = True
except ImportError:
    AsyncQdrantClient = None
    qmodels = None
    QDRANT_AVAILABLE = False

from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Initialize Qdrant client asynchronously
qdrant_client = (
    AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
    if settings.QDRANT_URL
    else AsyncQdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
) if QDRANT_AVAILABLE else None

async def ensure_collection_exists(collection_name: str, vector_size: int = 1024):
    """
    Ensure that the Qdrant collection exists.
    If not, create it with the specified vector size (1024 for bge-m3).
    """
    try:
        # Check if collection exists
        collections = await qdrant_client.get_collections()
        exists = any(col.name == collection_name for col in collections.collections)
        
        if not exists:
            logger.info(f"Création de la collection Qdrant '{collection_name}' avec la taille de vecteur {vector_size}...")
            await qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=qmodels.VectorParams(
                    size=vector_size,
                    distance=qmodels.Distance.COSINE
                )
            )
            # Create a payload index on price for efficient filtering
            await qdrant_client.create_payload_index(
                collection_name=collection_name,
                field_name="price",
                field_schema=qmodels.PayloadSchemaType.FLOAT,
            )
            logger.info(f"Collection '{collection_name}' créée avec succès.")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de Qdrant: {e}")
        raise

def get_qdrant_client() -> AsyncQdrantClient:
    return qdrant_client
