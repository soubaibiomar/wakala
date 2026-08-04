from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.services.ai.chat import chat_stream
from app.core.limiter import limiter
from app.models.user import User

class ChatMessagePayload(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="Message utilisateur")
    history: List[ChatMessagePayload] = Field(default_factory=list, description="Historique du chat")
    session_id: Optional[str] = None

router = APIRouter()

@router.post("/chat")
@limiter.limit("10/minute")
async def chat_endpoint(
    request: Request,
    payload: ChatRequest = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Endpoint pour le chat IA.
    Attend un payload JSON validé.
    Sauvegarde l'historique si l'utilisateur est connecté.
    """
    message = payload.message
    history = [{"role": msg.role, "content": msg.content} for msg in payload.history]
    
    # Define an async generator wrapper to save history
    async def stream_and_save():
        full_response = ""
        # 1. Obtenir un itérateur asynchrone
        iterator = chat_stream(message, history)
        
        # 2. Renvoyer les chunks au client
        try:
            async for chunk in iterator:
                full_response += chunk
                yield chunk
        except Exception as e:
            # En cas d'erreur de stream
            yield f"\n[Erreur: {str(e)}]"
            
        # 3. Sauvegarder en DB après complétion
        if current_user:
            from app.models.chat_history import ChatSession, ChatMessage, ChatRole
            import uuid
            
            session_id = payload.session_id
            
            try:
                # Retrieve or create session
                if session_id:
                    # check if session exists
                    from sqlalchemy import select
                    stmt = select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
                    result = await db.execute(stmt)
                    session = result.scalar_one_or_none()
                    if not session:
                        session_id = None
                
                if not session_id:
                    session = ChatSession(user_id=current_user.id)
                    db.add(session)
                    await db.commit()
                    await db.refresh(session)
                    session_id = str(session.id)

                # Add User Message
                user_msg = ChatMessage(session_id=session_id, role=ChatRole.user, contenu=message)
                db.add(user_msg)
                
                # Add Assistant Message
                bot_msg = ChatMessage(session_id=session_id, role=ChatRole.assistant, contenu=full_response)
                db.add(bot_msg)
                
                await db.commit()
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Erreur lors de la sauvegarde du chat: {e}")

    return StreamingResponse(
        stream_and_save(), 
        media_type="text/event-stream"
    )

@router.get("/chat/history")
async def get_chat_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    if not current_user:
        return []
        
    from sqlalchemy import select
    from app.models.chat_history import ChatSession, ChatMessage
    
    # Retrieve all sessions for the user, ordered by creation date
    stmt = select(ChatSession).where(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc())
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    response = []
    for session in sessions:
        stmt_msgs = select(ChatMessage).where(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc())
        msgs_result = await db.execute(stmt_msgs)
        messages = msgs_result.scalars().all()
        
        response.append({
            "session_id": session.id,
            "created_at": session.created_at,
            "messages": [{"id": msg.id, "role": msg.role.value, "content": msg.contenu, "timestamp": msg.created_at} for msg in messages]
        })
        
    return response

