import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import async_session_factory
from sqlalchemy import select, func
from app.models.vehicle import Vehicle

async def count():
    async with async_session_factory() as db:
        res = await db.execute(select(func.count(Vehicle.id)))
        print(res.scalar())

if __name__ == "__main__":
    asyncio.run(count())
