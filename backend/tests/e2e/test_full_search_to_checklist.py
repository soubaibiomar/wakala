import pytest
from httpx import AsyncClient, TimeoutException
from unittest.mock import patch
import time

@pytest.mark.asyncio
@patch("app.ml.nlp_pipeline.llm_extractor._GROQ_CHAT_URL", "http://localhost:9999/invalid")
@patch("app.ml.matching.matching_engine.semantic_search")
@patch("app.ml.matching.matching_engine.compute_collaborative_scores")
@patch("app.ml.trust_engine.trust_score_combiner.analyze_photos")
@patch("app.ml.trust_engine.trust_score_combiner.detect_price_anomaly")
@patch("app.ml.trust_engine.trust_score_combiner.detect_seller_pattern")
async def test_full_search_to_checklist(
    mock_seller, mock_price, mock_photo,
    mock_collab, mock_semantic,
    async_client: AsyncClient, override_get_db, mock_db_session, fake_vehicle_dict, fake_vehicles_list
):
    """
    Test E2E de l'ensemble du pipeline.
    Simule l'utilisateur interagissant via API.
    Mesure le temps global de complétion.
    """
    # 1. Setup All Mocks
    # We patched settings so API key is missing -> triggers fallback immediately
    
    # Qdrant returns 1 vehicle
    mock_semantic.return_value = [fake_vehicle_dict["id"]]
    
    # Neo4j returns collab score
    mock_collab.return_value = ([{"vehicle_id": fake_vehicle_dict["id"], "collaborative_score": 0.8}], False)
    
    # DB mock for matching engine
    from app.models.vehicle import Vehicle
    mock_vehicles = [Vehicle(**v) for v in fake_vehicles_list]
    # For matching_engine query
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = mock_vehicles
    # For checklist query
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = mock_vehicles[0]
    
    # Trust Engine Mocks
    mock_photo.return_value = 60.0
    mock_price.return_value = 50.0
    mock_seller.return_value = 100.0

    start_time = time.time()
    
    # 2. E2E Step 1: Search
    payload = {
        "query": "je veux une voiture économique 200k",
        "page": 1,
        "page_size": 10
    }
    search_response = await async_client.post("/api/search/parse", json=payload)
    assert search_response.status_code == 200
    search_data = search_response.json()
    assert len(search_data) > 0
    vehicle_id = search_data[0]["vehicle_id"]
    
    # 3. E2E Step 2: Checklist
    checklist_response = await async_client.get(f"/api/guided-journey/checklist/{vehicle_id}")
    assert checklist_response.status_code == 200
    checklist_data = checklist_response.json()
    assert "trust_score" in checklist_data
    
    total_time = time.time() - start_time
    
    # On valide que tout s'enchaîne sans casser la donnée
    assert checklist_data["vehicle_id"] == vehicle_id
    assert total_time < 2.0 # Le pipeline complet doit être rapide (surtout avec les fallbacks et mocks)
