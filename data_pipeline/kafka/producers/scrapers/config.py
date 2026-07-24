import os
from pathlib import Path

# --- Kafka ---
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_RAW = "listings.raw"

# --- User Agent ---
USER_AGENT = "VenteAutoBot/1.0 - projet académique - contact: contact@wakala.local"

# --- Rate Limiting ---
MIN_DELAY_SECONDS = 3
MAX_DELAY_SECONDS = 7
REQUEST_TIMEOUT = 15

# --- Retry Strategy ---
MAX_RETRIES = 3
BACKOFF_FACTOR = 2

# --- Scraper Config ---
MAX_LISTINGS_PER_RUN = 50
PAGES_PER_SOURCE = 3

# --- Dry-run fixture path ---
FIXTURE_DIR = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures" / "scraped_html"

# --- Scheduler ---
SCHEDULE_INTERVAL_HOURS = int(os.getenv("SCHEDULE_INTERVAL_HOURS", "1"))