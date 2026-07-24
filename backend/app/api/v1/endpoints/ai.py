from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any

from app.services.ai.chat import chat_stream
from app.core.limiter import limiter

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="Message utilisateur")
    history: List[ChatMessage] = Field(default_factory=list, description="Historique du chat")

router = APIRouter()

@router.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(
    request: Request,
    payload: ChatRequest = Body(...)
):
    """
    Endpoint pour le chat IA.
    Attend un payload JSON validé.
    """
    message = payload.message
    history = [{"role": msg.role, "content": msg.content} for msg in payload.history]
    
    # Fastapi StreamingResponse will iterate over the async generator
    return StreamingResponse(
        chat_stream(message, history), 
        media_type="text/event-stream"
    )
