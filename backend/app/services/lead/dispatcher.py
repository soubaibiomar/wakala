from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dealership import Showroom, Dealership
from app.models.catalog import BrandCatalog, ModelCatalog


async def dispatch_lead_to_showroom(
    session: AsyncSession,
    brand_slug: str,
    city: str
) -> Optional[Dict[str, Any]]:
    """
    Finds the optimal authorized concessionaire showroom in the user's city.
    If no showroom is in that specific city, falls back to the nearest regional hub (e.g. Casablanca / Rabat).
    """
    # 1. Search for brand
    brand_stmt = select(BrandCatalog).where(BrandCatalog.slug == brand_slug)
    brand_res = await session.execute(brand_stmt)
    brand = brand_res.scalars().first()

    # 2. Match Showroom in user's city
    stmt = select(Showroom).where(Showroom.city.ilike(f"%{city.strip()}%"))
    if brand:
        stmt = stmt.where(Showroom.dealership.has(Dealership.name.ilike(f"%{brand.name}%")))
    
    res = await session.execute(stmt)
    showroom = res.scalars().first()

    # Fallback to any showroom in the requested city or default hub (Casablanca)
    if not showroom:
        fallback_stmt = select(Showroom).where(Showroom.city.ilike("Casablanca"))
        fallback_res = await session.execute(fallback_stmt)
        showroom = fallback_res.scalars().first()

    if not showroom:
        return None

    return {
        "showroom_id": str(showroom.id),
        "name": showroom.name,
        "city": showroom.city,
        "address": showroom.address,
        "phone": showroom.phone,
        "dispatch_status": "READY_FOR_NOTIFICATION"
    }
