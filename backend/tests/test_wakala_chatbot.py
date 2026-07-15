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
    # Mocks the internal _get_llm of chatbot_chain
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
    Test 2: Vérifier que si la requête est vague, la validation bloque et retourne
    une question de clarification sans appeler Qdrant.
    """
    # Mock du LLM pour la validation de requête qui décide que c'est vague
    mock_get_llm.ainvoke.return_value.content = "Chhal le budget dyalek ?"
    
    with patch("app.rag.chatbot_chain.search_vehicles") as mock_search_vehicles:
        response = await chatbot_chain.answer("Je veux une voiture", "session-vague")
        
        # Le bot doit retourner la question de clarification
        assert response.reply == "Chhal le budget dyalek ?"
        # search_vehicles ne doit PAS être appelé car la validation a échoué
        mock_search_vehicles.assert_not_called()


@pytest.mark.asyncio
async def test_markdown_formatting_directive_applied(mock_langchain, mock_get_llm):
    """
    Test 3: Vérifier que si la requête est précise, le LLM est appelé et le RAG
    fonctionne correctement avec le prompt exigeant du Markdown.
    """
    # Etape 1: La validation LLM dit "OK" (requête assez précise)
    # Etape 2: Le LLM final répond avec du Markdown
    mock_get_llm.ainvoke.side_effect = [
        MagicMock(content="OK"),
        MagicMock(content="- Moteur: 1.5 dCi\n- Consommation: 4.5L/100km")
    ]
    
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
            
            response = await chatbot_chain.answer("Dacia Duster a Casablanca", "session-precise")
            
            assert "- Moteur:" in response.reply
            assert len(response.sources) == 1
            assert response.sources[0].vehicle_id == "v1"
            assert response.sources[0].image_url == "http://image.url"
            assert response.sources[0].price == "120000"
            mock_search_vehicles.assert_called_once()
