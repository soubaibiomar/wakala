#!/usr/bin/env python3
"""
Seed Development Database from Bronze Sample Data
==================================================

Loads a frozen snapshot of REAL scraped data (Parquet from Bronze layer)
into the local PostgreSQL database for development/testing.

This is NOT simulated data - it's an immutable snapshot of actual
scrapes from Avito.ma and Moteur.ma, versioned in the repository.

Usage:
    python -m data_pipeline.scripts.seed_from_bronze_sample
    python -m data_pipeline.scripts.seed_from_bronze_sample --sample-path data-pipeline/storage/sample-data
    python -m data_pipeline.scripts.seed_from_bronze_sample --count 50
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from data_pipeline.kafka.producers.scrapers.normalizer import ScraperNormalizer


# Default sample data location (versioned in repo)
DEFAULT_SAMPLE_PATH = PROJECT_ROOT / "data_pipeline" / "storage" / "sample-data"


def get_db_url():
    """Get database URL from environment or use local default"""
    import os
    return os.getenv(
        "DATABASE_URL",
        "postgresql://automind_user:automind_secret_password@localhost:5432/automind"
    )


def load_sample_parquet(sample_path: Path) -> pd.DataFrame:
    """Load all Parquet files from sample data directory"""
    parquet_files = list(sample_path.rglob("*.parquet"))
    if not parquet_files:
        raise FileNotFoundError(f"No Parquet files found in {sample_path}")

    dfs = [pd.read_parquet(f) for f in parquet_files]
    combined = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(combined)} rows from {len(parquet_files)} Parquet files")
    return combined


def normalize_sample_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize sample data to match vehicle table schema"""
    normalizer = ScraperNormalizer()

    # Convert each row using the normalizer (which expects dict)
    records = df.to_dict(orient='records')
    normalized = []

    for raw in records:
        try:
            norm = normalizer.normalize(raw)
            normalized.append(norm)
        except Exception as e:
            print(f"Warning: Failed to normalize record: {e}")

    result = pd.DataFrame(normalized)
    print(f"Normalized {len(result)} records")
    return result


def seed_vehicles(df: pd.DataFrame, db_url: str, limit: int = None):
    """Insert normalized vehicles into PostgreSQL"""
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if limit:
            df = df.head(limit)

        # Prepare for vehicle table insert
        # Map normalizer output to vehicle table columns
        vehicles_data = []
        for _, row in df.iterrows():
            vehicle = {
                "brand": row.get("brand", "unknown"),
                "model": row.get("model"),
                "year": row.get("year"),
                "price": row.get("price"),
                "mileage": row.get("mileage"),
                "fuel_type": row.get("fuel_type"),
                "transmission": row.get("transmission"),
                "city": row.get("city", "unknown"),
                "source_url": row.get("source_url"),
                "source": row.get("source", "unknown"),
                "scraped_at": row.get("scraped_at"),
            }
            # Remove None values for optional fields
            vehicle = {k: v for k, v in vehicle.items() if v is not None}
            vehicles_data.append(vehicle)

        if not vehicles_data:
            print("No valid vehicles to insert")
            return 0

        # Bulk insert using raw SQL for performance
        columns = vehicles_data[0].keys()
        cols_str = ", ".join(columns)
        placeholders = ", ".join([f":{c}" for c in columns])

        insert_sql = f"""
            INSERT INTO vehicles ({cols_str})
            VALUES ({placeholders})
            ON CONFLICT (source_url) DO NOTHING
        """

        result = session.execute(text(insert_sql), vehicles_data)
        session.commit()
        inserted = result.rowcount
        print(f"Inserted {inserted} vehicles into database")
        return inserted

    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description="Seed local PostgreSQL from frozen Bronze sample data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Use default sample data path
  python -m data_pipeline.scripts.seed_from_bronze_sample

  # Custom sample data path
  python -m data_pipeline.scripts.seed_from_bronze_sample --sample-path /path/to/sample-data

  # Limit number of records
  python -m data_pipeline.scripts.seed_from_bronze_sample --count 100

Notes:
  - Sample data must be Parquet files partitioned by dt=YYYY-MM-DD
  - This is REAL scraped data (not simulated), versioned in the repo
  - Requires local PostgreSQL running (docker-compose up postgres)
"""
    )
    parser.add_argument(
        "--sample-path",
        type=Path,
        default=DEFAULT_SAMPLE_PATH,
        help=f"Path to sample Parquet data (default: {DEFAULT_SAMPLE_PATH})"
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=None,
        help="Maximum number of records to load (default: all)"
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="PostgreSQL connection URL (default: from DATABASE_URL env or localhost)"
    )

    args = parser.parse_args()

    sample_path = args.sample_path
    if not sample_path.exists():
        print(f"Error: Sample path does not exist: {sample_path}")
        print("Run a live scrape first to generate sample data, or check the path.")
        sys.exit(1)

    db_url = args.db_url or get_db_url()

    print("=" * 60)
    print("AutoMind - Seed Database from Bronze Sample")
    print("=" * 60)
    print(f"Sample data: {sample_path}")
    print(f"Database:    {db_url.split('@')[-1] if '@' in db_url else db_url}")
    print(f"Limit:       {args.count or 'unlimited'}")
    print("=" * 60)

    try:
        # Load sample data
        df = load_sample_parquet(sample_path)

        # Normalize
        df_norm = normalize_sample_data(df)

        # Seed database
        inserted = seed_vehicles(df_norm, db_url, limit=args.count)

        print("=" * 60)
        print(f"Done! {inserted} vehicles seeded.")
        print("=" * 60)

    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()