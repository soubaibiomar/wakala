import json
import logging
import re

import httpx

from app.core.config import settings
from app.ml.nlp_pipeline.schemas import ExtractedCriteria
from app.ml.nlp_pipeline.budget_validator import normalize_and_validate_budget
from app.ml.nlp_pipeline.language_hints import analyze_language_hints

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """Tu es un extracteur NLP multilingue pour Wakala, une plateforme de vente automobile au Maroc.

MISSION : À partir d'une phrase utilisateur (Français, Anglais, Arabe standard, Darija en alphabet arabe, ou Darija en alphabet latin/arabizi, ou un mélange), extrais les critères de recherche automobile.

RÈGLES STRICTES :
1. Réponds UNIQUEMENT avec un objet JSON valide, sans texte avant ni après.
2. N'ajoute JAMAIS de commentaires.
3. Détecte la langue principale ou le mélange ("fr", "ar", "darija", ou "en"). Si c'est un mélange, mets melange_langues à true, et place les deux langues dans langues_presentes.
4. "confiance_langue" évalue ta certitude sur la détection des langues ("haute", "moyenne", "basse"). "confiance_extraction" évalue la certitude sur les critères budget/usage ("haute", "moyenne", "basse" si vague ou manquant).

NOTE SUR L'INDICE PRÉ-FILTRE : Tu recevras un "Indice pré-filtre" calculé par un algorithme. Sers-toi en pour t'aider (notamment pour l'Arabizi/Darija), mais prends la décision finale. Exemple: une phrase 100% française contenant juste un nom propre arabe ("Renault") ne doit pas devenir "darija" juste parce que l'indice s'est trompé.

Utilise EXACTEMENT cette structure JSON :
{
  "budget": <nombre en MAD ou null>,
  "usage_prevu": <"familial" | "urbain" | "longue_distance" | "professionnel" | "loisir" | null>,
  "priorites": <liste de strings>,
  "profil_passagers": <string ou null>,
  "langue_principale": <"fr" | "ar" | "darija" | "en">,
  "langues_presentes": <liste de "fr", "ar", "darija", "en">,
  "melange_langues": <true | false>,
  "confiance_langue": <"haute" | "moyenne" | "basse">,
  "confiance_extraction": <"haute" | "moyenne" | "basse">
}

EXEMPLES FEW-SHOT :
- User: [Indice: darija_probable_latin] "Bghit chi tomobila sghira dyal mdina b 10 malyoun"
  JSON: {"budget": 100000, "usage_prevu": "urbain", "priorites": ["économique"], "profil_passagers": null, "langue_principale": "darija", "langues_presentes": ["darija"], "melange_langues": false, "confiance_langue": "haute", "confiance_extraction": "haute"}

- User: [Indice: darija_probable_arabe] "بغيت طوموبيل عائلية ما تفوتش 15 مليون"
  JSON: {"budget": 150000, "usage_prevu": "familial", "priorites": [], "profil_passagers": "famille", "langue_principale": "darija", "langues_presentes": ["darija"], "melange_langues": false, "confiance_langue": "haute", "confiance_extraction": "haute"}

- User: [Indice: langue_etrangere_probable_ou_francais] "Je cherche une voiture"
  JSON: {"budget": null, "usage_prevu": null, "priorites": [], "profil_passagers": null, "langue_principale": "fr", "langues_presentes": ["fr"], "melange_langues": false, "confiance_langue": "haute", "confiance_extraction": "basse"}

- User: [Indice: darija_probable_latin] "salam, bghit voiture pas chere pour la ville"
  JSON: {"budget": null, "usage_prevu": "urbain", "priorites": ["économique"], "profil_passagers": null, "langue_principale": "darija", "langues_presentes": ["darija", "fr"], "melange_langues": true, "confiance_langue": "haute", "confiance_extraction": "basse"}
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

    indice_langue = analyze_language_hints(texte)
    user_prompt = f"[Indice: {indice_langue}] \"{texte.strip()}\""

    payload = {
        "model": getattr(settings, "GROQ_MODEL", "llama3-8b-8192"),
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
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
            usage_prevu = parsed.get("usage_prevu") if isinstance(parsed.get("usage_prevu"), str) else None
            priorites = [p for p in parsed.get("priorites", []) if isinstance(p, str)]
            profil = parsed.get("profil_passagers") if isinstance(parsed.get("profil_passagers"), str) else None
            
            langue_principale = parsed.get("langue_principale", "fr")
            langues_presentes = parsed.get("langues_presentes", ["fr"])
            melange_langues = parsed.get("melange_langues", False)
            confiance_langue = parsed.get("confiance_langue", "haute")
            confiance_extraction = parsed.get("confiance_extraction", "haute")
            
            criteria = ExtractedCriteria(
                budget=budget,
                usage_prevu=usage_prevu,
                priorites=priorites,
                profil_passagers=profil,
                langue_principale=langue_principale,
                langues_presentes=langues_presentes,
                melange_langues=melange_langues,
                confiance_langue=confiance_langue,
                confiance_extraction=confiance_extraction,
                erreur=False
            )
            
            # Boucle de clarification si la confiance est basse
            if confiance_extraction == "basse":
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
        langue=criteria.langue_principale or "darija"
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
            
    usage_prevu = None
    priorites = []
    
    if any(w in text_lower for w in ["famille", "familial", "3aila", "family", "kids", "wlad"]):
        usage_prevu = "familial"
    elif any(w in text_lower for w in ["ville", "urbain", "mdina", "commute", "daily", "work", "khdma", "everyday"]):
        usage_prevu = "urbain"
        
    if any(w in text_lower for w in ["eco", "économique", "rkhis", "rkhisa", "cheap", "ma3ndich", "flous", "flouss", "low budget"]):
        priorites.append("économique")
    if any(w in text_lower for w in ["fiable", "fiabilité", "mzyan", "mzyana", "sah", "3amal", "reliable", "sturdy"]):
        priorites.append("fiabilité")
        
    langue = "fr"
    langue = "fr"
    if any(char in texte for char in "أبتثجحخدذرزسشصضطظعغفقكلمنهوي"):
        langue = "ar"
    elif any(w in text_lower for w in ["bghit", "dyal", "mdina", "tomobila", "ma3ndich", "flous", "rkhis", "mzyan"]):
        langue = "darija"
    elif any(w in text_lower for w in ["car", "looking", "budget", "need", "cheap"]):
        if any(w in text_lower for w in ["is", "my", "for"]):
            langue = "en"
        
    return ExtractedCriteria(
        budget=budget,
        usage_prevu=usage_prevu,
        priorites=priorites,
        profil_passagers="famille" if usage_prevu == "familial" else None,
        confiance_langue="moyenne",
        confiance_extraction="moyenne",
        langue_principale=langue,
        langues_presentes=[langue],
        melange_langues=False,
        erreur=False
    )
