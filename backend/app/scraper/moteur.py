"""
Moteur.ma — scraper des annonces voiture occasion.
"""
import re
from typing import Optional

import cloudscraper
from bs4 import BeautifulSoup

from app.scraper.base import BaseScraper

BRANDS = [
    "Dacia", "Renault", "Peugeot", "Citroen", "Hyundai", "Kia", "Toyota",
    "Volkswagen", "BMW", "Mercedes", "Audi", "Ford", "Nissan", "Fiat",
    "MG", "Opel", "Seat", "Skoda", "Mitsubishi", "Mazda", "Honda",
    "Suzuki", "Subaru", "Volvo", "Mini", "Jeep", "Land Rover", "Range Rover",
    "Porsche", "Jaguar", "Lexus", "Infiniti", "Chevrolet", "Chrysler",
    "Dodge", "Iveco", "MAN", "Mercedes-Benz",
]

SKIP_WORDS = {"manuelle", "manuel", "automatique", "auto", "diesel", "essence",
              "hybride", "electrique", "gpl", "il", "y", "a", "km", "mad"}

FUEL_WORDS = {"diesel": "diesel", "essence": "essence", "hybride": "hybride",
              "electrique": "electrique", "électrique": "electrique", "gpl": "gpl"}

TRANS_WORDS = {"automatique": "automatique", "manuelle": "manuelle",
               "auto": "automatique", "manuel": "manuelle"}


class MoteurScraper(BaseScraper):
    SOURCE_NAME = "moteur.ma"
    SEARCH_URL = "https://www.moteur.ma/fr/voiture/achat-voiture-occasion/"

    def __init__(self):
        self.client = cloudscraper.create_scraper()
        self._brands_lower = {b.lower() for b in BRANDS}
        self._brands_sorted = sorted(BRANDS, key=len, reverse=True)

    def fetch_page(self, url: str, page: int = 1) -> list[dict]:
        full_url = f"{self.SEARCH_URL}?page={page}" if page > 1 else self.SEARCH_URL
        try:
            resp = self.client.get(full_url, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            print(f"  Erreur HTTP: {e}")
            return []
        return self._parse(resp.text)

    def _detect_brand(self, text: str) -> Optional[str]:
        text_lower = text.lower()
        for brand in self._brands_sorted:
            if brand.lower() == "man":
                continue
            if brand.lower() in text_lower:
                return brand
        return None

    def _parse(self, html: str) -> list[dict]:
        soup = BeautifulSoup(html, "lxml")
        cards = soup.find_all("div", class_=lambda c: c and "ads-index-card" in (c if isinstance(c, str) else " ".join(c)))
        results = []

        for card in cards:
            try:
                full_text = card.get_text(" ", strip=True)

                a = card.find("a", href=lambda h: h and "/detail-annonce/" in h)
                href = a["href"] if a else None
                title_text = a.get_text(strip=True) if a else ""

                price_el = card.select_one("[class*=price], [class*=prix]")
                price_raw = price_el.get_text(strip=True) if price_el else ""

                if "appeler" in price_raw.lower():
                    continue
                price = float(re.sub(r"[^\d]", "", price_raw))

                brand = self._detect_brand(full_text)
                if not brand:
                    continue

                # Extract model from title or from href slug
                model = ""
                if title_text:
                    model = title_text.replace(brand, "", 1).strip()
                if not model and href:
                    slug = href.rstrip(".html").split("/")[-1]
                    slug = re.sub(r"^" + re.escape(brand.lower()) + r"-?", "", slug, flags=re.IGNORECASE)
                    model = slug.replace("-", " ").title()

                year_match = re.search(r"\b(19\d{2}|20\d{2})\b", full_text)
                year = int(year_match.group(1)) if year_match else None

                mil_match = re.search(r"([\d\s]+)\s*km", full_text)
                mileage = None
                if mil_match:
                    mileage = int(re.sub(r"\s", "", mil_match.group(1)))

                fuel = None
                for word, val in FUEL_WORDS.items():
                    if re.search(r"(?<![a-zA-Z])" + re.escape(word) + r"(?![a-zA-Z])", full_text, re.IGNORECASE):
                        fuel = val
                        break

                transmission = None
                for word, val in TRANS_WORDS.items():
                    if re.search(r"(?<![a-zA-Z])" + re.escape(word) + r"(?![a-zA-Z])", full_text, re.IGNORECASE):
                        transmission = val
                        break

                # City: from card text, the word after brand+model
                city_match = re.search(rf"^{re.escape(brand)}\s+\S+\s+(\S+)", full_text)
                city = city_match.group(1) if city_match else None

                # Description
                desc_el = card.select_one(".text-description, .ad-desc, p.desc")
                description = desc_el.get_text(" ", strip=True) if desc_el else ""

                results.append({
                    "brand": brand,
                    "model": model,
                    "year": year,
                    "price": price,
                    "mileage": mileage,
                    "fuel_type": fuel,
                    "transmission": transmission,
                    "city": city,
                    "description": description,
                    "source": self.SOURCE_NAME,
                    "source_url": f"https://www.moteur.ma{href}" if href and href.startswith("/") else href,
                })
            except Exception:
                continue

        return results

    def close(self):
        pass
