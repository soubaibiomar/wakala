"""
Avito.ma — scraper via l'API Next.js (__NEXT_DATA__).
Contourne Cloudflare avec cloudscraper.
"""
import re
from typing import Optional

import cloudscraper

from app.scraper.base import BaseScraper

BRANDS = [
    "Dacia", "Renault", "Peugeot", "Citroen", "Hyundai", "Kia", "Toyota",
    "Volkswagen", "BMW", "Mercedes", "Audi", "Ford", "Nissan", "Fiat",
    "MG", "Opel", "Seat", "Skoda", "Mitsubishi", "Mazda", "Honda",
    "Suzuki", "Subaru", "Volvo", "Mini", "Jeep", "Land Rover", "Range Rover",
    "Porsche", "Jaguar", "Lexus", "Infiniti", "Chevrolet", "Chrysler",
    "Dodge", "Iveco", "MAN", "Peugeot", "Mercedes-Benz",
]

FUEL_MAP = {
    "Diesel": "diesel", "Essence": "essence", "Hybride": "hybride",
    "Hybride rechargeable": "hybride", "Électrique": "electrique",
    "Electrique": "electrique", "GPL": "gpl",
}

TRANS_MAP = {
    "Automatique": "automatique", "Manuelle": "manuelle",
    "Séquentielle": "automatique", "Semi-auto": "automatique",
}


class AvitoScraper(BaseScraper):
    SOURCE_NAME = "avito.ma"
    BASE_URL = "https://www.avito.ma"

    def __init__(self):
        self.client = cloudscraper.create_scraper()
        self._brands_lower = {b.lower() for b in BRANDS}

    def fetch_page(self, url: str, page: int = 1) -> list[dict]:
        if page > 1:
            sep = "&" if "?" in url else "?"
            full_url = f"{url}{sep}o={page}"
        else:
            full_url = url
        try:
            resp = self.client.get(full_url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Erreur HTTP {full_url}: {e}")
            return []
        return self._parse(resp.text)

    def _parse(self, html: str) -> list[dict]:
        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html, re.DOTALL
        )
        if not match:
            print("  __NEXT_DATA__ non trouvé dans la page")
            return []

        import json
        data = json.loads(match.group(1))
        try:
            ads = data["props"]["pageProps"]["componentProps"]["ads"]["ads"]
        except (KeyError, TypeError):
            print("  Structure JSON inattendue")
            return []

        results = []
        for ad in ads:
            vehicle = self._ad_to_vehicle(ad)
            if vehicle:
                results.append(vehicle)
        return results

    def _detect_brand(self, title: str) -> Optional[str]:
        title_lower = title.lower()
        for brand in sorted(BRANDS, key=len, reverse=True):
            if brand.lower() in title_lower:
                return brand
        return None

    def _extract_model(self, title: str, brand: str) -> str:
        rest = re.sub(r"(?i)\b" + re.escape(brand) + r"\b", "", title, count=1).strip()
        for suffix in ["à vendre", "a vendre", "en bon état", "bon état",
                       "d'occasion", "de luxe", "version luxe", "toutes options",
                       "excellent état", "très bon état"]:
            rest = re.sub(r"(?i)\b" + re.escape(suffix) + r"\b", "", rest).strip()
        rest = re.sub(r"\s+", " ", rest).strip()
        return rest[:60] if rest else ""

    def _ad_to_vehicle(self, ad: dict) -> Optional[dict]:
        try:
            title = ad.get("subject", "")

            price_info = ad.get("price", {})
            if not price_info or not price_info.get("value"):
                return None
            price = float(price_info["value"])

            location = ad.get("location", "")
            description = ad.get("description", "")

            params = {}
            for p in ad.get("params", {}).get("secondary", []):
                if "key" in p:
                    params[p["key"]] = p.get("value")

            year = None
            year_str = params.get("regdate", "")
            if year_str and str(year_str).isdigit():
                year = int(year_str)

            mileage = None
            mileage_val = params.get("mileage_exact")
            if mileage_val is not None:
                if isinstance(mileage_val, str):
                    mileage = int(re.sub(r"\s", "", mileage_val))
                else:
                    mileage = int(mileage_val)

            fuel = FUEL_MAP.get(params.get("fuel", ""))
            transmission = TRANS_MAP.get(params.get("bv", ""))

            brand = self._detect_brand(title)
            if not brand:
                return None

            model = self._extract_model(title, brand)
            if not model and mileage is not None:
                model = str(year) if year else ""

            return {
                "brand": brand,
                "model": model or "",
                "year": year,
                "price": price,
                "mileage": mileage,
                "fuel_type": fuel,
                "transmission": transmission,
                "city": location,
                "description": description[:500],
                "source": self.SOURCE_NAME,
                "source_url": ad.get("href"),
                "image_url": ad.get("defaultImage"),
                "seller_name": ad.get("seller", {}).get("name"),
                "seller_type": ad.get("seller", {}).get("type"),
            }
        except Exception as e:
            print(f"  Erreur parsing: {e}")
            return None

    def close(self):
        pass
