"""
train_pricing.py — Training script for XGBoost price model.

Reads vehicles from the Gold layer (PostgreSQL), trains the model,
and saves artifacts (model, encoders, scaler).

Can be run standalone or triggered by Airflow:
    python -m app.ml.pricing.train_pricing

Environment: DB connection via app.core.config settings.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.ml.pricing.price_model import price_model
from app.models.vehicle import Vehicle


async def train_from_db(min_samples: int = 50):
    print("[train_pricing] Loading vehicles from DB...")
    async with async_session_factory() as session:
        session: AsyncSession
        # Priorité aux annonces vendues (Argus)
        result = await session.execute(
            select(Vehicle).where(Vehicle.price.isnot(None), Vehicle.status == 'sold')
        )
        vehicles = list(result.scalars().all())

        if len(vehicles) < min_samples:
            print(f"[train_pricing] Cold Start: Not enough sold vehicles ({len(vehicles)}). Falling back to 'available'.")
            result = await session.execute(
                select(Vehicle).where(Vehicle.price.isnot(None), Vehicle.status == 'available')
            )
            vehicles.extend(list(result.scalars().all()))

    print(f"[train_pricing] Loaded {len(vehicles)} vehicles for training.")
    if len(vehicles) < min_samples:
        print(
            f"[train_pricing] WARNING: only {len(vehicles)} samples "
            f"(min {min_samples}). Model may underperform."
        )

    print("[train_pricing] Training XGBoost model...")
    price_model.train(vehicles)
    print("[train_pricing] Done. Model saved.")


def main():
    asyncio.run(train_from_db())


if __name__ == "__main__":
    main()
