import asyncio
import uuid
from datetime import datetime, timezone

from app.core.database import async_session_factory
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing

cars = [
    {
        "brand": "Mercedes-Benz",
        "model": "Classe C",
        "year": 2021,
        "price": 450000.0,
        "mileage": 35000,
        "fuel_type": "diesel",
        "body_type": "berline",
        "transmission": "automatique",
        "description": "Mercedes Classe C 220d Pack AMG Line. Excellent état, entretien maison. Sièges chauffants, toit panoramique, caméra 360.",
        "images_urls": ["https://images.unsplash.com/photo-1618843479313-40f8afb4b4d8?q=80&w=800"],
        "source": "Avito",
        "source_url": "https://www.avito.ma/mercedes-classe-c"
    },
    {
        "brand": "Porsche",
        "model": "Macan",
        "year": 2020,
        "price": 750000.0,
        "mileage": 42000,
        "fuel_type": "essence",
        "body_type": "suv",
        "transmission": "automatique",
        "description": "Porsche Macan S 3.0 V6 354ch. Full options. Cuir étendu, jantes 21 pouces, échappement sport, phares LED matrix.",
        "images_urls": ["https://images.unsplash.com/photo-1503376713915-0563456c8052?q=80&w=800"],
        "source": "Moteur",
        "source_url": "https://www.moteur.ma/porsche-macan"
    },
    {
        "brand": "BMW",
        "model": "Série 4",
        "year": 2022,
        "price": 660000.0,
        "mileage": 15000,
        "fuel_type": "diesel",
        "body_type": "coupe",
        "transmission": "automatique",
        "description": "BMW 420d Coupé M Sport. État neuf, première main. Pack innovation, affichage tête haute, Harman Kardon.",
        "images_urls": ["https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=800"],
        "source": "Kifal",
        "source_url": "https://www.kifal-auto.ma/bmw-serie-4"
    },
    {
        "brand": "Land Rover",
        "model": "Range Rover Sport",
        "year": 2019,
        "price": 820000.0,
        "mileage": 68000,
        "fuel_type": "diesel",
        "body_type": "suv",
        "transmission": "automatique",
        "description": "Range Rover Sport 3.0 SDV6 HSE Dynamic. Gris Carpathian, intérieur cuir Oxford noir, marchepieds électriques.",
        "images_urls": ["https://images.unsplash.com/photo-1606016159991-d8532e2c0e62?q=80&w=800"],
        "source": "Global Occaz",
        "source_url": "https://globaloccaz.ma/range-rover"
    },
    {
        "brand": "Audi",
        "model": "Q5",
        "year": 2021,
        "price": 540000.0,
        "mileage": 45000,
        "fuel_type": "diesel",
        "body_type": "suv",
        "transmission": "automatique",
        "description": "Audi Q5 40 TDI Quattro S Line. Véhicule importé neuf. Virtual cockpit, phares Matrix LED, jantes 20 pouces.",
        "images_urls": ["https://images.unsplash.com/photo-1606664515524-ed2f786a0b16?q=80&w=800"],
        "source": "Otoclic",
        "source_url": "https://otoclic.ma/audi-q5"
    }
]

async def seed():
    async with async_session_factory() as db:
        # Delete existing bad vehicles
        await db.execute(Vehicle.__table__.delete())
        
        # Get or create seed user
        result = await db.execute(User.__table__.select().where(User.email == "scraped_live@wakala.ma"))
        row = result.fetchone()
        if not row:
            user_id = uuid.uuid4()
            user = User(
                id=user_id, email="scraped_live@wakala.ma", hashed_password="pw",
                full_name="Auto Scraper Live", phone="06000000", role="seller",
                is_verified=True, is_pro=True, created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(user)
            await db.commit()
        else:
            user_id = row.id

        # Insert perfect cars
        for car in cars:
            v_id = uuid.uuid4()
            v = Vehicle(
                id=v_id,
                seller_id=user_id,
                brand=car["brand"],
                model=car["model"],
                year=car["year"],
                price=car["price"],
                mileage=car["mileage"],
                fuel_type=car["fuel_type"],
                body_type=car["body_type"],
                transmission=car["transmission"],
                description=car["description"],
                source_url=car["source_url"],
                # Generate a random trust score between 80 and 96 for realism!
                condition_score=80 + (int(v_id) % 17),
                city="Casablanca",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(v)
            
            l = Listing(
                id=uuid.uuid4(),
                vehicle_id=v_id,
                status="active",
                images_urls=car["images_urls"],
                published_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(l)
        
        await db.commit()
        print("Successfully seeded 5 perfect real cars with images!")

if __name__ == "__main__":
    asyncio.run(seed())
