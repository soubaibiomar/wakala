import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.offer import Offer
from pydantic import BaseModel, ConfigDict
from datetime import datetime

router = APIRouter()

# Schemas
class OfferCreate(BaseModel):
    vehicle_id: uuid.UUID
    amount: float
    message: str | None = None

class OfferUpdateStatus(BaseModel):
    status: str # "accepted", "rejected", "countered"
    
class VehicleMinimal(BaseModel):
    id: uuid.UUID
    brand: str
    model: str
    price: float
    model_config = ConfigDict(from_attributes=True)

class OfferResponse(BaseModel):
    id: uuid.UUID
    buyer_id: uuid.UUID
    vehicle_id: uuid.UUID
    amount: float
    status: str
    message: str | None
    created_at: datetime
    updated_at: datetime
    vehicle: VehicleMinimal | None = None
    model_config = ConfigDict(from_attributes=True)

@router.post("/", response_model=OfferResponse)
async def create_offer(
    offer_in: OfferCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify vehicle exists
    stmt = select(Vehicle).where(Vehicle.id == offer_in.vehicle_id)
    result = await db.execute(stmt)
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
        
    if vehicle.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot make an offer on your own vehicle")
        
    # Check for existing pending offer
    stmt = select(Offer).where(
        Offer.buyer_id == current_user.id,
        Offer.vehicle_id == offer_in.vehicle_id,
        Offer.status == "pending"
    )
    result = await db.execute(stmt)
    existing_offer = result.scalar_one_or_none()
    
    if existing_offer:
        raise HTTPException(status_code=400, detail="You already have a pending offer for this vehicle")
        
    new_offer = Offer(
        buyer_id=current_user.id,
        vehicle_id=offer_in.vehicle_id,
        amount=offer_in.amount,
        message=offer_in.message,
        status="pending"
    )
    
    db.add(new_offer)
    await db.commit()
    await db.refresh(new_offer)
    
    return new_offer


@router.get("/sent", response_model=List[OfferResponse])
async def get_sent_offers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Offer).options(selectinload(Offer.vehicle)).where(Offer.buyer_id == current_user.id).order_by(Offer.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/received", response_model=List[OfferResponse])
async def get_received_offers(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Offer).options(selectinload(Offer.vehicle)).join(Vehicle).where(Vehicle.seller_id == current_user.id).order_by(Offer.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.patch("/{offer_id}/status", response_model=OfferResponse)
async def update_offer_status(
    offer_id: uuid.UUID,
    status_update: OfferUpdateStatus,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if status_update.status not in ["accepted", "rejected", "countered"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    stmt = select(Offer).options(selectinload(Offer.vehicle)).where(Offer.id == offer_id)
    result = await db.execute(stmt)
    offer = result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    if offer.vehicle.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this offer")
        
    offer.status = status_update.status
    offer.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(offer)
    
    return offer
