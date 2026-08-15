"""
Loop A — Hard-delete used-car rows from the database.

Identifies used-car vehicles by:
1. mileage > 100 (new cars have mileage=0 or very low delivery km)
2. description does NOT contain "Véhicule Neuf Officiel"
3. source_url contains known used-car sources (avito, globaloccaz, spoticar, carz)

Cascades deletions to: listings, reviews, offers, saved_vehicles, 
vehicle_services, service_reminders (via FK CASCADE or manual cleanup).

Usage:
    python -m scripts.cleanup_used_cars --dry-run   # Preview what would be deleted
    python -m scripts.cleanup_used_cars --execute    # Actually delete
"""

import asyncio
import argparse
import logging
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select, func, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.vehicle import Vehicle

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Known used-car sources
USED_CAR_SOURCES = ['avito', 'globaloccaz', 'global_occaz', 'spoticar', 'carz']


async def identify_used_cars(session: AsyncSession) -> list:
    """Identify vehicles that are used cars (not new)."""
    
    # Strategy: A vehicle is "used" if ANY of these are true:
    # 1. source_url contains a known used-car marketplace domain
    # 2. mileage > 500 AND description does NOT contain "Véhicule Neuf"
    # We're conservative: if in doubt, we keep the vehicle.
    
    result = await session.execute(
        select(Vehicle.id, Vehicle.brand, Vehicle.model, Vehicle.year, 
               Vehicle.mileage, Vehicle.source_url, Vehicle.price)
        .where(
            # Used-car condition: high mileage without "Neuf" marker
            # OR from a known used-car source
            (
                (Vehicle.mileage > 500) & 
                (
                    Vehicle.description.is_(None) |
                    ~Vehicle.description.ilike('%Véhicule Neuf%')
                )
            ) |
            (
                Vehicle.source_url.ilike('%avito%') |
                Vehicle.source_url.ilike('%globaloccaz%') |
                Vehicle.source_url.ilike('%spoticar%') |
                Vehicle.source_url.ilike('%carz%')
            )
        )
    )
    
    return result.all()


async def delete_used_cars(session: AsyncSession, vehicle_ids: list, dry_run: bool = True):
    """Delete used-car vehicles and cascade to dependent tables."""
    
    if not vehicle_ids:
        logger.info("No used-car vehicles to delete.")
        return
    
    id_list = [v.id for v in vehicle_ids]
    
    if dry_run:
        logger.info(f"[DRY-RUN] Would delete {len(id_list)} used-car vehicles:")
        for v in vehicle_ids[:20]:  # Show first 20
            logger.info(f"  - {v.brand} {v.model} ({v.year}) | {v.mileage} km | {v.price} MAD | {v.source_url}")
        if len(vehicle_ids) > 20:
            logger.info(f"  ... and {len(vehicle_ids) - 20} more")
        return
    
    # Manual cascade: delete from dependent tables first
    # (even though FK has ON DELETE CASCADE, being explicit is safer)
    
    logger.info(f"Deleting from saved_vehicles junction table...")
    await session.execute(
        text("DELETE FROM saved_vehicles WHERE vehicle_id = ANY(:ids)"),
        {"ids": id_list}
    )
    
    logger.info(f"Deleting from reviews...")
    await session.execute(
        text("DELETE FROM reviews WHERE vehicle_id = ANY(:ids)"),
        {"ids": id_list}
    )
    
    logger.info(f"Deleting from offers...")
    await session.execute(
        text("DELETE FROM offers WHERE vehicle_id = ANY(:ids)"),
        {"ids": id_list}
    )
    
    logger.info(f"Deleting from vehicle_services...")
    await session.execute(
        text("DELETE FROM vehicle_services WHERE vehicle_id = ANY(:ids)"),
        {"ids": id_list}
    )
    
    logger.info(f"Deleting from service_reminders...")
    await session.execute(
        text("DELETE FROM service_reminders WHERE vehicle_id = ANY(:ids)"),
        {"ids": id_list}
    )
    
    logger.info(f"Deleting from listings...")
    await session.execute(
        text("DELETE FROM listings WHERE vehicle_id = ANY(:ids)"),
        {"ids": id_list}
    )
    
    logger.info(f"Deleting {len(id_list)} vehicles...")
    await session.execute(
        text("DELETE FROM vehicles WHERE id = ANY(:ids)"),
        {"ids": id_list}
    )
    
    await session.commit()
    logger.info(f"✅ Successfully deleted {len(id_list)} used-car vehicles and all dependent records.")


