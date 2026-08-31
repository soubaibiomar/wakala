from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import uuid
from typing import List, Optional
import shutil
import os
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.maintenance import VehicleService, ServiceReminder
from app.schemas.maintenance_schema import VehicleServiceResponse, ServiceReminderResponse

router = APIRouter()

UPLOAD_DIR = "uploads/receipts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/add", response_model=VehicleServiceResponse)
async def add_service(
    car_id: uuid.UUID = Form(...),
    service_type: str = Form(...),
    mileage: int = Form(...),
    date_str: str = Form(...),
    cost: Optional[float] = Form(None),
    notes: Optional[str] = Form(None),
    receipt: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify car ownership
    result = await db.execute(select(Vehicle).where(Vehicle.id == car_id, Vehicle.seller_id == current_user.id))
    vehicle = result.scalars().first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found or unauthorized")

    receipt_url = None
    if receipt:
        # Validation taille (max 5MB)
        if receipt.size and receipt.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="La facture est trop volumineuse (maximum 5MB).")

        # Validation type MIME
        allowed_mimes = {"application/pdf", "image/jpeg", "image/png", "image/webp"}
        if receipt.content_type and receipt.content_type.lower() not in allowed_mimes:
            raise HTTPException(
                status_code=400,
                detail="Format de fichier non supporté. Formats acceptés : PDF, JPEG, PNG, WEBP."
            )

        # Validation stricte de l'extension (liste blanche)
        allowed_extensions = {"pdf", "jpg", "jpeg", "png", "webp"}
        raw_ext = (receipt.filename or "").rsplit(".", 1)[-1].lower() if receipt.filename and "." in receipt.filename else ""
        if raw_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Extension de fichier non autorisée. Extensions acceptées : {', '.join(allowed_extensions)}"
            )

        # Enregistrement sécurisé avec nom UUID normalisé
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_name = f"{uuid.uuid4().hex}.{raw_ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(receipt.file, buffer)
        receipt_url = f"/uploads/receipts/{file_name}"

    try:
        service_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    new_service = VehicleService(
        user_id=current_user.id,
        car_id=car_id,
        service_type=service_type,
        mileage=mileage,
        date=service_date,
        cost=cost,
        receipt_url=receipt_url,
        notes=notes
    )

    db.add(new_service)
    
    # Simple reminder logic: update/create reminder based on service type
    if service_type.lower() in ["vidange", "oil change"]:
        # Next vidange in 15000 km or 1 year
        next_mileage = mileage + 15000
        # Check if reminder exists
        rem_res = await db.execute(select(ServiceReminder).where(ServiceReminder.car_id == car_id))
        reminder = rem_res.scalars().first()
        if not reminder:
            reminder = ServiceReminder(car_id=car_id, message="Prochaine vidange recommandée")
            db.add(reminder)
        
        reminder.trigger_mileage = next_mileage
        reminder.is_active = True
        reminder.message = f"Vidange recommandée à {next_mileage} km"

    await db.commit()
    await db.refresh(new_service)
    return new_service

@router.get("/history/{car_id}", response_model=List[VehicleServiceResponse])
async def get_service_history(
    car_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(VehicleService)
        .where(VehicleService.car_id == car_id, VehicleService.user_id == current_user.id)
        .order_by(desc(VehicleService.date))
    )
    return result.scalars().all()

@router.get("/reminders", response_model=List[ServiceReminderResponse])
async def get_reminders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Get all active reminders for user's vehicles
    result = await db.execute(
        select(ServiceReminder)
        .join(Vehicle)
        .where(Vehicle.seller_id == current_user.id, ServiceReminder.is_active == True)
    )
    return result.scalars().all()
