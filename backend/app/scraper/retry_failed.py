import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.scraper import FailedScrape
from app.scraper.hybrid_parser import parse_vehicle_page
import cloudscraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def retry_failed_urls():
    """
    Relance le scraping pour les URLs ayant échoué.
    """
    logger.info("Démarrage du processus de retry des URLs en échec...")
    client = cloudscraper.create_scraper()
    
    async with async_session_factory() as session:
        result = await session.execute(
            select(FailedScrape).where(FailedScrape.is_resolved == False)
        )
        failed_scrapes = result.scalars().all()
        
        if not failed_scrapes:
            logger.info("Aucune URL en échec à traiter.")
            return

        for failed in failed_scrapes:
            logger.info(f"Tentative de parsing de l'URL : {failed.url}")
            try:
                # Fetching the HTML content
                # This uses sync requests in a background thread or we just do it synchronously for the retry script
                resp = client.get(failed.url, timeout=30)
                resp.raise_for_status()
                
                # Parsing
                parsed_data = await parse_vehicle_page(resp.text, failed.url, session)
                if parsed_data:
                    logger.info(f"Succès pour {failed.url}: {parsed_data.brand} {parsed_data.model}")
                    failed.is_resolved = True
                    await session.commit()
                else:
                    logger.warning(f"Toujours en échec pour {failed.url}")
            except Exception as e:
                logger.error(f"Erreur lors de la récupération de {failed.url} : {e}")

if __name__ == "__main__":
    asyncio.run(retry_failed_urls())