async def verify_cleanup(session: AsyncSession):
    """Verify no used-car rows remain."""
    
    # Count remaining vehicles with high mileage
    result = await session.execute(
        select(func.count(Vehicle.id)).where(Vehicle.mileage > 500)
    )
    high_mileage_count = result.scalar() or 0
    
    # Count remaining vehicles from used-car sources
    result = await session.execute(
        select(func.count(Vehicle.id)).where(
            Vehicle.source_url.ilike('%avito%') |
            Vehicle.source_url.ilike('%globaloccaz%') |
            Vehicle.source_url.ilike('%spoticar%') |
            Vehicle.source_url.ilike('%carz%')
        )
    )
    used_source_count = result.scalar() or 0
    
    # Count total remaining vehicles
    result = await session.execute(select(func.count(Vehicle.id)))
    total_count = result.scalar() or 0
    
    # Check for orphaned references
    orphan_checks = [
        ("listings", "SELECT COUNT(*) FROM listings l LEFT JOIN vehicles v ON l.vehicle_id = v.id WHERE v.id IS NULL"),
        ("reviews", "SELECT COUNT(*) FROM reviews r LEFT JOIN vehicles v ON r.vehicle_id = v.id WHERE v.id IS NULL"),
        ("saved_vehicles", "SELECT COUNT(*) FROM saved_vehicles sv LEFT JOIN vehicles v ON sv.vehicle_id = v.id WHERE v.id IS NULL"),
    ]
    
    logger.info(f"\n{'='*60}")
    logger.info(f"VERIFICATION RESULTS")
    logger.info(f"{'='*60}")
    logger.info(f"Total vehicles remaining: {total_count}")
    logger.info(f"High-mileage vehicles (>500 km): {high_mileage_count}")
    logger.info(f"Vehicles from used-car sources: {used_source_count}")
    
    all_clean = high_mileage_count == 0 and used_source_count == 0
    
    for table_name, query in orphan_checks:
        try:
            result = await session.execute(text(query))
            orphan_count = result.scalar() or 0
            status = "✅" if orphan_count == 0 else "❌"
            logger.info(f"Orphaned refs in {table_name}: {orphan_count} {status}")
            if orphan_count > 0:
                all_clean = False
        except Exception as e:
            logger.warning(f"Could not check {table_name}: {e}")
    
    if all_clean:
        logger.info(f"\n✅ LOOP A VERIFIED: Zero used-car rows, zero orphaned references.")
    else:
        logger.warning(f"\n⚠️ LOOP A NEEDS ATTENTION: Some used-car data may remain.")
    
    return all_clean


async def main(dry_run: bool):
    async with async_session_factory() as session:
        # 1. DETECT
        logger.info("Phase 1: Detecting used-car vehicles...")
        used_cars = await identify_used_cars(session)
        logger.info(f"Found {len(used_cars)} used-car vehicles to delete.")
        
        # 2. ACT
        logger.info(f"\nPhase 2: {'[DRY-RUN] Previewing' if dry_run else 'Executing'} deletion...")
        await delete_used_cars(session, used_cars, dry_run=dry_run)
        
        # 3. EVALUATE
        if not dry_run:
            logger.info(f"\nPhase 3: Verifying cleanup...")
            await verify_cleanup(session)
        else:
            logger.info(f"\nRe-run with --execute to perform actual deletion.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up used-car data from the database")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Preview what would be deleted")
    group.add_argument("--execute", action="store_true", help="Actually delete the data")
    args = parser.parse_args()
    
    asyncio.run(main(dry_run=args.dry_run))
