"""
Kifal Auto Scraper — Occasion Certifiée (contrôle technique 200 points)
URL: https://occasion.kifal.ma/annonces
Structure: listing page → /annonce/{MARQUE_Modèle_Année_...}.htm (detail page)
Note: Le domaine principal est kifal-auto.ma, les annonces sont sur occasion.kifal.ma
"""
import os
import re
import yaml
import logging
from typing import List, Optional
from urllib.parse import unquote
from bs4 import BeautifulSoup

from core.base_scraper import BaseScraper
from models.listing import RawListing

logger = logging.getLogger(__name__)


class KifalScraper(BaseScraper):
    platform_name = "kifal_auto"
    listing_type = "occasion"
    is_certified = True

    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "sites.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["kifal_auto"]

        delay = tuple(self.config.get("delay", [3.0, 5.0]))
        super().__init__(polite_delay=delay)

        self.base_url = self.config["base_url"]
        self.selectors = self.config.get("selectors", {})

    def get_listing_urls(self, max_pages: int = 2) -> List[str]:
        urls = []
        for page in range(1, max_pages + 1):
            search_url = self.config["search_url"].format(page=page)
            resp = self.client.get(search_url)
            if resp.status_code != 200:
                logger.warning(f"[kifal_auto] Page {page} returned {resp.status_code}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select(self.selectors.get("listing_links", "a[href*='/annonce/']"))

            if not links:
                break

            for link in links:
                href = link.get("href", "")
                # Only keep actual annonce detail links (.htm)
                if "/annonce/" in href and href.endswith(".htm"):
                    if not href.startswith("http"):
                        href = self.base_url + href
                    urls.append(href)

        return list(set(urls))

    def parse_listing(self, html: str, url: str) -> Optional[RawListing]:
        soup = BeautifulSoup(html, "html.parser")

        # Title
        title_el = soup.select_one("h1") or soup.select_one(".annonce-title")
        if not title_el:
            return None
        title = title_el.text.strip()

        # Price
        prix = ""
        price_el = soup.select_one(".price") or soup.select_one(".annonce-price") or soup.select_one("[class*=price]")
        if price_el:
            prix = price_el.text.strip()

        # Description
        desc_el = soup.select_one(".annonce-description, .description, [class*=description]")
        description = desc_el.text.strip() if desc_el else title

        # Images
        images = []
        for img in soup.select(".gallery img, .annonce-gallery img, .carousel img, [class*=gallery] img"):
            src = img.get("src") or img.get("data-src")
            if src and "logo" not in src.lower() and "recaptcha" not in src.lower():
                if not src.startswith("http"):
                    src = self.base_url + src
                images.append(src)

        # Extract structured data from URL pattern:
        # /annonce/MARQUE_Modèle_Année_Carburant_Transmission_Ville_ID_REF.htm
        url_info = self._parse_url_pattern(url)

        # Also extract from page text as fallback
        page_text = soup.get_text()
        annee = url_info.get("annee") or self._extract_year(page_text)
        km = self._extract_km(page_text)
        carburant = url_info.get("carburant") or self._extract_field(page_text, ["diesel", "essence", "hybride", "electrique", "électrique"])
        transmission = url_info.get("transmission") or self._extract_field(page_text, ["automatique", "manuelle", "manuel"])

        # Kifal is always certified
        return RawListing(
            source_plateforme=self.platform_name,
            type_annonce="occasion",
            titre_brut=title,
            prix_brut=prix,
            description_brute=description,
            photos_urls=images,
            vendeur_info={"type": "professionnel_certifie", "label": "Kifal Auto", "garantie": "contrôle 200 points"},
            url_source=url,
            certifie=True,
            marque_brute=url_info.get("marque", ""),
            modele_brut=url_info.get("modele", ""),
            annee_brute=annee,
            kilometrage_brut=km,
            carburant_brut=carburant,
            transmission_brute=transmission,
            ville_brute=url_info.get("ville", ""),
        )

    # ── Helpers ──────────────────────────────────────────────

    def _parse_url_pattern(self, url: str) -> dict:
        """
        Parse Kifal URL pattern:
        /annonce/MARQUE_Modèle_Année_Carburant_Transmission_Ville_ID_REF.htm
        Example: /annonce/BMW_Série%202%20Gran%20Coupé_2025_Diesel_Automatique_CASABLANCA_7335_VEH00011V7.htm
        """
        try:
            path = unquote(url.split("/annonce/")[-1].replace(".htm", ""))
            parts = path.split("_")
            if len(parts) >= 6:
                return {
                    "marque": parts[0],
                    "modele": parts[1],
                    "annee": parts[2],
                    "carburant": parts[3].lower(),
                    "transmission": parts[4].lower(),
                    "ville": parts[5],
                }
        except Exception:
            pass
        return {}

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
