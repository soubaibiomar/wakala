import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from langchain_community.embeddings import OllamaEmbeddings
from qdrant_client.http import models as qmodels

from app.core.database import async_session_factory
from app.core.config import settings
from app.models.vehicle import Vehicle
from app.services.ai.qdrant import get_qdrant_client, ensure_collection_exists

logger = logging.getLogger(__name__)

async def generate_vehicle_description(v: Vehicle) -> str:
    """
    Crée une description riche pour le véhicule, optimisée pour la recherche sémantique.
    """
    desc = (
        f"Véhicule d'occasion {v.brand} {v.model}, année {v.year}. "
        f"Couleur: {v.color or 'Non spécifiée'}. "
        f"Kilométrage: {v.mileage} km. "
        f"Carburant: {v.fuel_type}. "
        f"Boîte de vitesses: {v.transmission}. "
        f"Carrosserie: {v.body_type}. "
        f"Localisation: {v.city}. "
        f"Prix demandé: {v.price} MAD. "
    )
    if v.description:
        desc += f"Description du vendeur: {v.description}"
    return desc

async def ingest_vehicles():
    """
    Récupère tous les véhicules de la base de données, 
    génère les embeddings et les stocke dans Qdrant.
    """
    logger.info("Début de l'ingestion des véhicules vers Qdrant...")
    
    # Assurez-vous que la collection existe (dimension 1024 pour bge-m3)
    await ensure_collection_exists(settings.QDRANT_COLLECTION, vector_size=1024)
    qdrant = get_qdrant_client()
    
    _ollama_base = settings.OLLAMA_BASE_URL.replace("/v1", "") if settings.OLLAMA_BASE_URL else "http://localhost:11434"
    embeddings_model = OllamaEmbeddings(
        base_url=_ollama_base,
        model="bge-m3"
    )

    async with async_session_factory() as session:
        result = await session.execute(select(Vehicle))
        vehicles = result.scalars().all()
        
        if not vehicles:
            logger.warning("Aucun véhicule trouvé dans la base de données.")
            return

        points = []
        for v in vehicles:
            # Création du texte
            text_content = await generate_vehicle_description(v)
            
            # Génération de l'embedding (bloquant pour l'API HTTP, donc on l'enveloppe si besoin, 
            # mais ainvoke est natif sur LangChain)
            vector = await embeddings_model.aembed_query(text_content)
            
            # Préparation du Point Struct pour Qdrant
            payload = {
                "vehicle_id": str(v.id),
                "brand": v.brand,
                "model": v.model,
                "year": v.year,
                "price": float(v.price),
                "fuel_type": v.fuel_type,
                "city": v.city,
                "status": v.status,
                "text_content": text_content
            }
            
            points.append(qmodels.PointStruct(
                id=str(v.id),
                vector=vector,
                payload=payload
            ))
            logger.info(f"Préparation terminée pour le véhicule {v.id} ({v.brand} {v.model})")
            
        # Upsert en lot
        if points:
            await qdrant.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=points
            )
            logger.info(f"{len(points)} véhicules insérés avec succès dans Qdrant.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(ingest_vehicles())
