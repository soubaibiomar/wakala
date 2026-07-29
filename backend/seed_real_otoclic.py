import sys
import os
import asyncio
import uuid
import random
import re
import urllib.request
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import async_session_factory
from sqlalchemy.future import select
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing

def parse_int(val):
    if not val: return None
    digits = re.sub(r'[^\d]', '', str(val))
    return int(digits) if digits else None

async def seed():
    cars = []
    
    MAX_PAGES = 50
    urls = []
    
    for page in range(1, MAX_PAGES + 1):
        print(f"Fetching page {page}...")
        search_url = f"https://www.otoclic.com/voitures-occasion-maroc/?page={page}"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.select("a.vehicle-card-link, div.listing-item a, a.card-car")
            for link in links:
                href = link.get('href')
                if href:
                    if not href.startswith("http"):
                        href = "https://www.otoclic.com" + href
                    urls.append(href)
        except Exception as e:
            print(f"Failed to fetch search page {page}: {e}")
            
    urls = list(set(urls))
    print(f"Found {len(urls)} unique listing URLs to scrape across {MAX_PAGES} pages.")
    
    for i, url in enumerate(urls):
        print(f"Scraping {i+1}/{len(urls)}: {url}")
        
        # Parse URL for data: peugeot-508-2-0-hdi...
        parts = url.split('/cars/')[-1].replace('/', '').split('-')
        
        brand = "Inconnu"
        model = "Inconnu"
        fuel = "diesel"
        trans = "manuelle"
        
        if len(parts) >= 2:
            brand = parts[0].capitalize()
            model = parts[1].capitalize()
            for part in parts:
                if part.lower() in ["hdi", "dci", "tdi", "diesel"]: fuel = "diesel"
                if part.lower() in ["essence", "1-0", "1-2", "1-4"]: fuel = "essence"
                if part.lower() in ["eat8", "auto", "dsg", "dct"]: trans = "automatique"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            detail_html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
        except Exception as e:
            print(f"Failed to fetch detail page {url}: {e}")
            continue
            
        detail_soup = BeautifulSoup(detail_html, 'html.parser')
        
        price_el = detail_soup.select_one(".price, h3")
        price = ""
        if price_el:
            price_text = price_el.get_text(strip=True).replace("\n", "")
            # Extract first number block (before "A partir de" if present)
            match = re.search(r'([\d\s\.]{3,})', price_text)
            if match:
                price = match.group(1)
            
        images = []
        for img in detail_soup.select("img"):
            src = img.get("src") or img.get("data-src")
            if src and "logo" not in src.lower() and "recaptcha" not in src.lower() and ("wp-content/uploads" in src or "img" in src):
                if not src.startswith("http"): src = "https://www.otoclic.com" + src
                images.append(src)
                
        cars.append({
            "brand": brand,
            "model": model,
            "year": random.randint(2015, 2024),
            "price": float(parse_int(price) or random.randint(50000, 300000)),
            "mileage": random.randint(30000, 150000), 
            "fuel_type": fuel,
            "body_type": "suv" if "suv" in model.lower() else "berline",
            "transmission": trans,
            "description": f"Véhicule d'occasion disponible sur Otoclic. {brand} {model}.",
            "images_urls": images,
            "source": "Otoclic",
            "source_url": url,
            "city": "Casablanca"
        })
        
    if not cars:
        print("No cars extracted from Otoclic!")
        return

    try:
        async with async_session_factory() as db:
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
                await db.flush()
            else:
                user_id = row.id

            added_count = 0
            for car in cars:
                # Vérifier si le véhicule existe déjà (basé sur l'URL source)
                existing = await db.execute(select(Vehicle).where(Vehicle.source_url == car["source_url"]))
                if existing.scalars().first():
                    continue  # Déjà en base, on skip
                    
                v_id = uuid.uuid4()
                v = Vehicle(
                    id=v_id, seller_id=user_id, 
                    brand=car["brand"][:50], 
                    model=car["model"][:100],
                    year=car["year"], price=car["price"], mileage=car["mileage"],
                    fuel_type=car["fuel_type"], body_type=car["body_type"], transmission=car["transmission"],
                    description=car["description"], source_url=car["source_url"],
                    condition_score=85,
                    city=car["city"][:50],
                    created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
                )
                db.add(v)
                
                imgs = car["images_urls"] or ["https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=600"]
                l = Listing(
                    id=uuid.uuid4(), vehicle_id=v_id, status="active", images_urls=imgs,
                    published_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(l)
                
                added_count += 1
            
            await db.commit()
            print(f"Scraping completed. Added {added_count} new vehicles to the database.")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed())
