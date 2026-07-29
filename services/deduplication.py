def generate_dedup_key(listing: dict) -> str:
    """Génère une clé de déduplication basée sur la marque, le modèle, l'année et la ville."""
    marque = listing.get("marque", "").lower().strip()
    modele = listing.get("modele", "").lower().strip()
    annee = str(listing.get("annee", ""))
    
    # On gère l'extraction basique de la ville (qui peut être dans vendeur_info ou ailleurs)
    vendeur = listing.get("vendeur_info", {})
    ville = vendeur.get("ville", "inconnue").lower().strip()
    
    return f"{marque}_{modele}_{annee}_{ville}"

def extract_price(prix_str: str) -> float:
    """Extrait le prix numérique d'une chaîne brute (ex: '80 000 DH' -> 80000.0)."""
    if not prix_str:
        return 0.0
    digits = ''.join(c for c in prix_str if c.isdigit())
    return float(digits) if digits else 0.0

def deduplicate_listings(listings: list[dict]) -> list[dict]:
    """
    Fusionne les doublons.
    Un doublon est défini par: même marque, modèle, année, ville ET un prix à ±2%.
    """
    dedup_map = {}
    
    for item in listings:
        key = generate_dedup_key(item)
        price = extract_price(item.get("prix_brut", ""))
        
        if key not in dedup_map:
            dedup_map[key] = []
            
        # Chercher si un véhicule existant dans cette clé a un prix à +-2%
        merged = False
        for existing in dedup_map[key]:
            existing_price = extract_price(existing.get("prix_brut", ""))
            
            # Si les deux prix sont > 0, on vérifie la marge de 2%
            if existing_price > 0 and price > 0:
                diff_percent = abs(existing_price - price) / existing_price
                if diff_percent <= 0.02:
                    # C'est un doublon, on fusionne
                    if "sources_multiples" not in existing:
                        existing["sources_multiples"] = [existing.get("source_plateforme")]
                    
                    if item.get("source_plateforme") not in existing["sources_multiples"]:
                        existing["sources_multiples"].append(item.get("source_plateforme"))
                    
                    # On garde aussi les URLs multiples
                    if "urls_multiples" not in existing:
                        existing["urls_multiples"] = [existing.get("url_source")]
                    if item.get("url_source") not in existing["urls_multiples"]:
                        existing["urls_multiples"].append(item.get("url_source"))
                        
                    merged = True
                    break
        
        if not merged:
            # Nouveau véhicule
            dedup_map[key].append(item)
            
    # Aplatir la map en une liste unique
    unique_listings = []
    for items in dedup_map.values():
        unique_listings.extend(items)
        
    return unique_listings
