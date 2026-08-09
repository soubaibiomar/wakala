import asyncio
from app.core.database import async_session_factory
from sqlalchemy import text

async def get_v():
    async with async_session_factory() as db:
        result = await db.execute(text('SELECT v.brand, v.model, l.images_urls FROM vehicles v LEFT JOIN listings l ON v.id = l.vehicle_id ORDER BY v.created_at DESC LIMIT 5;'))
        for row in result.fetchall():
            print(f"Brand: {row[0]}, Model: {row[1]}, Images: {row[2]}")

if __name__ == "__main__":
    asyncio.run(get_v())
