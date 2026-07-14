from typing import Annotated

from fastapi import APIRouter, HTTPException

from app.rag.chatbot_chain import chatbot_chain
from app.rag.schemas import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    try:
        response = await chatbot_chain.answer(
            message=payload.message,
            session_id=payload.session_id,
        )
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=503,
            detail="Assistant temporairement indisponible. Veuillez reessayer.",
        )
