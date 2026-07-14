#!/usr/bin/env python3
"""
Generate Frozen Bronze Sample Data
===================================

Runs the scrapers in LIVE mode once, saves the Bronze layer output
as Parquet files to data-pipeline/storage/sample-data/ for versioning.

This creates the immutable sample data used by seed_from_bronze_sample.py
for local development without network dependencies.

Run ONCE to generate the initial sample, then commit the Parquet files.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import logging
from datetime import datetime, timezone
import pyarrow as pa
import pyarrow.parquet as pq

from data_pipeline.kafka.producers.scrapers import config
from data_pipeline.kafka.producers.scrapers.avito_scraper import AvitoScraper
from data_pipeline.kafka.producers.scrapers.moteur_scraper import MoteurScraper
from data_pipeline.kafka.producers.scrapers.normalizer import ScraperNormalizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

SAMPLE_OUTPUT_DIR = PROJECT_ROOT / "data_pipeline" / "storage" / "sample-data"

SCHEMA = pa.schema([
    ("vehicle_id", pa.string()),
    ("source", pa.string()),
    ("event_type", pa.string()),
    ("timestamp", pa.string()),
    ("brand", pa.string()),
    ("model", pa.string()),
    ("year", pa.int32()),
    ("price", pa.int32()),
    ("mileage", pa.int32()),
    ("fuel_type", pa.string()),
    ("body_type", pa.string()),
    ("transmission", pa.string()),
    ("engine_power_hp", pa.int32()),
    ("color", pa.string()),
    ("doors", pa.int32()),
    ("seats", pa.int32()),
    ("city", pa.string()),
    ("description", pa.string()),
    ("seller_id", pa.string()),
])


def generate_sample_data(max_per_source: int = 20):
    """Run scrapers and save normalized output as versioned Parquet sample"""
    logger.info(f"Generating sample data (max {max_per_source} per source)...")
    logger.info(f"Output directory: {SAMPLE_OUTPUT_DIR}")

    scrapers = [AvitoScraper(), MoteurScraper()]
    normalizer = ScraperNormalizer()

    all_normalized = []

    for scraper in scrapers:
        try:
            logger.info(f"Scraping {scraper.source_name}...")
            raw_listings = scraper.fetch_listings(max_items=max_per_source)

            if not raw_listings:
                logger.warning(f"No listings from {scraper.source_name}")
                continue

            logger.info(f"Got {len(raw_listings)} raw listings from {scraper.source_name}")

            for raw in raw_listings:
                normalized = normalizer.normalize(raw)
                all_normalized.append(normalized)

        except Exception as e:
            logger.error(f"Error scraping {scraper.source_name}: {e}")

    if all_normalized:
        # Write to sample-data directly
        SAMPLE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        # Wrap each normalized listing to match schema format
        rows = []
        for norm in all_normalized:
            row = {
                "vehicle_id": norm.get("vehicle_id", ""),
                "source": norm.get("source", ""),
                "event_type": "listing_created",
                "timestamp": norm.get("timestamp", norm.get("scraped_at", "")),
                "brand": norm.get("brand", ""),
                "model": norm.get("model", ""),
                "year": norm.get("year", 0) or 0,
                "price": norm.get("price", 0) or 0,
                "mileage": norm.get("mileage", 0) or 0,
                "fuel_type": norm.get("fuel_type", ""),
                "body_type": norm.get("body_type", ""),
                "transmission": norm.get("transmission", ""),
                "engine_power_hp": norm.get("engine_power_hp", 0) or 0,
                "color": norm.get("color", ""),
                "doors": norm.get("doors", 0) or 0,
                "seats": norm.get("seats", 0) or 0,
                "city": norm.get("city", ""),
                "description": norm.get("description", ""),
                "seller_id": norm.get("seller_id", ""),
            }
            rows.append(row)
            
        table = pa.Table.from_pylist(rows, schema=SCHEMA)
        dt = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = SAMPLE_OUTPUT_DIR / f"dt={dt}"
        path.mkdir(parents=True, exist_ok=True)
        fname = path / f"sample_{datetime.now(timezone.utc).strftime('%H%M%S')}.parquet"
        pq.write_table(table, fname, compression="snappy")
        
        logger.info(f"Sample data written to {fname}")
    else:
        logger.warning("No data collected - sample not created")

    return len(all_normalized)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate frozen Bronze sample data")
    parser.add_argument("--max", type=int, default=20, help="Max listings per source")
    args = parser.parse_args()

    print("=" * 60)
    print("AutoMind - Generate Frozen Bronze Sample Data")
    print("=" * 60)
    print(f"WARNING: This makes REAL HTTP requests to Avito.ma and Moteur.ma")
    print(f"Max per source: {args.max}")
    print("=" * 60)

    count = generate_sample_data(args.max)
    print(f"\nGenerated sample with {count} normalized listings")
    print(f"Files saved to: {SAMPLE_OUTPUT_DIR}")