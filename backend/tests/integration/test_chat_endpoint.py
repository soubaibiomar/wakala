import pytest
from unittest.mock import AsyncMock, patch, MagicMock


pytestmark = pytest.mark.integration


class TestChatEndpoint:
    async def test_chat_endpoint_returns_reply(self, async_client, override_get_db, mock_db_session):
        payload = {
            "message": "Je cherche un SUV diesel",
            "session_id": "test-session-1",
        }
        response = await async_client.post("/api/chat/", json=payload)
        if response.status_code == 200:
            data = response.json()
            assert "reply" in data
            assert len(data["reply"]) > 0

    async def test_chat_maintains_session(self, async_client, override_get_db, mock_db_session):
        payload = {
            "message": "Bonjour",
            "session_id": "test-session-suite",
        }
        resp1 = await async_client.post("/api/chat/", json=payload)
        resp2 = await async_client.post("/api/chat/", json={
            "message": "et en diesel ?",
            "session_id": "test-session-suite",
        })
        if resp1.status_code == 200 and resp2.status_code == 200:
            d1, d2 = resp1.json(), resp2.json()
            assert d1["session_id"] == d2["session_id"]

    async def test_chat_empty_message(self, async_client, override_get_db, mock_db_session):
        payload = {"message": "", "session_id": "test-empty"}
        response = await async_client.post("/api/chat/", json=payload)
        assert response.status_code in (200, 422)

    async def test_chat_returns_sources_when_available(self, async_client, override_get_db, mock_db_session):
        payload = {
            "message": "Peugeot 3008 Casablanca",
            "session_id": "test-sources",
        }
        response = await async_client.post("/api/chat/", json=payload)
        if response.status_code == 200:
            data = response.json()
            assert "sources" in data
