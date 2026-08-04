from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_, desc
from typing import Annotated, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.message import Message
from app.models.user import User
from app.models.listing import Listing
from app.core.security import get_current_user

router = APIRouter(prefix="/messages", tags=["Messagerie"])

# --- Schemas ---

class MessageCreate(BaseModel):
    recipient_id: str
    listing_id: Optional[str] = None
    content: str = Field(..., min_length=1)

class UserBasic(BaseModel):
    id: str
    full_name: str
    avatar_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class ListingBasic(BaseModel):
    id: str
    vehicle_id: str
    
    class Config:
        from_attributes = True

class MessageRead(BaseModel):
    id: str
    sender_id: str
    recipient_id: str
    listing_id: Optional[str] = None
    content: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationContact(BaseModel):
    contact: UserBasic
    listing: Optional[ListingBasic]
    last_message: MessageRead
    unread_count: int

# --- Routes ---

@router.post("/", response_model=MessageRead, summary="Envoyer un message")
async def send_message(
    message_data: MessageCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    if message_data.recipient_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous envoyer un message à vous-même.")
        
    # Check if recipient exists
    result = await db.execute(select(User).where(User.id == message_data.recipient_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Destinataire introuvable.")
        
    if message_data.listing_id:
        result_listing = await db.execute(select(Listing).where(Listing.id == message_data.listing_id))
        if not result_listing.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Annonce introuvable.")

    new_msg = Message(
        sender_id=current_user.id,
        recipient_id=message_data.recipient_id,
        listing_id=message_data.listing_id,
        content=message_data.content
    )
    db.add(new_msg)
    await db.commit()
    await db.refresh(new_msg)
    return new_msg

@router.get("/{contact_id}", response_model=List[MessageRead], summary="Récupérer une conversation")
async def get_messages(
    contact_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    listing_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    query = select(Message).where(
        or_(
            and_(Message.sender_id == current_user.id, Message.recipient_id == contact_id),
            and_(Message.sender_id == contact_id, Message.recipient_id == current_user.id)
        )
    )
    if listing_id:
        query = query.where(Message.listing_id == listing_id)
        
    query = query.order_by(desc(Message.created_at)).offset(offset).limit(limit)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    # Mark as read for messages received by current user
    unread_messages = [m for m in messages if m.recipient_id == current_user.id and not m.is_read]
    if unread_messages:
        for m in unread_messages:
            m.is_read = True
        await db.commit()
        
    # Return in chronological order (oldest first)
    return list(reversed(messages))

@router.get("/user/conversations", response_model=List[ConversationContact], summary="Liste des conversations")
async def get_conversations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # This query finds the latest message for each contact (either they sent or received)
    # Since SQLAlchemy async with subqueries and group bys can be complex, we do a basic fetch and group in memory for this V1
    
    query = select(Message).where(
        or_(Message.sender_id == current_user.id, Message.recipient_id == current_user.id)
    ).order_by(desc(Message.created_at))
    
    result = await db.execute(query)
    all_messages = result.scalars().all()
    
    conversations = {}
    
    for msg in all_messages:
        contact_id = msg.recipient_id if msg.sender_id == current_user.id else msg.sender_id
        key = f"{contact_id}_{msg.listing_id or 'none'}"
        
        if key not in conversations:
            conversations[key] = {
                "contact_id": contact_id,
                "listing_id": msg.listing_id,
                "last_message": msg,
                "unread_count": 0
            }
        
        if msg.recipient_id == current_user.id and not msg.is_read:
            conversations[key]["unread_count"] += 1
            
    # Now fetch contact and listing details
    response = []
    for key, data in conversations.items():
        contact_res = await db.execute(select(User).where(User.id == data["contact_id"]))
        contact = contact_res.scalar_one_or_none()
        
        listing = None
        if data["listing_id"]:
            listing_res = await db.execute(select(Listing).where(Listing.id == data["listing_id"]))
            listing = listing_res.scalar_one_or_none()
            
        if contact:
            response.append(ConversationContact(
                contact=UserBasic.model_validate(contact),
                listing=ListingBasic.model_validate(listing) if listing else None,
                last_message=MessageRead.model_validate(data["last_message"]),
                unread_count=data["unread_count"]
            ))
            
    return sorted(response, key=lambda x: x.last_message.created_at, reverse=True)
