"""
tests/compliance/test_no_hallucinated_vehicle.py — Vérifie qu'aucune réponse
du chatbot ne mentionne un véhicule qui n'existe pas en base.

Principe directeur : toute réponse mentionnant un véhicule doit être
traçable à un enregistrement réel de la table vehicles.
"""

import re
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from app.ml.recommendation.compliance_guard import (
    verify_vehicles_exist,
    filter_recommendations,
    verify_single_vehicle,
)


# ── Catalogue de test connu ──────────────────────────────────────

KNOWN_VEHICLE_IDS = [
    "550e8400-e29b-41d4-a716-446655440001",
    "550e8400-e29b-41d4-a716-446655440002",
    "550e8400-e29b-41d4-a716-446655440003",
]

FAKE_VEHICLE_ID = "00000000-0000-0000-0000-000000000999"


def _mock_db_with_known_vehicles():
    """Crée un mock DB qui reconnaît les véhicules du catalogue connu."""
    db = AsyncMock()

    async def mock_execute(query):
        result = MagicMock()
        # Simulate: only return IDs that are in KNOWN_VEHICLE_IDS
        known = set(KNOWN_VEHICLE_IDS)
        matched = []
        for kid in known:
            matched.append((uuid.UUID(kid),))
        result.all = MagicMock(return_value=matched)
        return result

    db.execute = AsyncMock(side_effect=mock_execute)
    return db


# ── Tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_known_vehicle_passes_guard():
    """Un véhicule connu du catalogue doit passer le compliance guard."""
    db = _mock_db_with_known_vehicles()
    result = await verify_vehicles_exist(KNOWN_VEHICLE_IDS, db)
    assert len(result) == 3
    for vid in KNOWN_VEHICLE_IDS:
        assert vid in result


@pytest.mark.asyncio
async def test_unknown_vehicle_rejected():
    """Un véhicule inventé (UUID inexistant) doit être écarté."""
    db = _mock_db_with_known_vehicles()
    result = await verify_vehicles_exist(
        [FAKE_VEHICLE_ID, KNOWN_VEHICLE_IDS[0]], db
    )
    # The fake ID should NOT be in the result
    assert FAKE_VEHICLE_ID not in result


@pytest.mark.asyncio
async def test_invalid_uuid_format_rejected():
    """Un ID avec un format invalide doit être écarté silencieusement."""
    db = _mock_db_with_known_vehicles()
    result = await verify_vehicles_exist(["not-a-uuid", "also-invalid"], db)
    assert result == []


@pytest.mark.asyncio
async def test_empty_list_returns_empty():
    """Une liste vide retourne une liste vide."""
    db = _mock_db_with_known_vehicles()
    result = await verify_vehicles_exist([], db)
    assert result == []


@pytest.mark.asyncio
async def test_filter_recommendations_removes_invalid():
    """filter_recommendations ne conserve que les véhicules vérifiés."""
    db = _mock_db_with_known_vehicles()
    recs = [
        {"vehicle_id": KNOWN_VEHICLE_IDS[0], "score": 85},
        {"vehicle_id": FAKE_VEHICLE_ID, "score": 92},  # inventé
        {"vehicle_id": KNOWN_VEHICLE_IDS[1], "score": 78},
    ]
    filtered = await filter_recommendations(recs, db)
    ids = [r["vehicle_id"] for r in filtered]
    assert FAKE_VEHICLE_ID not in ids
    assert KNOWN_VEHICLE_IDS[0] in ids
    assert KNOWN_VEHICLE_IDS[1] in ids


@pytest.mark.asyncio
async def test_sold_vehicle_excluded():
    """
    Un véhicule avec status='sold' ne doit JAMAIS apparaître
    dans les recommandations.
    """
    db = AsyncMock()

    async def mock_execute(query):
        result = MagicMock()
        # Simulate: sold vehicles return empty
        result.all = MagicMock(return_value=[])
        return result

    db.execute = AsyncMock(side_effect=mock_execute)

    result = await verify_vehicles_exist(KNOWN_VEHICLE_IDS, db)
    # All should be rejected because the DB returns nothing
    assert len(result) == 0


@pytest.mark.asyncio
async def test_null_price_vehicle_excluded():
    """Un véhicule avec price=NULL ne doit pas passer le guard."""
    db = AsyncMock()

    async def mock_execute(query):
        result = MagicMock()
        # Only first vehicle has valid price
        result.all = MagicMock(return_value=[
            (uuid.UUID(KNOWN_VEHICLE_IDS[0]),)
        ])
        return result

    db.execute = AsyncMock(side_effect=mock_execute)

    result = await verify_vehicles_exist(KNOWN_VEHICLE_IDS, db)
    assert len(result) == 1
    assert result[0] == KNOWN_VEHICLE_IDS[0]
