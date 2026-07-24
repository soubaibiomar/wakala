import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
@patch("app.api.routes_guided_journey.compute_trust_score")
@patch("app.api.routes_search.matching_engine.search_with_persona")
async def test_guided_journey_integration_success(mock_search, mock_compute, async_client: AsyncClient, override_get_db, mock_db_session, fake_vehicle_dict):
    """
    Test d'intégration du parcours accompagné complet (avec services mockés).
    Vérifie le lien entre la recherche et la checklist.
    """
    # 1. Recherche
    mock_search.return_value = [
        {"vehicle_id": fake_vehicle_dict["id"], "match_score": 90.0, "content_score": 50.0, "collaborative_score": 40.0, "badges": ["Économique"]}
    ]
    
    payload = {
        "query": "je cherche une voiture pas chere",
        "page": 1,
        "page_size": 10
    }
    
    search_response = await async_client.post("/api/search/parse", json=payload)
    assert search_response.status_code == 200
    search_data = search_response.json()
    
    assert len(search_data) == 1
    vehicle_id = search_data[0]["vehicle_id"]
    
    # 2. Checklist pour le véhicule trouvé
    from app.models.vehicle import Vehicle
    from app.ml.trust_engine.schemas import TrustScoreResult
    
    v = Vehicle(**fake_vehicle_dict)
    mock_db_session.execute.return_value.scalar_one_or_none.return_value = v
    
    mock_compute.return_value = TrustScoreResult(
        vehicle_id=vehicle_id,
        trust_score=40.0,
        price_anomaly_score=30.0, # low score -> warning
        seller_pattern_score=50.0, # low score -> warning
        photo_damage_score=85.0,
        confidence="medium"
    )
    
    checklist_response = await async_client.get(f"/api/guided-journey/checklist/{vehicle_id}")
    assert checklist_response.status_code == 200
    checklist_data = checklist_response.json()
    
    assert checklist_data["trust_score"] == 40.0
    # On vérifie que la checklist contient les points de vigilance liés aux scores faibles
    warnings = [item for item in checklist_data["checklist"] if item.startswith("⚠️")]
    assert len(warnings) == 2 # Price & Seller
