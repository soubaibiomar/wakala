from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Optional
import uuid
from decimal import Decimal

class VehicleServiceBase(BaseModel):
    service_type: str
    mileage: int
    date: date
    cost: Optional[Decimal] = None
    notes: Optional[str] = None

class VehicleServiceCreate(VehicleServiceBase):
    car_id: uuid.UUID
    # receipt_url will be added by backend after upload

class VehicleServiceResponse(VehicleServiceBase):
    id: uuid.UUID
    user_id: uuid.UUID
    car_id: uuid.UUID
    receipt_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ServiceReminderBase(BaseModel):
    trigger_mileage: Optional[int] = None
    trigger_date: Optional[date] = None
    message: str

class ServiceReminderResponse(ServiceReminderBase):
    id: uuid.UUID
    car_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
