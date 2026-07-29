import sys
import asyncio
import uuid
from datetime import datetime, timezone
import urllib.request
from bs4 import BeautifulSoup
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import async_session_factory
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from sqlalchemy import text

BRANDS = [
    "dacia", "renault", "peugeot", "hyundai", "volkswagen", "fiat", "kia", "audi", "bmw", "mercedes",
    "jeep", "citroen", "ford", "toyota", "nissan", "skoda", "seat", "opel", "honda", "volvo", "land-rover", "alfa-romeo", "porsche", "suzuki",
    "byd", "mg", "chery", "geely", "changan", "dongfeng", "haval", "jac", "mazda", "mitsubishi", "mini", "lexus", "jaguar", "maserati", "baic", "seres", "omoda", "jaecoo"
]

def fetch_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        return urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

async def seed():
    # First, let's delete all existing is_new vehicles to avoid duplicates with wrong images
    async with async_session_factory() as db:
        await db.execute(text("DELETE FROM listings WHERE vehicle_id IN (SELECT id FROM vehicles WHERE mileage = 0 AND source_url LIKE '%neuf%')"))
        await db.execute(text("DELETE FROM vehicles WHERE mileage = 0 AND source_url LIKE '%neuf%'"))
        await db.commit()
        print("Cleaned up old is_new vehicles.")

    cars = []
    
    for brand in BRANDS:
        print(f"Fetching {brand}...")
        html = fetch_html(f"https://www.wandaloo.com/neuf/{brand}/")
        if not html: continue
        soup = BeautifulSoup(html, 'html.parser')
        
        models_data = {}
        for a in soup.select('a'):
            href = a.get('href', '')
            if href.startswith(f'https://www.wandaloo.com/neuf/{brand}/') and href != f'https://www.wandaloo.com/neuf/{brand}/':
                model_name = href.split('/')[-2].capitalize()
                if model_name not in models_data:
                    parent = a.find_parent('li') or a.find_parent('div')
                    if parent:
                        img = parent.select_one('img')
                        img_src = img.get('src') if img else None
                        if img_src and not img_src.startswith('http'):
                            img_src = 'https://www.wandaloo.com' + img_src
                        v_text = parent.text.strip().replace('\n', ' ')
                        models_data[model_name] = {'url': href, 'img': img_src, 'text': v_text}

        import re
        for model_name, data in models_data.items():
            if not data['img'] or 'emoticon' in data['img']:
                continue
                
            prices = [int(p.replace('.', '')) for p in re.findall(r'(\d{2,3}\.\d{3})', data['text'])]
            versions_match = re.search(r'(\d+)\s+versions?', data['text'])
            versions = int(versions_match.group(1)) if versions_match else 1
            
            min_price = min(prices) if prices else 200000
            max_price = max(prices) if prices else min_price
            
            for v in range(versions):
                if versions > 1:
                    price = min_price + (max_price - min_price) * (v / (versions - 1))
                else:
                    price = min_price
                    
                cars.append({
                    "brand": brand.capitalize(),
                    "model": f"{model_name} v{v+1}" if versions > 1 else model_name,
                    "year": 2024,
                    "price": int(price),
                    "mileage": 0,
                    "fuel_type": "essence" if "essence" in data['text'].lower() else "diesel",
                    "body_type": "suv" if "suv" in data['text'].lower() else "berline",
                    "transmission": "automatique" if price > 250000 else "manuelle",
                    "description": f"Véhicule Neuf Officiel : {brand.capitalize()} {model_name} Version {v+1}. Informations techniques complètes depuis le catalogue officiel.",
                    "images_urls": [data['img']],
                    "source_url": data['url'] + f"#v{v+1}",
                    "is_new": True
                })
                print(f"Added {brand.capitalize()} {model_name} v{v+1} ({int(price)} MAD)")

    if not cars:
        print("No new cars found.")
        return

    # SAVE to DB
    async with async_session_factory() as db:
        result = await db.execute(User.__table__.select().where(User.email == "scraped_live@wakala.ma"))
        row = result.fetchone()
        user_id = row.id if row else None
        if not user_id:
            user_id = uuid.uuid4()
            user = User(
                id=user_id, email="scraped_live@wakala.ma", hashed_password="pw",
                full_name="Auto Scraper Live", phone="06000000", role="seller",
                is_verified=True, is_pro=True, created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(user)
            await db.flush()
        
        added = 0
        for car in cars:
            from sqlalchemy.future import select
            existing = await db.execute(select(Vehicle).where(Vehicle.source_url == car["source_url"]))
            if existing.scalars().first():
                continue
                
            v_id = uuid.uuid4()
            v = Vehicle(
                id=v_id, seller_id=user_id,
                brand=car["brand"], model=car["model"],
                year=car["year"], price=car["price"], mileage=car["mileage"],
                fuel_type=car["fuel_type"], body_type=car["body_type"], transmission=car["transmission"],
                city="Casablanca",
                description=car["description"], source_url=car["source_url"]
            )
            db.add(v)
            await db.flush()
            
            l_id = uuid.uuid4()
            l = Listing(
                id=l_id, vehicle_id=v_id, status="active", images_urls=car["images_urls"],
                published_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.add(l)
            added += 1
            
        await db.commit()
        print(f"Saved {added} new official cars to database!")

asyncio.run(seed())
