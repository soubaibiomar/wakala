"""
scrapers/base_scraper.py
Classe abstraite commune pour tous les scrapers Wakala.
Chaque plateforme hérite de cette classe et implémente uniquement
les méthodes spécifiques à sa structure HTML.
"""
from abc import ABC, abstractmethod
from scrapers.utils.anti_detection import AntiDetectionSession
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("wakala.scraper")


class BaseScraper(ABC):
    """
    Contrat commun pour tous les scrapers de la marketplace Wakala.

    Attributs de classe à redéfinir :
        platform_name  – identifiant court de la plateforme (ex: "avito")
        listing_type   – "neuf" ou "occasion"
        base_url       – URL racine du site (ex: "https://www.moteur.ma")
    """
    platform_name: str
    listing_type: str   # "neuf" ou "occasion"
    base_url: str

    def __init__(self):
        self.session = AntiDetectionSession()

    # ------------------------------------------------------------------ #
    # Méthodes abstraites (à implémenter par chaque sous-classe)
    # ------------------------------------------------------------------ #

    @abstractmethod
    def get_listing_urls(self, page: int) -> list[str]:
        """Retourne la liste des URLs d'annonces individuelles pour la page donnée."""
        ...

    @abstractmethod
    def parse_listing(self, html: str, url: str) -> dict:
        """
        Parse le HTML d'une annonce individuelle et retourne le schéma brut commun :
        {
            "source_plateforme": str,
            "type_annonce": "neuf" | "occasion",
            "titre_brut": str,
            "prix_brut": str,
            "description_brute": str,
            "photos_urls": list[str],
            "vendeur_info": dict,
            "date_publication": str | None,
            "url_source": str,
            "certifie": bool
        }
        """
        ...

    # ------------------------------------------------------------------ #
    # Helpers partagés (évite la duplication inter-scrapers)
    # ------------------------------------------------------------------ #

    def _make_soup(self, html: str) -> BeautifulSoup:
        """Crée un objet BeautifulSoup à partir du HTML brut."""
        return BeautifulSoup(html, "html.parser")

    def _absolute_url(self, href: str) -> str:
        """Convertit un lien relatif en URL absolue."""
        if not href:
            return ""
        if href.startswith("http"):
            return href
        if href.startswith("//"):
            return "https:" + href
        return self.base_url.rstrip("/") + "/" + href.lstrip("/")

    def _extract_text(self, soup: BeautifulSoup, selectors: list[str], default: str = "") -> str:
        """Essaie une liste de sélecteurs CSS et retourne le texte du premier match."""
        for sel in selectors:
            elem = soup.select_one(sel)
            if elem and elem.text.strip():
                return elem.text.strip()
        return default

    def _extract_images(self, soup: BeautifulSoup, selectors: list[str] | None = None) -> list[str]:
        """
        Extrait les URLs d'images depuis le HTML.
        Cherche src, data-src, data-lazy-src sur les éléments ciblés.
        """
        if selectors is None:
            selectors = ["img"]
        urls = []
        for sel in selectors:
            for img in soup.select(sel):
                src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or ""
                if src and not src.startswith("data:"):
                    urls.append(self._absolute_url(src))
        return list(dict.fromkeys(urls))  # déduplique en gardant l'ordre

    def _build_raw_listing(
        self,
        titre: str,
        prix: str,
        description: str,
        photos: list[str],
        vendeur_info: dict,
        date_pub: str | None,
        url: str,
        certifie: bool | None = None,
    ) -> dict:
        """Construit le dictionnaire de sortie brute conforme au schéma commun."""
        return {
            "source_plateforme": self.platform_name,
            "type_annonce": self.listing_type,
            "titre_brut": titre,
            "prix_brut": prix,
            "description_brute": description,
            "photos_urls": photos[:10],
            "vendeur_info": vendeur_info,
            "date_publication": date_pub,
            "url_source": url,
            "certifie": certifie if certifie is not None else False,
        }
