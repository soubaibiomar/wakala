import json
import logging
import re

import httpx

from app.core.config import settings
from app.ml.nlp_pipeline.schemas import ExtractedCriteria
from app.ml.nlp_pipeline.budget_validator import normalize_and_validate_budget

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """Tu es un extracteur NLP multilingue pour Wakala, une plateforme de vente automobile au Maroc.

MISSION : À partir d'une phrase utilisateur (Français, Anglais, Arabe standard, Darija en alphabet arabe, ou Darija en alphabet latin/arabizi, ou un mélange), extrais les critères de recherche automobile.

RÈGLES STRICTES :
1. Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ni après.
2. N'ajoute JAMAIS de commentaires.
3. Détecte la langue principale ("fr", "ar", "darija", ou "en").
4. Évalue ta "confiance" ("haute", "moyenne", "basse"). "basse" signifie que tu as dû deviner (phrase vague, mélange ambigu, ou budget/usage manquant).

Utilise EXACTEMENT cette structure JSON :
{
  "budget": <nombre en MAD ou null>,
  "usage": <string ou null>,
  "priorites": <liste de strings>,
  "profil_passagers": <string ou null>,
  "langue_detectee": <"fr" | "ar" | "darija" | "en">,
  "confiance": <"haute" | "moyenne" | "basse">
}

EXEMPLES FEW-SHOT :
- User: "Bghit chi tomobila sghira dyal mdina b 10 malyoun"
  JSON: {"budget": 100000, "usage": "urbain", "priorites": ["économique"], "profil_passagers": null, "langue_detectee": "darija", "confiance": "haute"}

- User: "بغيت طوموبيل عائلية ما تفوتش 15 مليون"
  JSON: {"budget": 150000, "usage": "familial", "priorites": [], "profil_passagers": "famille", "langue_detectee": "darija", "confiance": "haute"}

- User: "I am looking for a reliable SUV for my family, around 300k"
  JSON: {"budget": 300000, "usage": "familial", "priorites": ["fiabilité", "espace"], "profil_passagers": "famille", "langue_detectee": "en", "confiance": "haute"}

- User: "Je cherche une voiture"
  JSON: {"budget": null, "usage": null, "priorites": [], "profil_passagers": null, "langue_detectee": "fr", "confiance": "basse"}

- User: "Ana ma3endich budget kbir, bghit tomobila mzyana"
  JSON: {"budget": null, "usage": null, "priorites": ["économique", "fiabilité"], "profil_passagers": null, "langue_detectee": "darija", "confiance": "basse"}
"""

_CLARIFICATION_PROMPT = """Tu es un assistant virtuel amical pour Wakala (plateforme automobile au Maroc).
L'utilisateur a fourni une requête vague. Ta mission est de poser UNE SEULE question courte et naturelle pour obtenir l'information critique manquante.
Pose la question DANS LA MÊME LANGUE que celle de l'utilisateur (français, anglais, arabe standard, ou darija/arabizi).
Ne dis pas "je n'ai pas compris" ou "il manque des informations". Demande directement l'information d'un ton amical.
Priorité des informations manquantes : {missing_field}.
Requête initiale : {texte}
Langue détectée : {langue}

Réponds UNIQUEMENT avec la question, sans guillemets, sans rien d'autre.
"""

_GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
_TIMEOUT = 5.0

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
        "max_tokens": 200,
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
            budget = normalize_and_validate_budget(parsed.get("budget"))
            usage = parsed.get("usage") if isinstance(parsed.get("usage"), str) else None
            priorites = [p for p in parsed.get("priorites", []) if isinstance(p, str)]
            profil = parsed.get("profil_passagers") if isinstance(parsed.get("profil_passagers"), str) else None
            langue = parsed.get("langue_detectee", "fr")
            confiance = parsed.get("confiance", "haute")
            
            criteria = ExtractedCriteria(
                budget=budget,
                usage=usage,
                priorites=priorites,
                profil_passagers=profil,
                langue_detectee=langue,
                confiance=confiance,
                erreur=False
            )
            
            # Boucle de clarification si la confiance est basse
            if confiance == "basse":
                question = await generer_clarification(texte, criteria, api_key)
                criteria.statut = "clarification_requise"
                criteria.question = question
                
            return criteria
            
    except Exception as e:
        logger.warning(f"Groq API error or timeout in NLP extraction, using fallback: {e}")
        return _fallback_extraction(texte)

async def generer_clarification(texte: str, criteria: ExtractedCriteria, api_key: str) -> str:
    """Génère une question de clarification dans la langue d'origine."""
    
    # Déterminer le champ prioritaire manquant
    missing_field = "le budget (combien ils veulent dépenser)"
    if criteria.budget is not None:
        missing_field = "l'usage principal (ville, famille, trajet long...)"
    
    prompt = _CLARIFICATION_PROMPT.format(
        missing_field=missing_field,
        texte=texte,
        langue=criteria.langue_detectee or "darija"
    )
    
    payload = {
        "model": getattr(settings, "GROQ_MODEL", "llama3-8b-8192"),
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 100,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            res = await client.post(_GROQ_CHAT_URL, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"].strip().strip('"')
    except Exception as e:
        logger.warning(f"Error generating clarification question: {e}")
        return "Pourriez-vous préciser votre budget ou l'usage prévu pour le véhicule ?"

def _fallback_extraction(texte: str) -> ExtractedCriteria:
    """Extraction basique par regex si le LLM échoue ou timeout."""
    budget = None
    
    text_lower = texte.lower()
    validated = normalize_and_validate_budget(text_lower)
    if validated:
        budget = validated
            
    usage = None
    priorites = []
    
    if "famille" in text_lower or "familial" in text_lower or "3aila" in text_lower:
        usage = "familial"
    elif "ville" in text_lower or "urbain" in text_lower or "mdina" in text_lower:
        usage = "urbain"
        
    if "eco" in text_lower or "économique" in text_lower or "rkhis" in text_lower:
        priorites.append("économique")
    if "fiable" in text_lower or "fiabilité" in text_lower or "mzyan" in text_lower:
        priorites.append("fiabilité")
        
    return ExtractedCriteria(
        budget=budget,
        usage=usage,
        priorites=priorites,
        profil_passagers="famille" if usage == "familial" else None,
        confiance="moyenne",
        langue_detectee="fr",
        erreur=False
    )
