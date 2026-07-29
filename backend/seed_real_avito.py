import sys
import os
import asyncio
import uuid
import random
import re
import json
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
    
    MAX_PAGES = 50
    urls = []
    
    for page in range(1, MAX_PAGES + 1):
        print(f"Fetching page {page}...")
        search_url = f"https://www.avito.ma/fr/maroc/voitures_d_occasion?o={page}"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
            soup = BeautifulSoup(html, 'html.parser')
            links = [a['href'] for a in soup.select('a') if 'href' in a.attrs and '/vi/' in a['href'] or '/voitures_d_occasion/' in a['href']]
            for href in links:
                if not href.startswith("http"):
                    href = "https://www.avito.ma" + href
                if "voitures_d_occasion" in href and ".htm" in href:
                    urls.append(href)
        except Exception as e:
            print(f"Failed to fetch search page {page}: {e}")
            
    urls = list(set(urls))
    print(f"Found {len(urls)} unique listing URLs to scrape across {MAX_PAGES} pages.")
    
    for i, url in enumerate(urls):
        print(f"Scraping {i+1}/20: {url}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            detail_html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
        except Exception as e:
            print(f"Failed to fetch detail page {url}: {e}")
            continue
            
        detail_soup = BeautifulSoup(detail_html, 'html.parser')
        
        next_data = detail_soup.find("script", id="__NEXT_DATA__")
        if not next_data:
            print("No __NEXT_DATA__ found")
            continue
            
        try:
            data = json.loads(next_data.text)
            ad = (
                data.get("props", {})
                .get("pageProps", {})
                .get("initialReduxState", {})
                .get("ad", {})
                .get("view", {})
                .get("adInfo", {})
            )

            if not ad:
                print("No adInfo found")
                continue

            title = ad.get("subject", "")
            price = ad.get("price", {}).get("value", 0)
            
            params = {p.get("name"): p.get("value") for p in ad.get("params", [])}
            brand = params.get("Marque", "")
            model = params.get("Modèle", "")
            year = params.get("Année-Modèle", "")
            mileage = params.get("Kilométrage", "100000")
            fuel = params.get("Type de carburant", "diesel")
            trans = params.get("Boite de vitesses", "manuelle")
            
            if not brand and title:
                parts = title.split()
                brand = parts[0] if parts else "Inconnu"
                model = " ".join(parts[1:]) if len(parts) > 1 else title
            
            images = []
            for img in ad.get("images", []):
                images.append(img.get("url"))
            
            # Fetch description safely
            desc = ad.get("description", "")
            if isinstance(desc, list):
                desc = "\n".join(desc)
                
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
                "source": "Avito",
                "source_url": url,
                "is_new": False
            })
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            pass
        
    if not cars:
        print("No cars extracted from Avito!")
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
                    description=car["description"][:1000] if car["description"] else "Véhicule sur Avito", source_url=car["source_url"],
                    condition_score=80 + (int(v_id) % 17), city="Marrakech",
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
                db.add(l)
                added_count += 1
            
            await db.commit()
            print(f"Scraping completed. Added {added_count} new vehicles to the database.")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed())
