import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from app.core.database import async_session_factory
from sqlalchemy import select
from app.models.vehicle import Vehicle

async def get_desc():
    async with async_session_factory() as db:
        res = await db.execute(select(Vehicle.description).where(Vehicle.description.ilike('%Véhicule Neuf Officiel%')).limit(1))
        print(res.scalar())

if __name__ == '__main__':
    asyncio.run(get_desc())
