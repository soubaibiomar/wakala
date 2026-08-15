import argparse
import logging
import time
from typing import List, Dict, Any

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

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

from .dealers.dealer_registry import DealerRegistry
from .dealers.generic_dealer_scraper import GenericDealerScraper

from .normalizer import ScraperNormalizer
from .kafka_publisher import KafkaPublisher
from .schema_validator import SchemaValidator
from .health_monitor import HealthMonitor
from .resilience_loop import ResilienceLoop

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def run_single_scraper(scraper, dry_run: bool = True):
    """
    Executes the scraping pipeline for a single isolated source.
    """
    logger.info(f"--- Starting isolated scraping job for {scraper.source_name} ---")
    
    # 1. DETECT
    res_loop = ResilienceLoop()
    normal_interval = get_interval_for_source(scraper.source_name)
    if not res_loop.should_run(scraper.source_name, normal_interval):
        return 0

    normalizer = ScraperNormalizer()
    publisher = KafkaPublisher() if not dry_run else None
    monitor = HealthMonitor(scraper.source_name)
    
    valid_listings = []

    try:
        if dry_run:
            logger.info(f"[DRY-RUN] Would fetch up to {config.MAX_LISTINGS_PER_RUN} listings from {scraper.source_name}")
            raw_listings = []
        else:
            raw_listings = scraper.fetch_listings(max_items=config.MAX_LISTINGS_PER_RUN)

        if not raw_listings:
            logger.warning(f"No listings retrieved from {scraper.source_name}")
            return 0

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
                
            valid_listings.append(normalized)

        if dry_run:
            logger.info(f"[DRY-RUN] {scraper.source_name} generated {len(valid_listings)} valid listings.")
            return 0

        if valid_listings:
            published = publisher.publish_listings(valid_listings)
            logger.info(f"Successfully published {published} listings for {scraper.source_name}")
            return published

    except Exception as e:
        logger.error(f"Isolated Error executing scraper {scraper.source_name}: {e}")
    finally:
        # 3. EVALUATE
        failed_fields = []
        if not dry_run:
            # We determine failed fields if the success rate of a field is 0
            if monitor.total_attempted > 0:
                for field, count in monitor.field_successes.items():
                    if count == 0:
                        failed_fields.append(field)
            
            http_status = getattr(scraper, 'last_http_status', None)
            html_snippet = getattr(scraper, 'last_html', None)
            
            res_loop.evaluate_scrape(
                source_name=scraper.source_name,
                raw_listings=valid_listings,
                http_status=http_status,
                html_snippet=html_snippet,
                failed_fields=failed_fields
            )
            
            monitor.finalize_run()
            if publisher:
                publisher.close()
    
    return 0

def get_interval_for_source(source_name: str) -> int:
    """Returns interval in hours for a given source."""
    if "avito" in source_name.lower():
        return 0.33  # ~20 minutes
    elif "wandaloo" in source_name.lower() or "moteur_new" in source_name.lower():
        return 4.0   # 4 hours for new cars
    elif "dealer_" in source_name.lower():
        return 24.0  # 24 hours for generic dealers
    return config.SCHEDULE_INTERVAL_HOURS

def main():
    parser = argparse.ArgumentParser(description="Wakala Scraper Orchestrator")
    parser.add_argument("--live", action="store_true", help="Disable dry-run and perform actual HTTP requests")
    parser.add_argument("--schedule", action="store_true", help="Run continuously with isolated APScheduler tasks")
    parser.add_argument("--once", action="store_true", help="Run all active sources once in sequence and exit")
    args = parser.parse_args()

    dry_run = not args.live

    # Base platform scrapers
    # ── PIVOT: New vehicles only ──────────────────────────────────
    # Used-only scrapers disabled (code kept for reversibility):
    #   AvitoScraper()        — used-car marketplace
    #   GlobalOccazScraper()  — used-car marketplace  
    #   SpoticarScraper()     — certified used cars
    #   CarzScraper()         — used-car marketplace
    # To re-enable: uncomment and re-run scrapers to repopulate data.
    # ──────────────────────────────────────────────────────────────
    scrapers = [
        # AvitoScraper(),          # DISABLED — used-only (pivot neuf)
        MoteurScraper(),
        WandalooScraper(),
        LeguideautoScraper(),
        # CarzScraper(),           # DISABLED — used-only (pivot neuf)
        KifalScraper(),
        OtoclicScraper(),
        # GlobalOccazScraper(),    # DISABLED — used-only (pivot neuf)
        # SpoticarScraper()        # DISABLED — used-only (pivot neuf)
    ]

    # Dynamically add dealer scrapers
    registry = DealerRegistry()
    active_dealers = registry.get_active_dealers()
    for dealer_config in active_dealers:
        scrapers.append(GenericDealerScraper(dealer_config))

    logger.info(f"Loaded {len(scrapers)} active scrapers ({len(active_dealers)} from dealers.yaml).")

    if args.schedule:
        logger.info(f"Starting APScheduler for isolated periodic scraping. Dry Run: {dry_run}")
        
        # Use ThreadPoolExecutor to ensure total isolation between scraper jobs
        executors = {
            'default': ThreadPoolExecutor(max_workers=5)
        }
        scheduler = BlockingScheduler(executors=executors)
        
        for scraper in scrapers:
            interval_hours = get_interval_for_source(scraper.source_name)
            interval_minutes = int(interval_hours * 60)
            
            logger.info(f"Scheduling {scraper.source_name} to run every {interval_minutes} minutes.")
            
            scheduler.add_job(
                run_single_scraper,
                'interval',
                minutes=interval_minutes,
                args=[scraper, dry_run],
                id=f"job_{scraper.source_name}",
                replace_existing=True,
                max_instances=1 # Prevents overlaps if a job takes too long
            )

        try:
            # Trigger them all once immediately asynchronously
            for scraper in scrapers:
                scheduler.add_job(
                    run_single_scraper,
                    'date',
                    run_date=None, # run immediately
                    args=[scraper, dry_run]
                )
            
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped.")
    else:
        # Single run
        logger.info("Running single sequential execution of all active scrapers.")
        total_published = 0
        for scraper in scrapers:
            total_published += run_single_scraper(scraper, dry_run)
        logger.info(f"Finished single run. Total published: {total_published}")

if __name__ == "__main__":
    main()