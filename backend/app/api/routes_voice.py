import base64
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request, Form
from app.core.limiter import limiter
from app.core.security import get_current_user
from app.models.user import User
from app.services.voice_transcription import transcrire_audio, detect_transcription_language
from app.services.voice_synthesis import synthesize_speech, normalize_language
from app.services.ai.chat import chat_stream
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/transcribe")
@limiter.limit("30/minute")
async def transcribe_voice(request: Request, audio: UploadFile = File(...), _user: User = Depends(get_current_user)):
    """
    Pipeline de transcription vocale multi-modèles spécialisé (Maroc / Darija / Arabe / Français) :
    1. CohereLabs Arabic Transcribe (CohereLabs/cohere-transcribe-arabic-07-2026)
    2. HuBERT Darija spécialisé (amineouaki/hubert-darija-combined)
    3. Whisper Groq / Fallback
    """
    if not audio or not audio.filename:
        raise HTTPException(status_code=400, detail="Aucun fichier audio fourni.")

    if not (audio.content_type or "").startswith("audio/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un fichier audio.")
    if audio.size and audio.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Le fichier audio est trop volumineux (maximum 10MB).")

    try:
        text = await transcrire_audio(audio)
        if text.startswith("ERROR:"):
            logger.error(f"[Voice API] Erreur interne de transcription: {text}")
            raise HTTPException(status_code=500, detail="Échec de la transcription vocale.")

        logger.info("[Voice API] Transcription réussie")
        return {"text": text, "language": detect_transcription_language(text)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Voice API] Erreur inattendue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne de traitement audio.")


def _validate_duration(audio_bytes: bytes, filename: str) -> None:
    """Use ffprobe with fixed arguments; generated temp paths are never shell-parsed."""
    suffix = Path(filename).suffix.lower() or ".webm"
    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", temp_path],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        duration = float(result.stdout.strip())
        if duration <= 0 or duration > settings.VOICE_MAX_SECONDS:
            raise HTTPException(status_code=400, detail="L'enregistrement audio est trop long.")
    except FileNotFoundError:
        # Minimal images may not ship ffprobe; byte and provider limits still apply.
        logger.warning("ffprobe unavailable; duration validation is limited to byte size")
    except (ValueError, subprocess.SubprocessError):
        raise HTTPException(status_code=400, detail="Format audio invalide.")
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


def _parse_history(raw_history: str) -> list[dict[str, str]]:
    try:
        value: Any = json.loads(raw_history or "[]")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Historique audio invalide.") from exc
    if not isinstance(value, list) or len(value) > 30:
        raise HTTPException(status_code=400, detail="Historique audio invalide.")
    safe_history: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict) or item.get("role") not in {"user", "assistant"} or not isinstance(item.get("content"), str):
            raise HTTPException(status_code=400, detail="Historique audio invalide.")
        content = item["content"].strip()
        if not content or len(content) > 5000:
            raise HTTPException(status_code=400, detail="Historique audio invalide.")
        safe_history.append({"role": item["role"], "content": content})
    return safe_history


@router.post("/assistant")
@limiter.limit("10/minute")
async def voice_assistant(
    request: Request,
    audio: UploadFile = File(...),
    history_json: str = Form("[]"),
    language: str | None = Form(None),
    _user: User = Depends(get_current_user),
):
    """Secure STT → multilingual chatbot → optional TTS pipeline."""
    if not audio or not audio.filename or not (audio.content_type or "").startswith("audio/"):
        raise HTTPException(status_code=400, detail="Fichier audio invalide.")
    audio_bytes = await audio.read(10 * 1024 * 1024 + 1)
    if not audio_bytes or len(audio_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Le fichier audio est invalide ou trop volumineux.")
    _validate_duration(audio_bytes, audio.filename)
    history = _parse_history(history_json)

    try:
        await audio.seek(0)
        transcript = await transcrire_audio(audio)
        if transcript.startswith("ERROR:") or not transcript.strip():
            raise HTTPException(status_code=502, detail="Échec de la transcription vocale.")
        # Detect every utterance so a user can switch languages without first
        # touching the selector. The selected language is only a fallback for
        # very short/ambiguous transcripts.
        detected_language = normalize_language(detect_transcription_language(transcript))
        if not transcript.strip() and language:
            detected_language = normalize_language(language)
        chunks: list[str] = []
        async for chunk in chat_stream(transcript[:5000], history, language=detected_language):
            chunks.append(chunk)
        reply = "".join(chunks).strip()
        audio_result = await synthesize_speech(reply[:5000], detected_language) if reply else None
        return {
            "text": transcript,
            "reply": reply,
            "language": detected_language,
            "audio_base64": base64.b64encode(audio_result).decode("ascii") if audio_result else None,
            "tts_available": bool(audio_result),
        }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Voice assistant pipeline failed")
        raise HTTPException(status_code=502, detail="Le service vocal est temporairement indisponible.")
