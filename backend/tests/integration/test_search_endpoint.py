import pytest
from httpx import AsyncClient
from app.main import app
from unittest.mock import patch
import time

@pytest.mark.asyncio
@patch("app.api.routes_search.matching_engine.search_with_persona")
async def test_search_endpoint_integration(mock_search):
    # Mocking the internal method just to test the endpoint schema & fast execution
    mock_search.return_value = [
        {"vehicle_id": "123", "match_score": 95.0, "content_score": 50.0, "collaborative_score": 45.0, "badges": ["Économique"]}
    ]
    
    start = time.time()
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/search/parse", json={
            "query": "voiture",
            "page": 1,
            "page_size": 20
        })
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 0.5  # Doit être très rapide avec un mock interne
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["vehicle_id"] == "123"
