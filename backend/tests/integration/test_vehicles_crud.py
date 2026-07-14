import pytest
from unittest.mock import patch


pytestmark = pytest.mark.integration


class TestVehiclesCRUD:
    async def test_list_vehicles_empty(self, async_client, override_get_db, mock_db_session):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []

        response = await async_client.get("/api/vehicles/")
        assert response.status_code == 200

    async def test_list_vehicles_with_data(self, async_client, override_get_db, mock_db_session,
                                            fake_vehicles_list):
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = fake_vehicles_list

        response = await async_client.get("/api/vehicles/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 3

    async def test_get_vehicle_by_id_not_found(self, async_client, override_get_db, mock_db_session):
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

        response = await async_client.get("/api/vehicles/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    async def test_get_vehicle_by_id_found(self, async_client, override_get_db, mock_db_session,
                                             fake_vehicle_dict):
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = fake_vehicle_dict

        response = await async_client.get("/api/vehicles/550e8400-e29b-41d4-a716-446655440001")
        assert response.status_code == 200
        data = response.json()
        assert data.get("id") == "550e8400-e29b-41d4-a716-446655440001"
