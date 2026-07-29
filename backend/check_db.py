import asyncio
import uuid
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.core.database import async_session_factory
from sqlalchemy import text

async def main():
    async with async_session_factory() as db:
        result = await db.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [r[0] for r in result.fetchall()]
        print('Tables:', tables)
        
        if 'vehicles' in tables:
            rows = await db.execute(text("SELECT id, mileage FROM vehicles LIMIT 5"))
            print('Vehicles mileage:', [dict(r._mapping) for r in rows])
        
        if 'listings' in tables:
            rows = await db.execute(text("SELECT id, kilometrage FROM listings LIMIT 5"))
            print('Listings kilometrage:', [dict(r._mapping) for r in rows])
        
if __name__ == '__main__':
    asyncio.run(main())
