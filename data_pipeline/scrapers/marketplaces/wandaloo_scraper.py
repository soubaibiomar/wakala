"""
Wandaloo.com Scraper — Occasion + Neuf (Catalogues)
URL occasion: https://www.wandaloo.com/occasion/
URL neuf:     https://www.wandaloo.com/neuf/
Structure: HTML classique, catalogues neuf avec navigation Marque > Modèle > Version (.html)
"""
import os
import re
import yaml
import uuid
import logging
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper
from models.listing import RawListing
from utils.normalizer import clean_price, clean_mileage, normalize_fuel, normalize_transmission

logger = logging.getLogger(__name__)


class WandalooScraper(BaseScraper):
    platform_name = "wandaloo"
    listing_type = "both"
    is_certified = False

    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "sites.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["wandaloo"]

        delay = tuple(self.config.get("delay", [3.0, 5.0]))
        super().__init__(polite_delay=delay)

        self.base_url = self.config["base_url"]
        self.selectors = self.config.get("selectors", {})

    def get_listing_urls(self, max_pages: int = 2) -> List[str]:
        urls = []

        # --- 1. Wandaloo Occasion ---
        for page in range(1, max_pages + 1):
            search_url = self.config["used_url"].format(page=page)
            resp = self.client.get(search_url)
            if resp.status_code != 200:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select(self.selectors.get("listing_links", "ul.listing li a"))

            if not links:
                break

            for link in links:
                href = link.get("href")
                if href and "/occasion/" in href:
                    if not href.startswith("http"):
                        href = self.base_url + href
                    urls.append(href)

        # --- 2. Wandaloo Neuf (Catalogues) ---
        try:
            resp = self.client.get(self.config["new_url"])
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                brand_links = soup.select(self.selectors.get("new_brand_links", "a[href*='/neuf/']"))

                brands = set()
                for link in brand_links:
                    href = link.get("href")
                    if href and href != "/neuf/":
                        if href.endswith(".html"):
                            full = self.base_url + href if not href.startswith("http") else href
                            urls.append(full)
                        else:
                            brands.add(self.base_url + href if not href.startswith("http") else href)

                # Traverse brand pages to find version links
                for b_url in list(brands)[:max_pages]:
                    b_resp = self.client.get(b_url)
                    if b_resp.status_code == 200:
                        b_soup = BeautifulSoup(b_resp.text, "html.parser")
                        version_links = b_soup.select("a[href$='.html']")
                        for vl in version_links:
                            v_href = vl.get("href")
                            if v_href and "/neuf/" in v_href:
                                if not v_href.startswith("http"):
                                    v_href = self.base_url + v_href
                                urls.append(v_href)
        except Exception as e:
            logger.warning(f"[wandaloo] Error fetching neuf catalogs: {e}")

        return list(set(urls))

    def parse_listing(self, html: str, url: str) -> Optional[RawListing]:
        soup = BeautifulSoup(html, "html.parser")

        is_new = "/neuf/" in url
        type_annonce = "neuf" if is_new else "occasion"

        title_el = soup.select_one(self.selectors.get("title", "h1"))
        if not title_el:
            return None

        title = title_el.text.strip()
        text_content = soup.get_text()

        # Price
        prix = ""
        price_match = re.search(r"([\d\s\.,]+)\s*DHS?", text_content, re.IGNORECASE)
        if price_match:
            prix = price_match.group(0).strip()

        # Mileage
        km = ""
        if is_new:
            km = "0"
        else:
            km_match = re.search(r"([\d\s]+)\s*km", text_content, re.IGNORECASE)
            if km_match:
                km = km_match.group(1).strip()

        # Year
        annee = ""
        if is_new:
            annee = str(datetime.now().year)
        else:
            year_match = re.search(r"Année\s*:\s*(\d{4})", text_content, re.IGNORECASE)
            if year_match:
                annee = year_match.group(1)

        # Fuel / Transmission
        carburant = self._extract_field(text_content, ["diesel", "essence", "hybride", "electrique", "électrique"])
        transmission = self._extract_field(text_content, ["automatique", "manuelle", "manuel"])

        # Brand / Model from title
        parts = title.split()
        marque = parts[0] if parts else ""
        modele = " ".join(parts[1:3]) if len(parts) > 1 else ""

        # Images
        images = []
        for img in soup.select(".gallery img, div#slider img, .overview img"):
            src = img.get("src")
            if src:
                if not src.startswith("http"):
                    src = self.base_url + src
                images.append(src)

        # Description
        desc_el = soup.select_one(".description") or soup.select_one(".text-content")
        description = desc_el.text.strip() if desc_el else title

        # Vendeur info (only for occasion)
        vendeur = {}
        if not is_new:
            seller_el = soup.select_one(".vendeur, .seller-info")
            if seller_el:
                vendeur["nom"] = seller_el.text.strip()

        return RawListing(
            source_plateforme=self.platform_name,
            type_annonce=type_annonce,
            titre_brut=title,
            prix_brut=prix,
            description_brute=description,
            photos_urls=images,
            vendeur_info=vendeur,
            url_source=url,
            certifie=False,
            marque_brute=marque,
            modele_brut=modele,
            annee_brute=annee,
            kilometrage_brut=km,
            carburant_brut=carburant,
            transmission_brute=transmission,
        )

    def _extract_field(self, text: str, keywords: list) -> str:
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                return kw
        return ""
