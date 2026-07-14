import pytest
from unittest.mock import patch


pytestmark = pytest.mark.integration


class TestRecommendationEndpoint:
    async def test_recommendation_endpoint_reachable(self, async_client, override_get_db, mock_db_session):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []

        payload = {
            "query": "SUV diesel Casablanca",
            "filters": {"fuel_type": "diesel", "body_type": "suv"},
            "page": 1,
            "page_size": 5,
        }
        response = await async_client.post("/api/recommendation/", json=payload)
        assert response.status_code == 200

    async def test_recommendation_returns_valid_structure(self, async_client, override_get_db, mock_db_session):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []

        payload = {
            "query": "voiture pas cher",
            "page": 1,
            "page_size": 3,
        }
        response = await async_client.post("/api/recommendation/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "method" in data

    async def test_recommendation_empty_query(self, async_client, override_get_db, mock_db_session):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []

        payload = {"query": "", "page": 1, "page_size": 5}
        response = await async_client.post("/api/recommendation/", json=payload)
        assert response.status_code == 200

    async def test_recommendation_with_filters(self, async_client, override_get_db, mock_db_session):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []

        payload = {
            "query": "voiture",
            "filters": {"price_min": 10000, "price_max": 50000},
            "page": 1,
            "page_size": 5,
        }
        response = await async_client.post("/api/recommendation/", json=payload)
        assert response.status_code == 200
