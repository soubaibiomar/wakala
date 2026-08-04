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
            html = await fetch_html(client, f"https://www.wandaloo.com/occasion/?page={page}")
            if not html:
                print(f"Empty HTML returned for page {page}.")
                break
                
            soup = BeautifulSoup(html, 'html.parser')
            links = [a['href'] for a in soup.select('a') if 'href' in a.attrs and '/occasion/' in a['href'] and '.html' in a['href']]
            
            new_urls_count = 0
            for href in links:
                if not href.startswith("http"):
                    href = "https://www.wandaloo.com" + href
                if href not in urls:
                    urls.append(href)
                    new_urls_count += 1
                    
            print(f"Scanned page {page}, found {new_urls_count} new URLs.")
            if new_urls_count == 0:
                print(f"DEBUG HTML start: {html[:200]}")
                has_more = False
                break
                
            page += 1
            await asyncio.sleep(0.5) # small delay to avoid rate limits
            
        print(f"Found {len(urls)} unique listing URLs to scrape across {page-1} pages.")
        
        # Concurrency limit for detail pages
        semaphore = asyncio.Semaphore(15)
        
        async def process_url(url):
            async with semaphore:
                detail_html = await fetch_html(client, url)
                if not detail_html:
                    return None
                    
                detail_soup = BeautifulSoup(detail_html, 'html.parser')
                
                title_el = detail_soup.select_one("h1")
                title = title_el.get_text(strip=True).replace("\n", " ") if title_el else ""
                if not title:
                    return None
            
                price_el = detail_soup.select_one(".price, .prix")
                price = price_el.get_text(strip=True).replace("\n", "") if price_el else ""
                
                images = []
                for img in detail_soup.select(".galleria-image img, #gallery img, .slider img, .car-img img"):
                    src = img.get("src") or img.get("data-src")
                    if src:
                        if not src.startswith("http"): src = "https://www.wandaloo.com" + src
                        images.append(src)
                        
                # Extract seller description
                seller_desc_el = detail_soup.select_one('p.information')
                seller_desc = seller_desc_el.get_text('\n', strip=True) + '\n\n' if seller_desc_el else ''

                # Parse table specs & advanced sections
                specs = {}
                specs_markdown = ""
                
                # 1. Fallback basic specs from icons
                for li in detail_soup.select('ul.icons.clearfix li'):
                    titre = li.select_one('.titre')
                    tag = li.select_one('.tag')
                    if titre and tag:
                        specs[titre.get_text(strip=True).lower()] = tag.get_text(strip=True)
                        
                # 2. Extract full tech sheet from .cell accordions
                for cell in detail_soup.select('.cell'):
                    category = cell.select_one('.head')
                    if category:
                        cat_name = category.get_text(strip=True)
                        import re
                        cat_name = re.sub(r'Afficher[\+\-]?', '', cat_name).strip()
                        cat_name = re.sub(r'\(\d+\)$', '', cat_name).strip()
                        
                        if cat_name and cat_name != 'En détail...':
                            specs_markdown += f'\n### {cat_name}\n\n'
                            specs_markdown += '| Caractéristique | Valeur |\n|---|---|\n'
                            for li in cell.select('li'):
                                param = li.select_one('.param')
                                value = li.select_one('.value')
                                if param and value:
                                    val_text = value.get_text(strip=True)
                                    if not val_text and value.select_one('img'):
                                        img_src = value.select_one('img').get('src', '')
                                        if 'oui' in img_src: val_text = 'Oui'
                                        elif 'non' in img_src: val_text = 'Non'
                                    specs_markdown += f'| **{param.get_text(strip=True)}** | {val_text} |\n'
                                    # basic specs extraction for fallback
                                    p_lower = param.get_text(strip=True).lower()
                                    v_lower = val_text.lower()
                                    if 'carburant' in p_lower or 'energie' in p_lower: specs['carburant'] = v_lower
                                    if 'boite' in p_lower or 'transmission' in p_lower: specs['boite de vitesses'] = v_lower
                        
                # Get brand and model from title first, or specs
                brand = specs.get("marque", "")
                model = specs.get("modèle", "")
                if not brand and title:
                    parts = title.split()
                    brand = parts[0] if parts else "Inconnu"
                    model = " ".join(parts[1:]) if len(parts) > 1 else title
                    
                year = specs.get("année", "2015")
                if "modèle" in specs and str(specs["modèle"]).isdigit(): year = specs["modèle"]  # Sometimes year is under model in icons
                
                mileage = specs.get("kilométrage", "100000")
                if not parse_int(mileage):
                    mileage = "100000"
                fuel = specs.get("carburant", "diesel")
                trans = specs.get("boite de vitesses", "manuelle")
                
                full_desc = f"{seller_desc}## Fiche Technique Détaillée\n{specs_markdown}" if specs_markdown else f"{seller_desc}Véhicule {brand} {model} trouvé sur Wandaloo."

                return {
                    "brand": brand,
                    "model": model,
                    "year": parse_int(year) or 2015,
                    "price": float(parse_int(price) or random.randint(50000, 300000)),
                    "mileage": parse_int(mileage) or 100000,
                    "fuel_type": "essence" if "essence" in fuel.lower() else ("hybride" if "hybride" in fuel.lower() else "diesel"),
                    "body_type": "suv" if "suv" in title.lower() else "berline",
                    "transmission": "automatique" if "auto" in trans.lower() else "manuelle",
                    "description": full_desc,
                    "images_urls": images,
                    "source": "Wandaloo",
                    "source_url": url,
                    "is_new": False
                }

        print(f"Processing detail pages...")
        tasks = [process_url(u) for u in urls]
        processed_cars = await asyncio.gather(*tasks)
        cars = [c for c in processed_cars if c is not None]
        
    if not cars:
        print("No cars extracted from Wandaloo!")
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
                    condition_score=80 + (int(v_id) % 17), city="Rabat",
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
