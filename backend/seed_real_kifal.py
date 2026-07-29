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
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing

def parse_int(val):
    if not val: return None
    digits = re.sub(r'[^\d]', '', str(val))
    return int(digits) if digits else None

async def seed():
    cars = []
    
    # Base search URL
    MAX_PAGES = 50
    urls = []
    
    for page in range(1, MAX_PAGES + 1):
        print(f"Fetching page {page}...")
        search_url = f"https://occasion.kifal.ma/annonces?page={page}"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
            soup = BeautifulSoup(html, 'html.parser')
            links = [a['href'] for a in soup.select('a') if 'href' in a.attrs and '/annonce/' in a['href'] and '.htm' in a['href']]
            for href in links:
                if not href.startswith("http"):
                    href = "https://occasion.kifal.ma" + href
                urls.append(href)
        except Exception as e:
            print(f"Failed to fetch search page {page}: {e}")
            
    urls = list(set(urls))
    print(f"Found {len(urls)} unique listing URLs to scrape across {MAX_PAGES} pages.")
    
    for i, url in enumerate(urls):
        print(f"Scraping {i+1}/20: {url}")
        
        # Parse URL for data: MARQUE_Modèle_Année_Carburant_Transmission_Ville_ID_REF.htm
        parts = url.split('/')[-1].replace('%20', ' ').replace('.htm', '').split('_')
        
        brand = "Inconnu"
        model = "Inconnu"
        year = "2015"
        fuel = "diesel"
        trans = "manuelle"
        city = "Casablanca"
        
        if len(parts) >= 6:
            brand = parts[0]
            model = parts[1]
            year = parts[2]
            fuel = parts[3]
            trans = parts[4]
            city = parts[5]
            
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            detail_html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
        except Exception as e:
            print(f"Failed to fetch detail page {url}: {e}")
            continue
            
        detail_soup = BeautifulSoup(detail_html, 'html.parser')
        
        price_el = detail_soup.select_one(".price, .annonce-price, h2, h3")
        price = ""
        if price_el:
            price = price_el.get_text(strip=True).replace("\n", "")
            
        images = []
        for img in detail_soup.select("img"):
            src = img.get("src") or img.get("data-src")
            if src:
                lower_src = src.lower()
                if (
                    "logo" not in lower_src 
                    and "recaptcha" not in lower_src
                    and "ma.svg" not in lower_src
                    and "brands" not in lower_src
                    and "users" not in lower_src
                    and "google.png" not in lower_src
                    and ".svg" not in lower_src
                ):
                    if not src.startswith("http"): src = "https://occasion.kifal.ma" + src
                    images.append(src)
                
        # Kifal has certified vehicles, meaning better score
        cars.append({
            "brand": brand,
            "model": model,
            "year": parse_int(year) or 2015,
            "price": float(parse_int(price) or random.randint(50000, 300000)),
            "mileage": random.randint(30000, 150000), # URL doesn't have it, set random
            "fuel_type": "essence" if "essence" in fuel.lower() else ("hybride" if "hybride" in fuel.lower() else "diesel"),
            "body_type": "suv" if "suv" in model.lower() else "berline",
            "transmission": "automatique" if "auto" in trans.lower() else "manuelle",
            "description": f"Véhicule certifié Kifal Auto. Modèle: {brand} {model}. Inspection: 200 points de contrôle.",
            "images_urls": images,
            "source": "Kifal",
            "source_url": url,
            "city": city.capitalize()
        })
        
    if not cars:
        print("No cars extracted from Kifal!")
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
                # Vérifier si le véhicule existe déjà
                from sqlalchemy.future import select
                existing = await db.execute(select(Vehicle).where(Vehicle.source_url == car["source_url"]))
                if existing.scalars().first():
                    continue
                    
                v_id = uuid.uuid4()
                v = Vehicle(
                    id=v_id, seller_id=user_id, 
                    brand=car["brand"][:50], 
                    model=car["model"][:100],
                    year=car["year"], price=car["price"], mileage=car["mileage"],
                    fuel_type=car["fuel_type"], body_type=car["body_type"], transmission=car["transmission"],
                    description=car["description"], source_url=car["source_url"],
                    condition_score=95, # Certified vehicle = high score!
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
