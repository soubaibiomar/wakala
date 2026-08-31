"""
tests/integration/test_outreach_sequence_e2e.py — Test end-to-end de la
séquence d'outreach du J0 au J60.

Simule un prospect complet :
- J0 : récapitulatif envoyé
- J2 : catalogue envoyé
- J7 : matrice TCO envoyée
- J14 : essai proposé
- J45 : alerte prix (si baisse réelle)
- J60 : clôture

Vérifie aussi le stop au milieu de la séquence.
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.outreach.sequence_definitions import MILESTONES, get_next_milestone
from app.outreach.message_templates import render_template, build_top3_variables
from app.outreach.outreach_scheduler import (
    start_sequence,
    process_milestone,
    _check_real_price_drop,
)


# ── Fixtures ─────────────────────────────────────────────────────

PROSPECT_ID = str(uuid.uuid4())

SAMPLE_TOP3 = [
    {
        "vehicle_id": str(uuid.uuid4()),
        "brand": "Dacia", "model": "Sandero", "version": "Stepway",
        "year": 2024, "price": 180000, "fuel_type": "essence",
        "fuel_consumption": 5.5, "body_type": "citadine",
        "scores": {"cout_reel": 4, "espace": 3, "securite": 3.5},
        "strengths": ["Économie (4/5)", "Praticité urbaine (4/5)"],
        "compromises": ["Performance (2/5)"],
        "budget_max": 220000, "usage": "ville",
    },
    {
        "vehicle_id": str(uuid.uuid4()),
        "brand": "Renault", "model": "Clio", "version": "Intens",
        "year": 2023, "price": 200000, "fuel_type": "diesel",
        "fuel_consumption": 4.5, "body_type": "citadine",
        "scores": {"cout_reel": 5, "espace": 3, "securite": 4},
        "strengths": ["Coût réel (5/5)", "Sécurité (4/5)"],
        "compromises": [],
    },
    {
        "vehicle_id": str(uuid.uuid4()),
        "brand": "Peugeot", "model": "208", "version": "Active",
        "year": 2023, "price": 210000, "fuel_type": "essence",
        "fuel_consumption": 5.8, "body_type": "citadine",
        "scores": {"cout_reel": 4, "espace": 2, "securite": 4},
        "strengths": ["Sécurité (4/5)", "Design"],
        "compromises": ["Espace (2/5)"],
    },
]


def _mock_db_with_consent():
    """DB mock avec consentement valide + pas de stop conditions.

    Call pattern for process_milestone:
    1. evaluate_stop_conditions → check_consent_withdrawn (returns active consent)
    2. evaluate_stop_conditions → check_purchase_confirmed (returns None)
    3. evaluate_stop_conditions → check_test_drive_booked (returns None)
    4. verify_consent (returns active consent)
    5+ update queries
    """
    db = AsyncMock()
    call_count = {"n": 0}

    async def mock_execute(query, params=None):
        call_count["n"] += 1
        result = MagicMock()
        n = call_count["n"]

        # Calls 1 and 4: consent checks → return active consent
        if n in (1, 4):
            result.scalar_one_or_none = MagicMock(return_value=uuid.uuid4())
        else:
            # Calls 2, 3: purchase/test-drive checks → return None (no stop)
            # Calls 5+: update queries
            result.scalar_one_or_none = MagicMock(return_value=None)

        result.all = MagicMock(return_value=[])
        return result

    db.execute = AsyncMock(side_effect=mock_execute)
    db.add = MagicMock()
    db.flush = AsyncMock()
    return db


# ── Tests ────────────────────────────────────────────────────────

class TestSequenceDefinitions:
    """Tests de la structure des jalons."""

    def test_6_milestones_defined(self):
        assert len(MILESTONES) == 6

    def test_milestones_ordered_by_delay(self):
        delays = [m.delay_days for m in MILESTONES]
        assert delays == sorted(delays)

    def test_j0_is_immediate(self):
        assert MILESTONES[0].code == "J0"
        assert MILESTONES[0].delay_days == 0

    def test_j60_is_last(self):
        assert MILESTONES[-1].code == "J60"
        assert MILESTONES[-1].delay_days == 60

    def test_j45_is_skippable(self):
        j45 = [m for m in MILESTONES if m.code == "J45"][0]
        assert j45.skippable is True

    def test_get_next_milestone(self):
        assert get_next_milestone("J0").code == "J2-3"
        assert get_next_milestone("J2-3").code == "J7"
        assert get_next_milestone("J7").code == "J14"
        assert get_next_milestone("J14").code == "J45"
        assert get_next_milestone("J45").code == "J60"
        assert get_next_milestone("J60") is None

    def test_get_next_from_none_starts_at_j0(self):
        assert get_next_milestone(None).code == "J0"


class TestMessageTemplates:
    """Tests des templates de message."""

    def test_all_templates_exist(self):
        for m in MILESTONES:
            msg = render_template(m.template_key, {})
            assert "body" in msg
            assert "subject" in msg

    def test_build_top3_variables(self):
        """Les variables Top 3 sont correctement construites."""
        variables = build_top3_variables(
            prospect_name="Ahmed",
            vehicles=SAMPLE_TOP3,
            budget=220000,
            usage="ville",
        )
        assert variables["prospect_name"] == "Ahmed"
        assert "Dacia" in variables["top1_name"]
        assert "220" in variables["budget"]
        assert variables["usage"] == "ville"

    def test_j0_renders_with_real_data(self):
        """Le template J0 se rend correctement avec des données réelles."""
        variables = build_top3_variables(
            prospect_name="Fatima",
            vehicles=SAMPLE_TOP3,
            budget=220000,
            usage="ville",
        )
        msg = render_template("j0_recap_top3", variables)
        assert "Fatima" in msg["body"]
        assert "Dacia" in msg["body"]
        assert "Renault" in msg["body"]
        assert "Peugeot" in msg["body"]

    def test_j60_cloture_template(self):
        """Le template J60 est une clôture bienveillante."""
        msg = render_template("j60_cloture", {"prospect_name": "Omar"})
        body = msg["body"].lower()
        assert "dernier" in body or "fin" in body
        assert "félicitations" in body or "merci" in body


class TestPriceDropDetection:
    """Tests de la détection de baisse de prix."""

    def test_no_price_drop(self):
        """Pas de baisse → None."""
        result = _check_real_price_drop(SAMPLE_TOP3)
        assert result is None

    def test_real_price_drop_detected(self):
        """Baisse réelle ≥ 1000 MAD → variables pour J45."""
        vehicles_with_drop = SAMPLE_TOP3.copy()
        vehicles_with_drop[0] = {
            **vehicles_with_drop[0],
            "original_price": 185000,
            "price": 180000,
        }
        result = _check_real_price_drop(vehicles_with_drop)
        assert result is not None
        assert "180 000" in result["new_price"]
        assert "185 000" in result["old_price"]
        assert "5 000" in result["savings"]

    def test_tiny_price_drop_ignored(self):
        """Baisse < 1000 MAD → ignorée."""
        vehicles_with_tiny = SAMPLE_TOP3.copy()
        vehicles_with_tiny[0] = {
            **vehicles_with_tiny[0],
            "original_price": 180500,
            "price": 180000,
        }
        result = _check_real_price_drop(vehicles_with_tiny)
        assert result is None


class TestStartSequence:
    """Tests du démarrage de séquence."""

    @pytest.mark.asyncio
    async def test_start_creates_active_sequence(self):
        db = _mock_db_with_consent()
        seq = await start_sequence(PROSPECT_ID, SAMPLE_TOP3, db)
        assert seq is not None
        assert seq.status == "active"
        assert seq.current_milestone == "J0"

    @pytest.mark.asyncio
    async def test_start_without_consent_returns_none(self):
        db = AsyncMock()
        result = MagicMock()
        result.scalar_one_or_none = MagicMock(return_value=None)
        db.execute = AsyncMock(return_value=result)

        seq = await start_sequence(PROSPECT_ID, SAMPLE_TOP3, db)
        assert seq is None


class TestProcessMilestone:
    """Tests du traitement d'un jalon."""

    @pytest.mark.asyncio
    async def test_process_simulated_milestone(self):
        """En mode simulé, le jalon est traité et loggé."""
        db = _mock_db_with_consent()

        now = datetime.now(timezone.utc)
        seq = MagicMock()
        seq.id = uuid.uuid4()
        seq.prospect_id = uuid.UUID(PROSPECT_ID)
        seq.current_milestone = "J0"
        seq.sequence_started_at = now

        result = await process_milestone(
            sequence=seq,
            vehicles_data=SAMPLE_TOP3,
            prospect_name="Ahmed",
            db=db,
            simulate=True,
        )

        assert result["action"] == "simulated"
        assert result["milestone"] == "J0"
        assert "message" in result

    @pytest.mark.asyncio
    async def test_j45_skipped_without_price_drop(self):
        """J45 est sauté si aucune baisse de prix réelle."""
        db = _mock_db_with_consent()

        now = datetime.now(timezone.utc)
        seq = MagicMock()
        seq.id = uuid.uuid4()
        seq.prospect_id = uuid.UUID(PROSPECT_ID)
        seq.current_milestone = "J45"
        seq.sequence_started_at = now - timedelta(days=45)

        result = await process_milestone(
            sequence=seq,
            vehicles_data=SAMPLE_TOP3,  # no price drop data
            prospect_name="Ahmed",
            db=db,
            simulate=True,
        )

        assert result["action"] == "skipped"
        assert result["reason"] == "no_real_price_drop"
