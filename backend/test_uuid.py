from app.core.qdrant_client import get_qdrant_client
from app.core.config import settings

qdrant = get_qdrant_client()
qdrant.delete_collection(collection_name=settings.QDRANT_COLLECTION)
print("Collection dropped!")
