import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from app.core.limiter import limiter
from app.services.voice_transcription import transcrire_audio

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/transcribe")
@limiter.limit("30/minute")
async def transcribe_voice(request: Request, audio: UploadFile = File(...)):
    """
    Pipeline de transcription vocale multi-modèles spécialisé (Maroc / Darija / Arabe / Français) :
    1. CohereLabs Arabic Transcribe (CohereLabs/cohere-transcribe-arabic-07-2026)
    2. HuBERT Darija spécialisé (amineouaki/hubert-darija-combined)
    3. Whisper Groq / Fallback
    """
    if not audio or not audio.filename:
        raise HTTPException(status_code=400, detail="Aucun fichier audio fourni.")

    try:
        text = await transcrire_audio(audio)
        if text.startswith("ERROR:"):
            logger.error(f"[Voice API] Erreur interne de transcription: {text}")
            raise HTTPException(status_code=500, detail="Échec de la transcription vocale.")

        logger.info(f"[Voice API] Transcription réussie: '{text}'")
        return {"text": text}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Voice API] Erreur inattendue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement audio: {str(e)}")
