import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def run_migrations():
    print(f"Connecting to {settings.DATABASE_URL.replace('postgresql+asyncpg', 'postgresql')}")
    # We would normally run alembic, but since this project has raw SQL migrations in `database/postgres/migrations/`, we'll just execute it.
    engine = create_async_engine(settings.DATABASE_URL)
    
    with open('../database/postgres/migrations/013_maintenance_module.sql', 'r', encoding='utf-8') as f:
        sql = f.read()

    async with engine.begin() as conn:
        from sqlalchemy import text
        try:
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            for stmt in statements:
                await conn.execute(text(stmt))
            print("Migration 013 applied successfully.")
        except Exception as e:
            print(f"Error applying migration: {e}")

if __name__ == "__main__":
    asyncio.run(run_migrations())
