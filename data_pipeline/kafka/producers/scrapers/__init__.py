"""
AutoMind Scraper Producer Package
==================================

Real web scrapers (Avito.ma, Moteur.ma) as the sole Kafka producer
for the listings.raw topic. No simulated data.
"""

from .config import (
    BOOTSTRAP_SERVERS,
    TOPIC_RAW,
    USER_AGENT,
    MIN_DELAY_SECONDS,
    MAX_DELAY_SECONDS,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    BACKOFF_FACTOR,
    MAX_LISTINGS_PER_RUN,
    PAGES_PER_SOURCE,
    SCHEDULE_INTERVAL_HOURS,
)

from .base_scraper import BaseScraper
from .avito_scraper import AvitoScraper
from .moteur_scraper import MoteurScraper
from .normalizer import ScraperNormalizer

# Optional imports (require extra dependencies)
try:
    from .kafka_publisher import KafkaPublisher
    __all_kafka__ = ["KafkaPublisher"]
except ImportError:
    KafkaPublisher = None
    __all_kafka__ = []

try:
    from .scheduler import run_scraping_job
    __all_scheduler__ = ["run_scraping_job"]
except ImportError:
    run_scraping_job = None
    __all_scheduler__ = []

__all__ = [
    "BOOTSTRAP_SERVERS",
    "TOPIC_RAW",
    "USER_AGENT",
    "MIN_DELAY_SECONDS",
    "MAX_DELAY_SECONDS",
    "REQUEST_TIMEOUT",
    "MAX_RETRIES",
    "BACKOFF_FACTOR",
    "MAX_LISTINGS_PER_RUN",
    "PAGES_PER_SOURCE",
    "SCHEDULE_INTERVAL_HOURS",
    "BaseScraper",
    "AvitoScraper",
    "MoteurScraper",
    "ScraperNormalizer",
] + __all_kafka__ + __all_scheduler__