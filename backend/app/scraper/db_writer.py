"""
DbWriter — insère les données (générées/scrapées) dans PostgreSQL.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.vehicle import Vehicle


async def _get_or_create_default_seller(session: AsyncSession) -> uuid.UUID:
    result = await session.execute(
        select(User).limit(1)
    )
    user = result.scalar_one_or_none()
    if user:
        return user.id

    default_seller = User(
        full_name="Vendeur Wakala",
        email="contact@wakala.ma",
        phone="+212600000000",
        hashed_password="$2b$12$placeholder",
        role="seller",
        is_verified=True,
        preferences={},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(default_seller)
    await session.flush()
    return default_seller.id


async def save_vehicle(session: AsyncSession, data: dict) -> Vehicle:
    seller_id = await _get_or_create_default_seller(session)

    vehicle = Vehicle(
        seller_id=data.get("seller_id") or seller_id,
        brand=data.get("brand") or "Inconnu",
        model=data.get("model") or "Inconnu",
        year=data.get("year") or 2020,
        price=float(data.get("price", 0)),
        mileage=data.get("mileage") or 0,
        fuel_type=data.get("fuel_type") or "essence",
        body_type=data.get("body_type") or "berline",
        transmission=data.get("transmission") or "manuelle",
        engine_power_hp=data.get("engine_power_hp"),
        color=data.get("color"),
        doors=data.get("doors"),
        seats=data.get("seats"),
        city=data.get("city") or "Casablanca",
        description=data.get("description") or "",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(vehicle)
    await session.flush()
    return vehicle


async def save_vehicles(session: AsyncSession, vehicles: list[dict]) -> int:
    count = 0
    for v in vehicles:
        try:
            await save_vehicle(session, v)
            count += 1
        except Exception as e:
            print(f"  Erreur insertion {v.get('brand')} {v.get('model')}: {e}")
            await session.rollback()
    return count
