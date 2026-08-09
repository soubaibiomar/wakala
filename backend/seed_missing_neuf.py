import sys
import asyncio
import uuid
from datetime import datetime, timezone
import urllib.request
import re
from bs4 import BeautifulSoup
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import async_session_factory
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from sqlalchemy.future import select

TARGET_BRANDS = [
    ("mercedes", "Mercedes-Benz"),
    ("maserati", "Maserati"),
    ("gwm", "Haval"),
    ("baic", "BAIC"),
    ("seres", "Seres"),
    ("changan", "Changan"),
    ("dfsk", "DFSK"),
    ("alfa-romeo", "Alfa Romeo"),
    ("land-rover", "Land Rover"),
    ("citroen", "Citroën"),
    ("bmw", "BMW"),
    ("audi", "Audi"),
    ("porsche", "Porsche"),
    ("zeekr", "Zeekr"),
    ("leapmotor", "Leapmotor"),
    ("exeed", "Exeed"),
]

def fetch_html(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        return urllib.request.urlopen(req, timeout=10).read().decode('utf-8', 'ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

async def run_seed():
    async with async_session_factory() as db:
        res = await db.execute(select(User).where(User.email == "scraped_live@wakala.ma"))
        user = res.scalars().first()
        if not user:
            user = User(
                id=uuid.uuid4(), email="scraped_live@wakala.ma", hashed_password="pw",
                full_name="Auto Scraper Live", phone="06000000", role="seller",
                is_verified=True, is_pro=True
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
        user_id = user.id
        print(f"Using Seller User ID: {user_id}")

        for slug, brand_display_name in TARGET_BRANDS:
            print(f"\n==========================================")
            print(f"Fetching brand: {brand_display_name} (slug: {slug})")
            print(f"==========================================")
            
            brand_url = f"https://www.wandaloo.com/neuf/{slug}/"
            html = fetch_html(brand_url)
            if not html:
                print(f"Could not load brand page {brand_url}")
                continue
                
            soup = BeautifulSoup(html, 'html.parser')
            
            models_data = {}
            for a in soup.select('a'):
                href = a.get('href', '')
                if f'/neuf/{slug}/' in href and href != brand_url and href != f'https://www.wandaloo.com/neuf/{slug}':
                    if not href.startswith('http'):
                        href = 'https://www.wandaloo.com' + href
                    
                    parts = [p for p in href.split('/') if p]
                    if len(parts) >= 2:
                        model_slug = parts[-1]
                        if model_slug == slug or '.html' in model_slug:
                            continue
                        model_name = model_slug.replace('-', ' ').title()
                        
                        if model_name not in models_data:
                            parent = a.find_parent('li') or a.find_parent('div')
                            img_src = None
                            v_text = ""
                            if parent:
                                img = parent.select_one('img')
                                if img:
                                    img_src = img.get('src') or img.get('data-src')
                                    if img_src and not img_src.startswith('http'):
                                        img_src = 'https://www.wandaloo.com' + img_src
                                v_text = parent.text.strip().replace('\n', ' ')
                            models_data[model_name] = {'url': href, 'img': img_src, 'text': v_text, 'slug': model_slug}

            print(f"Found {len(models_data)} models for {brand_display_name}: {list(models_data.keys())}")
            
            brand_cars = []
            for model_name, data in models_data.items():
                print(f"  --> Model: {brand_display_name} {model_name}...")
                model_html = fetch_html(data['url'])
                if not model_html:
                    continue
                m_soup = BeautifulSoup(model_html, 'html.parser')
                
                if not data['img']:
                    m_img = m_soup.select_one('.photo img, .main-photo img, .car-picture img')
                    if m_img:
                        src = m_img.get('src') or m_img.get('data-src')
                        if src and not src.startswith('http'):
                            src = 'https://www.wandaloo.com' + src
                        data['img'] = src
                
                version_links = []
                for a in m_soup.select('a'):
                    href = a.get('href', '')
                    if 'fiche-technique' in href and '.html' in href:
                        if not href.startswith('http'):
                            href = 'https://www.wandaloo.com' + href
                        if not any(v['href'] == href for v in version_links):
                            v_name = a.text.strip()
                            if not v_name:
                                v_name = a.get('title', '').replace('Fiche technique', '').replace('Fiche Technique', '').strip()
                            if not v_name:
                                v_name = href.split('/')[-1].replace('.html', '').replace('-', ' ')
                            version_links.append({'href': href, 'name': v_name})
                            
                if not version_links:
                    price_el = m_soup.select_one('.price, [class*=prix]')
                    price_str = price_el.get_text() if price_el else ""
                    digits = re.sub(r'[^\d]', '', price_str)
                    price = int(digits) if digits else 300000
                    
                    brand_cars.append({
                        "brand": brand_display_name,
                        "model": model_name,
                        "version": "Standard",
                        "year": 2024,
                        "price": price,
                        "mileage": 0,
                        "fuel_type": "diesel" if "diesel" in data['text'].lower() else "essence",
                        "body_type": "suv" if "suv" in (data['text'] + model_name).lower() else "berline",
                        "transmission": "automatique",
                        "engine_power_hp": 150,
                        "description": f"Véhicule Neuf Officiel : {brand_display_name} {model_name}.\n\nDécouvrez le nouveau {brand_display_name} {model_name} disponible au Maroc.",
                        "images_urls": [data['img']] if data['img'] else ["https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800&q=80"],
                        "source_url": data['url']
                    })
                    continue

                for v_data in version_links[:4]:  # save up to 4 key versions per model
                    v_link = v_data['href']
                    v_name = v_data['name']
                    v_html = fetch_html(v_link)
                    if not v_html:
                        continue
                    v_soup = BeautifulSoup(v_html, 'html.parser')
                    
                    v_img = data['img']
                    v_img_el = v_soup.select_one('.fiche-photo img, .photo img')
                    if v_img_el:
                        v_img_src = v_img_el.get('src') or v_img_el.get('data-src')
                        if v_img_src and not v_img_src.startswith('http'):
                            v_img_src = 'https://www.wandaloo.com' + v_img_src
                        if v_img_src:
                            v_img = v_img_src
                    
                    price_el = v_soup.select_one('.price, [class*=prix]')
                    price_str = price_el.get_text() if price_el else ""
                    digits = re.sub(r'[^\d]', '', price_str)
                    price = int(digits) if digits else 350000

                    fuel = "diesel"
                    engine_hp = None
                    transmission = "automatique"
                    body_type = "suv" if "suv" in (data['text'] + model_name).lower() else "berline"
                    
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
                                        
                                        p_lower = param.get_text(strip=True).lower()
                                        v_lower = val_text.lower()
                                        
                                        if 'energie' in p_lower or 'carburant' in p_lower:
                                            if 'essence' in v_lower: fuel = 'essence'
                                            elif 'diesel' in v_lower: fuel = 'diesel'
                                            elif 'hybride' in v_lower: fuel = 'hybride'
                                            elif 'electrique' in v_lower or 'électrique' in v_lower: fuel = 'electrique'
                                        
                                        if 'boîte' in p_lower or 'transmission' in p_lower:
                                            if 'auto' in v_lower: transmission = 'automatique'
                                            elif 'manuel' in v_lower: transmission = 'manuelle'
                                            
                                        if 'carrosserie' in p_lower:
                                            if 'suv' in v_lower or '4x4' in v_lower: body_type = 'suv'
                                            elif 'citadine' in v_lower: body_type = 'citadine'
                                            elif 'berline' in v_lower: body_type = 'berline'
                                            elif 'coupe' in v_lower or 'coupé' in v_lower: body_type = 'coupe'
                                            elif 'cabriolet' in v_lower: body_type = 'cabriolet'
                                            
                                        if 'puissance' in p_lower and 'dynamique' in p_lower:
                                            match = re.search(r'(\d+)', v_lower)
                                            if match: engine_hp = int(match.group(1))

                    full_desc = f"Véhicule Neuf Officiel : {brand_display_name} {model_name} {v_name}.\n\n{description}\n## Fiche Technique Détaillée\n{specs_markdown}"

                    brand_cars.append({
                        "brand": brand_display_name,
                        "model": model_name,
                        "version": v_name,
                        "year": 2024,
                        "price": price,
                        "mileage": 0,
                        "fuel_type": fuel,
                        "body_type": body_type,
                        "transmission": transmission,
                        "engine_power_hp": engine_hp or 150,
                        "description": full_desc,
                        "images_urls": [v_img] if v_img else ["https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800&q=80"],
                        "source_url": v_link
                    })

            # Save immediately for this brand
            brand_added = 0
            for car in brand_cars:
                existing = await db.execute(select(Vehicle).where(Vehicle.source_url == car["source_url"]))
                existing_v = existing.scalars().first()
                if existing_v:
                    existing_v.brand = car["brand"]
                    existing_v.model = car["model"]
                    existing_v.version = car["version"]
                    existing_v.price = car["price"]
                    existing_v.fuel_type = car["fuel_type"]
                    existing_v.body_type = car["body_type"]
                    existing_v.transmission = car["transmission"]
                    existing_v.description = car["description"]
                    continue
                    
                v_id = uuid.uuid4()
                v = Vehicle(
                    id=v_id, seller_id=user_id,
                    brand=car["brand"], model=car["model"], version=car.get("version"),
                    year=car["year"], price=car["price"], mileage=0,
                    fuel_type=car["fuel_type"], body_type=car["body_type"], transmission=car["transmission"],
                    city="Casablanca",
                    engine_power_hp=car.get("engine_power_hp"),
                    description=car["description"], source_url=car["source_url"]
                )
                db.add(v)
                
                l_id = uuid.uuid4()
                l = Listing(
                    id=l_id, vehicle_id=v_id, status="active", images_urls=car["images_urls"],
                    published_at=datetime.now(timezone.utc)
                )
                db.add(l)
                brand_added += 1
                
            await db.commit()
            print(f"  ==> Saved {brand_added} new cars for brand {brand_display_name}!")

if __name__ == "__main__":
    asyncio.run(run_seed())
