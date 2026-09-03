from typing import Annotated

from fastapi import APIRouter, HTTPException, Request

from app.rag.chatbot_chain import chatbot_chain
from app.rag.schemas import ChatRequest, ChatResponse
from app.core.limiter import limiter

router = APIRouter()


@router.post("/", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat(request: Request, payload: ChatRequest):
    try:
        response = await chatbot_chain.answer(
            message=payload.message,
            session_id=payload.session_id,
        )
        return response
    except Exception as e:
        import logging
        logging.getLogger(__name__).exception("Chatbot request failed")
        raise HTTPException(
            status_code=503,
            detail="Assistant temporairement indisponible. Veuillez reessayer.",
        )
