import sys
import os
import asyncio
import uuid
import random
import re
import json
import httpx
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

async def fetch_html(client: httpx.AsyncClient, url: str) -> str:
    try:
        response = await client.get(url, timeout=15.0)
        return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

async def seed():
    cars = []
    
    page = 1
    has_more = True
    urls = []
    
    print("Fetching search pages dynamically...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    async with httpx.AsyncClient(headers=headers) as client:
        while has_more and page <= 100:
            html = await fetch_html(client, f"https://www.avito.ma/fr/maroc/voitures_d_occasion?o={page}")
            if not html:
                print(f"Empty HTML returned for page {page}.")
                break
                
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.select("a[href*='/vi/']")
            
            new_urls_count = 0
            for link in links:
                href = link.get('href')
                if href:
                    if href not in urls:
                        urls.append(href)
                        new_urls_count += 1
                        
            print(f"Scanned page {page}, found {new_urls_count} new URLs.")
            if new_urls_count == 0:
                print(f"DEBUG HTML start: {html[:200]}")
                has_more = False
                break
                
            page += 1
            await asyncio.sleep(0.5)

            
        print(f"Found {len(urls)} unique listing URLs to scrape across {page-1} pages.")
        
        semaphore = asyncio.Semaphore(15)
        
        async def process_url(url):
            async with semaphore:
                detail_html = await fetch_html(client, url)
                if not detail_html:
                    return None
                    
                detail_soup = BeautifulSoup(detail_html, 'html.parser')
                
                next_data = detail_soup.find("script", id="__NEXT_DATA__")
                if not next_data:
                    print("No __NEXT_DATA__ found")
                    return None
                    
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
                        return None

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
                        
                    return {
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
                    }
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
                    return None
                    
        print(f"Processing detail pages...")
        tasks = [process_url(u) for u in urls]
        processed_cars = await asyncio.gather(*tasks)
        cars = [c for c in processed_cars if c is not None]
        
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
                added_count += 1
            
            await db.commit()
            print(f"Scraping completed. Added {added_count} new vehicles to the database.")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed())
