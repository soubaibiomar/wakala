"""
api/routes_consent.py — Endpoints REST pour la gestion du consentement prospect.

Conforme à la loi 09-08/CNDP :
- POST /api/consent : enregistre le consentement explicite
- DELETE /api/consent/{prospect_id} : retrait (opt-out)
- GET /api/consent/{prospect_id} : vérifie le statut
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.limiter import limiter
from app.models.outreach import ProspectConsent

router = APIRouter()


# ─── Schémas requête/réponse ─────────────────────────────────────

class ConsentRequest(BaseModel):
    prospect_id: UUID
    channel: str = Field(
        ..., pattern="^(whatsapp|email|sms)$",
        description="Canal de communication accepté",
    )
    purpose: str = Field(
        default="recommendation_outreach",
        description="Finalité déclarée du consentement",
    )
    consent_source: str = Field(
        ..., pattern="^(web|whatsapp|chatbot)$",
        description="Source du consentement",
    )


class ConsentResponse(BaseModel):
    id: UUID
    prospect_id: UUID
    channel: str
    purpose: str
    consented_at: datetime
    opt_out_at: Optional[datetime] = None
    consent_source: str
    is_active: bool


class ConsentStatusResponse(BaseModel):
    prospect_id: UUID
    consents: list[ConsentResponse]
    has_active_consent: bool


# ─── Endpoints ───────────────────────────────────────────────────

@router.post("/", response_model=ConsentResponse, status_code=201)
@limiter.limit("20/minute")
async def register_consent(
    request: Request,
    payload: ConsentRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Enregistre le consentement explicite d'un prospect.
    Le prospect accepte d'être contacté via le canal spécifié
    pour la finalité déclarée.
    """
    consent = ProspectConsent(
        prospect_id=payload.prospect_id,
        channel=payload.channel,
        purpose=payload.purpose,
        consent_source=payload.consent_source,
        consented_at=datetime.now(timezone.utc),
    )
    db.add(consent)
    await db.flush()

    return ConsentResponse(
        id=consent.id,
        prospect_id=consent.prospect_id,
        channel=consent.channel,
        purpose=consent.purpose,
        consented_at=consent.consented_at,
        opt_out_at=consent.opt_out_at,
        consent_source=consent.consent_source,
        is_active=consent.is_active,
    )


@router.delete("/{prospect_id}", status_code=200)
@limiter.limit("10/minute")
async def withdraw_consent(
    request: Request,
    prospect_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrait du consentement (opt-out).
    Met à jour opt_out_at pour TOUS les consentements actifs du prospect.
    Toute séquence d'outreach en cours sera stoppée par stop_conditions.
    """
    now = datetime.now(timezone.utc)
    result = await db.execute(
        update(ProspectConsent)
        .where(
            ProspectConsent.prospect_id == prospect_id,
            ProspectConsent.opt_out_at.is_(None),
        )
        .values(opt_out_at=now)
        .returning(ProspectConsent.id)
    )
    updated_ids = result.all()

    if not updated_ids:
        raise HTTPException(
            status_code=404,
            detail="Aucun consentement actif trouvé pour ce prospect.",
        )

    return {
        "message": "Consentement retiré avec succès.",
        "prospect_id": str(prospect_id),
        "consents_withdrawn": len(updated_ids),
        "opt_out_at": now.isoformat(),
    }


@router.get("/{prospect_id}", response_model=ConsentStatusResponse)
async def get_consent_status(
    prospect_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Vérifie le statut du consentement d'un prospect."""
    result = await db.execute(
        select(ProspectConsent).where(
            ProspectConsent.prospect_id == prospect_id
        )
    )
    consents = list(result.scalars().all())

    consent_responses = [
        ConsentResponse(
            id=c.id,
            prospect_id=c.prospect_id,
            channel=c.channel,
            purpose=c.purpose,
            consented_at=c.consented_at,
            opt_out_at=c.opt_out_at,
            consent_source=c.consent_source,
            is_active=c.is_active,
        )
        for c in consents
    ]

    has_active = any(c.is_active for c in consent_responses)

    return ConsentStatusResponse(
        prospect_id=prospect_id,
        consents=consent_responses,
        has_active_consent=has_active,
    )
