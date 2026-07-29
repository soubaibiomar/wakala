import asyncio
from app.core.database import async_session_factory
from sqlalchemy import text

async def get():
    async with async_session_factory() as db:
        res = await db.execute(text("SELECT images_urls FROM listings l JOIN vehicles v ON l.vehicle_id = v.id WHERE v.source_url LIKE '%kifal%' LIMIT 1;"))
        for row in res:
            print(row[0])

asyncio.run(get())
