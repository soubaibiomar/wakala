"""
Déduplication Inter-Plateformes
Fusionne les doublons cross-site en gardant une seule entrée avec sources_multiples.
Un doublon = même marque + modèle + année + ville + prix (±2%).
"""
import logging
from typing import List

logger = logging.getLogger(__name__)


def generate_dedup_key(listing: dict) -> str:
    """Génère une clé de déduplication basée sur marque, modèle, année, ville."""
    marque = str(listing.get("marque", listing.get("marque_brute", ""))).lower().strip()
    modele = str(listing.get("modele", listing.get("modele_brut", ""))).lower().strip()
    annee = str(listing.get("annee", listing.get("annee_brute", "")))
    ville = str(listing.get("ville", listing.get("ville_brute", "inconnue"))).lower().strip()

    return f"{marque}_{modele}_{annee}_{ville}"


def extract_price(listing: dict) -> float:
    """Extrait le prix numérique d'un listing (normalisé ou brut)."""
    # Try normalized price first
    prix = listing.get("prix_mad", 0)
    if isinstance(prix, (int, float)) and prix > 0:
        return float(prix)

    # Fallback to raw price string
    prix_str = str(listing.get("prix_brut", ""))
    digits = "".join(c for c in prix_str if c.isdigit())
    return float(digits) if digits else 0.0


def deduplicate_listings(listings: List[dict]) -> List[dict]:
    """
    Fusionne les doublons inter-plateformes.

    Un doublon est défini par:
    - Même clé de déduplication (marque + modèle + année + ville)
    - Prix à ±2% l'un de l'autre

    Signal de fiabilité : une annonce présente sur plusieurs plateformes
    avec un prix cohérent est un signal positif.

    Returns:
        Liste des annonces uniques avec sources_multiples renseigné
    """
    dedup_map: dict[str, list] = {}
    total_merged = 0

    for item in listings:
        key = generate_dedup_key(item)
        price = extract_price(item)

        if key not in dedup_map:
            dedup_map[key] = []

        # Check if this is a duplicate of an existing entry
        merged = False
        for existing in dedup_map[key]:
            existing_price = extract_price(existing)

            # Both prices must be > 0 to compare
            if existing_price > 0 and price > 0:
                diff_percent = abs(existing_price - price) / existing_price
                if diff_percent <= 0.02:  # ±2% tolerance
                    # MERGE: keep existing, add source info
                    if "sources_multiples" not in existing:
                        existing["sources_multiples"] = [existing.get("source_plateforme")]

                    new_source = item.get("source_plateforme")
                    if new_source not in existing["sources_multiples"]:
                        existing["sources_multiples"].append(new_source)

                    # Keep track of all source URLs
                    if "urls_multiples" not in existing:
                        existing["urls_multiples"] = [existing.get("url_source")]
                    if item.get("url_source") not in existing["urls_multiples"]:
                        existing["urls_multiples"].append(item.get("url_source"))

                    # Keep the one with more photos
                    existing_photos = len(existing.get("photos_urls", []))
                    new_photos = len(item.get("photos_urls", []))
                    if new_photos > existing_photos:
                        existing["photos_urls"] = item.get("photos_urls", [])

                    # If either is certified, mark as certified
                    if item.get("certifie", False):
                        existing["certifie"] = True

                    merged = True
                    total_merged += 1
                    break

        if not merged:
            dedup_map[key].append(item)

    # Flatten
    unique_listings = []
    for items in dedup_map.values():
        unique_listings.extend(items)

    logger.info(
        f"Déduplication: {len(listings)} entrées → {len(unique_listings)} uniques "
        f"({total_merged} doublons fusionnés)"
    )

    return unique_listings
