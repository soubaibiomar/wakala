import argparse
import logging
import time
from typing import List, Dict, Any

from apscheduler.schedulers.blocking import BlockingScheduler

from . import config
from .avito_scraper import AvitoScraper
from .moteur_scraper import MoteurScraper
from .wandaloo_scraper import WandalooScraper
from .leguideauto_scraper import LeguideautoScraper
from .carz_scraper import CarzScraper
from .kifal_scraper import KifalScraper
from .otoclic_scraper import OtoclicScraper
from .global_occaz_scraper import GlobalOccazScraper
from .spoticar_scraper import SpoticarScraper
from .normalizer import ScraperNormalizer
from .kafka_publisher import KafkaPublisher
from .schema_validator import SchemaValidator
from .health_monitor import HealthMonitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def run_scraping_job(dry_run: bool = True) -> int:
    """
    Executes the scraping pipeline for all configured sources.
    Returns the number of listings published to Kafka.
    """
    logger.info(f"Starting scraping job. Dry Run: {dry_run}")

    scrapers = [
        AvitoScraper(), 
        MoteurScraper(),
        WandalooScraper(),
        LeguideautoScraper(),
        CarzScraper(),
        KifalScraper(),
        OtoclicScraper(),
        GlobalOccazScraper(),
        SpoticarScraper()
    ]
    normalizer = ScraperNormalizer()
    publisher = KafkaPublisher() if not dry_run else None

    all_normalized_listings = []

    for scraper in scrapers:
        monitor = HealthMonitor(scraper.source_name)
        try:
            logger.info(f"Processing {scraper.source_name} (max {config.MAX_LISTINGS_PER_RUN} items)")

            if dry_run:
                logger.info(f"[DRY-RUN] Would fetch up to {config.MAX_LISTINGS_PER_RUN} listings from {scraper.source_name}")
                # Return empty list in dry-run - real fixtures are used in tests
                raw_listings = []
            else:
                raw_listings = scraper.fetch_listings(max_items=config.MAX_LISTINGS_PER_RUN)

            if not raw_listings:
                logger.warning(f"No listings retrieved from {scraper.source_name}")
                continue

            logger.info(f"Retrieved {len(raw_listings)} raw listings from {scraper.source_name}")

            for raw in raw_listings:
                if not dry_run:
                    monitor.record_attempt()
                
                normalized = normalizer.normalize(raw)
                
                # Validate Schema
                is_valid, errors = SchemaValidator.validate(normalized)
                if not is_valid:
                    logger.warning(f"Validation failed for {scraper.source_name} listing: {errors}")
                    continue
                    
                if not dry_run:
                    monitor.record_success(normalized)
                    
                all_normalized_listings.append(normalized)

        except Exception as e:
            logger.error(f"Error executing scraper {scraper.source_name}: {e}")
        finally:
            if not dry_run:
                monitor.finalize_run()

    if dry_run:
        logger.info(f"[DRY-RUN] Would publish {len(all_normalized_listings)} listings to Kafka")
        for item in all_normalized_listings:
            logger.debug(f"[DRY-RUN] Normalized item: {item}")
        return 0

    if all_normalized_listings:
        published = publisher.publish_listings(all_normalized_listings)
        publisher.close()
        return published
    else:
        logger.info("No listings gathered in this run.")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Wakala Scraper Producer - Real scrapers as sole Kafka source")
    parser.add_argument("--live", action="store_true", help="Disable dry-run and perform actual HTTP requests")
    parser.add_argument("--schedule", action="store_true", help="Run continuously with APScheduler")
    parser.add_argument("--once", action="store_true", help="Run a single scraping job and exit")
    args = parser.parse_args()

    dry_run = not args.live

    if args.schedule:
        logger.info(f"Starting APScheduler for periodic scraping (every {config.SCHEDULE_INTERVAL_HOURS}h). Dry Run: {dry_run}")
        scheduler = BlockingScheduler()
        scheduler.add_job(run_scraping_job, 'interval', hours=config.SCHEDULE_INTERVAL_HOURS, args=[dry_run])
        try:
            # Run once immediately, then on schedule
            run_scraping_job(dry_run)
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped.")
    else:
        # Single run (default)
        run_scraping_job(dry_run)


if __name__ == "__main__":
    main()