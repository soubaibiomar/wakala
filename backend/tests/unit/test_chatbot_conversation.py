from unittest.mock import AsyncMock, patch

import pytest

from app.rag.chatbot_chain import ChatbotChain, NO_MATCH_REPLY
from app.rag.conversation_memory import conversation_memory


pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def clear_conversations():
    conversation_memory._sessions.clear()
    yield
    conversation_memory._sessions.clear()


@pytest.mark.asyncio
async def test_three_turn_conversation_is_grounded_and_keeps_context():
    vehicle = {
        "vehicle_id": "peugeot-3008-1",
        "score": 0.91,
        "metadata": {
            "brand": "Peugeot", "model": "3008", "year": 2022,
            "price": 285000, "mileage": 45000, "fuel_type": "diesel",
            "body_type": "SUV", "city": "Casablanca",
        },
    }
    chain = ChatbotChain()
    fake_llm = AsyncMock()
    fake_llm.ainvoke.return_value.content = "Peugeot 3008 2022, diesel, a Casablanca : 285000 MAD."
    chain._get_llm = lambda: fake_llm

    with patch("app.rag.chatbot_chain.search_vehicles", return_value=[vehicle]) as search, \
         patch("app.rag.chatbot_chain.search_reviews", return_value=[]), \
         patch("app.rag.chatbot_chain.enrich_with_graph", new=AsyncMock(return_value={})), \
         patch("app.rag.chatbot_chain.get_popularity_scores", new=AsyncMock(return_value={})):
        first = await chain.answer("Je cherche un SUV a Casablanca", "conversation-1")
        second = await chain.answer("et en diesel ?", "conversation-1")
        third = await chain.answer("Quel est son prix ?", "conversation-1")

    assert all("Peugeot 3008" in answer.reply for answer in (first, second, third))
    assert all(answer.sources[0].vehicle_id == "peugeot-3008-1" for answer in (first, second, third))
    assert "Je cherche un SUV a Casablanca" in search.call_args_list[1].args[0]
    assert len(conversation_memory.get_history("conversation-1")) == 6


@pytest.mark.asyncio
async def test_empty_retrieval_never_calls_the_llm_or_invents_a_vehicle():
    chain = ChatbotChain()
    with patch("app.rag.chatbot_chain.search_vehicles", return_value=[]), \
         patch("app.rag.chatbot_chain.search_reviews", return_value=[]), \
         patch.object(chain, "_get_llm") as get_llm:
        response = await chain.answer("Montre-moi une voiture volante", "conversation-empty")

    assert response.reply == NO_MATCH_REPLY
    assert response.sources == []
    get_llm.assert_not_called()
