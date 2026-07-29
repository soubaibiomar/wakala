import requests
from apps.api.config import OLLAMA_URL, LLM_MODEL

def generate_explanation(persona_id: str, hard_filters: dict, soft_features: list[str], car_details: dict) -> str:
    """
    Génère une justification via Qwen 2.5 Coder, en injectant uniquement des valeurs déjà calculées.
    Ne permet aucune hallucination de chiffres.
    """
    filters_str = ", ".join([f"{k}={v}" for k, v in hard_filters.items()])
    softs_str = ", ".join(soft_features)
    
    prompt = f"""
    Tu es l'assistant IA de la marketplace automobile Wakala.
    Justifie la recommandation suivante pour un utilisateur avec le persona '{persona_id}'.
    Ne donne AUCUNE autre information technique. Ne crée aucun faux chiffre. Base-toi uniquement sur les faits fournis.
    
    Faits:
    - Véhicule recommandé: {car_details.get('titre')}
    - Contraintes dures respectées par le véhicule: {filters_str}
    - Critères doux matchés: {softs_str}
    
    Rédige une justification de 2 phrases maximum, directement adressée à l'utilisateur.
    """
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": LLM_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"Recommandée car elle correspond à votre recherche (Erreur IA: {str(e)})"
