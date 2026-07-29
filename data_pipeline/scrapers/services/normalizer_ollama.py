"""
Normalisation Ollama — Différenciée neuf / occasion / certifié
Passe les RawListing bruts à Ollama pour extraction structurée et enrichissement.
"""
import json
import os
import logging
import requests

logger = logging.getLogger(__name__)

# Configuration Ollama (utilise les mêmes variables que le Docker compose)
OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/v1").rstrip("/")
LLM_MODEL = os.environ.get("OLLAMA_MODEL_TEXT", "qwen3:8b")


def normalize_listing(raw: dict) -> dict:
    """
    Passe le dictionnaire brut de l'annonce à Ollama pour normalisation.
    Gère la différence entre annonce 'neuf', 'occasion' et 'occasion certifiée'.

    Args:
        raw: Dictionnaire brut (RawListing.model_dump())

    Returns:
        Dictionnaire enrichi avec les champs normalisés par Ollama
    """
    type_annonce = raw.get("type_annonce", "occasion")
    certifie = raw.get("certifie", False)

    # ── Construction du prompt selon le type ──────────────────

    if type_annonce == "neuf":
        # ANNONCE CATALOGUE CONSTRUCTEUR
        # Pas de vendeur individuel → pas de signaux_suspects
        # Le prix est un prix catalogue, pas un prix négocié
        prompt_instruction = """
Tu analyses une annonce de voiture NEUVE provenant d'un catalogue concessionnaire.

INSTRUCTIONS SPÉCIFIQUES POUR LE NEUF :
- Extrais : marque, modele, annee, carburant, transmission, prix_catalogue_mad.
- Identifie les "promotions_detectees" : remise affichée, crédit gratuit, offre de reprise,
  bonus écologique, pack d'options offert, etc.
- NE GÉNÈRE AUCUN "signaux_suspects". Il n'y a pas de fraude vendeur individuelle ici.
  C'est une fiche technique officielle de concessionnaire.
- Le prix est un prix catalogue officiel — n'applique PAS la logique "prix suspect vs marché".
"""
    elif certifie:
        # OCCASION CERTIFIÉE (Kifal Auto 200 points, Spoticar Stellantis)
        prompt_instruction = """
Tu analyses une annonce de voiture d'OCCASION CERTIFIÉE (inspection professionnelle).

INSTRUCTIONS SPÉCIFIQUES POUR L'OCCASION CERTIFIÉE :
- Extrais : marque, modele, annee, carburant, transmission, kilometrage, prix_mad.
- Identifie les "signaux_suspects" classiques (incohérence km/année, prix anormal).
- Note la certification dans "certification_info" : type de contrôle, garantie incluse.
- Les véhicules certifiés ont un niveau de confiance de base plus élevé.
"""
    else:
        # OCCASION STANDARD (particulier ou pro)
        prompt_instruction = """
Tu analyses une annonce de voiture d'OCCASION (particulier ou professionnel).

INSTRUCTIONS SPÉCIFIQUES POUR L'OCCASION :
- Extrais : marque, modele, annee, carburant, transmission, kilometrage, prix_mad, ville.
- Identifie les "signaux_suspects" liés à la fraude :
  * Prix trop bas par rapport au marché marocain
  * Mention "urgent", "prix fixe", "pas de négociation"
  * Description vague ou copiée-collée
  * Incohérence entre kilométrage et année
- Ne génère pas de "promotions_detectees".
"""

    prompt = f"""Tu es le normalisateur IA de la marketplace Wakala (marché automobile marocain).
{prompt_instruction}

Annonce Brute :
{json.dumps(raw, ensure_ascii=False, indent=2)}

Réponds UNIQUEMENT avec un JSON valide. Exemple de structure attendue :
{{
  "marque": "Peugeot",
  "modele": "208",
  "annee": 2024,
  "carburant": "essence",
  "transmission": "automatique",
  "kilometrage": 45000,
  "prix_mad": 180000,
  "ville": "Casablanca",
  "signaux_suspects": [],
  "promotions_detectees": [],
  "certification_info": null
}}
"""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=30,
        )
        response.raise_for_status()
        text_response = response.json().get("response", "")
        normalized_data = json.loads(text_response)

        # Fusionner avec les données brutes
        result = raw.copy()
        result.update(normalized_data)
        return result

    except Exception as e:
        logger.warning(f"Ollama normalization failed for {raw.get('url_source', '?')}: {e}")
        # Fallback : retourner les données brutes avec extraction basique
        return _fallback_normalize(raw)


def _fallback_normalize(raw: dict) -> dict:
    """
    Normalisation de secours sans Ollama.
    Utilise les champs bruts déjà extraits par le scraper.
    """
    result = raw.copy()
    result["marque"] = raw.get("marque_brute", "").strip() or "Inconnu"
    result["modele"] = raw.get("modele_brut", "").strip() or "Inconnu"

    # Année
    annee_str = raw.get("annee_brute", "")
    try:
        result["annee"] = int(annee_str) if annee_str and annee_str.isdigit() else 2025
    except ValueError:
        result["annee"] = 2025

    # Prix
    prix_str = raw.get("prix_brut", "")
    digits = "".join(c for c in prix_str if c.isdigit())
    result["prix_mad"] = int(digits) if digits else 0

    result["carburant"] = raw.get("carburant_brut", "")
    result["transmission"] = raw.get("transmission_brute", "")
    result["ville"] = raw.get("ville_brute", "Maroc")
    result["signaux_suspects"] = []
    result["promotions_detectees"] = []

    return result
