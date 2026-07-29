import logging
from fastapi import UploadFile
import httpx
from app.core.config import settings
import tempfile
import os

logger = logging.getLogger(__name__)

_WHISPER_API_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
_TIMEOUT = 10.0

async def transcrire_whisper(fichier_audio: UploadFile) -> str:
    """
    Transcrit un fichier audio en texte via l'API Whisper de Groq.
    
    IMPORTANT: Whisper (même whisper-large-v3-turbo) a des limites de fiabilité 
    sur le Darija (dialecte marocain), en particulier avec du code-switching 
    (mélange de français et darija). Il peut parfois halluciner ou translittérer 
    de façon étrange. C'est pourquoi le frontend doit toujours permettre à l'utilisateur 
    de modifier la transcription avant de lancer l'extraction NLP.
    """
    api_key = getattr(settings, "groq_api_key", None) or getattr(settings, "GROQ_API_KEY", None)
    if not api_key:
        logger.error("GROQ_API_KEY non configurée pour Whisper")
        raise ValueError("API Key manquante")
        
    # Read the file content
    content = await fichier_audio.read()
    
    # We need to send it as multipart/form-data
    # httpx expects files as a dictionary where value is (filename, file-object, content-type)
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "whisper-large-v3-turbo",
        "response_format": "text"
    }
    
    files = {
        "file": (fichier_audio.filename or "audio.webm", content, fichier_audio.content_type or "audio/webm")
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
            
            transcription = response.text
            return transcription.strip()
            
    except Exception as e:
        error_detail = ""
        if hasattr(e, "response") and e.response is not None:
            error_detail = f"Status {e.response.status_code}: {e.response.text}"
        logger.error(f"Erreur lors de la transcription Whisper: {e} | {error_detail}")
        return f"ERROR: {e} | {error_detail}"
