import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

engine = create_async_engine('postgresql+asyncpg://wakala_user:wakala_secret_password@localhost:5433/wakala')

async def run():
    async with engine.begin() as conn:
        with open('alembic/versions/014_failed_scrapes.sql') as f:
            sql = f.read()
        await conn.execute(text(sql))
    print('Migration 014 ran successfully.')

asyncio.run(run())
