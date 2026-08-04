import sys
import os
import asyncio
import uuid
import random
import re
import httpx
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

async def fetch_html(client: httpx.AsyncClient, url: str) -> str:
    try:
        response = await client.get(url, timeout=15.0)
        return response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return ""

async def seed():
    print("Cleaning up old moteur.ma vehicles to fix mileage bug...")
    async with async_session_factory() as db:
        from sqlalchemy import text
        await db.execute(text("DELETE FROM listings WHERE vehicle_id IN (SELECT id FROM vehicles WHERE source_url LIKE '%moteur.ma%')"))
        await db.execute(text("DELETE FROM vehicles WHERE source_url LIKE '%moteur.ma%'"))
        await db.commit()
    print("Cleanup complete. Starting import...")
    
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
            html = await fetch_html(client, f"https://www.moteur.ma/fr/voiture/achat-voiture-occasion/recherche/?page={page}")
            if not html:
                print(f"Empty HTML returned for page {page}.")
                break
                
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.select("div.item-card9-imgs a.link, div.picture a")
            
            new_urls_count = 0
            for link in links:
                href = link.get('href')
                if href:
                    if not href.startswith("http"):
                        href = "https://www.moteur.ma" + href
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
                
                title_el = detail_soup.select_one("h1, h3.title, h3")
                title = title_el.get_text(strip=True).replace("\n", " ") if title_el else ""
                if not title:
                    return None
                
                price_el = detail_soup.select_one(".ad-hero-price-col") or detail_soup.select_one("div.price") or detail_soup.select_one(".price")
                price = price_el.get_text(strip=True).replace("\n", "") if price_el else ""
                
                desc_el = detail_soup.select_one("div.desc") or detail_soup.select_one(".text-content")
                desc = desc_el.get_text(strip=True) if desc_el else ""
                # Prevent taking the Neuf banner as description
                if "À partir de" in desc:
                    desc = ""
                
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
                        key = cols[0].get_text(strip=True).replace(':', '').lower()
                        val = cols[1].get_text(strip=True)
                        specs[key] = val
                    elif len(cols) == 4:
                        key1 = cols[0].get_text(strip=True).replace(':', '').lower()
                        val1 = cols[1].get_text(strip=True)
                        specs[key1] = val1
                        
                        key2 = cols[2].get_text(strip=True).replace(':', '').lower()
                        val2 = cols[3].get_text(strip=True)
                        specs[key2] = val2
                        
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
                    "source": "Moteur",
                    "source_url": url,
                    "is_new": False
                }
                
        print(f"Processing detail pages...")
        tasks = [process_url(u) for u in urls]
        processed_cars = await asyncio.gather(*tasks)
        cars = [c for c in processed_cars if c is not None]
        
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
