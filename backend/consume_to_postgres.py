import asyncio
import json
import uuid
import sys
import os
import httpx
from datetime import datetime, timezone
from confluent_kafka import Consumer, KafkaError

from app.core.database import async_session_factory
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from app.core.config import settings

KAFKA_BOOTSTRAP = settings.KAFKA_BOOTSTRAP_SERVERS

UPLOAD_DIR = "uploads/scraped"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def download_image(url: str) -> str:
    """Download an image and return its local relative URL. Return original if failed."""
    if not url or not url.startswith("http"):
        return url
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                ext = url.split('.')[-1].split('?')[0][:4]
                if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                    ext = 'jpg'
                filename = f"{uuid.uuid4()}.{ext}"
                filepath = os.path.join(UPLOAD_DIR, filename)
                
                def save_file():
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                
                await asyncio.to_thread(save_file)
                
                return f"http://localhost:8000/{UPLOAD_DIR}/{filename}"
            return url
    except Exception as e:
        print(f"Failed to download image {url}: {e}")
        return url

async def consume_to_postgres():
    print(f"Connecting to Kafka at {KAFKA_BOOTSTRAP}...")
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': 'wakala-postgres-consumer',
        'auto.offset.reset': 'earliest'
    })
    consumer.subscribe(['listings.raw'])

    print("Kafka consumer started! Listening for scraped listings...")
    
    # We will use the same "Auto Scraper Live" user logic
    async with async_session_factory() as db:
        result = await db.execute(User.__table__.select().where(User.email == "scraped_live@wakala.ma"))
        row = result.fetchone()
        
        if not row:
            user_id = uuid.uuid4()
            # Génère un mot de passe aléatoire sécurisé (ce compte système ne doit
            # jamais être utilisé pour une connexion humaine)
            from app.core.security import hash_password
            import secrets as _secrets
            _system_pw = hash_password(_secrets.token_urlsafe(64))
            user = User(
                id=user_id,
                email="scraped_live@wakala.ma",
                hashed_password=_system_pw, 
                full_name="Auto Scraper Live",
                phone="+212600000001",
                role="seller",
                is_verified=True,
                is_pro=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(user)
            await db.commit()
        else:
            user_id = row.id

    # Listen to Kafka indefinitely
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            await asyncio.sleep(1)
            continue
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print(f"Kafka error: {msg.error()}")
            continue

        try:
            event = json.loads(msg.value().decode("utf-8"))
            data = event.get("data", {})
            if not data:
                continue
                
            # Wakala is strictly a new car platform (0 km)
            mileage = data.get("mileage") or 0
            year = data.get("year") or 2026
            if mileage > 0 or year < 2024:
                print(f"Skipping used vehicle ({data.get('brand')} {data.get('model')} - {year}, {mileage} km) — Wakala is new cars only.")
                continue

            print(f"Received new car listing from Kafka: {data.get('brand')} {data.get('model')}")
            
            async with async_session_factory() as db:
                vehicle_id = uuid.uuid4()
                
                price = data.get("price")
                try:
                    price = float(price)
                except (ValueError, TypeError):
                    price = 100000.0

                v = Vehicle(
                    id=vehicle_id,
                    seller_id=user_id,
                    brand=str(data.get("brand") or "Inconnu"),
                    model=str(data.get("model") or "Inconnu"),
                    year=year,
                    mileage=0,
                    condition="new",
                    source="wakala_catalogue",
                    fuel_type=data.get("fuel_type") or "diesel",
                    body_type=data.get("body_type") or "suv",
                    transmission=data.get("transmission") or "manuelle",
                    city=str(data.get("city") or "Casablanca"),
                    price=price,
                    description=data.get("description", "") or f"Véhicule Neuf Officiel — {data.get('brand')} {data.get('model')}.",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(v)
                
                listing_id = uuid.uuid4()
                raw_images = data.get("images_urls") or ["https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=600"]
                
                # Download all images concurrently
                local_images = await asyncio.gather(*[download_image(img_url) for img_url in raw_images])
                    
                l = Listing(
                    id=listing_id,
                    vehicle_id=vehicle_id,
                    status="active",
                    published_at=datetime.now(timezone.utc),
                    images_urls=list(local_images),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(l)
                await db.commit()
                print(f"Saved {data.get('brand')} {data.get('model')} to Postgres!")
                
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(consume_to_postgres())
    except KeyboardInterrupt:
        print("Stopped consumer.")
