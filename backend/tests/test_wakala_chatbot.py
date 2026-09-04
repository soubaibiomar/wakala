import sys
from pathlib import Path
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.schemas import ChatRequest
from app.rag.conversation_memory import InMemoryConversationMemory
from app.rag.chatbot_chain import SYSTEM_PROMPT, chatbot_chain


@pytest.fixture
def mock_langchain():
    with patch("app.rag.chatbot_chain.LANGCHAIN_AVAILABLE", True):
        yield


@pytest.fixture
def mock_get_llm():
    # Mocks settings.OPENROUTER_API_KEY to None and mocks the internal _get_llm of chatbot_chain
    with patch("app.rag.chatbot_chain.settings.OPENROUTER_API_KEY", None):
        with patch.object(chatbot_chain, "_get_llm") as mock_method:
            llm_instance = AsyncMock()
            mock_method.return_value = llm_instance
            yield llm_instance


@pytest.mark.asyncio
async def test_system_prompt_darija_and_09_08():
    """
    Test 1 & 4: Vérifier que le prompt système contient bien les instructions 
    pour la Darija et la conformité Loi 09-08.
    """
    assert "Darija" in SYSTEM_PROMPT
    assert "LOI 09-08" in SYSTEM_PROMPT
    assert "données personnelles" in SYSTEM_PROMPT
    assert "Markdown" in SYSTEM_PROMPT
    assert "MAD" in SYSTEM_PROMPT


@pytest.mark.asyncio
async def test_validation_refusal_for_vague_queries(mock_langchain, mock_get_llm):
    """
    Test 2: Vérifier que si la requête est vague, la validation retourne
    une question de clarification.
    """
    mock_get_llm.ainvoke.return_value = MagicMock(content="Chhal le budget dyalek ?")
    
    question = await chatbot_chain._validate_query("Je veux une voiture", [])
    assert question == "Chhal le budget dyalek ?"

    # Requête avec critères suffisants -> None
    mock_get_llm.ainvoke.return_value = MagicMock(content="OK")
    valid = await chatbot_chain._validate_query("Clio diesel 120000 MAD Casablanca", [])
    assert valid is None


@pytest.mark.asyncio
async def test_markdown_formatting_directive_applied(mock_langchain, mock_get_llm):
    """
    Test 3: Vérifier que si la requête est transmise au LLM, le RAG
    fonctionne correctement et extrait les sources.
    """
    mock_get_llm.ainvoke.return_value = MagicMock(content="- Moteur: 1.5 dCi\n- Consommation: 4.5L/100km")
    
    with patch("app.rag.chatbot_chain.search_vehicles") as mock_search_vehicles:
        mock_search_vehicles.return_value = [
            {
                "vehicle_id": "v1", 
                "score": 0.95, 
                "metadata": {
                    "brand": "Dacia", 
                    "model": "Duster", 
                    "price": 120000,
                    "images": ["http://image.url"]
                }
            }
        ]
        
        with patch("app.rag.chatbot_chain.search_reviews") as mock_search_reviews:
            mock_search_reviews.return_value = []
            with patch("app.rag.chatbot_chain.enrich_with_graph", new_callable=AsyncMock) as mock_graph:
                mock_graph.return_value = {}
                with patch("app.rag.chatbot_chain.get_popularity_scores", new_callable=AsyncMock) as mock_pop:
                    mock_pop.return_value = {}
                    response = await chatbot_chain.answer("Dacia Duster a Casablanca", "session-precise")
                    
                    assert "- Moteur:" in response.reply
                    assert len(response.sources) == 1
                    assert response.sources[0].vehicle_id == "v1"
                    assert response.sources[0].image_url == "http://image.url"
                    assert response.sources[0].price == "120000"
                    mock_search_vehicles.assert_called_once()
