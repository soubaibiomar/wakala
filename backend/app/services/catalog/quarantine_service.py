from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import BrandCatalog, ModelCatalog, TrimCatalog
from app.models.staging_ingestion import StagedCatalogScrape, CatalogIngestAnomaly


MAX_SAFE_PRICE_VARIANCE_PCT = 0.25  # 25% price change threshold


async def evaluate_staged_scrape(
    session: AsyncSession,
    staged_item: StagedCatalogScrape
) -> Dict[str, Any]:
    """
    Evaluates an incoming staged car scrape against the live catalog.
    Detects price spikes, drops, or missing data and logs anomalies into quarantine.
    """
    # 1. Look for existing live brand & model
    brand_stmt = select(BrandCatalog).where(BrandCatalog.name.ilike(staged_item.brand_name))
    brand_res = await session.execute(brand_stmt)
    brand = brand_res.scalars().first()

    if not brand:
        staged_item.status = "PENDING_REVIEW"
        staged_item.anomaly_flag = True
        staged_item.anomaly_reason = f"Unknown brand: {staged_item.brand_name}"
        return {"status": "FLAGGED", "reason": staged_item.anomaly_reason}

    model_stmt = select(ModelCatalog).where(
        ModelCatalog.brand_id == brand.id,
        ModelCatalog.name.ilike(staged_item.model_name)
    )
    model_res = await session.execute(model_stmt)
    model = model_res.scalars().first()

    if not model:
        staged_item.status = "PENDING_REVIEW"
        staged_item.anomaly_flag = True
        staged_item.anomaly_reason = f"New model detected: {staged_item.model_name} (Requires verification)"
        return {"status": "FLAGGED", "reason": staged_item.anomaly_reason}

    # 2. Check for existing Trim to compare pricing
    trim_stmt = select(TrimCatalog).where(
        TrimCatalog.model_id == model.id,
        TrimCatalog.name.ilike(staged_item.trim_name)
    )
    trim_res = await session.execute(trim_stmt)
    existing_trim = trim_res.scalars().first()

    if existing_trim:
        old_price = existing_trim.price_mad
        new_price = staged_item.scraped_price_mad

        if old_price > 0:
            variance = abs(new_price - old_price) / old_price
            if variance > MAX_SAFE_PRICE_VARIANCE_PCT:
                anomaly_type = "PRICE_SPIKE" if new_price > old_price else "PRICE_DROP"
                anomaly = CatalogIngestAnomaly(
                    staged_scrape_id=staged_item.id,
                    brand_name=staged_item.brand_name,
                    model_name=staged_item.model_name,
                    trim_name=staged_item.trim_name,
                    anomaly_type=anomaly_type,
                    severity="CRITICAL" if variance > 0.40 else "MEDIUM",
                    old_value=f"{old_price:.2f} MAD",
                    new_value=f"{new_price:.2f} MAD",
                    details=f"Price changed by {variance * 100:.1f}% (exceeds {MAX_SAFE_PRICE_VARIANCE_PCT * 100:.0f}% safety margin)"
                )
                session.add(anomaly)
                staged_item.status = "QUARANTINED"
                staged_item.anomaly_flag = True
                staged_item.anomaly_reason = anomaly.details
                return {"status": "QUARANTINED", "anomaly": anomaly_type, "variance_pct": round(variance * 100, 2)}

        # Safe update
        existing_trim.price_mad = new_price
        if staged_item.scraped_promo_price_mad:
            existing_trim.promo_price_mad = staged_item.scraped_promo_price_mad
        staged_item.status = "PROMOTED"
        staged_item.promoted_at = datetime.utcnow()
        return {"status": "PROMOTED", "action": "PRICE_UPDATED", "price_mad": new_price}

    # New trim within existing verified model
    staged_item.status = "AUTO_APPROVED"
    return {"status": "AUTO_APPROVED", "action": "NEW_TRIM_READY"}
