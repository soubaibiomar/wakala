"""
outreach/outreach_scheduler.py — Programme les jalons d'outreach pour
chaque prospect consentant, à partir de la date du Top 3 présenté.

MODE SIMULÉ par défaut : les messages sont loggés en base et en console,
aucun envoi réel tant que le canal (WhatsApp/email) n'est pas confirmé.
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outreach import OutreachSequence, ProspectConsent
from app.outreach.sequence_definitions import (
    MILESTONES,
    MILESTONE_MAP,
    get_next_milestone,
)
from app.outreach.message_templates import render_template, build_top3_variables
from app.outreach.stop_conditions import (
    evaluate_stop_conditions,
    stop_sequence,
)

logger = logging.getLogger(__name__)


async def verify_consent(prospect_id: str, db: AsyncSession) -> bool:
    """
    Vérifie qu'un consentement valide et non retiré existe pour ce prospect.
    Vérification SYSTÉMATIQUE avant chaque envoi, pas seulement à l'inscription.
    """
    pid = uuid.UUID(str(prospect_id))
    result = await db.execute(
        select(ProspectConsent.id).where(
            ProspectConsent.prospect_id == pid,
            ProspectConsent.opt_out_at.is_(None),
            ProspectConsent.purpose.in_(["recommendation_outreach", "outreach"]),
        ).limit(1)
    )
    return result.scalar_one_or_none() is not None


async def start_sequence(
    prospect_id: str,
    top3_vehicles: list[dict],
    db: AsyncSession,
) -> Optional[OutreachSequence]:
    """
    Démarre une nouvelle séquence d'outreach pour un prospect consentant.

    1. Vérifie le consentement
    2. Crée l'enregistrement OutreachSequence
    3. Programme le premier jalon (J0)
    """
    # Vérification consentement — OBLIGATOIRE
    if not await verify_consent(prospect_id, db):
        logger.warning(
            "OUTREACH_BLOCKED: No active consent for prospect %s — "
            "sequence NOT started",
            prospect_id,
        )
        return None

    now = datetime.now(timezone.utc)
    pid = uuid.UUID(str(prospect_id))

    vehicle_ids = [v.get("vehicle_id", "") for v in top3_vehicles[:3]]

    sequence = OutreachSequence(
        prospect_id=pid,
        top3_vehicle_ids=vehicle_ids,
        sequence_started_at=now,
        current_milestone="J0",
        next_scheduled_at=now,  # J0 is immediate
        status="active",
    )
    db.add(sequence)
    await db.flush()

    logger.info(
        "OUTREACH_STARTED: Sequence %s for prospect %s — %d vehicles",
        sequence.id, prospect_id, len(vehicle_ids),
    )

    return sequence


async def process_milestone(
    sequence: OutreachSequence,
    vehicles_data: list[dict],
    prospect_name: str,
    db: AsyncSession,
    simulate: bool = True,
) -> dict[str, Any]:
    """
    Traite un jalon dû pour une séquence donnée.

    1. Vérifie les conditions d'arrêt
    2. Vérifie le consentement (à nouveau)
    3. Génère le message depuis le template
    4. Envoie (ou simule) le message
    5. Programme le jalon suivant

    Retourne un dict avec le résultat de l'opération.
    """
    prospect_id = str(sequence.prospect_id)
    current = sequence.current_milestone

    # 1. Conditions d'arrêt
    stop_reason = await evaluate_stop_conditions(prospect_id, db)
    if stop_reason:
        await stop_sequence(str(sequence.id), stop_reason, db)
        return {
            "action": "stopped",
            "reason": stop_reason,
            "milestone": current,
        }

    # 2. Vérification consentement (systématique)
    if not await verify_consent(prospect_id, db):
        await stop_sequence(str(sequence.id), "consent_not_found", db)
        return {
            "action": "stopped",
            "reason": "consent_not_found",
            "milestone": current,
        }

    # 3. Récupérer le milestone courant
    milestone = MILESTONE_MAP.get(current)
    if not milestone:
        logger.error("Unknown milestone code: %s", current)
        return {"action": "error", "reason": f"unknown_milestone_{current}"}

    # 4. Vérification spéciale J45 : baisse de prix réelle requise
    if milestone.code == "J45" and milestone.skippable:
        price_drop = _check_real_price_drop(vehicles_data)
        if not price_drop:
            logger.info(
                "OUTREACH_SKIP: J45 skipped for prospect %s — no real price drop",
                prospect_id,
            )
            # Passer directement au jalon suivant
            next_milestone = get_next_milestone(current)
            if next_milestone:
                now = datetime.now(timezone.utc)
                start = sequence.sequence_started_at
                next_date = start + timedelta(days=next_milestone.delay_days)

                await db.execute(
                    update(OutreachSequence)
                    .where(OutreachSequence.id == sequence.id)
                    .values(
                        current_milestone=next_milestone.code,
                        next_scheduled_at=next_date,
                        updated_at=now,
                    )
                )
            return {
                "action": "skipped",
                "milestone": "J45",
                "reason": "no_real_price_drop",
            }

    # 5. Générer le message
    variables = build_top3_variables(
        prospect_name=prospect_name,
        vehicles=vehicles_data,
        budget=vehicles_data[0].get("budget_max") if vehicles_data else None,
        usage=vehicles_data[0].get("usage") if vehicles_data else None,
    )

    # Variables spéciales pour J45
    if milestone.code == "J45":
        price_drop = _check_real_price_drop(vehicles_data)
        if price_drop:
            variables.update(price_drop)

    message = render_template(milestone.template_key, variables)

    # 6. Envoyer ou simuler
    if simulate:
        logger.info(
            "OUTREACH_SIMULATED [%s] → prospect=%s channel=%s\n"
            "Subject: %s\nBody: %s",
            milestone.code, prospect_id, milestone.channel,
            message["subject"], message["body"][:200] + "...",
        )
        send_result = {"status": "simulated", "channel": milestone.channel}
    else:
        # TODO: Intégrer le vrai envoi WhatsApp/Email quand disponible
        send_result = {"status": "simulated", "channel": milestone.channel}

    # 7. Programmer le jalon suivant
    next_milestone = get_next_milestone(current)
    now = datetime.now(timezone.utc)

    if next_milestone:
        start = sequence.sequence_started_at
        next_date = start + timedelta(days=next_milestone.delay_days)

        await db.execute(
            update(OutreachSequence)
            .where(OutreachSequence.id == sequence.id)
            .values(
                current_milestone=next_milestone.code,
                next_scheduled_at=next_date,
                updated_at=now,
            )
        )
    else:
        # Séquence terminée
        await db.execute(
            update(OutreachSequence)
            .where(OutreachSequence.id == sequence.id)
            .values(
                status="completed",
                next_scheduled_at=None,
                updated_at=now,
            )
        )

    return {
        "action": "sent" if not simulate else "simulated",
        "milestone": milestone.code,
        "channel": milestone.channel,
        "message": message,
        "next_milestone": next_milestone.code if next_milestone else None,
    }


def _check_real_price_drop(vehicles_data: list[dict]) -> Optional[dict]:
    """
    Vérifie si un véhicule du Top 3 a eu une vraie baisse de prix.
    Retourne les variables pour le template J45 si oui, None sinon.

    CRITIQUE : Ne doit JAMAIS retourner un chiffre inventé.
    La baisse doit être réellement calculée depuis une comparaison
    de prix en base.
    """
    for v in vehicles_data:
        old_price = v.get("original_price")
        new_price = v.get("price") or v.get("current_price")

        if old_price and new_price and float(old_price) > float(new_price):
            savings = float(old_price) - float(new_price)
            if savings >= 1000:  # Seuil minimum de 1000 MAD pour notifier
                return {
                    "vehicle_name": f"{v.get('brand', '')} {v.get('model', '')}",
                    "old_price": f"{float(old_price):,.0f} MAD".replace(",", " "),
                    "new_price": f"{float(new_price):,.0f} MAD".replace(",", " "),
                    "savings": f"{savings:,.0f} MAD".replace(",", " "),
                }

    return None
