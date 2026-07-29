import json
import requests
from apps.api.config import OLLAMA_URL, LLM_MODEL

def extract_constraints(query: str) -> dict:
    """
    Fait appel à Ollama (Qwen 2.5 Coder) pour extraire les hard_filters et soft_features.
    Retourne un dictionnaire strict :
    {"hard_filters": {...}, "soft_features": [...]}
    """
    prompt = f"""
    Tu es un extracteur JSON strict. Analyse la requête suivante et sépare les contraintes dures (qui peuvent être filtrées en SQL) des attributs doux (qui seront vectorisés).
    Requête : "{query}"
    
    Réponds UNIQUEMENT avec un objet JSON valide, sans markdown, sans aucun autre texte, avec cette structure exacte :
    {{"hard_filters": {{"budget_max": entier, "places_min": entier}}, "soft_features": ["mot1", "mot2"]}}
    """
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=10
        )
        response.raise_for_status()
        text_response = response.json().get("response", "")
        
        # S'assure que c'est bien parsable
        data = json.loads(text_response)
        return data
    except Exception as e:
        # En cas d'erreur ou de fallback (pour les tests)
        raise RuntimeError(f"Erreur extraction NLP: {str(e)}")
