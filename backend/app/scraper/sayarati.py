"""
Sayarati.ma — scraper d'annonces véhicules.
"""
import re
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from app.scraper.base import BaseScraper


class SayaratiScraper(BaseScraper):
    BASE_URL = "https://www.sayarati.ma"
    SOURCE_NAME = "sayarati.ma"

    def scrape_search_page(self, url: str, page: int = 1) -> list[dict]:
        full_url = f"{url}?page={page}" if page > 1 else url
        try:
            resp = self.client.get(full_url)
            resp.raise_for_status()
        except Exception:
            return []
        soup = BeautifulSoup(resp.text, "lxml")
        results = []
        for link_el in soup.find_all("a", href=lambda h: h and ("/annonce" in h or "/occasion" in h)):
            link = link_el.get("href", "")
            if not link or link == "#":
                continue
            listing_url = urljoin(self.BASE_URL, link)
            data = self.scrape_listing(listing_url)
            if data:
                results.append(data)
            self._rate_limit()
        return results

    def scrape_listing(self, url: str) -> Optional[dict]:
        try:
            resp = self.client.get(url)
            resp.raise_for_status()
        except Exception:
            return None
        soup = BeautifulSoup(resp.text, "lxml")

        title_el = soup.select_one("h1, .title, [class*=title]")
        title = title_el.get_text(strip=True) if title_el else ""

        price = None
        price_el = soup.select_one("[class*=price], [itemprop=price], .prix")
        if price_el:
            raw = re.sub(r"[^\d]", "", price_el.get_text(strip=True))
            if raw:
                price = float(raw)

        year = None
        mileage = None
        fuel = None
        trans = None
        city = None

        for row in soup.select("[class*=info] li, [class*=props] li, table tr, .detail p"):
            text = row.get_text(" ", strip=True).lower()
            if "année" in text or "annee" in text:
                m = re.search(r"(\d{4})", text)
                if m:
                    year = int(m.group(1))
            if "kilométrage" in text or "km" in text:
                m = re.search(r"([\d\s]+)\s*km", text)
                if m:
                    mileage = int(re.sub(r"\s", "", m.group(1)))
            if "carburant" in text or "énergie" in text:
                if "diesel" in text:
                    fuel = "diesel"
                elif "essence" in text:
                    fuel = "essence"
                elif "hybride" in text:
                    fuel = "hybride"
                elif "électrique" in text or "electrique" in text:
                    fuel = "electrique"
            if "boîte" in text or "transmission" in text or "boite" in text:
                if "automatique" in text or "auto" in text:
                    trans = "automatique"
                elif "manuelle" in text or "manuel" in text:
                    trans = "manuelle"
            if "ville" in text:
                parts = text.split(":")
                if len(parts) > 1:
                    city = parts[-1].strip().title()

        brand = None
        model = None
        if title:
            parts = title.split()
            if len(parts) >= 2:
                brand = parts[0]
                model = " ".join(parts[1:])

        if not brand:
            brand_el = soup.select_one("[class*=brand], [itemprop=brand]")
            if brand_el:
                brand = brand_el.get_text(strip=True)

        return {
            "brand": brand,
            "model": model,
            "year": year,
            "price": price,
            "mileage": mileage,
            "fuel_type": fuel,
            "transmission": trans,
            "city": city,
            "source": self.SOURCE_NAME,
            "source_url": url,
            "description": title,
        }
