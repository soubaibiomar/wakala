import re
import uuid
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.catalog import TrimCatalog
from app.models.dealership import Dealership, Showroom
from app.models.lead_inquiry import LeadInquiry

router = APIRouter(prefix="/v1", tags=["Showrooms & Test Drives"])

MOROCCAN_PHONE_REGEX = re.compile(r'^(?:\+212|0)([567])(\d{8})$')


class TestDriveRequest(BaseModel):
    trim_id: str
    showroom_id: Optional[str] = None
    full_name: str = Field(..., min_length=2, max_length=120)
    phone_number: str = Field(..., description="Numéro marocain (ex: 0661234567 ou +212661234567)")
    email: Optional[str] = None
    city: str = Field(..., min_length=2, max_length=100)
    preferred_date: Optional[str] = None
    message: Optional[str] = Field(None, max_length=2000)
    cndp_consent_accepted: bool = Field(..., description="Consentement CNDP Loi 09-08")

    @field_validator("phone_number")
    def validate_moroccan_phone(cls, v: str) -> str:
        cleaned = re.sub(r'[\s.-]', '', v.strip())
        match = MOROCCAN_PHONE_REGEX.match(cleaned)
        if not match:
            raise ValueError("Veuillez saisir un numéro de téléphone marocain valide (ex: 06 61 23 45 67 ou +212 6 61 23 45 67)")
        # Normalize to E.164 (+212XXXXXXXXX)
        prefix = match.group(1)
        rest = match.group(2)
        return f"+212{prefix}{rest}"


class QuoteProformaRequest(BaseModel):
    trim_id: str
    showroom_id: Optional[str] = None
    full_name: str = Field(..., min_length=2, max_length=120)
    phone_number: str = Field(..., description="Numéro marocain")
    email: Optional[str] = None
    city: str = Field(..., min_length=2, max_length=100)
    company_name: Optional[str] = Field(None, max_length=255)
    cndp_consent_accepted: bool = True

    @field_validator("phone_number")
    def validate_moroccan_phone(cls, v: str) -> str:
        cleaned = re.sub(r'[\s.-]', '', v.strip())
        match = MOROCCAN_PHONE_REGEX.match(cleaned)
        if not match:
            raise ValueError("Veuillez saisir un numéro de téléphone marocain valide")
        prefix = match.group(1)
        rest = match.group(2)
        return f"+212{prefix}{rest}"


@router.get("/showrooms")
async def list_showrooms(
    city: Optional[str] = Query(None, description="Filtrer par ville"),
    brand: Optional[str] = Query(None, description="Filtrer par marque"),
    db: AsyncSession = Depends(get_db)
):
    """
    Liste tous les showrooms officiels agréés au Maroc pour réservation d'essai.
    """
    stmt = (
        select(Showroom)
        .join(Dealership, Dealership.id == Showroom.dealership_id)
        .options(selectinload(Showroom.dealership))
        .where(Showroom.is_active.is_(True))
    )
    if city:
        stmt = stmt.where(Showroom.city.ilike(f"%{city.strip()}%"))

    res = await db.execute(stmt)
    showrooms = res.scalars().all()

    results = []
    for s in showrooms:
        brands = s.brand_affiliations or []
        if brand and not any(brand.lower() in b.lower() for b in brands):
            continue

        results.append({
            "id": str(s.id),
            "name": s.name,
            "city": s.city,
            "address": s.address,
            "phone": s.phone,
            "latitude": float(s.latitude) if s.latitude else None,
            "longitude": float(s.longitude) if s.longitude else None,
            "brands": brands,
            "dealership": {
                "id": str(s.dealership.id),
                "name": s.dealership.name,
                "website": s.dealership.website
            }
        })

    return results


@router.post("/leads/test-drive")
async def book_test_drive(
    payload: TestDriveRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Enregistre une demande d'essai sur route en showroom avec conformité CNDP.
    """
    if not payload.cndp_consent_accepted:
        raise HTTPException(
            status_code=400,
            detail="Le consentement CNDP (Loi n° 09-08) est obligatoire pour transmettre votre demande."
        )

    try:
        t_uuid = uuid.UUID(payload.trim_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de finition invalide")

    trim_res = await db.execute(select(TrimCatalog).where(TrimCatalog.id == t_uuid))
    trim = trim_res.scalar_one_or_none()
    if not trim:
        raise HTTPException(status_code=404, detail="Finition de véhicule introuvable")

    showroom_uuid = None
    if payload.showroom_id:
        try:
            showroom_uuid = uuid.UUID(payload.showroom_id)
        except ValueError:
            pass

    inquiry = LeadInquiry(
        trim_id=t_uuid,
        showroom_id=showroom_uuid,
        inquiry_type="TEST_DRIVE",
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        email=payload.email,
        city=payload.city,
        preferred_date=payload.preferred_date,
        message=payload.message,
        phone_verified=True,  # Instant confirmation in digital showroom flow
        cndp_consent_accepted=True,
        cndp_consent_timestamp=datetime.now(timezone.utc),
        cndp_privacy_version="2026-v1",
        dispatch_status="VERIFIED_PENDING_DISPATCH"
    )
    db.add(inquiry)
    await db.commit()

    return {
        "status": "success",
        "inquiry_id": str(inquiry.id),
        "message": f"Votre demande d'essai pour la {trim.name} a été enregistrée avec succès ! Un conseiller commercial de votre showroom vous contactera sous 24h.",
        "confirmation_details": {
            "full_name": inquiry.full_name,
            "phone_number": inquiry.phone_number,
            "city": inquiry.city,
            "preferred_date": inquiry.preferred_date,
            "cndp_protected": True
        }
    }


@router.post("/leads/quote-proforma")
async def request_proforma_quote(
    payload: QuoteProformaRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Génération et demande de devis proforma officiel concessionnaire.
    """
    try:
        t_uuid = uuid.UUID(payload.trim_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de finition invalide")

    trim_res = await db.execute(select(TrimCatalog).where(TrimCatalog.id == t_uuid))
    trim = trim_res.scalar_one_or_none()
    if not trim:
        raise HTTPException(status_code=404, detail="Finition de véhicule introuvable")

    inquiry = LeadInquiry(
        trim_id=t_uuid,
        inquiry_type="QUOTE_PROFORMA",
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        email=payload.email,
        city=payload.city,
        message=f"Demande de devis proforma pour {payload.company_name or 'Particulier'}",
        phone_verified=True,
        cndp_consent_accepted=True,
        dispatch_status="VERIFIED_PENDING_DISPATCH"
    )
    db.add(inquiry)
    await db.commit()

    return {
        "status": "success",
        "inquiry_id": str(inquiry.id),
        "message": f"Votre demande de devis proforma pour la {trim.name} a été transmise au service commercial.",
    }
