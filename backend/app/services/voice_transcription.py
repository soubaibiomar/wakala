import logging
from typing import Optional
from fastapi import UploadFile
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

# ─── Modèles ASR Spécialisés Arabe & Darija ──────────────────────────────────
# 1. CohereLabs Arabic Transcribe (HF: CohereLabs/cohere-transcribe-arabic-07-2026)
_COHERE_ARABIC_MODEL = "CohereLabs/cohere-transcribe-arabic-07-2026"
_HF_COHERE_INFERENCE_URL = f"https://api-inference.huggingface.co/models/{_COHERE_ARABIC_MODEL}"
_HF_COHERE_ROUTER_URL = f"https://router.huggingface.co/hf-inference/models/{_COHERE_ARABIC_MODEL}"

# 2. HuBERT Darija Marocain (HF: amineouaki/hubert-darija-combined)
_HUBERT_DARIJA_MODEL = "amineouaki/hubert-darija-combined"
_HF_HUBERT_INFERENCE_URL = f"https://api-inference.huggingface.co/models/{_HUBERT_DARIJA_MODEL}"
_HF_HUBERT_ROUTER_URL = f"https://router.huggingface.co/hf-inference/models/{_HUBERT_DARIJA_MODEL}"

# 3. Whisper Groq Fallback
_WHISPER_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
_TIMEOUT = 12.0

# ─── Dictionnaire de normalisation phonétique Darija automobile ──────────────
DARIJA_AUTO_TERMS = {
    "tomobil": "tomobila",
    "tonobil": "tomobila",
    "tonobila": "tomobila",
    "sayara": "sayara",
    "sayarat": "sayarat",
    "mazout": "mazot",
    "lisance": "lisans",
    "lissans": "lisans",
    "essence": "essence",
    "diwana": "diwana",
    "nqi": "n9iya",
    "nqiha": "n9iya",
    "n9i": "n9iya",
    "rkhiss": "rkhis",
    "rkhissa": "rkhisa",
    "chhal": "chhal",
    "bghit": "bghit",
    "baghi": "baghi",
    "otomatik": "automatique",
    "otomatikia": "automatique",
    "manwel": "manuelle",
}


def normalize_darija_transcript(text: str) -> str:
    """Normalise les termes automobiles Darija transcrits pour fiabiliser le NLP."""
    if not text:
        return ""
    words = text.split()
    normalized = []
    for w in words:
        w_clean = w.lower().strip(".,?!:;")
        replacement = DARIJA_AUTO_TERMS.get(w_clean, w)
        normalized.append(replacement)
    return " ".join(normalized)


def detect_transcription_language(text: str) -> str:
    """Conservative local language detection; no user text is sent to a detector."""
    if not text:
        return "fr"
    if any("\u0600" <= char <= "\u06ff" for char in text):
        lower = text.lower()
        return "darija" if any(term in lower for term in ("شنو", "بغيت", "واش", "عندي", "بزاف")) else "ar"
    lower = text.lower()
    if any(term in lower.split() for term in ("the", "what", "which", "want", "need", "car", "budget")):
        return "en"
    if any(term in lower.split() for term in ("je", "cherche", "voiture", "bonjour", "budget", "merci")):
        return "fr"
    if any(term in lower.split() for term in ("bghit", "baghi", "chhal", "tomobil", "sayara")):
        return "darija"
    return "fr"


def _get_hf_headers(content_type: str = "audio/webm") -> dict:
    """Génère les headers HTTP pour l'Inference API Hugging Face."""
    headers = {"Content-Type": content_type}
    hf_token = getattr(settings, "HF_TOKEN", None) or getattr(settings, "HUGGINGFACE_API_KEY", None)
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
    return headers


