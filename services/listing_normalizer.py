"""
services/listing_normalizer.py
Normalisation des annonces brutes via Ollama (LLM local).

DISTINCTION NEUF vs OCCASION :
  - OCCASION : Extraire marque/modèle/année + détecter les signaux_suspects
    (prix trop bas, description vague, "urgent", etc.) pour alimenter le moteur
    de recommandation. Le prix est un prix négocié/affiché par un particulier.
  - NEUF : Extraire marque/modèle/année + détecter les promotions_detectees
    (remise, crédit gratuit, offre de reprise). NE PAS générer de signaux_suspects
    car il n'y a pas de vendeur individuel — c'est un catalogue constructeur.
    Le prix est un prix catalogue officiel.
"""
import json
import logging
import requests

logger = logging.getLogger("wakala.normalizer")

# Configuration Ollama
OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "qwen2.5-coder"


# ── Prompts systèmes distincts pour neuf et occasion ───────────

SYSTEM_PROMPT_OCCASION = """Tu es le normalisateur IA de Wakala, marketplace automobile marocaine.
Tu analyses une annonce de voiture d'OCCASION publiée par un particulier ou un professionnel.

CONSIGNE :
1. Extrais : marque, modele, annee (entier), carburant, boite_vitesse, kilometrage (entier ou null).
2. Identifie les "signaux_suspects" : un tableau de chaînes décrivant des indices potentiels
   de problème (ex: "prix très bas par rapport au marché", "description vague",
   "mot urgent détecté", "photo générique/stock"). Tableau vide si rien de suspect.
3. NE génère PAS de "promotions_detectees" — ce champ n'existe pas pour l'occasion.

Réponds UNIQUEMENT avec un JSON valide. Aucun texte avant ou après."""

SYSTEM_PROMPT_NEUF = """Tu es le normalisateur IA de Wakala, marketplace automobile marocaine.
Tu analyses une fiche de voiture NEUVE issue d'un catalogue concessionnaire/constructeur.

CONSIGNE :
1. Extrais : marque, modele, annee (entier), carburant, boite_vitesse.
   Le kilometrage est toujours 0 pour du neuf (ne pas le mettre).
2. Identifie les "promotions_detectees" : un tableau de chaînes décrivant les offres
   commerciales (ex: "remise de 10 000 DH", "crédit 0%", "offre de reprise",
   "pack options offert"). Tableau vide si aucune promotion.
3. NE génère AUCUN "signaux_suspects" — il n'y a pas de fraude vendeur individuel ici.
   Le prix est un prix catalogue officiel, pas un prix négocié.

Réponds UNIQUEMENT avec un JSON valide. Aucun texte avant ou après."""


def normalize_listing(raw_listing: dict) -> dict:
    """
    Passe le dictionnaire brut de l'annonce à Ollama pour normalisation.
    Gère la différence entre annonce 'neuf' et 'occasion' via deux prompts
    systèmes distincts, pour éviter que le LLM n'invente des signaux suspects
    sur une fiche constructeur.

    Args:
        raw_listing: dict conforme au schéma brut de BaseScraper.parse_listing()

    Returns:
        dict enrichi avec les champs normalisés (marque, modele, annee, etc.)
    """
    type_annonce = raw_listing.get("type_annonce", "occasion")

    # Sélection du prompt système selon le type
    if type_annonce == "neuf":
        system_prompt = SYSTEM_PROMPT_NEUF
    else:
        system_prompt = SYSTEM_PROMPT_OCCASION

    # Construction du prompt utilisateur
    user_prompt = f"""Annonce brute à normaliser :
{json.dumps(raw_listing, ensure_ascii=False, indent=2)}

Réponds avec un JSON valide contenant les champs extraits."""

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "system": system_prompt,
                "prompt": user_prompt,
                "stream": False,
                "format": "json",
            },
            timeout=30,
        )
        response.raise_for_status()

        text_response = response.json().get("response", "")
        normalized_data = json.loads(text_response)

        # Fusionner avec les données de base (les champs normalisés écrasent les bruts)
        result = raw_listing.copy()
        result.update(normalized_data)
        return result

    except requests.exceptions.ConnectionError:
        logger.warning(
            "Ollama non disponible (localhost:11434). "
            "Retour des données brutes sans normalisation."
        )
        return raw_listing
    except json.JSONDecodeError as e:
        logger.error(f"Réponse Ollama non-JSON: {e}")
        return raw_listing
    except Exception as e:
        logger.error(f"Erreur de normalisation Ollama: {e}")
        return raw_listing
