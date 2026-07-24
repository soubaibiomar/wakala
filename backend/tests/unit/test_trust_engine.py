import pytest
import asyncio
import time
from unittest.mock import patch, AsyncMock
from app.ml.trust_engine.trust_score_combiner import compute_trust_score
from app.models.vehicle import Vehicle

@pytest.fixture
def sample_vehicle():
    return Vehicle(
        id="123",
        price=100000,
        year=2020,
        mileage=50000,
        engine_power_hp=100,
        doors=5,
        seats=5,
        brand="Renault",
        model="Clio",
        fuel_type="diesel",
        body_type="citadine",
        transmission="manuelle",
        city="Casablanca"
    )

@pytest.mark.asyncio
@patch("app.ml.trust_engine.trust_score_combiner.analyze_photos")
@patch("app.ml.trust_engine.trust_score_combiner.detect_price_anomaly")
@patch("app.ml.trust_engine.trust_score_combiner.detect_seller_pattern")
async def test_trust_engine_parallel_execution(mock_seller, mock_price, mock_photo, sample_vehicle):
    # Simulate slow IO for each task
    async def slow_mock_1(*args, **kwargs):
        await asyncio.sleep(0.2)
        return 90.0
        
    async def slow_mock_2(*args, **kwargs):
        await asyncio.sleep(0.3)
        return 80.0
        
    async def slow_mock_3(*args, **kwargs):
        await asyncio.sleep(0.2)
        return 95.0
        
    mock_photo.side_effect = slow_mock_1
    mock_price.side_effect = slow_mock_2
    mock_seller.side_effect = slow_mock_3
    
    start_time = time.time()
    result = await compute_trust_score(sample_vehicle)
    elapsed = time.time() - start_time
    
    # If sequential, elapsed > 0.7s
    # If parallel, elapsed ~ 0.3s
    assert elapsed < 0.5
    
    assert result.trust_score > 0
    assert result.confidence == "high" # 3 signals present

@pytest.mark.asyncio
@patch("app.ml.trust_engine.trust_score_combiner.analyze_photos")
@patch("app.ml.trust_engine.trust_score_combiner.detect_price_anomaly")
@patch("app.ml.trust_engine.trust_score_combiner.detect_seller_pattern")
async def test_trust_engine_missing_photos(mock_seller, mock_price, mock_photo, sample_vehicle):
    mock_photo.return_value = None # Pas de photos
    mock_price.return_value = 100.0
    mock_seller.return_value = 100.0
    
    result = await compute_trust_score(sample_vehicle)
    
    # Le score doit être calculé sur la base de 0.8 de poids total, ramené à 100% de 100.0 => 100.0
    # Et la confidence doit être "medium" car le poids total est 0.8 (>= 0.6)
    assert result.confidence == "medium"
    assert result.photo_damage_score is None
    assert result.trust_score == 100.0 # (100*0.4 + 100*0.4) / 0.8 = 100
    
@pytest.mark.asyncio
@patch("app.ml.trust_engine.trust_score_combiner.analyze_photos")
@patch("app.ml.trust_engine.trust_score_combiner.detect_price_anomaly")
@patch("app.ml.trust_engine.trust_score_combiner.detect_seller_pattern")
async def test_trust_engine_price_anomaly(mock_seller, mock_price, mock_photo, sample_vehicle):
    mock_photo.return_value = 90.0
    mock_price.return_value = 20.0 # Anomalie forte
    mock_seller.return_value = 100.0
    
    result = await compute_trust_score(sample_vehicle)
    
    # (90*0.2 + 20*0.4 + 100*0.4) / 1.0 = (18 + 8 + 40) = 66
    assert result.trust_score == 66.0
