import asyncio
from app.core.database import async_session_factory
from sqlalchemy import text

async def update():
    async with async_session_factory() as db:
        await db.execute(text("""
            UPDATE vehicles
            SET mileage = 0
            WHERE id IN (
                SELECT id FROM (
                    SELECT id, ROW_NUMBER() OVER(PARTITION BY brand ORDER BY created_at DESC) as rn
                    FROM vehicles
                ) t
                WHERE t.rn <= 2
            );
        """))
        await db.commit()
        print("Successfully updated vehicles to be NEW (mileage=0).")

asyncio.run(update())
