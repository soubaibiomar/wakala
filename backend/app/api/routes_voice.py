import os
from fastapi import APIRouter, UploadFile, File, HTTPException
import whisper
import tempfile
import asyncio

router = APIRouter()

# Load the whisper model once when the module loads
# We use the 'base' or 'tiny' model for CPU to keep latency reasonable
print("Loading Whisper model (this may take a few seconds on first run)...")
model = whisper.load_model("base")
print("Whisper model loaded.")

@router.post("/transcribe")
async def transcribe_voice(audio: UploadFile = File(...)):
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
        result = await loop.run_in_executor(None, lambda: model.transcribe(temp_path, language="fr"))
        
        text = result.get("text", "").strip()
        return {"text": text}
    except Exception as e:
        print(f"Whisper transcription error: {e}")
        raise HTTPException(status_code=500, detail="Transcription failed.")
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)
