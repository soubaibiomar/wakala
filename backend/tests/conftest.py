import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings


@pytest.fixture(scope="session")
def app() -> FastAPI:
    from app.main import app as _app
    return _app


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient, None]:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_db_session():
    """Session mock avec chaîne await execute() → .scalars().all() fonctionnelle.

    Les tests peuvent personnaliser les retours via:
      session.execute.return_value                  → execute_result
      session.execute.return_value.scalars.return_value → scalars_result
      session.execute.return_value.scalars.return_value.all.return_value = [...]
      session.execute.return_value.scalar_one_or_none.return_value = object
      session.execute.return_value.first.return_value = object
    """
    session = AsyncMock(spec=AsyncSession)

    scalars_result = MagicMock()
    scalars_result.all.return_value = []
    scalars_result.first.return_value = None
    scalars_result.scalar_one_or_none.return_value = None
    scalars_result.fetchall.return_value = []

    execute_result = AsyncMock()
    execute_result.scalars = MagicMock(return_value=scalars_result)
    execute_result.scalar = MagicMock(return_value=0)
    execute_result.first = MagicMock(return_value=None)
    execute_result.scalar_one_or_none = MagicMock(return_value=None)
    execute_result.fetchall = MagicMock(return_value=[])
    execute_result.return_value = execute_result  # await → self

    session.execute = AsyncMock(return_value=execute_result)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    session.add_all = MagicMock()
    return session


@pytest.fixture
def override_get_db(app: FastAPI, mock_db_session: AsyncMock):
    async def _get_db_override():
        yield mock_db_session

    app.dependency_overrides.clear()
    from app.core.database import get_db
    app.dependency_overrides[get_db] = _get_db_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def fake_vehicle_dict() -> dict:
    return {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "seller_id": "550e8400-e29b-41d4-a716-446655440099",
        "brand": "Renault",
        "model": "Clio",
        "version": "Intens",
        "year": 2022,
        "mileage": 15000,
        "fuel_type": "diesel",
        "body_type": "citadine",
        "transmission": "manuelle",
        "engine_power_hp": 90,
        "color": "Noir",
        "doors": 5,
        "seats": 5,
        "city": "Casablanca",
        "postal_code": "20000",
        "price": 18500.0,
        "description": "Renault Clio en excellent etat",
        "created_at": "2024-01-15T10:00:00Z",
        "updated_at": "2024-01-15T10:00:00Z",
    }


@pytest.fixture
def fake_vehicles_list() -> list[dict]:
    return [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "seller_id": "550e8400-e29b-41d4-a716-446655440099",
            "brand": "Renault", "model": "Clio", "year": 2022,
            "mileage": 15000, "fuel_type": "diesel", "body_type": "citadine",
            "transmission": "manuelle", "engine_power_hp": 90,
            "city": "Casablanca", "price": 18500.0,
            "doors": 5, "seats": 5,
            "created_at": "2024-01-15T10:00:00Z",
            "updated_at": "2024-01-15T10:00:00Z",
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440002",
            "seller_id": "550e8400-e29b-41d4-a716-446655440099",
            "brand": "Peugeot", "model": "3008", "year": 2021,
            "mileage": 35000, "fuel_type": "diesel", "body_type": "suv",
            "transmission": "automatique", "engine_power_hp": 130,
            "city": "Rabat", "price": 28500.0,
            "doors": 5, "seats": 5,
            "created_at": "2024-01-14T10:00:00Z",
            "updated_at": "2024-01-14T10:00:00Z",
        },
        {
            "id": "550e8400-e29b-41d4-a716-446655440003",
            "seller_id": "550e8400-e29b-41d4-a716-446655440100",
            "brand": "Toyota", "model": "Corolla", "year": 2023,
            "mileage": 8000, "fuel_type": "hybride", "body_type": "berline",
            "transmission": "automatique", "engine_power_hp": 140,
            "city": "Casablanca", "price": 32000.0,
            "doors": 4, "seats": 5,
            "created_at": "2024-01-13T10:00:00Z",
            "updated_at": "2024-01-13T10:00:00Z",
        },
    ]


@pytest.fixture
def fake_user_dict() -> dict:
    return {
        "id": "550e8400-e29b-41d4-a716-446655440099",
        "name": "Test User",
        "email": "test@example.com",
        "phone": "0666666666",
        "role": "buyer",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture(autouse=True)
def mock_external_services():
    with (
        patch("app.rag.chatbot_chain.ChatOpenAI") as mock_openai,
        patch("app.rag.vector_search.search_vehicles") as mock_search,
        patch("app.rag.vector_search.search_reviews") as mock_reviews,
        patch("app.rag.graph_context.enrich_with_graph") as mock_graph,
        patch("app.rag.graph_context.get_popularity_scores") as mock_pop,
    ):
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Reponse test du chatbot."))
        mock_openai.return_value = mock_llm

        mock_search.return_value = []
        mock_reviews.return_value = []
        mock_graph.return_value = {}
        mock_pop.return_value = {}

        yield


@pytest.fixture
def patch_jwt():
    with patch("app.core.security.decode_token") as mock:
        mock.return_value = {
            "sub": "550e8400-e29b-41d4-a716-446655440099",
            "role": "buyer",
        }
        yield mock
