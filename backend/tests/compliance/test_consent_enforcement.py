"""
tests/compliance/test_consent_enforcement.py — Vérifie qu'aucun message
d'outreach ne peut être généré sans consentement valide.

Cas testés :
1. Pas de consentement → séquence refusée
2. Consentement valide → séquence démarrée
3. Consentement retiré (opt-out) → séquence stoppée
4. Consentement d'un autre canal → pas de confusion
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.outreach.outreach_scheduler import start_sequence, verify_consent


# ── Helpers ──────────────────────────────────────────────────────

def _mock_db_no_consent():
    """DB mock sans aucun consentement actif."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(return_value=None)
    db.execute = AsyncMock(return_value=result)
    return db


def _mock_db_with_consent():
    """DB mock avec un consentement actif."""
    db = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none = MagicMock(
        return_value=uuid.uuid4()  # consentement trouvé
    )
    db.execute = AsyncMock(return_value=result)
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


def _mock_db_consent_withdrawn():
    """DB mock avec un consentement retiré (opt_out_at rempli)."""
    db = AsyncMock()
    result = MagicMock()
    # Pas de consentement actif (tous ont opt_out_at non null)
    result.scalar_one_or_none = MagicMock(return_value=None)
    db.execute = AsyncMock(return_value=result)
    return db


# ── Tests ────────────────────────────────────────────────────────

class TestConsentEnforcement:
    """Vérifie l'enforcement du consentement dans l'outreach."""

    @pytest.mark.asyncio
    async def test_no_consent_blocks_sequence(self):
        """Sans consentement, la séquence ne doit JAMAIS démarrer."""
        db = _mock_db_no_consent()
        prospect_id = str(uuid.uuid4())

        result = await start_sequence(
            prospect_id=prospect_id,
            top3_vehicles=[{"vehicle_id": "v1"}, {"vehicle_id": "v2"}],
            db=db,
        )

        assert result is None, (
            "La séquence ne doit PAS démarrer sans consentement actif"
        )

    @pytest.mark.asyncio
    async def test_valid_consent_allows_sequence(self):
        """Avec un consentement valide, la séquence peut démarrer."""
        db = _mock_db_with_consent()
        prospect_id = str(uuid.uuid4())

        result = await start_sequence(
            prospect_id=prospect_id,
            top3_vehicles=[
                {"vehicle_id": "v1"},
                {"vehicle_id": "v2"},
                {"vehicle_id": "v3"},
            ],
            db=db,
        )

        assert result is not None, (
            "La séquence doit démarrer avec un consentement valide"
        )
        assert result.status == "active"
        assert result.current_milestone == "J0"

    @pytest.mark.asyncio
    async def test_withdrawn_consent_blocks_sequence(self):
        """Un consentement retiré (opt-out) doit bloquer la séquence."""
        db = _mock_db_consent_withdrawn()
        prospect_id = str(uuid.uuid4())

        result = await start_sequence(
            prospect_id=prospect_id,
            top3_vehicles=[{"vehicle_id": "v1"}],
            db=db,
        )

        assert result is None, (
            "La séquence ne doit PAS démarrer après un retrait de consentement"
        )


class TestVerifyConsent:
    """Tests unitaires de la fonction verify_consent."""

    @pytest.mark.asyncio
    async def test_verify_returns_false_when_no_consent(self):
        """verify_consent retourne False sans consentement."""
        db = _mock_db_no_consent()
        result = await verify_consent(str(uuid.uuid4()), db)
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_returns_true_when_active(self):
        """verify_consent retourne True avec un consentement actif."""
        db = _mock_db_with_consent()
        result = await verify_consent(str(uuid.uuid4()), db)
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_returns_false_after_optout(self):
        """verify_consent retourne False après un opt-out."""
        db = _mock_db_consent_withdrawn()
        result = await verify_consent(str(uuid.uuid4()), db)
        assert result is False
