"""
services/ingestion_pipeline.py
Orchestration multi-plateformes : exécute séquentiellement les scrapers actifs,
normalise via Ollama, puis déduplique.

L'exécution est séquentielle par plateforme (pas en parallèle) pour respecter
les délais anti-détection définis dans config.py.
"""
import importlib
import traceback
import time
import logging
from datetime import datetime

from config import ACTIVE_SCRAPERS, SCRAPER_DELAYS, CACHE_TTL_HOURS
from services.listing_normalizer import normalize_listing
from services.deduplication import deduplicate_listings

logger = logging.getLogger("wakala.pipeline")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def get_scraper_class(scraper_name: str):
    """
    Importe dynamiquement la classe du scraper depuis scrapers/platforms/{name}.py.
    Cherche la première classe qui hérite de BaseScraper.
    """
    module_name = f"scrapers.platforms.{scraper_name}"
    module = importlib.import_module(module_name)

    from scrapers.base_scraper import BaseScraper
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (
            isinstance(attr, type)
            and issubclass(attr, BaseScraper)
            and attr is not BaseScraper
        ):
            return attr
    raise ValueError(f"Aucune classe scraper trouvée dans {module_name}")


def run_pipeline(max_pages: int = 1) -> list[dict]:
    """
    Exécute le pipeline complet d'ingestion :
    1. Scraping séquentiel de toutes les plateformes actives
    2. Normalisation Ollama (neuf vs occasion)
    3. Déduplication inter-plateformes

    Args:
        max_pages: nombre de pages à scraper par plateforme (défaut: 1)

    Returns:
        Liste des annonces uniques normalisées
    """
    all_raw_listings = []
    stats = {}
    start_time = datetime.now()

    logger.info("=" * 60)
    logger.info("DÉMARRAGE DU PIPELINE D'INGESTION WAKALA")
    logger.info(f"Scrapers actifs : {len(ACTIVE_SCRAPERS)}")
    logger.info(f"Pages par plateforme : {max_pages}")
    logger.info("=" * 60)

    # ── Phase 1 : Scraping séquentiel ──────────────────────────
    for scraper_name in ACTIVE_SCRAPERS:
        logger.info(f"\n{'─' * 40}")
        logger.info(f"[LANCEMENT] {scraper_name}")
        stats[scraper_name] = {"scraped": 0, "cached": 0, "errors": 0}

        try:
            scraper_cls = get_scraper_class(scraper_name)
            scraper = scraper_cls()
            delay = SCRAPER_DELAYS.get(scraper.platform_name, 2)

            for page in range(1, max_pages + 1):
                logger.info(f"  Page {page}/{max_pages}...")
                try:
                    urls = scraper.get_listing_urls(page=page)
                    logger.info(f"  → {len(urls)} URL(s) trouvée(s)")

                    if not urls:
                        logger.warning(
                            f"  ⚠ Aucune URL trouvée pour {scraper_name} page {page}. "
                            f"La structure HTML a peut-être changé."
                        )
                        break

                    for url in urls:
                        try:
                            response = scraper.session.get(url, delay=delay)
                            if response.status_code != 200:
                                logger.warning(f"  HTTP {response.status_code} pour {url}")
                                stats[scraper_name]["errors"] += 1
                                continue

                            raw_listing = scraper.parse_listing(response.text, url)
                            all_raw_listings.append(raw_listing)
                            stats[scraper_name]["scraped"] += 1

                        except Exception as e:
                            logger.error(f"  Erreur parsing {url}: {e}")
                            stats[scraper_name]["errors"] += 1

                except Exception as e:
                    logger.error(f"  Erreur get_listing_urls page {page}: {e}")
                    stats[scraper_name]["errors"] += 1

        except Exception as e:
            logger.error(f"Erreur critique sur {scraper_name}: {e}")
            traceback.print_exc()

    # ── Phase 2 : Normalisation Ollama ─────────────────────────
    logger.info(f"\n{'=' * 60}")
    logger.info(f"NORMALISATION OLLAMA ({len(all_raw_listings)} annonces)")
    logger.info("=" * 60)

    normalized_listings = []
    for i, raw in enumerate(all_raw_listings):
        try:
            norm = normalize_listing(raw)
            normalized_listings.append(norm)
            if (i + 1) % 10 == 0:
                logger.info(f"  Normalisées : {i + 1}/{len(all_raw_listings)}")
        except Exception as e:
            logger.error(f"  Erreur normalisation: {e}")
            normalized_listings.append(raw)  # Fallback : on garde le brut

    # ── Phase 3 : Déduplication ────────────────────────────────
    logger.info(f"\n{'=' * 60}")
    logger.info("DÉDUPLICATION INTER-PLATEFORMES")
    logger.info("=" * 60)

    unique_listings = deduplicate_listings(normalized_listings)

    # ── Résumé ─────────────────────────────────────────────────
    elapsed = (datetime.now() - start_time).total_seconds()

    logger.info(f"\n{'=' * 60}")
    logger.info("RÉSUMÉ D'INGESTION")
    logger.info("=" * 60)
    for s_name, s_data in stats.items():
        status = "✓" if s_data["scraped"] > 0 else "✗"
        logger.info(
            f"  {status} [{s_name}] "
            f"Scrapées: {s_data['scraped']} | "
            f"Erreurs: {s_data['errors']}"
        )

    logger.info(f"\n  Total annonces brutes : {len(all_raw_listings)}")
    logger.info(f"  Total après normalisation : {len(normalized_listings)}")
    logger.info(f"  Total uniques (après dédup) : {len(unique_listings)}")
    logger.info(f"  Durée totale : {elapsed:.1f}s")
    logger.info("=" * 60)

    return unique_listings


if __name__ == "__main__":
    run_pipeline(max_pages=1)
