#!/usr/bin/env python3
"""
AutoMind Scraper Producer - Entry Point
========================================

Single entry point for the Kafka producer using REAL scrapers
(Avito.ma, Moteur.ma) as the sole data source for listings.raw topic.

Usage:
    # Dry-run (default) - no network requests, for development/CI
    python -m data_pipeline.kafka.producers.scrapers.run_producer

    # Live mode - actual HTTP requests to scrape sites
    python -m data_pipeline.kafka.producers.scrapers.run_producer --live

    # Scheduled runs every 12 hours
    python -m data_pipeline.kafka.producers.scrapers.run_producer --live --schedule

IMPORTANT:
- Dry-run is DEFAULT to prevent accidental scraping during development
- Use --live explicitly to enable real HTTP requests
- Respects robots.txt, rate limits, and retries 5xx errors only
"""

import argparse
import logging
import sys
from pathlib import Path

# Ensure project root is in path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from data_pipeline.kafka.producers.scrapers import config
from data_pipeline.kafka.producers.scrapers.scheduler import run_scraping_job
from data_pipeline.kafka.topics_config import ensure_topics

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="AutoMind Scraper Producer - Real scrapers as sole Kafka source",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run (default) - simulates without network requests
  python -m data_pipeline.kafka.producers.scrapers.run_producer

  # Live mode - actual scraping (use responsibly!)
  python -m data_pipeline.kafka.producers.scrapers.run_producer --live

  # Scheduled live scraping every 12 hours
  python -m data_pipeline.kafka.producers.scrapers.run_producer --live --schedule

Notes:
  - Dry-run mode is DEFAULT to prevent accidental scraping in dev/CI
  - Real scrapers: Avito.ma, Moteur.ma (no simulated data anywhere)
  - Rate limits: 3-7s between requests, respects robots.txt
  - Retries: only on 5xx errors, never on 403/429
"""
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Enable live mode - perform actual HTTP requests (disabled by default)"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run continuously with APScheduler (interval from config)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicit dry-run mode (default behavior, redundant with no --live)"
    )

    args = parser.parse_args()

    # --dry-run is default; --live explicitly enables network
    dry_run = not args.live

    # Validate configuration
    logger.info(f"Bootstrap servers: {config.BOOTSTRAP_SERVERS}")
    logger.info(f"Target topic: {config.TOPIC_RAW}")
    logger.info(f"Max listings per run: {config.MAX_LISTINGS_PER_RUN}")
    logger.info(f"Pages per source: {config.PAGES_PER_SOURCE}")
    logger.info(f"Mode: {'LIVE (real HTTP requests)' if not dry_run else 'DRY-RUN (no network)'}")

    if not dry_run:
        logger.warning("=" * 60)
        logger.warning("LIVE MODE ENABLED - Real HTTP requests will be made")
        logger.warning("Ensure you have permission to scrape target sites")
        logger.warning("Respect robots.txt and rate limits")
        logger.warning("=" * 60)

    # Ensure Kafka topics exist
    try:
        ensure_topics(config.BOOTSTRAP_SERVERS)
    except Exception as e:
        logger.error(f"Failed to ensure Kafka topics: {e}")
        if not dry_run:
            sys.exit(1)

    if args.schedule:
        if dry_run:
            logger.info("Scheduling dry-runs periodically (no network)")
        else:
            logger.info(f"Starting scheduled live scraping (every {config.SCHEDULE_INTERVAL_HOURS}h)")
        from apscheduler.schedulers.blocking import BlockingScheduler
        scheduler = BlockingScheduler()
        scheduler.add_job(run_scraping_job, 'interval', hours=config.SCHEDULE_INTERVAL_HOURS, args=[dry_run])
        # Run once immediately
        run_scraping_job(dry_run)
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped")
    else:
        run_scraping_job(dry_run)


if __name__ == "__main__":
    main()