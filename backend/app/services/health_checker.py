import asyncio
import logging
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from app.core.database import async_session_maker
from app.models.vehicle import Vehicle

logger = logging.getLogger(__name__)

async def check_vehicle_availability(session: AsyncSession, vehicle: Vehicle):
    """
    Vérifie si l'URL source du véhicule est toujours accessible.
    Si non (404, 410, etc.), marque le véhicule comme 'sold'.
    """
    if not vehicle.source_url:
        return
        
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            # On utilise GET car certains serveurs bloquent HEAD ou retournent 405
            # On met un user-agent classique pour éviter les blocages basiques
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            response = await client.get(vehicle.source_url, headers=headers)
            
            # Si le site retourne 404, l'annonce n'existe plus
            if response.status_code == 404:
                logger.info(f"Véhicule {vehicle.id} introuvable (404). Marquage comme 'sold'.")
                vehicle.status = 'sold'
                await session.commit()
            
            # TODO: Implémenter la recherche du "bouton de contact" dans `response.text` si nécessaire
            
    except httpx.RequestError as e:
        logger.warning(f"Erreur de requête pour {vehicle.source_url}: {e}")
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la vérification de {vehicle.id}: {e}")

async def run_health_checker_loop():
    """
    Boucle infinie exécutant le Health Checker périodiquement (ex: toutes les 6 heures).
    """
    logger.info("Démarrage du Health Checker (Vérification de disponibilité)...")
    
    while True:
        try:
            async with async_session_maker() as session:
                # Récupère tous les véhicules "available" ayant une URL
                stmt = select(Vehicle).where(Vehicle.status == 'available').where(Vehicle.source_url.isnot(None))
                result = await session.execute(stmt)
                vehicles = result.scalars().all()
                
                logger.info(f"Health Checker: {len(vehicles)} véhicules à vérifier.")
                
                # Vérifie les véhicules par lots (ex: 5 requêtes simultanées)
                chunk_size = 5
                for i in range(0, len(vehicles), chunk_size):
                    chunk = vehicles[i:i+chunk_size]
                    await asyncio.gather(*(check_vehicle_availability(session, v) for v in chunk))
                    await asyncio.sleep(2) # Pause entre les lots pour ne pas se faire bannir
                    
        except Exception as e:
            logger.error(f"Erreur critique dans le Health Checker: {e}")
            
        # Attendre X heures (ex: 6 heures)
        await asyncio.sleep(60 * 60 * 6)

def start_health_checker():
    """
    Lance le Health Checker en tâche de fond.
    """
    asyncio.create_task(run_health_checker_loop())
