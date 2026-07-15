from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import logging
import re

from bs4 import BeautifulSoup

from .base_scraper import BaseScraper
from . import config
from .selector_loader import SelectorLoader
from .extraction_fallback import FallbackExtractor

logger = logging.getLogger(__name__)


class AvitoScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            base_url="https://www.avito.ma/fr/maroc/voitures_d'occasion",
            source_name="avito"
        )
        self.selector_loader = SelectorLoader()

    def fetch_listings(self, max_items: int = config.MAX_LISTINGS_PER_RUN) -> List[Dict[str, Any]]:
        logger.info(f"Starting to fetch listings from {self.source_name} (max {max_items})")

        all_listings = []
        pages = self.build_pagination_urls(config.PAGES_PER_SOURCE)

        for page_url in pages:
            if len(all_listings) >= max_items:
                break

            html = self.fetch_page(page_url)
            if not html:
                logger.warning(f"Failed to fetch or prohibited by robots.txt: {page_url}")
                continue

            page_listings = self._parse_listings_page(html, max_items - len(all_listings))
            all_listings.extend(page_listings)

        logger.info(f"Fetched {len(all_listings)} listings from {self.source_name}")
        return all_listings[:max_items]

    def build_pagination_urls(self, max_pages: int) -> List[str]:
        """Avito uses ?o={page} for pagination (1-indexed)"""
        urls = [self.base_url]
        for page in range(2, max_pages + 1):
            urls.append(f"{self.base_url}?o={page}")
        return urls

    def _parse_listings_page(self, html: str, max_items: int) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'html.parser')
        listings = []

        # Avito uses Next.js with __NEXT_DATA__ JSON
        next_data_script = soup.find('script', id='__NEXT_DATA__')
        if next_data_script:
            try:
                data = json.loads(next_data_script.string)
                return self._parse_next_data(data, max_items)
            except Exception as e:
                logger.warning(f"Failed to parse __NEXT_DATA__, falling back to HTML parsing: {e}")

        # Fallback: HTML parsing (less reliable)
        selectors = self.selector_loader.load(self.source_name)
        card_sel = selectors.get("listing_card", "div[data-testid='ad-list-item']")
        listing_elements = soup.select(card_sel)
        for elem in listing_elements[:max_items]:
            try:
                listing = self._parse_listing_element(elem)
                if listing:
                    listings.append(listing)
            except Exception as e:
                logger.error(f"Error parsing Avito listing element: {e}")

        return listings

    def _parse_next_data(self, data: dict, max_items: int) -> List[Dict[str, Any]]:
        """Parse the Next.js __NEXT_DATA__ JSON structure"""
        listings = []
        try:
            page_props = data.get('props', {}).get('pageProps', {})
            
            # 1. Try componentProps
            cp = page_props.get('componentProps', {})
            ads = cp.get('ads', {}).get('ads', [])
            
            # 2. Try old structure
            if not ads:
                ads = page_props.get('ads', []) or page_props.get('initialAds', [])

            for ad in ads[:max_items]:
                title = ad.get('title', 'No title')
                listing = self._parse_ad_json(ad)
                brand = listing.get('brand', 'N/A') if listing else 'N/A'
                model = listing.get('model', '') or ''
                if listing:
                    listings.append(listing)

        except Exception as e:
            logger.error(f"Error parsing __NEXT_DATA__: {e}")

        return listings

    def _parse_ad_json(self, ad: dict) -> Optional[Dict[str, Any]]:
        """Parse a single ad from the JSON structure"""
        try:
            # Extract URL
            ad_url = ad.get('url') or ad.get('link') or ad.get('ad_url')
            if ad_url and not ad_url.startswith('http'):
                ad_url = f"https://www.avito.ma{ad_url}"

            # Extract price
            price = ad.get('price') or ad.get('price_value')
            if isinstance(price, dict):
                price = price.get('value') or price.get('formatted')

            # Extract location
            location = ad.get('location') or ad.get('city') or ad.get('region_name')

            # Extract title/brand/model
            title = ad.get('title') or ad.get('subject') or ''
            brand, model = self._extract_brand_model(title)

            # Extract details from attributes or params
            attrs = ad.get('attributes', [])
            
            if not attrs and 'params' in ad:
                params_dict = ad['params']
                attrs = params_dict.get('primary', []) + params_dict.get('secondary', [])
            
            year = None
            mileage = None
            fuel_type = None
            transmission = None
            body_type = None

            for attr in attrs:
                key = attr.get('key', '').lower()
                val = attr.get('value')
                label = attr.get('label', '').lower()
                if 'year' in key or 'regdate' in key or 'année' in label:
                    year = self._parse_int(val)
                elif 'mileage' in key or 'kilom' in label:
                    mileage = self._parse_int(val)
                elif 'fuel' in key or 'carburant' in label:
                    fuel_type = str(val).lower() if val else None
                elif 'transmission' in key or 'bv' in key or 'boîte' in label:
                    transmission = str(val).lower() if val else None
                elif 'body' in key or 'carrosserie' in label:
                    body_type = str(val).lower() if val else None

            raw_data = {
                "source": self.source_name,
                "source_url": ad_url,
                "price": str(price) if price else None,
                "brand": brand,
                "model": model,
                "city": location,
                "year": year,
                "mileage": mileage,
                "fuel_type": fuel_type,
                "body_type": body_type,
                "transmission": transmission,
                "scraped_at": datetime.utcnow().isoformat(),
                "images_urls": ad.get('images', []) or []
            }
            return raw_data
        except Exception as e:
            logger.error(f"Error parsing ad JSON: {e}")
            return None

    def _parse_listing_element(self, elem) -> Optional[Dict[str, Any]]:
        """Fallback HTML parsing for list page elements"""
        try:
            selectors = self.selector_loader.load(self.source_name)
            fields = selectors.get("fields", {})
            fallbacks = selectors.get("fallback_fields", {})
            
            source_url = FallbackExtractor.extract_attr(
                elem, fields.get("url"), "href", fallbacks.get("url")
            )
            if source_url and not source_url.startswith('http'):
                source_url = f"https://www.avito.ma{source_url}"

            price = FallbackExtractor.extract_text(
                elem, fields.get("price"), fallbacks.get("price"), heuristic="price"
            )
            
            title = FallbackExtractor.extract_text(
                elem, fields.get("title"), fallbacks.get("title")
            )
            brand, model = self._extract_brand_model(title or '')
            
            city = FallbackExtractor.extract_text(
                elem, fields.get("city"), fallbacks.get("city")
            )

            return {
                "source": self.source_name,
                "source_url": source_url,
                "price": price_elem.get_text(strip=True) if price_elem else None,
                "brand": brand,
                "model": model,
                "city": location_elem.get_text(strip=True) if location_elem else None,
                "year": None,
                "mileage": None,
                "fuel_type": None,
                "body_type": None,
                "transmission": None,
                "scraped_at": datetime.utcnow().isoformat(),
                "images_urls": []
            }
        except Exception as e:
            logger.error(f"Error parsing listing element: {e}")
            return None

    def _extract_brand_model(self, title: str) -> tuple:
        """Extract brand and model from title string"""
        if not title:
            return None, None

        # Common Moroccan car brands
        brands = [
            'Dacia', 'Renault', 'Peugeot', 'Citroën', 'Citroen',
            'Hyundai', 'Kia', 'Toyota', 'Volkswagen', 'VW',
            'BMW', 'Mercedes', 'Audi', 'Ford', 'Fiat',
            'Nissan', 'Mitsubishi', 'Suzuki', 'Honda', 'Mazda',
            'Opel', 'Chevrolet', 'Jeep', 'Land Rover', 'Range Rover',
            'Volvo', 'Seat', 'Skoda', 'Mini', 'Smart',
            'Iveco', 'MAN', 'Scania', 'Mercedes-Benz'
        ]

        title_lower = title.lower()
        for brand in brands:
            if title_lower.startswith(brand.lower() + ' ') or title_lower == brand.lower():
                model = title[len(brand):].strip()
                return brand, model if model else None

        # Fallback: first word as brand
        parts = title.split()
        if parts:
            return parts[0], ' '.join(parts[1:]) if len(parts) > 1 else None
        return None, None

    def _parse_int(self, val: Any) -> Optional[int]:
        if not val:
            return None
        try:
            digits = re.sub(r'[^\d]', '', str(val))
            return int(digits) if digits else None
        except Exception:
            return None