async def transcrire_cohere_arabic(audio_bytes: bytes, content_type: str = "audio/webm") -> Optional[str]:
    """
    Transcrit l'audio avec le modèle CohereLabs Arabic Transcribe
    (CohereLabs/cohere-transcribe-arabic-07-2026).
    """
    headers = _get_hf_headers(content_type)

    for url in [_HF_COHERE_ROUTER_URL, _HF_COHERE_INFERENCE_URL]:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.post(url, content=audio_bytes, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "text" in data:
                        text = data["text"].strip()
                        if text:
                            logger.info(f"[Cohere Transcribe Arabic] Transcription réussie: {text}")
                            return normalize_darija_transcript(text)
                    elif isinstance(data, list) and len(data) > 0 and "text" in data[0]:
                        text = data[0]["text"].strip()
                        if text:
                            logger.info(f"[Cohere Transcribe Arabic] Transcription réussie: {text}")
                            return normalize_darija_transcript(text)
                else:
                    logger.debug(f"[Cohere Arabic] Status {response.status_code} sur {url}")
        except Exception as e:
            logger.debug(f"[Cohere Arabic] Erreur sur {url}: {e}")

    return None


async def transcrire_hubert_darija(audio_bytes: bytes, content_type: str = "audio/webm") -> Optional[str]:
    """
    Transcrit l'audio avec le modèle HuBERT Darija (amineouaki/hubert-darija-combined).
    """
    headers = _get_hf_headers(content_type)

    for url in [_HF_HUBERT_ROUTER_URL, _HF_HUBERT_INFERENCE_URL]:
        try:
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                response = await client.post(url, content=audio_bytes, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "text" in data:
                        text = data["text"].strip()
                        if text:
                            logger.info(f"[HuBERT Darija] Transcription réussie: {text}")
                            return normalize_darija_transcript(text)
                    elif isinstance(data, list) and len(data) > 0 and "text" in data[0]:
                        text = data[0]["text"].strip()
                        if text:
                            logger.info(f"[HuBERT Darija] Transcription réussie: {text}")
                            return normalize_darija_transcript(text)
                else:
                    logger.debug(f"[HuBERT Darija] Status {response.status_code} sur {url}")
        except Exception as e:
            logger.debug(f"[HuBERT Darija] Erreur sur {url}: {e}")

    return None


async def transcrire_whisper(audio_bytes: bytes, filename: str = "audio.webm", content_type: str = "audio/webm") -> str:
    """
    Transcrit l'audio via l'API Whisper de Groq (fallback ultra-rapide).
    """
    api_key = getattr(settings, "groq_api_key", None) or getattr(settings, "GROQ_API_KEY", None)
    if not api_key:
        logger.error("GROQ_API_KEY non configurée pour Whisper")
        return "ERROR: Aucune clé de transcription vocale disponible."

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "whisper-large-v3-turbo",
        "response_format": "text"
    }

    files = {
        "file": (filename, audio_bytes, content_type)
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            response = await client.post(
                _WHISPER_API_URL,
                data=data,
                files=files,
                headers=headers
            )
            response.raise_for_status()
            transcription = response.text.strip()
            return normalize_darija_transcript(transcription)

    except Exception as e:
        error_detail = ""
        if hasattr(e, "response") and e.response is not None:
            error_detail = f"Status {e.response.status_code}: {e.response.text}"
        logger.error(f"Erreur lors de la transcription Whisper: {e} | {error_detail}")
        return f"ERROR: {e} | {error_detail}"


async def transcrire_audio(fichier_audio: UploadFile) -> str:
    """
    Pipeline de transcription vocale multi-modèles :
    1. CohereLabs Arabic Transcribe (`CohereLabs/cohere-transcribe-arabic-07-2026`)
    2. HuBERT Darija spécialisé (`amineouaki/hubert-darija-combined`)
    3. Whisper Groq (`whisper-large-v3-turbo`) en fallback
    """
    # Hard cap the bytes read even when the multipart parser did not provide a size.
    audio_bytes = await fichier_audio.read(10 * 1024 * 1024 + 1)
    if len(audio_bytes) > 10 * 1024 * 1024:
        return "ERROR: audio file exceeds the 10MB limit"
    filename = fichier_audio.filename or "audio.webm"
    content_type = fichier_audio.content_type or "audio/webm"

    # 1. CohereLabs Arabic Transcribe (07-2026)
    cohere_result = await transcrire_cohere_arabic(audio_bytes, content_type=content_type)
    if cohere_result:
        return cohere_result

    # 2. HuBERT Darija (Amine Ouaki)
    hubert_result = await transcrire_hubert_darija(audio_bytes, content_type=content_type)
    if hubert_result:
        return hubert_result

    # 3. Whisper Groq Fallback
    return await transcrire_whisper(audio_bytes, filename=filename, content_type=content_type)
