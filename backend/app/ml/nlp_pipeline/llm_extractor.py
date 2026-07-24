import json
import logging
import re

import httpx

from app.core.config import settings
from app.ml.nlp_pipeline.schemas import ExtractedCriteria
from app.ml.nlp_pipeline.budget_validator import normalize_and_validate_budget

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """Tu es un extracteur NLP pour une plateforme de vente automobile au Maroc (Wakala).

MISSION : À partir d'une phrase utilisateur en français, darija ou arabizi, extrais les critères de recherche automobile.

RÈGLES STRICTES :
1. Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ni après.
2. N'ajoute JAMAIS de commentaires, d'explications ou de markdown.
3. Utilise EXACTEMENT cette structure :
{
  "budget": <nombre en MAD ou null>,
  "usage": <string ou null>,
  "priorites": <liste de strings>,
  "profil_passagers": <string ou null>
}
"""

_GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
_TIMEOUT = 3.0  # Timeout court imposé par la Partie 2

async def extract_search_criteria(texte: str) -> ExtractedCriteria:
    if not texte or not texte.strip():
        return ExtractedCriteria(erreur=True)

    try:
        api_key = getattr(settings, "groq_api_key", None) or getattr(settings, "GROQ_API_KEY", None)
        if not api_key:
             raise ValueError("GROQ_API_KEY non configurée")
    except ValueError as e:
        logger.error(str(e))
        return _fallback_extraction(texte)

    payload = {
        "model": getattr(settings, "GROQ_MODEL", "llama3-8b-8192"),
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": texte.strip()},
        ],
        "temperature": 0.1,
        "max_tokens": 150,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(_GROQ_CHAT_URL, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            
            # Post-processing
            return ExtractedCriteria(
                budget=normalize_and_validate_budget(parsed.get("budget")),
                usage=parsed.get("usage") if isinstance(parsed.get("usage"), str) else None,
                priorites=[p for p in parsed.get("priorites", []) if isinstance(p, str)],
                profil_passagers=parsed.get("profil_passagers") if isinstance(parsed.get("profil_passagers"), str) else None,
                erreur=False
            )
            
    except Exception as e:
        logger.warning(f"Groq API error or timeout in NLP extraction, using fallback: {e}")
        return _fallback_extraction(texte)

def _fallback_extraction(texte: str) -> ExtractedCriteria:
    """Extraction basique par regex si le LLM échoue ou timeout."""
    budget = None
    
    # Try to extract numbers that could be budgets
    # Match patterns like "200k", "1.5m", or just numbers
    text_lower = texte.lower()
    validated = normalize_and_validate_budget(text_lower)
    if validated:
        budget = validated
            
    # Naive extraction for usage/priority
    usage = None
    priorites = []
    
    if "famille" in text_lower or "familial" in text_lower:
        usage = "familial"
    elif "ville" in text_lower or "urbain" in text_lower:
        usage = "urbain"
        
    if "eco" in text_lower or "économique" in text_lower or "pas cher" in text_lower:
        priorites.append("économique")
    if "fiable" in text_lower or "fiabilité" in text_lower:
        priorites.append("fiabilité")
        
    return ExtractedCriteria(
        budget=budget,
        usage=usage,
        priorites=priorites,
        profil_passagers="famille" if usage == "familial" else None,
        erreur=False
    )
