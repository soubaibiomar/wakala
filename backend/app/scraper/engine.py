"""
Engine — orchestre les scrapers et sauvegarde les résultats.
"""
import logging
from typing import Optional

from app.scraper.avito import AvitoScraper
from app.scraper.moteur import MoteurScraper

logger = logging.getLogger(__name__)

SCRAPERS = {
    "avito": AvitoScraper,
    "moteur": MoteurScraper,
}

SEARCH_URLS = {
    "avito": "https://www.avito.ma/fr/maroc/voitures_d_occasion/a_vendre",
    "moteur": "",  # moteur uses self.SEARCH_URL
}


async def scrape_source(name: str, pages: int = 1) -> list[dict]:
    cls = SCRAPERS.get(name)
    if not cls:
        logger.warning("Scraper %s inconnu", name)
        return []
    url = SEARCH_URLS.get(name, "")

    scraper = cls()
    all_listings = []
    try:
        for page in range(1, pages + 1):
            logger.info("%s — page %d/%d", name, page, pages)
            try:
                listings = scraper.fetch_page(url, page=page)
                all_listings.extend(listings)
                logger.info("  → %d annonces trouvées", len(listings))
            except Exception as e:
                logger.error("  Erreur page %d: %s", page, e)
                break
    finally:
        scraper.close()

    return all_listings


async def run_all(pages: int = 1, sources: Optional[list[str]] = None) -> dict[str, list[dict]]:
    results = {}
    target = sources or list(SCRAPERS.keys())
    for name in target:
        logger.info("Démarrage scraper: %s", name)
        listings = await scrape_source(name, pages=pages)
        results[name] = listings
        logger.info("%s: %d annonces récupérées", name, len(listings))
    return results
