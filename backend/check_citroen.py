import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path('/app')))
from app.core.database import async_session_factory
from sqlalchemy import select, func
from app.models.vehicle import Vehicle

async def check():
    async with async_session_factory() as session:
        result = await session.execute(select(func.count(Vehicle.id)).where(Vehicle.brand.ilike("%citro%"), Vehicle.mileage == 0))
        count = result.scalar()
        print(f"Citroen neuf count: {count}")

asyncio.run(check())
