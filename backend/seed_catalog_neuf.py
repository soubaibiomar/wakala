import sys
import os
import asyncio
import uuid
import re
import urllib.request
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import async_session_factory
from app.models.catalog import BrandCatalog, ModelCatalog, TechSpecCatalog

def clean_text(text):
    return text.replace('\n', ' ').replace('\r', '').replace('\t', '').strip()

def parse_price(val):
    if not val: return None
    digits = re.sub(r'[^\d]', '', str(val))
    return float(digits) if digits else None

def parse_int(val):
    if not val: return None
    digits = re.sub(r'[^\d]', '', str(val))
    return int(digits) if digits else None

def parse_float(val):
    if not val: return None
    digits = re.sub(r'[^\d\.]', '', str(val).replace(',', '.'))
    try:
        return float(digits)
    except:
        return None

async def seed_catalog():
    # Only scraping a few prominent brands to keep it fast, but logic applies to all
    target_brands = [
        'dacia', 'renault', 'peugeot', 'hyundai', 'volkswagen',
        'fiat', 'kia', 'ford', 'citroen', 'opel', 
        'toyota', 'nissan', 'audi', 'bmw', 'mercedes-benz', 
        'jeep', 'skoda', 'seat', 'cupra', 'alfa-romeo', 
        'suzuki', 'honda', 'mazda', 'mitsubishi', 'land-rover',
        'volvo', 'porsche', 'lexus', 'jaguar', 'ds', 
        'mini', 'chery', 'mg', 'geely', 'haval', 'byd'
    ]
    
    brand_data_list = []

    for brand_slug in target_brands:
        print(f"Scraping Brand: {brand_slug.upper()}")
        url = f'https://www.wandaloo.com/neuf/{brand_slug}/'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urllib.request.urlopen(req).read().decode('utf-8', 'ignore')
        except Exception as e:
            print(f"Failed to fetch brand {brand_slug}: {e}")
            continue
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get brand logo
        logo_el = soup.select_one('.brand-logo img')
        logo_url = logo_el['src'] if logo_el and 'src' in logo_el.attrs else None
        if logo_url and not logo_url.startswith('http'):
            logo_url = 'https://www.wandaloo.com' + logo_url
            
        # Get models
        model_links = []
        for a in soup.select('a'):
            href = a.get('href', '')
            if f'/neuf/{brand_slug}/' in href and href.endswith('/') and len(href.split('/')) == 6: # e.g. /neuf/dacia/duster/
                if href not in model_links:
                    model_links.append(href)
                    
        print(f"  Found {len(model_links)} models for {brand_slug.upper()}")
        
        models_data = []
        
        for model_link in model_links:
            model_slug = model_link.strip('/').split('/')[-1]
            if model_slug == brand_slug: continue # avoid /neuf/dacia/ -> dacia
            
            print(f"    Scraping Model: {model_slug.upper()}")
            m_req = urllib.request.Request(model_link, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                m_html = urllib.request.urlopen(m_req).read().decode('utf-8', 'ignore')
            except Exception:
                continue
                
            m_soup = BeautifulSoup(m_html, 'html.parser')
            
            # Find version links
            version_links = []
            for a in m_soup.select('a'):
                href = a.get('href', '')
                if 'fiche-technique' in href and '.html' in href and href not in version_links:
                    version_links.append(href)
                    
            print(f"      Found {len(version_links)} versions for {model_slug.upper()}")
            
            specs_data = []
            for v_link in version_links:
                v_req = urllib.request.Request(v_link, headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    v_html = urllib.request.urlopen(v_req).read().decode('utf-8', 'ignore')
                except Exception:
                    continue
                v_soup = BeautifulSoup(v_html, 'html.parser')
                
                # Title
                title_el = v_soup.select_one('h1')
                v_title = clean_text(title_el.get_text()) if title_el else v_link.split('/')[-2].replace('-', ' ').upper()
                
                # Price
                price_el = v_soup.select_one('.price, [class*=prix]')
                price_str = price_el.get_text() if price_el else ""
                price = parse_price(price_str)
                
                # Extract simple specs from table rows or list items
                # We do a basic keyword matching to find Engine Power, Fuel, etc.
                fuel = None
                engine_hp = None
                transmission = None
                consumption = None
                
                for el in v_soup.select('li, td'):
                    text = clean_text(el.get_text()).lower()
                    if 'essence' in text: fuel = 'essence'
                    elif 'diesel' in text: fuel = 'diesel'
                    elif 'hybride' in text: fuel = 'hybride'
                    elif 'electrique' in text: fuel = 'electrique'
                    
                    if 'automatique' in text or 'auto' in text: transmission = 'automatique'
                    elif 'manuelle' in text or 'manuel' in text: transmission = 'manuelle'
                    
                    if ' ch ' in text or 'chevaux' in text:
                        match = re.search(r'(\d+)\s*(ch|chevaux)', text)
                        if match: engine_hp = int(match.group(1))
                        
                    if 'l/100' in text:
                        match = re.search(r'([\d\.\,]+)\s*l/100', text)
                        if match: consumption = parse_float(match.group(1))
                        
                specs_data.append({
                    "version_name": v_title[:200],
                    "price_new_mad": price,
                    "fuel_type": fuel,
                    "engine_power_hp": engine_hp,
                    "transmission": transmission,
                    "consumption_l_100": consumption
                })
                
            models_data.append({
                "name": model_slug.replace('-', ' ').upper()[:100],
                "specs": specs_data
            })
            
        brand_data_list.append({
            "name": brand_slug.upper()[:100],
            "logo_url": logo_url[:255] if logo_url else None,
            "models": models_data
        })
        
    print("\n--- Scraping complete, saving to database ---")
    
    try:
        async with async_session_factory() as db:
            for b_data in brand_data_list:
                # Insert or get Brand
                result = await db.execute(BrandCatalog.__table__.select().where(BrandCatalog.name == b_data["name"]))
                row = result.fetchone()
                if not row:
                    b_id = uuid.uuid4()
                    brand = BrandCatalog(
                        id=b_id, name=b_data["name"], logo_url=b_data["logo_url"],
                        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
                    )
                    db.add(brand)
                else:
                    b_id = row.id
                    
                for m_data in b_data["models"]:
                    # Insert or get Model
                    m_res = await db.execute(ModelCatalog.__table__.select().where(
                        (ModelCatalog.brand_id == b_id) & (ModelCatalog.name == m_data["name"])
                    ))
                    m_row = m_res.fetchone()
                    if not m_row:
                        m_id = uuid.uuid4()
                        model = ModelCatalog(
                            id=m_id, brand_id=b_id, name=m_data["name"],
                            created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
                        )
                        db.add(model)
                    else:
                        m_id = m_row.id
                        
                    for s_data in m_data["specs"]:
                        # Insert Tech Spec
                        s_res = await db.execute(TechSpecCatalog.__table__.select().where(
                            (TechSpecCatalog.model_id == m_id) & (TechSpecCatalog.version_name == s_data["version_name"])
                        ))
                        s_row = s_res.fetchone()
                        if not s_row:
                            spec = TechSpecCatalog(
                                id=uuid.uuid4(), model_id=m_id, version_name=s_data["version_name"],
                                price_new_mad=s_data["price_new_mad"], fuel_type=s_data["fuel_type"],
                                engine_power_hp=s_data["engine_power_hp"], transmission=s_data["transmission"],
                                consumption_l_100=s_data["consumption_l_100"],
                                created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)
                            )
                            db.add(spec)
                            
            await db.commit()
            print("Successfully saved catalog to database!")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed_catalog())
