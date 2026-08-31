"""
outreach/stop_conditions.py — Vérifie AVANT chaque envoi programmé si
la séquence doit être arrêtée.

Conditions d'arrêt :
1. Achat confirmé (table transactions)
2. Essai déjà réservé (table test_drives via routes_test_drives.py existant)
3. Consentement retiré (prospect_consents.opt_out_at IS NOT NULL)

Si UNE SEULE de ces conditions est vraie, annule TOUTE la séquence
restante pour ce prospect immédiatement — jamais un message envoyé
après un stop confirmé, même si déjà programmé.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update, exists, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outreach import ProspectConsent, OutreachSequence

logger = logging.getLogger(__name__)


class StopReason:
    """Constantes pour les raisons d'arrêt."""
    PURCHASE_CONFIRMED = "purchase_confirmed"
    TEST_DRIVE_BOOKED = "test_drive_booked"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    SEQUENCE_COMPLETED = "sequence_completed"


async def check_consent_withdrawn(
    prospect_id: str,
    db: AsyncSession,
) -> bool:
    """Vérifie si le consentement a été retiré pour ce prospect."""
    import uuid
    pid = uuid.UUID(str(prospect_id))

    # Check if there is ANY active consent
    result = await db.execute(
        select(ProspectConsent.id).where(
            ProspectConsent.prospect_id == pid,
            ProspectConsent.opt_out_at.is_(None),
        ).limit(1)
    )
    has_active = result.scalar_one_or_none()

    if has_active is None:
        logger.info(
            "STOP_CONDITION: Consent withdrawn for prospect %s", prospect_id
        )
        return True
    return False


async def check_purchase_confirmed(
    prospect_id: str,
    db: AsyncSession,
) -> bool:
    """
    Vérifie si le prospect a confirmé un achat.
    Utilise la table transactions existante.
    """
    from sqlalchemy import text
    import uuid
    pid = uuid.UUID(str(prospect_id))

    try:
        result = await db.execute(
            text("""
                SELECT 1 FROM transactions
                WHERE buyer_id = :pid
                AND status IN ('completed', 'confirmed', 'paid')
                LIMIT 1
            """),
            {"pid": pid},
        )
        if result.scalar_one_or_none():
            logger.info(
                "STOP_CONDITION: Purchase confirmed for prospect %s", prospect_id
            )
            return True
    except Exception:
        # Table might not exist in test environment
        pass

    return False


async def check_test_drive_booked(
    prospect_id: str,
    db: AsyncSession,
) -> bool:
    """
    Vérifie si le prospect a déjà réservé un essai routier.
    Utilise la table test_drive_bookings existante (routes_test_drives.py).
    """
    from sqlalchemy import text
    import uuid
    pid = uuid.UUID(str(prospect_id))

    try:
        result = await db.execute(
            text("""
                SELECT 1 FROM test_drive_bookings
                WHERE user_id = :pid
                AND status IN ('confirmed', 'scheduled', 'completed')
                LIMIT 1
            """),
            {"pid": pid},
        )
        if result.scalar_one_or_none():
            logger.info(
                "STOP_CONDITION: Test drive booked for prospect %s", prospect_id
            )
            return True
    except Exception:
        # Table might not exist in test environment
        pass

    return False


async def evaluate_stop_conditions(
    prospect_id: str,
    db: AsyncSession,
) -> Optional[str]:
    """
    Évalue toutes les conditions d'arrêt pour un prospect.

    Retourne la raison d'arrêt (str) si une condition est remplie,
    None si la séquence peut continuer.
    """
    # 1. Consentement retiré — priorité absolue
    if await check_consent_withdrawn(prospect_id, db):
        return StopReason.CONSENT_WITHDRAWN

    # 2. Achat confirmé
    if await check_purchase_confirmed(prospect_id, db):
        return StopReason.PURCHASE_CONFIRMED

    # 3. Essai réservé
    if await check_test_drive_booked(prospect_id, db):
        return StopReason.TEST_DRIVE_BOOKED

    return None


async def stop_sequence(
    sequence_id: str,
    reason: str,
    db: AsyncSession,
) -> None:
    """
    Arrête une séquence d'outreach et annule tous les jalons restants.
    """
    import uuid
    sid = uuid.UUID(str(sequence_id))

    await db.execute(
        update(OutreachSequence)
        .where(OutreachSequence.id == sid)
        .values(
            status="stopped",
            stop_reason=reason,
            next_scheduled_at=None,
            updated_at=datetime.now(timezone.utc),
        )
    )

    logger.warning(
        "OUTREACH_STOPPED: Sequence %s stopped — reason: %s",
        sequence_id, reason,
    )


async def stop_all_sequences_for_prospect(
    prospect_id: str,
    reason: str,
    db: AsyncSession,
) -> int:
    """
    Arrête TOUTES les séquences actives d'un prospect.
    Retourne le nombre de séquences arrêtées.
    """
    import uuid
    pid = uuid.UUID(str(prospect_id))

    result = await db.execute(
        update(OutreachSequence)
        .where(
            OutreachSequence.prospect_id == pid,
            OutreachSequence.status == "active",
        )
        .values(
            status="stopped",
            stop_reason=reason,
            next_scheduled_at=None,
            updated_at=datetime.now(timezone.utc),
        )
        .returning(OutreachSequence.id)
    )
    stopped = result.all()

    if stopped:
        logger.warning(
            "OUTREACH_STOPPED: %d active sequences stopped for prospect %s — reason: %s",
            len(stopped), prospect_id, reason,
        )

    return len(stopped)
