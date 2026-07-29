"""
Otoclic.com Scraper — Occasion avec reprise
URL: https://www.otoclic.com/acheter-votre-voiture-doccasion/
Structure: listing page → /cars/{slug}/  (detail page)
"""
import os
import re
import yaml
import uuid
import logging
from typing import List, Optional
from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper
from models.listing import RawListing

logger = logging.getLogger(__name__)


class OtoclicScraper(BaseScraper):
    platform_name = "otoclic"
    listing_type = "occasion"
    is_certified = False

    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "sites.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["otoclic"]

        delay = tuple(self.config.get("delay", [2.0, 4.0]))
        super().__init__(polite_delay=delay)

        self.base_url = self.config["base_url"]
        self.selectors = self.config.get("selectors", {})

    def get_listing_urls(self, max_pages: int = 2) -> List[str]:
        urls = []
        for page in range(1, max_pages + 1):
            search_url = self.config["search_url"].format(page=page)
            resp = self.client.get(search_url)
            if resp.status_code != 200:
                logger.warning(f"[otoclic] Page {page} returned {resp.status_code}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select(self.selectors.get("listing_links", "a[href*='/cars/']"))

            if not links:
                break

            for link in links:
                href = link.get("href")
                if href and "/cars/" in href and href.count("/") >= 4:
                    if not href.startswith("http"):
                        href = self.base_url + href
                    urls.append(href)

        return list(set(urls))

    def parse_listing(self, html: str, url: str) -> Optional[RawListing]:
        soup = BeautifulSoup(html, "html.parser")

        # Title
        title_el = soup.select_one(self.selectors.get("title", "h1"))
        if not title_el:
            return None
        title = title_el.text.strip()

        # Price — Otoclic uses .price.car-price or .new-price
        prix = ""
        price_el = soup.select_one(".new-price") or soup.select_one(".price.car-price")
        if price_el:
            prix = price_el.text.strip()

        # Description
        desc_el = soup.select_one(".car-description, .description")
        description = desc_el.text.strip() if desc_el else title

        # Images — Otoclic has a proper gallery
        images = []
        for img in soup.select(".gallery img, .car-gallery img"):
            src = img.get("src") or img.get("data-src")
            if src:
                if not src.startswith("http"):
                    src = self.base_url + src
                images.append(src)

        # Specs — Otoclic lists specs in .vehicle-spec containers
        specs_text = ""
        for spec in soup.select(".vehicle-spec-container, .vehicle-spec, [class*=spec]"):
            specs_text += " " + spec.text.strip()

        # Extract structured fields from specs
        marque = self._extract_from_title(title, 0)
        modele = self._extract_from_title(title, 1)
        annee = self._extract_year(specs_text + " " + title)
        km = self._extract_km(specs_text)
        carburant = self._extract_field(specs_text, ["diesel", "essence", "hybride", "electrique", "électrique"])
        transmission = self._extract_field(specs_text, ["automatique", "manuelle", "manuel"])

        # Vendeur info
        vendeur = {}
        seller_el = soup.select_one(".dealer-name, .seller-name, .agency-name")
        if seller_el:
            vendeur["nom"] = seller_el.text.strip()

        return RawListing(
            source_plateforme=self.platform_name,
            type_annonce="occasion",
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

    # ── Helpers ──────────────────────────────────────────────

    def _extract_from_title(self, title: str, index: int) -> str:
        parts = title.split()
        return parts[index] if len(parts) > index else ""

    def _extract_year(self, text: str) -> str:
        match = re.search(r"\b(19|20)\d{2}\b", text)
        return match.group(0) if match else ""

    def _extract_km(self, text: str) -> str:
        match = re.search(r"([\d\s\.]+)\s*km", text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def _extract_field(self, text: str, keywords: list) -> str:
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                return kw
        return ""
