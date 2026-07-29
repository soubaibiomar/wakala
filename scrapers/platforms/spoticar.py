"""
Spoticar.ma – Véhicules certifiés Stellantis
Structure HTML inspectée le 29/07/2026 :
  - URL : https://www.spoticar.ma/voitures-occasion
  - Le site est construit sur Drupal (PSA/Stellantis CMS).
  - Les annonces sont chargées dynamiquement via JavaScript (pas dans le HTML SSR).
  - 0 cartes trouvées dans le HTML statique.
  - Le site utilise Google Maps API + Woosmap pour la géolocalisation.
  - Les liens filtres pointent vers /voitures-occasion/{categorie} (berline, citadine, etc.)
  - robots.txt : pas de restriction sur /voitures-occasion

STRATÉGIE : Spoticar étant un partenaire Stellantis professionnel, la meilleure
approche est de chercher une API back-end (XHR). Le HTML statique ne contient pas
les données véhicules — elles sont injectées par JS.

En attendant une intégration API, ce scraper parse les liens de catégorie
et tente d'extraire les données de la page détail véhicule (qui peut contenir
les infos en HTML).
"""
from scrapers.base_scraper import BaseScraper


class SpoticarScraper(BaseScraper):
    platform_name = "spoticar"
    listing_type = "occasion"
    base_url = "https://www.spoticar.ma"

    def get_listing_urls(self, page: int) -> list[str]:
        """
        La page de listing Spoticar est rendue côté client (JS).
        On ne peut pas extraire les URLs des annonces depuis le HTML statique.
        En production, il faudra :
          1. Utiliser Playwright pour rendre le JS, OU
          2. Intercepter l'API XHR utilisée par le frontend Drupal.

        Pour l'instant, on retourne une liste vide et on logue un warning.
        """
        print(
            f"[spoticar] AVERTISSEMENT : Le site charge les annonces via JavaScript. "
            f"Les données ne sont pas disponibles en HTML statique. "
            f"Envisagez d'utiliser Playwright ou de contacter Spoticar pour un flux API."
        )

        # Tentative : certaines pages de détail sont indexées et accessibles
        search_url = f"{self.base_url}/voitures-occasion?page={page}"
        try:
            response = self.session.get(search_url, delay=2)
            if response.status_code != 200:
                return []
            soup = self._make_soup(response.text)

            urls = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                # Les fiches véhicule individuelles sur Spoticar
                if "/voitures-occasion/" in href and href.count("/") >= 3:
                    full_url = self._absolute_url(href)
                    # Exclure les pages de catégorie (berline, citadine, etc.)
                    if full_url.count("/") > 4:
                        urls.append(full_url)

            return list(dict.fromkeys(urls))
        except Exception as e:
            print(f"[spoticar] Erreur get_listing_urls: {e}")
            return []

    def parse_listing(self, html: str, url: str) -> dict:
        soup = self._make_soup(html)

        titre = self._extract_text(soup, ["h1", ".vehicle-title", "[class*=title]"], "")
        prix = self._extract_text(soup, ["[class*=price]", "[class*=prix]"], "")
        description = self._extract_text(soup, [
            "[class*=description]",
            ".vehicle-description",
            ".content p",
        ], "")

        photos = self._extract_images(soup, [
            "img[src*=spoticar]",
            "img[src*=psa]",
            "img[src*=stellantis]",
        ])

        return self._build_raw_listing(
            titre=titre,
            prix=prix,
            description=description,
            photos=photos,
            vendeur_info={"type": "professionnel_certifie"},
            date_pub=None,
            url=url,
            certifie=True,  # Spoticar = véhicules certifiés Stellantis
        )
