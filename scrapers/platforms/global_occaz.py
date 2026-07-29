"""
Global Occaz – Occasion
Inspecté le 29/07/2026 :
  - Le site www.globaloccaz.ma est INACCESSIBLE (timeout de connexion).
  - Cela peut être dû à un problème de serveur, une fermeture du site,
    ou un blocage géographique/IP.

Ce scraper est un placeholder structurel. Il retourne systématiquement
des listes vides et logue un avertissement clair pour que le pipeline
ne crash pas mais signale le problème.
"""
from scrapers.base_scraper import BaseScraper


class GlobalOccazScraper(BaseScraper):
    platform_name = "global_occaz"
    listing_type = "occasion"
    base_url = "https://www.globaloccaz.ma"

    def get_listing_urls(self, page: int) -> list[str]:
        """
        AVERTISSEMENT : globaloccaz.ma est inaccessible (timeout).
        Vérifier périodiquement si le site revient en ligne.
        """
        print(
            f"[global_occaz] AVERTISSEMENT : globaloccaz.ma est inaccessible "
            f"(timeout lors de la dernière inspection). Scraper désactivé."
        )
        try:
            response = self.session.get(
                f"{self.base_url}/vehicules-doccasion/?page={page}",
                delay=2,
            )
            if response.status_code != 200:
                print(f"[global_occaz] HTTP {response.status_code}")
                return []
            soup = self._make_soup(response.text)
            urls = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/vehicule/" in href or "/annonce/" in href:
                    urls.append(self._absolute_url(href))
            return list(dict.fromkeys(urls))
        except Exception as e:
            print(f"[global_occaz] Erreur (attendue): {e}")
            return []

    def parse_listing(self, html: str, url: str) -> dict:
        soup = self._make_soup(html)
        return self._build_raw_listing(
            titre=self._extract_text(soup, ["h1", ".title"], ""),
            prix=self._extract_text(soup, ["[class*=price]", "[class*=prix]"], ""),
            description=self._extract_text(soup, ["[class*=description]", "p"], ""),
            photos=self._extract_images(soup),
            vendeur_info={},
            date_pub=None,
            url=url,
            certifie=False,
        )
