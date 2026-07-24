import logging
from qdrant_client.http import models as qmodels

from app.core.config import settings
from app.models.vehicle import Vehicle
from app.services.ai.qdrant import get_qdrant_client
from app.services.ai.ingestion import generate_vehicle_description
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger(__name__)

async def upsert_vehicle_to_qdrant(vehicle: Vehicle):
    """
    Met à jour ou insère un véhicule unique dans Qdrant de manière asynchrone.
    """
    try:
        qdrant = get_qdrant_client()
        embeddings_model = OpenAIEmbeddings(
            model="text-embedding-3-small", 
            openai_api_key=settings.OPENAI_API_KEY
        )

        text_content = await generate_vehicle_description(vehicle)
        vector = await embeddings_model.aembed_query(text_content)

        payload = {
            "vehicle_id": str(vehicle.id),
            "brand": vehicle.brand,
            "model": vehicle.model,
            "year": vehicle.year,
            "price": float(vehicle.price),
            "fuel_type": vehicle.fuel_type,
            "city": vehicle.city,
            "status": vehicle.status,  # Critical for filtering
            "text_content": text_content
        }

        point = qmodels.PointStruct(
            id=str(vehicle.id),
            vector=vector,
            payload=payload
        )

        await qdrant.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=[point]
        )
        logger.info(f"Véhicule {vehicle.id} synchronisé avec succès dans Qdrant (status: {vehicle.status}).")
    except Exception as e:
        logger.error(f"Échec de la synchronisation Qdrant pour le véhicule {vehicle.id} : {e}")

async def delete_vehicle_from_qdrant(vehicle_id: str):
    """
    Supprime un véhicule de Qdrant.
    """
    try:
        qdrant = get_qdrant_client()
        await qdrant.delete(
            collection_name=settings.QDRANT_COLLECTION,
            points_selector=qmodels.PointIdsList(
                points=[vehicle_id],
            ),
        )
        logger.info(f"Véhicule {vehicle_id} supprimé de Qdrant.")
    except Exception as e:
        logger.error(f"Échec de la suppression Qdrant pour le véhicule {vehicle_id} : {e}")
