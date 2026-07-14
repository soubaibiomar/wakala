import pytest


pytestmark = pytest.mark.integration


class TestVisionEndpoint:
    async def test_vision_endpoint_reachable(self, async_client):
        pytest.skip("Module vision pas encore implemente dans les routes API")

    async def test_upload_image_returns_analysis(self, async_client):
        pytest.skip("Necessite endpoint /api/vision et une image test")

    async def test_upload_invalid_file_returns_422(self, async_client):
        pytest.skip("Necessite endpoint /api/vision")

    async def test_damage_detection_in_response(self, async_client):
        pytest.skip("Necessite endpoint /api/vision")
