"""
Wandaloo.com – Catalogue Neuf
Structure HTML inspectée le 29/07/2026 :
  - URL : /neuf/prix-voiture-neuve-maroc.html (117 entrées trouvées)
  - Conteneur par modèle : div.col-sm-9.post-content
  - Marque + Modèle : h3.titre > a (ex: "CITROEN AMI")
  - Prix catalogue : p.prix (ex: "90.900 <sup>DH</sup>")
  - Détails : ul.detail > li (Carburant, CV, Chevaux)
  - Lien fiche complète : a.btn.gris-blanc (href = /neuf/{marque}/{modele}/)
  - Image : dans la page détail du modèle, pas dans la liste

Ce scraper parse la page catalogue directement : chaque entrée est un modèle
avec son prix de départ, pas une annonce individuelle.
"""
from scrapers.base_scraper import BaseScraper
import re


class WandalooNeufScraper(BaseScraper):
    platform_name = "wandaloo"
    listing_type = "neuf"
    base_url = "https://www.wandaloo.com"

    def get_listing_urls(self, page: int) -> list[str]:
        """
        La page /neuf/prix-voiture-neuve-maroc.html contient TOUTES les entrées
        (pas de pagination). On retourne les liens vers les fiches modèle.
        """
        if page > 1:
            return []  # Pas de pagination, tout est sur la page 1

        catalog_url = f"{self.base_url}/neuf/prix-voiture-neuve-maroc.html"
        try:
            response = self.session.get(catalog_url, delay=4)
            if response.status_code != 200:
                return []
            soup = self._make_soup(response.text)

            urls = []
            # Liens vers les fiches modèle : a.btn.gris-blanc ou h3.titre > a
            for a in soup.select("h3.titre a, a.btn.gris-blanc"):
                href = a.get("href", "")
                if "/neuf/" in href:
                    urls.append(self._absolute_url(href))

            return list(dict.fromkeys(urls))
        except Exception as e:
            print(f"[wandaloo_neuf] Erreur get_listing_urls: {e}")
            return []

    def parse_listing(self, html: str, url: str) -> dict:
        """
        Parse la fiche d'un modèle neuf sur Wandaloo.
        Si le HTML provient de la page catalogue, on parse le bloc directement.
        Si c'est la page détail du modèle, on parse h1 + prix.
        """
        soup = self._make_soup(html)

        titre = self._extract_text(soup, ["h1", "h3.titre"], "")
        # Prix : p.prix contient "90.900 <sup>DH</sup>" → on nettoie
        prix_raw = self._extract_text(soup, ["p.prix", ".prix", "[class*=price]"], "")
        # Normaliser le format de prix wandaloo ("90.900 DH" → "90 900 DH")
        prix = re.sub(r"(\d+)\.(\d{3})", r"\1 \2", prix_raw).strip()

        # Détails techniques
        details = []
        for li in soup.select("ul.detail li"):
            details.append(li.text.strip())
        description = " | ".join(details) if details else ""

        # Photos
        photos = self._extract_images(soup, [
            "img[src*=wandaloo]",
            "img[src*=neuf]",
            ".photo img",
        ])

        return self._build_raw_listing(
            titre=titre,
            prix=prix,
            description=description,
            photos=photos,
            vendeur_info={},  # Catalogue constructeur
            date_pub=None,
            url=url,
            certifie=False,
        )
