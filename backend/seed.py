import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing

async def seed():
    async for db in get_db():
        # Create a test user
        user_id = uuid.uuid4()
        test_user = User(
            id=user_id,
            email="test@wakala.ma",
            password_hash="hashed_password", 
            name="Wakala Test",
            role="seller",
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(test_user)
        
        # Create Vehicle 1
        v1_id = uuid.uuid4()
        v1 = Vehicle(
            id=v1_id,
            seller_id=user_id,
            brand="Peugeot",
            model="208",
            year=2021,
            mileage=45000,
            fuel_type="diesel",
            body_type="citadine",
            transmission="manuelle",
            doors=5,
            seats=5,
            city="Casablanca",
            price=145000.0,
            condition_score=8.5,
            popularity_score=0.9,
            description="Voiture première main, entretien régulier. Idéale pour la ville.",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(v1)
        
        # Create Listing 1
        l1_id = uuid.uuid4()
        l1 = Listing(
            id=l1_id,
            vehicle_id=v1_id,
            status="active",
            published_at=datetime.now(timezone.utc),
            images_urls=["https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=600"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(l1)

        # Create Vehicle 2
        v2_id = uuid.uuid4()
        v2 = Vehicle(
            id=v2_id,
            seller_id=user_id,
            brand="Volkswagen",
            model="Golf 8",
            version="R-Line",
            year=2022,
            mileage=15000,
            fuel_type="diesel",
            body_type="berline",
            transmission="automatique",
            doors=5,
            seats=5,
            city="Rabat",
            price=320000.0,
            condition_score=9.5,
            popularity_score=0.95,
            description="Toutes options, état neuf.",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(v2)
        
        # Create Listing 2
        l2_id = uuid.uuid4()
        l2 = Listing(
            id=l2_id,
            vehicle_id=v2_id,
            status="active",
            published_at=datetime.now(timezone.utc),
            images_urls=["https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?q=80&w=600"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(l2)

        # Create Vehicle 3
        v3_id = uuid.uuid4()
        v3 = Vehicle(
            id=v3_id,
            seller_id=user_id,
            brand="Dacia",
            model="Duster",
            year=2020,
            mileage=80000,
            fuel_type="diesel",
            body_type="suv",
            transmission="manuelle",
            doors=5,
            seats=5,
            city="Marrakech",
            price=125000.0,
            condition_score=7.0,
            popularity_score=0.8,
            description="Bon état, robuste pour tous les chemins.",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(v3)
        
        # Create Listing 3
        l3_id = uuid.uuid4()
        l3 = Listing(
            id=l3_id,
            vehicle_id=v3_id,
            status="active",
            published_at=datetime.now(timezone.utc),
            images_urls=["https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=600"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(l3)

        await db.commit()
        print("Database seeded with 3 vehicles successfully!")
        break

if __name__ == "__main__":
    asyncio.run(seed())
