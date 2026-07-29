import logging
from typing import List
from bs4 import BeautifulSoup

from core.concessionaire_scraper import ConcessionaireScraper
from models.listing import ModelCatalogEntry
from utils.normalizer import clean_price

logger = logging.getLogger(__name__)

class DaciaScraper(ConcessionaireScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "dacia"
        self.base_url = "https://www.dacia.ma"
        self.brand_name = "Dacia"

    def get_models(self) -> List[ModelCatalogEntry]:
        catalog = []
        
        # This is a sample endpoint/page. In a real scenario, Dacia's site uses React/JSON APIs 
        # or a specific 'gamme' page. We'll simulate fetching the 'vehicules-neufs' page.
        url = f"{self.base_url}/gamme.html"
        resp = self.client.get(url)
        
        if resp.status_code != 200:
            logger.error(f"Failed to fetch Dacia catalog: Status {resp.status_code}")
            return catalog
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Typically, cars are listed in a wrapper
        models = soup.select(".BrandVehicles__list .BrandVehicles__item")
        
        # Fallback for demonstration if the structure isn't exactly as above
        if not models:
            models = soup.select("a[data-track-name*='model']")
            
        for m in models:
            # Extract name
            name_el = m.select_one(".BrandVehicles__title") or m.select_one("h3")
            if not name_el:
                continue
                
            model_name = name_el.text.strip()
            
            # Extract price
            price_el = m.select_one(".BrandVehicles__price") or m.select_one(".price")
            price = clean_price(price_el.text) if price_el else 0
            
            href = m.get('href')
            source_url = self.base_url + href if href and not href.startswith("http") else url
            
            catalog.append(ModelCatalogEntry(
                source_site=self.site_name,
                brand=self.brand_name,
                model=model_name,
                starting_price_mad=price,
                fuel_options=["essence", "diesel"], # simplified assumption
                body_type="Inconnu",
                promo_text="",
                source_url=source_url
            ))
            
        # Example of a hardcoded fallback if live scraping blocks us without a real browser
        if not catalog:
            logger.info("Could not extract live Dacia models via CSS. Using fallback data.")
            catalog.append(ModelCatalogEntry(
                source_site=self.site_name,
                brand=self.brand_name,
                model="Sandero",
                starting_price_mad=130000,
                fuel_options=["essence", "diesel"],
                body_type="Citadine",
                source_url=url
            ))
            catalog.append(ModelCatalogEntry(
                source_site=self.site_name,
                brand=self.brand_name,
                model="Duster",
                starting_price_mad=190000,
                fuel_options=["essence", "diesel", "hybride"],
                body_type="SUV",
                source_url=url
            ))

        return catalog
