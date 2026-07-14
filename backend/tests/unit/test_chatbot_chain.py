import pytest

from app.rag.chatbot_chain import (
    SYSTEM_PROMPT,
    _format_vehicle_context,
    _format_graph_context,
    _format_review_context,
    _format_history,
)
from app.rag.conversation_memory import InMemoryConversationMemory
from app.rag.schemas import ChatRequest, ChatResponse, SourceReference


pytestmark = pytest.mark.unit


class TestChatbotSchemas:
    def test_chat_request(self):
        req = ChatRequest(message="Bonjour", session_id="s1", user_id=None)
        assert req.message == "Bonjour"
        assert req.session_id == "s1"

    def test_source_reference(self):
        src = SourceReference(vehicle_id="v1", vehicle_title="Peugeot 3008",
                              relevance_score=0.89, source_type="vector_search")
        assert src.relevance_score == 0.89

    def test_chat_response(self):
        resp = ChatResponse(reply="Bonjour", sources=[], session_id="s1")
        assert resp.reply == "Bonjour"


class TestConversationMemory:
    def test_empty_history(self):
        mem = InMemoryConversationMemory()
        assert mem.get_history("x") == []

    def test_add_turns(self):
        mem = InMemoryConversationMemory()
        mem.add_turn("s", "Bonjour", "Bonjour !")
        mem.add_turn("s", "Je cherche une voiture", "Quel type ?")
        history = mem.get_history("s")
        assert len(history) == 4

    def test_get_last_user_message(self):
        mem = InMemoryConversationMemory()
        mem.add_turn("s", "Hello", "Hi")
        assert mem.get_last_user_message("s") == "Hello"

    def test_clear(self):
        mem = InMemoryConversationMemory()
        mem.add_turn("s", "Hello", "Hi")
        mem.clear("s")
        assert mem.get_history("s") == []

    def test_max_turns_enforced(self):
        mem = InMemoryConversationMemory()
        for i in range(10):
            mem.add_turn("s", f"msg-{i}", f"reply-{i}")
        assert len(mem.get_history("s")) <= 12

    def test_session_isolation(self):
        mem = InMemoryConversationMemory()
        mem.add_turn("s1", "Hello", "Hi")
        mem.add_turn("s2", "Other", "Hey")
        assert len(mem.get_history("s1")) == 2
        assert len(mem.get_history("s2")) == 2


class TestFormatFunctions:
    def test_format_vehicle_context(self):
        vehicles = [{"vehicle_id": "v1", "score": 0.89, "metadata": {
            "brand": "Peugeot", "model": "3008", "year": 2022,
            "price": 28500, "mileage": 45000, "fuel_type": "diesel",
            "body_type": "suv", "city": "Casablanca",
        }}]
        ctx = _format_vehicle_context(vehicles)
        assert "Peugeot" in ctx
        assert "28500" in ctx

    def test_format_vehicle_context_empty(self):
        assert "Aucun vehicule" in _format_vehicle_context([])

    def test_format_graph_context(self):
        enriched = {"v1": {"similar_vehicles": [{"id": "v2", "title": "Renault Captur"}]}}
        popularity = {"v1": 0.92}
        ctx = _format_graph_context(enriched, popularity)
        assert "v1" in ctx

    def test_format_graph_context_empty(self):
        assert "Aucune donnee" in _format_graph_context({}, {})

    def test_format_review_context(self):
        reviews = [{"text": "Excellent vehicule", "rating": 5}]
        ctx = _format_review_context(reviews)
        assert "Excellent" in ctx
        assert "5/5" in ctx

    def test_format_review_context_empty(self):
        assert "Aucun avis" in _format_review_context([])

    def test_format_history(self):
        history = [{"role": "user", "content": "Bonjour"},
                   {"role": "assistant", "content": "Bonjour !"}]
        ctx = _format_history(history)
        assert "Utilisateur" in ctx
        assert "AutoMind" in ctx

    def test_format_history_empty(self):
        assert "Aucun echange" in _format_history([])

    def test_system_prompt_has_anti_hallucination(self):
        has_no_invent = "invente" in SYSTEM_PROMPT.lower()
        assert has_no_invent, "Le prompt systeme doit interdire l'invention"
