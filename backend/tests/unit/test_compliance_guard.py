"""
tests/unit/test_compliance_guard.py — Tests du garde-fou anti-hallucination.

Vérifie :
- Véhicule fictif (UUID inexistant) → écarté
- Véhicule avec status='sold' → écarté
- Véhicule avec price=NULL → écarté
- Véhicule valide → conservé
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ml.recommendation.compliance_guard import (
    verify_vehicles_exist,
    filter_recommendations,
    verify_single_vehicle,
)


VALID_ID_1 = "550e8400-e29b-41d4-a716-446655440001"
VALID_ID_2 = "550e8400-e29b-41d4-a716-446655440002"
INVALID_ID = "00000000-0000-0000-0000-000000000999"


def _db_returns(vehicle_uuids: list[str]):
    """Helper: mock DB that returns the given UUIDs."""
    db = AsyncMock()
    rows = [(uuid.UUID(vid),) for vid in vehicle_uuids]
    result = MagicMock()
    result.all = MagicMock(return_value=rows)
    db.execute = AsyncMock(return_value=result)
    return db


class TestVerifyVehiclesExist:

    @pytest.mark.asyncio
    async def test_valid_vehicle_passes(self):
        db = _db_returns([VALID_ID_1])
        result = await verify_vehicles_exist([VALID_ID_1], db)
        assert VALID_ID_1 in result

    @pytest.mark.asyncio
    async def test_invalid_vehicle_rejected(self):
        db = _db_returns([VALID_ID_1])
        result = await verify_vehicles_exist([VALID_ID_1, INVALID_ID], db)
        assert VALID_ID_1 in result
        assert INVALID_ID not in result

    @pytest.mark.asyncio
    async def test_sold_vehicle_excluded(self):
        """DB returns empty → all rejected (simulates sold vehicles)."""
        db = _db_returns([])
        result = await verify_vehicles_exist([VALID_ID_1], db)
        assert result == []

    @pytest.mark.asyncio
    async def test_null_price_excluded(self):
        """DB returns only vehicles with valid price — this is by query design."""
        db = _db_returns([VALID_ID_1])  # only ID_1 has valid price
        result = await verify_vehicles_exist([VALID_ID_1, VALID_ID_2], db)
        assert VALID_ID_1 in result
        assert VALID_ID_2 not in result

    @pytest.mark.asyncio
    async def test_empty_input(self):
        db = _db_returns([])
        result = await verify_vehicles_exist([], db)
        assert result == []

    @pytest.mark.asyncio
    async def test_invalid_uuid_format(self):
        db = _db_returns([])
        result = await verify_vehicles_exist(["not-valid", "also-bad"], db)
        assert result == []


class TestFilterRecommendations:

    @pytest.mark.asyncio
    async def test_filters_invalid_recommendations(self):
        db = _db_returns([VALID_ID_1])
        recs = [
            {"vehicle_id": VALID_ID_1, "score": 85},
            {"vehicle_id": INVALID_ID, "score": 95},
        ]
        filtered = await filter_recommendations(recs, db)
        assert len(filtered) == 1
        assert filtered[0]["vehicle_id"] == VALID_ID_1

    @pytest.mark.asyncio
    async def test_empty_recommendations(self):
        db = _db_returns([])
        filtered = await filter_recommendations([], db)
        assert filtered == []


class TestVerifySingleVehicle:

    @pytest.mark.asyncio
    async def test_valid_single(self):
        db = _db_returns([VALID_ID_1])
        assert await verify_single_vehicle(VALID_ID_1, db) is True

    @pytest.mark.asyncio
    async def test_invalid_single(self):
        db = _db_returns([])
        assert await verify_single_vehicle(INVALID_ID, db) is False
