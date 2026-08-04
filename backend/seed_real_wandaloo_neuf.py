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
    "dacia", "renault", "peugeot", "hyundai", "volkswagen",
    "fiat", "kia", "ford", "citroen", "opel", 
    "toyota", "nissan", "audi", "bmw", "mercedes-benz", 
    "jeep", "skoda", "seat", "cupra", "alfa-romeo", 
    "suzuki", "honda", "mazda", "mitsubishi", "land-rover",
    "volvo", "porsche", "lexus", "jaguar", "ds", 
    "mini", "chery", "mg", "geely", "haval", "byd",
    "omoda", "jaecoo", "xpeng", "dongfeng", "gac", "jac", 
    "foton", "tata", "abarth", "smart", "ssangyong"
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
                
            print(f"  Fetching model versions for {brand.capitalize()} {model_name}...")
            # Fetch model page to get versions
            model_html = fetch_html(data['url'])
            if not model_html: continue
            m_soup = BeautifulSoup(model_html, 'html.parser')
            
            version_links = []
            for a in m_soup.select('a'):
                href = a.get('href', '')
                if 'fiche-technique' in href and '.html' in href and not any(v['href'] == href for v in version_links):
                    v_name = a.text.strip()
                    if not v_name:
                        v_name = a.get('title', '').replace('Fiche technique', '').replace('Fiche Technique', '').strip()
                    if not v_name:
                        v_name = href.split('/')[-1].replace('.html', '').replace('-', ' ')
                    version_links.append({'href': href, 'name': v_name})
                    
            if not version_links:
                continue

            for v_data in version_links:
                v_link = v_data['href']
                v_name = v_data['name']
                v_html = fetch_html(v_link)
                if not v_html: continue
                v_soup = BeautifulSoup(v_html, 'html.parser')
                
                # Extract specs
                price_el = v_soup.select_one('.price, [class*=prix]')
                price_str = price_el.get_text() if price_el else ""
                digits = re.sub(r'[^\d]', '', price_str)
                price = int(digits) if digits else 200000

                fuel = "diesel"
                engine_hp = None
                transmission = "manuelle"
                conso = None
                vmax = None
                
                # parse ul/li or td
                specs_markdown = ""
                description = ""
                
                for cell in v_soup.select('.cell'):
                    category = cell.select_one('.head')
                    if category:
                        cat_name = category.get_text(strip=True)
                        cat_name = re.sub(r'Afficher[\+\-]?', '', cat_name).strip()
                        cat_name = re.sub(r'\(\d+\)$', '', cat_name).strip()
                        
                        if cat_name == 'En détail...':
                            details = cell.select_one('.params2')
                            if details:
                                for hidden in details.select('.Hchouma'):
                                    hidden.extract()
                                description = details.get_text('\n', strip=True) + '\n'
                        else:
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
                                    
                                    # Extract key basic specs for DB columns
                                    p_lower = param.get_text(strip=True).lower()
                                    v_lower = val_text.lower()
                                    
                                    if 'energie' in p_lower:
                                        if 'essence' in v_lower: fuel = 'essence'
                                        elif 'diesel' in v_lower: fuel = 'diesel'
                                        elif 'hybride' in v_lower: fuel = 'hybride'
                                        elif 'electrique' in v_lower: fuel = 'electrique'
                                    
                                    if 'boîte' in p_lower or 'transmission' in p_lower:
                                        if 'auto' in v_lower: transmission = 'automatique'
                                        elif 'manuel' in v_lower: transmission = 'manuelle'
                                        
                                    if 'puissance' in p_lower and 'dynamique' in p_lower:
                                        match = re.search(r'(\d+)', v_lower)
                                        if match: engine_hp = int(match.group(1))

                full_desc = f"Véhicule Neuf Officiel : {brand.capitalize()} {model_name} {v_name}.\n\n{description}\n## Fiche Technique Détaillée\n{specs_markdown}"

                final_model_name = v_name if (len(v_name) > 3 and model_name.lower() in v_name.lower()) else f"{model_name} {v_name}"

                cars.append({
                    "brand": brand.capitalize(),
                    "model": model_name,
                    "version": v_name,
                    "year": 2024,
                    "price": price,
                    "mileage": 0,
                    "fuel_type": fuel,
                    "body_type": "suv" if "suv" in data['text'].lower() else "berline",
                    "transmission": transmission,
                    "engine_power_hp": engine_hp,
                    "description": full_desc,
                    "images_urls": [data['img']],
                    "source_url": v_link,
                    "is_new": True
                })
                print(f"Added {brand.capitalize()} {final_model_name} ({price} MAD)")

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
                brand=car["brand"], model=car["model"], version=car.get("version"),
                year=car["year"], price=car["price"], mileage=car["mileage"],
                fuel_type=car["fuel_type"], body_type=car["body_type"], transmission=car["transmission"],
                city="Casablanca",
                engine_power_hp=car.get("engine_power_hp"),
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
