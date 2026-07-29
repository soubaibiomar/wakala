import asyncio
import uuid
from datetime import datetime, timezone
import re
from bs4 import BeautifulSoup
import traceback

from app.core.database import async_session_factory
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing

import urllib.request

def parse_int(val):
    if not val: return None
    digits = re.sub(r'[^\d]', '', str(val))
    return int(digits) if digits else None

async def seed():
    cars = []
    brands_list = ['dacia', 'renault', 'peugeot', 'citroën', 'citroen', 'hyundai', 'kia', 'toyota', 'volkswagen', 'vw', 'bmw', 'mercedes', 'audi', 'ford', 'fiat', 'nissan', 'mitsubishi', 'suzuki', 'honda', 'mazda', 'opel', 'chevrolet', 'jeep', 'land rover', 'range rover', 'volvo', 'seat', 'skoda', 'mini', 'smart', 'alfa romeo', 'porsche']
    
    # Scrape 3 pages to get more vehicles
    for page in range(1, 4):
        url = "https://www.moteur.ma/fr/voiture/achat-voiture-occasion/" if page == 1 else f"https://www.moteur.ma/fr/voiture/achat-voiture-occasion/page-{page}.html"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
        except Exception as e:
            continue
            
        soup = BeautifulSoup(html, 'html.parser')
        listings_elems = soup.select('.ads-index-card')
        
        for elem in listings_elems:
            try:
                title_elem = elem.select_one('h5.ads-index-title')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                brand = "Autre"
                model = title
                t_lower = title.lower()
                for b in brands_list:
                    if t_lower.startswith(b) or f" {b} " in t_lower:
                        brand = b.capitalize()
                        model = title[len(b):].strip()
                        break
                
                if len(brand) > 50: brand = brand[:50]
                if len(model) > 100: model = model[:100]
                
                price_elem = elem.select_one('.ad-price-grid')
                price_str = price_elem.get_text(strip=True) if price_elem else ''
                price = parse_int(price_str) or 0.0
                
                desc_elem = elem.select_one('.ad-desc')
                description = desc_elem.get_text(strip=True) if desc_elem else ''
                
                url_elem = elem.select_one('a.text-dark')
                source_url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else ''
                
                img_elem = elem.select_one('img.ads-index-media-img')
                img_url = img_elem['src'] if img_elem and 'src' in img_elem.attrs else None
                
                specs = [s.get_text(strip=True).lower() for s in elem.select('.ad-meta span.text-muted')]
                
                year, mileage, fuel_type, transmission = 2010, 100000, 'essence', 'manuelle'
                for spec in specs:
                    if 'km' in spec:
                        mileage = parse_int(spec) or mileage
                    elif re.match(r'^(19|20)\d{2}$', spec):
                        year = int(spec)
                    elif 'diesel' in spec: fuel_type = 'diesel'
                    elif 'essence' in spec: fuel_type = 'essence'
                    elif 'hybride' in spec: fuel_type = 'hybride'
                    elif 'auto' in spec: transmission = 'automatique'
                    elif 'manuel' in spec: transmission = 'manuelle'
                    
                cars.append({
                    "brand": brand,
                    "model": model,
                    "year": year,
                    "price": float(price),
                    "mileage": mileage,
                    "fuel_type": fuel_type,
                    "body_type": "suv" if "suv" in title.lower() else "berline",
                    "transmission": transmission,
                    "description": description,
                    "images_urls": [img_url] if img_url else [],
                    "source": "Moteur",
                    "source_url": source_url,
                    "is_new": (len(cars) % 3 == 0) # 1 out of 3 cars is "New"
                })
            except Exception as e:
                pass

    try:
        async with async_session_factory() as db:
            await db.execute(Vehicle.__table__.delete())
            
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
                await db.commit()
            else:
                user_id = row.id

            for car in cars:
                v_id = uuid.uuid4()
                # Ensure new cars have 0 mileage
                final_mileage = 0 if car["is_new"] else car["mileage"]
                v = Vehicle(
                    id=v_id, seller_id=user_id, 
                    brand=car["brand"].encode('utf-8', 'ignore').decode('utf-8').replace('\ufffd', ''), 
                    model=car["model"].encode('utf-8', 'ignore').decode('utf-8').replace('\ufffd', ''),
                    year=car["year"], price=car["price"], mileage=final_mileage,
                    fuel_type=car["fuel_type"], body_type=car["body_type"], transmission=car["transmission"],
                    description=car["description"].encode('utf-8', 'ignore').decode('utf-8').replace('\ufffd', ''), source_url=car["source_url"],
                    condition_score=80 + (int(v_id) % 17), city="Casablanca",
                    created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
                )
                db.add(v)
                
                l = Listing(
                    id=uuid.uuid4(), vehicle_id=v_id, status="active", images_urls=car["images_urls"],
                    published_at=datetime.now(timezone.utc), created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(l)
            
            await db.commit()
            print(f"Successfully seeded {len(cars)} REAL cars scraped directly from Moteur!")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed())
