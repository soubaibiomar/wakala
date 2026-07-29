import asyncio
import json
import uuid
import sys
from datetime import datetime, timezone
from confluent_kafka import Consumer, KafkaError

from app.core.database import async_session_factory
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from app.core.config import settings

KAFKA_BOOTSTRAP = settings.KAFKA_BOOTSTRAP_SERVERS

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
            user = User(
                id=user_id,
                email="scraped_live@wakala.ma",
                hashed_password="hashed_password", 
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
                
            print(f"Received listing from Kafka: {data.get('brand')} {data.get('model')}")
            
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
                    year=data.get("year") if data.get("year") is not None else 2020,
                    mileage=data.get("mileage") if data.get("mileage") is not None else 0,
                    fuel_type=data.get("fuel_type") or "diesel",
                    body_type=data.get("body_type") or "suv",
                    transmission=data.get("transmission") or "manuelle",
                    city=str(data.get("city") or "Casablanca"),
                    price=price,
                    description=data.get("description", ""),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(v)
                
                listing_id = uuid.uuid4()
                images = data.get("images_urls") or ["https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=600"]
                    
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
                await db.commit()
                print(f"Saved {data.get('brand')} {data.get('model')} to Postgres!")
                
        except Exception as e:
            print(f"Error processing message: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(consume_to_postgres())
    except KeyboardInterrupt:
        print("Stopped consumer.")
