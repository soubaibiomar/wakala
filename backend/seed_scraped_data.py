import sys
import os
from pathlib import Path
import asyncio
import uuid
from datetime import datetime, timezone
import random

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from data_pipeline.kafka.producers.scrapers.avito_scraper import AvitoScraper
from data_pipeline.kafka.producers.scrapers.moteur_scraper import MoteurScraper

from app.core.database import async_session_factory
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing

def fetch_data():
    print("Fetching data from Avito...")
    avito = AvitoScraper()
    avito_listings = avito.fetch_listings(5)
    
    print("Fetching data from Moteur.ma...")
    moteur = MoteurScraper()
    moteur_listings = moteur.fetch_listings(5)
    
    return avito_listings + moteur_listings

async def seed_scraped_data(all_scraped):
    print(f"Total listings fetched: {len(all_scraped)}")
    
    if len(all_scraped) == 0:
        print("No listings fetched! Exiting.")
        return
        
    async with async_session_factory() as db:
        # Find or create a user for these scraped listings
        result = await db.execute(User.__table__.select().where(User.email == "scraped_live@wakala.ma"))
        row = result.fetchone()
        
        if not row:
            user_id = uuid.uuid4()
            user = User(
                id=user_id,
                email="scraped_live@wakala.ma",
                password_hash="hashed_password", 
                name="Auto Scraper Live",
                role="seller",
                is_verified=True,
                is_pro=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(user)
            await db.flush()
        else:
            user_id = row.id

        inserted = 0
        for data in all_scraped:
            if not data: continue
            
            # basic clean and validate
            price_str = data.get("price")
            price = 0.0
            if price_str:
                try:
                    price_str = str(price_str).replace(' ', '').replace('MAD', '').replace(',', '').strip()
                    price = float(price_str)
                except ValueError:
                    price = random.uniform(50000, 300000)
            
            if price == 0.0:
                price = random.uniform(50000, 300000)

            fuel = data.get("fuel_type") or "essence"
            valid_fuels = ["essence", "diesel", "hybride", "hybride_rechargeable", "electrique", "gpl", "hydrogene"]
            if fuel not in valid_fuels: fuel = "diesel"

            body = data.get("body_type") or "berline"
            valid_bodies = ["citadine", "berline", "suv", "break", "coupe", "cabriolet", "monospace", "utilitaire", "pick_up"]
            if body not in valid_bodies: body = "suv"

            trans = data.get("transmission") or "manuelle"
            valid_trans = ["manuelle", "automatique", "semi_auto"]
            if trans not in valid_trans: trans = "manuelle"

            vehicle_id = uuid.uuid4()
            v = Vehicle(
                id=vehicle_id,
                seller_id=user_id,
                brand=str(data.get("brand") or "Inconnu"),
                model=str(data.get("model") or "Inconnu"),
                year=data.get("year") or 2018,
                mileage=data.get("mileage") or 100000,
                fuel_type=fuel,
                body_type=body,
                transmission=trans,
                city=str(data.get("city") or "Casablanca"),
                price=price,
                condition_score=random.uniform(60, 95),
                popularity_score=random.uniform(0.5, 0.99),
                description=f"Source: {data.get('source_url', 'Unknown')}",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(v)
            
            listing_id = uuid.uuid4()
            images = data.get("images_urls", [])
            if not images:
                images = ["https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=600"]
                
            l = Listing(
                id=listing_id,
                vehicle_id=vehicle_id,
                status="active",
                published_at=datetime.now(timezone.utc),
                images_urls=images,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(l)
            inserted += 1
            
        await db.commit()
        print(f"Successfully saved {inserted} REAL scraped vehicles to DB!")

if __name__ == "__main__":
    scraped = fetch_data()
    asyncio.run(seed_scraped_data(scraped))
