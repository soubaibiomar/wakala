import asyncio
import random
import os
import sys

# Ensure we can import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

async def fix_mileages():
    print(f"Connecting to {settings.DATABASE_URL}...")
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Fetch vehicles with 0 mileage that don't have 'véhicule neuf' in their description
        result = await session.execute(text("SELECT id, year, description FROM vehicles WHERE mileage = 0 OR mileage IS NULL OR mileage = -1"))
        rows = result.fetchall()
        
        print(f"Found {len(rows)} vehicles with 0/-1/null mileage.")
        
        count = 0
        for row in rows:
            v_id = row[0]
            year = row[1]
            description = row[2] or ""
            
            if "véhicule neuf" in description.lower():
                continue
                
            if year is None:
                year = 2018
            
            # Realistic mileage calculation
            age = max(1, 2024 - year)
            base_mileage = age * 15000
            random_variation = random.randint(int(base_mileage * 0.8), int(base_mileage * 1.2))
            
            await session.execute(
                text("UPDATE vehicles SET mileage = :mileage WHERE id = :id"),
                {"mileage": random_variation, "id": v_id}
            )
            count += 1
            
        await session.commit()
        print(f"Successfully updated {count} used vehicles to have realistic mileage.")

if __name__ == "__main__":
    asyncio.run(fix_mileages())
