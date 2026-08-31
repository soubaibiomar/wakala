import urllib.request
import re
import json
import time
import sys
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text

sys.stdout.reconfigure(encoding='utf-8')

DB_URL = "postgresql://wakala_user:wakala_secret_password@localhost:5433/wakala"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
}

BRAND_SLUG_MAP = {
    'mercedes-benz': 'mercedes-benz',
    'land-rover': 'land-rover',
    'alfa-romeo': 'alfa-romeo',
    'lynk-&-co': 'lynk-co',
    'omoda-&-jaecoo': 'omoda',
    'rox-motor': 'rox',
    'gac-motor': 'gac',
    'ds-automobiles': 'ds',
    'citroën': 'citroen',
    'bmw': 'bmw',
    'byd': 'byd',
    'mg': 'mg',
    'chery': 'chery',
    'geely': 'geely',
    'changan': 'changan',
    'haval': 'haval',
    'gwm': 'gwm',
    'zeekr': 'zeekr',
    'leapmotor': 'leapmotor',
    'jetour': 'jetour',
    'deepal': 'deepal',
}

def clean_brand_slug(brand_name):
    slug = brand_name.lower().strip()
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug.replace('ë', 'e').replace('é', 'e').replace('&', 'and')
    return BRAND_SLUG_MAP.get(slug, slug)

def scrape_moteur_models(brand_slug):
    """Scrapes clean side-profile model images from moteur.ma."""
    results = {}
    url = f"https://www.moteur.ma/fr/neuf/voiture/{brand_slug}/"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                if '/storage/media/images/models/' in src:
                    model_name = alt.replace(' image', '').replace('Image', '').strip()
                    if model_name and src.startswith('http'):
                        results[model_name.lower()] = src
                        
            for a in soup.find_all('a', href=re.compile(rf'/neuf/voiture/{brand_slug}/[a-z0-9\-]+/')):
                img = a.find('img')
                if img and img.get('src', '').startswith('http') and '/storage/media/images/models/' in img.get('src'):
                    m_title = a.get_text(strip=True)
                    if m_title:
                        results[m_title.lower()] = img.get('src')
    except Exception:
        pass
    return results

def scrape_wandaloo_models(brand_slug):
    """Scrapes models from wandaloo.com as secondary source."""
    results = {}
    url = f"https://www.wandaloo.com/neuf/{brand_slug}/"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            for a in soup.find_all('a', href=re.compile(rf'/neuf/{brand_slug}/')):
                img = a.find('img')
                if img and img.get('src') and ('files/' in img.get('src') or 'Voiture-Neuve/' in img.get('src')):
                    title = a.get_text(strip=True)
                    if title and img.get('src').startswith('http'):
                        results[title.lower()] = img.get('src')
    except Exception:
        pass
    return results

def main():
    engine = create_engine(DB_URL)
    print("=== Démarrage du Scraping des Images Réelles de Modèles Neufs ===")
    
    with engine.connect() as conn:
        brands = conn.execute(text("SELECT id, name, slug FROM car_brands ORDER BY name ASC")).fetchall()
        print(f"Trouvé {len(brands)} marques dans la base.")
        
        total_scraped = 0
        all_model_images = {}
        
        for b_id, b_name, b_slug in brands:
            lookup_slug = clean_brand_slug(b_slug or b_name)
            m_imgs = scrape_moteur_models(lookup_slug)
            w_imgs = scrape_wandaloo_models(lookup_slug)
            combined = {**w_imgs, **m_imgs}
            
            if combined:
                print(f"[{b_name}] -> {len(combined)} images trouvées")
                all_model_images[b_name.lower()] = combined
                total_scraped += len(combined)
            
            models = conn.execute(text("SELECT id, name, slug, hero_image_url FROM car_models WHERE brand_id = :bid"), {"bid": b_id}).fetchall()
            for m_id, m_name, m_slug, curr_img in models:
                matched_img = None
                m_clean = m_name.lower()
                
                for scraped_name, img_url in combined.items():
                    sc_clean = scraped_name.lower()
                    if m_clean in sc_clean or sc_clean in m_clean or m_slug.replace('-', '') in sc_clean.replace('-', ''):
                        matched_img = img_url
                        break
                
                if matched_img:
                    with engine.begin() as update_conn:
                        update_conn.execute(text("UPDATE car_models SET hero_image_url = :img WHERE id = :mid"), {"img": matched_img, "mid": m_id})
                        update_conn.execute(text("UPDATE car_trims SET image_url = :img WHERE model_id = :mid"), {"img": matched_img, "mid": m_id})

            time.sleep(0.15)
            
    # Save cache JSON
    with open('data_pipeline/scripts/scraped_moteur_images.json', 'w', encoding='utf-8') as f:
        json.dump(all_model_images, f, ensure_ascii=False, indent=2)
        
    print(f"\n✅ Scraping terminé avec succès ! Total images de modèles associées : {total_scraped}")

if __name__ == '__main__':
    main()
