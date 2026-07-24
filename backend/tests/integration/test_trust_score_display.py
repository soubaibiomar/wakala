import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
@patch("app.api.routes_guided_journey.compute_trust_score")
async def test_trust_score_display_format(mock_compute, async_client: AsyncClient, override_get_db, mock_db_session, fake_vehicle_dict):
    from app.ml.trust_engine.schemas import TrustScoreResult
    
    # 1. Arrange
    # Mock DB return
    from app.models.vehicle import Vehicle
    v = Vehicle(**fake_vehicle_dict)
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = v
    
    # Mock TrustScoreResult
    mock_compute.return_value = TrustScoreResult(
        vehicle_id=fake_vehicle_dict["id"],
        trust_score=75.5,
        price_anomaly_score=60.0,
        seller_pattern_score=90.0,
        photo_damage_score=80.0,
        confidence="medium"
    )
    
    # 2. Act
    response = await async_client.get(f"/api/guided-journey/checklist/{fake_vehicle_dict['id']}")
    
    # 3. Assert
    assert response.status_code == 200
    data = response.json()
    assert data["trust_score"] == 75.5
    assert data["confidence"] == "medium"
    
    # Check that warning about price anomaly was included because score < 70
    assert any("prix est inhabituellement bas" in item for item in data["checklist"])
    # Check that seller pattern warning is NOT included because score > 70
    assert not any("courtier non déclaré" in item for item in data["checklist"])

@pytest.mark.asyncio
async def test_trust_score_invalid_uuid(async_client: AsyncClient):
    response = await async_client.get("/api/guided-journey/checklist/not-a-uuid")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_trust_score_not_found(async_client: AsyncClient, override_get_db, mock_db_session):
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = None
    
    response = await async_client.get("/api/guided-journey/checklist/550e8400-e29b-41d4-a716-446655440000")
    assert response.status_code == 404
