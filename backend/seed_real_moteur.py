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
        search_url = f"https://www.moteur.ma/fr/voiture/achat-voiture-occasion/recherche/?page={page}"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.select("div.item-card9-imgs a.link, div.picture a")
            for link in links:
                href = link.get('href')
                if href:
                    if not href.startswith("http"):
                        href = "https://www.moteur.ma" + href
                    urls.append(href)
        except Exception as e:
            print(f"Failed to fetch search page {page}: {e}")
            
    urls = list(set(urls))
    print(f"Found {len(urls)} unique listing URLs to scrape across {MAX_PAGES} pages.")
    
    for i, url in enumerate(urls): # Scrape all found listings
        print(f"Scraping {i+1}/20: {url}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            detail_html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
        except Exception as e:
            print(f"Failed to fetch detail page {url}: {e}")
            continue
            
        detail_soup = BeautifulSoup(detail_html, 'html.parser')
        
        # New parsing logic we fixed earlier
        title_el = detail_soup.select_one("h1, h3.title, h3")
        title = title_el.get_text(strip=True).replace("\n", " ") if title_el else ""
        
        price_el = detail_soup.select_one("div.price") or detail_soup.select_one(".price")
        price = price_el.get_text(strip=True).replace("\n", "") if price_el else ""
        
        desc_el = detail_soup.select_one("div.desc") or detail_soup.select_one(".text-content")
        desc = desc_el.get_text(strip=True) if desc_el else ""
        
        images = []
        for img in detail_soup.select("div.slider img, .picture img, .carousel-item img, .ad-gallery-slide img, .slide-show-image img"):
            src = img.get("src") or img.get("data-src")
            if src:
                if not src.startswith("http"): src = "https://www.moteur.ma" + src
                images.append(src)
                
        # Parse table specs
        specs = {}
        for row in detail_soup.find_all('tr'):
            cols = row.find_all(['th', 'td'])
            if len(cols) == 2:
                key = cols[0].get_text(strip=True).lower()
                val = cols[1].get_text(strip=True)
                specs[key] = val
                
        # Get brand and model from title first, or specs
        brand = specs.get("marque", "Inconnu")
        model = specs.get("modèle", "Inconnu")
        if brand == "Inconnu" and title:
            parts = title.split()
            brand = parts[0] if parts else "Inconnu"
            model = " ".join(parts[1:]) if len(parts) > 1 else title
            
        year = specs.get("année", "2015")
        mileage = specs.get("kilométrage", "100000")
        fuel = specs.get("carburant", "diesel")
        trans = specs.get("boite de vitesses", "manuelle")
        
        cars.append({
            "brand": brand,
            "model": model,
            "year": parse_int(year) or 2015,
            "price": float(parse_int(price) or random.randint(50000, 300000)),
            "mileage": parse_int(mileage) or 100000,
            "fuel_type": "essence" if "essence" in fuel.lower() else ("hybride" if "hybride" in fuel.lower() else "diesel"),
            "body_type": "suv" if "suv" in title.lower() else "berline",
            "transmission": "automatique" if "auto" in trans.lower() else "manuelle",
            "description": desc,
            "images_urls": images,
            "source": "Moteur",
            "source_url": url,
            "is_new": False
        })
        
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
                    condition_score=80 + (int(v_id) % 17), city="Casablanca",
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
