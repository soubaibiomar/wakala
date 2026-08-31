"""
tests/unit/test_stop_conditions.py — Tests des conditions d'arrêt de l'outreach.

Vérifie :
- Achat confirmé → séquence stoppée
- Essai réservé → séquence stoppée
- Consentement retiré → séquence stoppée
- Aucune condition → séquence continue
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.outreach.stop_conditions import (
    StopReason,
    check_consent_withdrawn,
    check_purchase_confirmed,
    check_test_drive_booked,
    evaluate_stop_conditions,
)


# ── Helpers ──────────────────────────────────────────────────────

def _db_scalar_returns(value):
    """DB mock avec scalar_one_or_none retournant la valeur donnée."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=value)
    db.execute = AsyncMock(return_value=result)
    return db


# ── Tests check_consent_withdrawn ────────────────────────────────

class TestConsentWithdrawn:
    @pytest.mark.asyncio
    async def test_active_consent_not_withdrawn(self):
        """Consentement actif → pas retiré."""
        db = _db_scalar_returns(uuid.uuid4())  # consent found
        result = await check_consent_withdrawn(str(uuid.uuid4()), db)
        assert result is False

    @pytest.mark.asyncio
    async def test_no_consent_is_withdrawn(self):
        """Pas de consentement actif → considéré comme retiré."""
        db = _db_scalar_returns(None)  # no active consent
        result = await check_consent_withdrawn(str(uuid.uuid4()), db)
        assert result is True


# ── Tests check_purchase_confirmed ───────────────────────────────

class TestPurchaseConfirmed:
    @pytest.mark.asyncio
    async def test_no_purchase(self):
        """Pas d'achat confirmé."""
        db = _db_scalar_returns(None)
        result = await check_purchase_confirmed(str(uuid.uuid4()), db)
        assert result is False

    @pytest.mark.asyncio
    async def test_purchase_found(self):
        """Achat confirmé trouvé."""
        db = _db_scalar_returns(1)
        result = await check_purchase_confirmed(str(uuid.uuid4()), db)
        assert result is True


# ── Tests check_test_drive_booked ────────────────────────────────

class TestTestDriveBooked:
    @pytest.mark.asyncio
    async def test_no_test_drive(self):
        """Pas d'essai réservé."""
        db = _db_scalar_returns(None)
        result = await check_test_drive_booked(str(uuid.uuid4()), db)
        assert result is False

    @pytest.mark.asyncio
    async def test_test_drive_found(self):
        """Essai réservé trouvé."""
        db = _db_scalar_returns(1)
        result = await check_test_drive_booked(str(uuid.uuid4()), db)
        assert result is True


# ── Tests evaluate_stop_conditions ───────────────────────────────

class TestEvaluateStopConditions:
    @pytest.mark.asyncio
    async def test_no_stop_condition(self):
        """Aucune condition d'arrêt → None."""
        db = AsyncMock()
        # All checks return "no stop"
        result_consent = MagicMock()
        result_consent.scalar_one_or_none = MagicMock(return_value=uuid.uuid4())

        result_purchase = MagicMock()
        result_purchase.scalar_one_or_none = MagicMock(return_value=None)

        result_test = MagicMock()
        result_test.scalar_one_or_none = MagicMock(return_value=None)

        db.execute = AsyncMock(side_effect=[
            result_consent,   # check_consent: active
            result_purchase,  # check_purchase: none
            result_test,      # check_test_drive: none
        ])

        reason = await evaluate_stop_conditions(str(uuid.uuid4()), db)
        assert reason is None

    @pytest.mark.asyncio
    async def test_consent_withdrawn_stops_first(self):
        """Consentement retiré → arrêt en priorité."""
        db = _db_scalar_returns(None)  # no active consent
        reason = await evaluate_stop_conditions(str(uuid.uuid4()), db)
        assert reason == StopReason.CONSENT_WITHDRAWN
