from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any

from app.services.ai.chat import chat_stream

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(
    payload: Dict[str, Any] = Body(...)
):
    """
    Endpoint pour le chat IA.
    Attend un payload JSON du type:
    {
        "message": "Bonjour, je cherche une voiture",
        "history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    }
    Retourne une réponse en streaming (Server-Sent Events) ou un flux de texte brut.
    """
    message = payload.get("message")
    history = payload.get("history", [])
    
    if not message:
        raise HTTPException(status_code=400, detail="Le champ 'message' est requis.")
    
    # Fastapi StreamingResponse will iterate over the async generator
    return StreamingResponse(
        chat_stream(message, history), 
        media_type="text/event-stream"
    )
