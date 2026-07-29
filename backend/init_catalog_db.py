import sys
import os
import asyncio
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent))

from app.core.database import Base, engine
from app.models.catalog import BrandCatalog, ModelCatalog, TechSpecCatalog

async def init_catalog_db():
    print("Creating catalog tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Done!")

if __name__ == "__main__":
    asyncio.run(init_catalog_db())
