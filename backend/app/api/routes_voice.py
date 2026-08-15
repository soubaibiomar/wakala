import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Request
import whisper
import tempfile
import asyncio

router = APIRouter()

from app.core.limiter import limiter

# Lazy load the whisper model on first request to avoid slow startup
_model = None

def get_whisper_model():
    global _model
    if _model is None:
        print("Loading Whisper model (lazy)...")
        _model = whisper.load_model("base")
        print("Whisper model loaded.")
    return _model

@router.post("/transcribe")
@limiter.limit("5/minute")
async def transcribe_voice(request: Request, audio: UploadFile = File(...)):
    """
    Receives an audio file (e.g. webm, wav, mp4) and transcribes it using Whisper.
    """
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file provided.")

    # Save uploaded audio to a temporary file
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            temp_audio.write(await audio.read())
            temp_path = temp_audio.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save audio: {str(e)}")

    try:
        # Run Whisper transcription
        # Since Whisper blocks the event loop, we run it in a threadpool
        loop = asyncio.get_running_loop()
        # Using task="transcribe" to keep the original language, or translate to French?
        # For our search, transcribing in French/Darija is fine.
        model_instance = get_whisper_model()
        result = await loop.run_in_executor(None, lambda: model_instance.transcribe(temp_path, language="fr"))
        
        text = result.get("text", "").strip()
        return {"text": text}
    except Exception as e:
        print(f"Whisper transcription error: {e}")
        raise HTTPException(status_code=500, detail="Transcription failed.")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
