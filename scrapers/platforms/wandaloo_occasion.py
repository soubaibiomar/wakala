"""
Wandaloo.com – Annonces Occasion
Structure HTML inspectée le 29/07/2026 :
  - La section occasion de Wandaloo redirige vers un dépôt d'annonce
    (/occasion/voiture-occasion-maroc-vendre.html = formulaire de dépôt).
  - La page d'annonces (/occasion/voiture-occasion-maroc-annonce.html)
    retourne "Contenu indisponible" lors des inspections.
  - Wandaloo semble avoir migré ou désactivé son module d'annonces occasion.
  - Ce scraper tente un parsing best-effort mais est désactivable via config.

NOTE : robots.txt de wandaloo.com retourne une page HTML "Contenu indisponible"
au lieu d'un vrai robots.txt — le site a potentiellement un problème de
configuration serveur.
"""
from scrapers.base_scraper import BaseScraper


class WandalooOccasionScraper(BaseScraper):
    platform_name = "wandaloo"
    listing_type = "occasion"
    base_url = "https://www.wandaloo.com"

    def get_listing_urls(self, page: int) -> list[str]:
        """
        Wandaloo occasion : /occasion/voiture-occasion-maroc-annonce.html
        Lors de l'inspection, cette page retourne très peu de contenu exploitable.
        """
        search_url = f"{self.base_url}/occasion/voiture-occasion-maroc-annonce.html?page={page}"
        try:
            response = self.session.get(search_url, delay=4)
            if response.status_code != 200:
                return []
            soup = self._make_soup(response.text)

            # Wandaloo n'a pas de structure de carte classique pour l'occasion.
            # On cherche des liens vers des fiches véhicule individuelles.
            urls = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                # Liens occasion individuels (pattern attendu si le module est actif)
                if "/occasion/" in href and href.endswith(".html"):
                    full = self._absolute_url(href)
                    # Exclure les pages de navigation/catégorie
                    if "annonce" not in full and "vendre" not in full and "argus" not in full:
                        urls.append(full)

            return list(dict.fromkeys(urls))
        except Exception as e:
            print(f"[wandaloo_occasion] Erreur get_listing_urls: {e}")
            return []

    def parse_listing(self, html: str, url: str) -> dict:
        soup = self._make_soup(html)

        titre = self._extract_text(soup, ["h1", ".titre", "h2"], "")
        prix = self._extract_text(soup, [".prix", "[class*=price]"], "")
        description = self._extract_text(soup, [".description", ".content", "p"], "")

        photos = self._extract_images(soup, ["img[src*=wandaloo]", "img[src*=upload]"])

        return self._build_raw_listing(
            titre=titre,
            prix=prix,
            description=description,
            photos=photos,
            vendeur_info={},
            date_pub=None,
            url=url,
            certifie=False,
        )
