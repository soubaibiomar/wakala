"""
Moteur.ma Scraper — Occasion + Neuf (Catalogues)
URL occasion: https://www.moteur.ma/fr/voiture/achat-voiture-occasion/recherche/
URL neuf:     https://www.moteur.ma/fr/voiture/voiture-neuve/
Structure: HTML classique, catalogues neuf avec navigation Marque > Modèle > Version
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

logger = logging.getLogger(__name__)


class MoteurScraper(BaseScraper):
    platform_name = "moteur"
    listing_type = "both"
    is_certified = False

    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "sites.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)["moteur"]

        delay = tuple(self.config.get("delay", [2.0, 4.0]))
        super().__init__(polite_delay=delay)

        self.base_url = self.config["base_url"]
        self.selectors = self.config.get("selectors", {})

    def get_listing_urls(self, max_pages: int = 2) -> List[str]:
        urls = []

        # --- 1. Moteur Occasion ---
        for page in range(1, max_pages + 1):
            search_url = self.config["search_url"].format(page=page)
            resp = self.client.get(search_url)
            if resp.status_code != 200:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            links = soup.select(self.selectors["listing_links"])

            if not links:
                break

            for link in links:
                href = link.get("href")
                if href:
                    if not href.startswith("http"):
                        href = self.base_url + href
                    urls.append(href)

        # --- 2. Moteur Neuf (Catalogues) ---
        try:
            new_url = self.config.get("new_url", "")
            if new_url:
                resp = self.client.get(new_url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    brand_links = soup.select(self.selectors.get("new_listing_links", "a[href*='/fr/neuf/voiture/']"))

                    brands = set()
                    for link in brand_links:
                        href = link.get("href")
                        if href:
                            brands.add(href if href.startswith("http") else self.base_url + href)

                    for b_url in list(brands)[:max_pages]:
                        b_resp = self.client.get(b_url)
                        if b_resp.status_code == 200:
                            b_soup = BeautifulSoup(b_resp.text, "html.parser")
                            model_links = b_soup.select("a[href*='/fr/neuf/voiture/']")
                            models = set()
                            for ml in model_links:
                                m_href = ml.get("href")
                                if m_href and len(m_href.split("/")) >= 7:
                                    models.add(m_href if m_href.startswith("http") else self.base_url + m_href)

                            for m_url in list(models)[:max_pages]:
                                m_resp = self.client.get(m_url)
                                if m_resp.status_code == 200:
                                    m_soup = BeautifulSoup(m_resp.text, "html.parser")
                                    version_links = m_soup.select("a[href$='.html']")
                                    for vl in version_links:
                                        v_href = vl.get("href")
                                        if v_href and "/neuf/voiture/" in v_href:
                                            urls.append(v_href if v_href.startswith("http") else self.base_url + v_href)
        except Exception as e:
            logger.warning(f"[moteur] Error fetching neuf catalogs: {e}")

        return list(set(urls))

    def parse_listing(self, html: str, url: str) -> Optional[RawListing]:
        soup = BeautifulSoup(html, "html.parser")

        is_new = "/neuf/voiture/" in url
        type_annonce = "neuf" if is_new else "occasion"

        # Title
        title_el = soup.select_one(self.selectors.get("title", "h3.title")) or soup.select_one("h1")
        if not title_el:
            return None
        title = title_el.text.strip()

        # Price
        prix = ""
        price_el = soup.select_one(self.selectors.get("price", ".price"))
        if price_el:
            prix = price_el.text.strip()

        # Brand
        brand_el = soup.select_one(self.selectors.get("brand", ".brand"))
        marque = brand_el.text.strip() if brand_el else ""

        # Model
        model_el = soup.select_one(self.selectors.get("model", ".model"))
        modele = model_el.text.strip() if model_el else ""

        # Year
        annee = ""
        year_el = soup.select_one(self.selectors.get("year", ".year"))
        if year_el and year_el.text.strip().isdigit():
            annee = year_el.text.strip()
        elif is_new:
            annee = str(datetime.now().year)

        # Mileage
        km = ""
        if is_new:
            km = "0"
        else:
            mileage_el = soup.select_one(self.selectors.get("mileage", ".mileage"))
            if mileage_el:
                km = mileage_el.text.strip()

        # Fuel
        fuel_el = soup.select_one(self.selectors.get("fuel_type", ".fuel"))
        carburant = fuel_el.text.strip() if fuel_el else ""

        # Transmission
        trans_el = soup.select_one(self.selectors.get("transmission", ".transmission"))
        transmission = trans_el.text.strip() if trans_el else ""

        # City
        city_el = soup.select_one(self.selectors.get("city", ".city"))
        ville = city_el.text.strip() if city_el else ""

        # Description
        desc_el = soup.select_one(self.selectors.get("description", ".desc"))
        description = desc_el.text.strip() if desc_el else title

        # Images
        images = []
        for img in soup.select(self.selectors.get("images", ".slider img")):
            src = img.get("src") or img.get("data-src")
            if src:
                if not src.startswith("http"):
                    src = self.base_url + src
                images.append(src)

        return RawListing(
            source_plateforme=self.platform_name,
            type_annonce=type_annonce,
            titre_brut=title,
            prix_brut=prix,
            description_brute=description,
            photos_urls=images,
            vendeur_info={},
            url_source=url,
            certifie=False,
            marque_brute=marque,
            modele_brut=modele,
            annee_brute=annee,
            kilometrage_brut=km,
            carburant_brut=carburant,
            transmission_brute=transmission,
            ville_brute=ville,
        )
        # --- 2. Moteur Neuf (Catalogues) ---
        try:
            new_url = self.config.get("new_url", "")
            if new_url:
                resp = self.client.get(new_url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    brand_links = soup.select(self.selectors.get("new_listing_links", "a[href*='/fr/neuf/voiture/']"))

                    brands = set()
                    for link in brand_links:
                        href = link.get("href")
                        if href:
                            brands.add(href if href.startswith("http") else self.base_url + href)

                    for b_url in list(brands)[:max_pages]:
                        b_resp = self.client.get(b_url)
                        if b_resp.status_code == 200:
                            b_soup = BeautifulSoup(b_resp.text, "html.parser")
                            model_links = b_soup.select("a[href*='/fr/neuf/voiture/']")
                            models = set()
                            for ml in model_links:
                                m_href = ml.get("href")
                                if m_href and len(m_href.split("/")) >= 7:
                                    models.add(m_href if m_href.startswith("http") else self.base_url + m_href)

                            for m_url in list(models)[:max_pages]:
                                m_resp = self.client.get(m_url)
                                if m_resp.status_code == 200:
                                    m_soup = BeautifulSoup(m_resp.text, "html.parser")
                                    version_links = m_soup.select("a[href$='.html']")
                                    for vl in version_links:
                                        v_href = vl.get("href")
                                        if v_href and "/neuf/voiture/" in v_href:
                                            urls.append(v_href if v_href.startswith("http") else self.base_url + v_href)
        except Exception as e:
            logger.warning(f"[moteur] Error fetching neuf catalogs: {e}")

        return list(set(urls))

    def parse_listing(self, html: str, url: str) -> Optional[RawListing]:
        soup = BeautifulSoup(html, "html.parser")

        is_new = "/neuf/voiture/" in url
        type_annonce = "neuf" if is_new else "occasion"

        # Title
        title_el = soup.select_one(self.selectors.get("title", "h3.title")) or soup.select_one("h1")
        if not title_el:
            return None
        title = title_el.text.strip()

        # Price
        prix = ""
        price_el = soup.select_one(self.selectors.get("price", ".price"))
        if price_el:
            prix = price_el.text.strip()

        # Brand
        brand_el = soup.select_one(self.selectors.get("brand", ".brand"))
        marque = brand_el.text.strip() if brand_el else ""

        # Model
        model_el = soup.select_one(self.selectors.get("model", ".model"))
        modele = model_el.text.strip() if model_el else ""

        # Year
        annee = ""
        year_el = soup.select_one(self.selectors.get("year", ".year"))
        if year_el and year_el.text.strip().isdigit():
            annee = year_el.text.strip()
        elif is_new:
            annee = str(datetime.now().year)

        # Mileage
        km = ""
        if is_new:
            km = "0"
        else:
            mileage_el = soup.select_one(self.selectors.get("mileage", ".mileage"))
            if mileage_el:
                km = mileage_el.text.strip()

        # Fuel
        fuel_el = soup.select_one(self.selectors.get("fuel_type", ".fuel"))
        carburant = fuel_el.text.strip() if fuel_el else ""

        # Transmission
        trans_el = soup.select_one(self.selectors.get("transmission", ".transmission"))
        transmission = trans_el.text.strip() if trans_el else ""

        # City
        city_el = soup.select_one(self.selectors.get("city", ".city"))
        ville = city_el.text.strip() if city_el else ""

        # Description
        desc_el = soup.select_one(self.selectors.get("description", ".desc"))
        description = desc_el.text.strip() if desc_el else title

        # Images
        images = []
        for img in soup.select(self.selectors.get("images", ".slider img")):
            src = img.get("src") or img.get("data-src")
            if src:
                if not src.startswith("http"):
                    src = self.base_url + src
                images.append(src)

        return RawListing(
            source_plateforme=self.platform_name,
            type_annonce=type_annonce,
            titre_brut=title,
            prix_brut=prix,
            description_brute=description,
            photos_urls=images,
            vendeur_info={},
            url_source=url,
            certifie=False,
            marque_brute=marque,
            modele_brut=modele,
            annee_brute=annee,
            kilometrage_brut=km,
            carburant_brut=carburant,
            transmission_brute=transmission,
            ville_brute=ville,
        )
