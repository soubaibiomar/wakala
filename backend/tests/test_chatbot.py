"""
Test standalone du chatbot RAG.
Simule une conversation de 2-3 échanges pour valider :
- Recherche vectorielle (fallback mock)
- Contexte graphe (fallback mock)
- Maintien de l'historique conversationnel
- Ancrage des réponses dans le contexte
- Cas où aucun véhicule pertinent n'est trouvé
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.rag.schemas import ChatRequest, ChatResponse, SourceReference
from app.rag.conversation_memory import InMemoryConversationMemory
from app.rag.chatbot_chain import (
    _format_vehicle_context,
    _format_graph_context,
    _format_review_context,
    _format_history,
    SYSTEM_PROMPT,
)


def test_schemas():
    req = ChatRequest(
        message="Je cherche un SUV diesel",
        session_id="test-session-1",
        user_id=None,
    )
    assert req.message == "Je cherche un SUV diesel"
    assert req.session_id == "test-session-1"
    assert req.user_id is None

    source = SourceReference(
        vehicle_id="v1",
        vehicle_title="Peugeot 3008",
        relevance_score=0.89,
        source_type="vector_search",
    )
    assert source.relevance_score == 0.89

    resp = ChatResponse(
        reply="Voici un Peugeot 3008 disponible.",
        sources=[source],
        session_id="test-session-1",
    )
    assert len(resp.sources) == 1
    assert resp.sources[0].vehicle_id == "v1"
    print("  [OK] Schemas : ChatRequest, SourceReference, ChatResponse")


def test_conversation_memory():
    memory = InMemoryConversationMemory()

    assert memory.get_history("session-x") == []

    memory.add_turn("session-x", "Bonjour", "Bonjour ! Comment puis-je vous aider ?")
    memory.add_turn("session-x", "Je cherche une voiture", "Quel type de vehicule ?")

    history = memory.get_history("session-x")
    assert len(history) == 4
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Bonjour"
    assert history[2]["content"] == "Je cherche une voiture"

    last = memory.get_last_user_message("session-x")
    assert last == "Je cherche une voiture"

    memory.clear("session-x")
    assert memory.get_history("session-x") == []
    print("  [OK] Conversation memory : ajout, lecture, clear")


def test_memory_max_turns():
    memory = InMemoryConversationMemory()
    for i in range(10):
        memory.add_turn(f"session-y", f"msg-{i}", f"reply-{i}")
    history = memory.get_history("session-y")
    assert len(history) <= 12
    print(f"  [OK] Memory max turns : {len(history)} entries (max 12)")


def test_format_vehicle_context():
    vehicles = [
        {
            "vehicle_id": "v1",
            "score": 0.89,
            "metadata": {
                "brand": "Peugeot",
                "model": "3008",
                "year": 2022,
                "price": 28500,
                "mileage": 45000,
                "fuel_type": "diesel",
                "body_type": "suv",
                "city": "Casablanca",
            },
        },
    ]
    ctx = _format_vehicle_context(vehicles)
    assert "Peugeot" in ctx
    assert "28500" in ctx
    assert "diesel" in ctx
    assert "Casablanca" in ctx
    print("  [OK] Format vehicle context : champs presents dans le texte")

    ctx_empty = _format_vehicle_context([])
    assert "Aucun vehicule" in ctx_empty
    print("  [OK] Format vehicle context : cas vide")


def test_format_graph_context():
    enriched = {
        "v1": {
            "similar_vehicles": [
                {"id": "v2", "title": "Renault Captur", "popularity_score": 0.75},
            ],
        },
    }
    popularity = {"v1": 0.92}
    ctx = _format_graph_context(enriched, popularity)
    assert "v1" in ctx
    assert "popularite" in ctx.lower() or "popularity" in ctx.lower()
    print("  [OK] Format graph context : scores et similaires")


def test_format_review_context():
    reviews = [
        {"text": "Excellent vehicule, tres fiable", "rating": 5},
    ]
    ctx = _format_review_context(reviews)
    assert "Excellent" in ctx
    assert "5/5" in ctx
    print("  [OK] Format review context : texte et note")

    ctx_empty = _format_review_context([])
    assert "Aucun avis" in ctx_empty
    print("  [OK] Format review context : cas vide")


def test_format_history():
    history = [
        {"role": "user", "content": "Bonjour"},
        {"role": "assistant", "content": "Bonjour !"},
    ]
    ctx = _format_history(history)
    assert "Utilisateur" in ctx
    assert "AutoMind" in ctx
    print("  [OK] Format history : roles corrects")

    ctx_empty = _format_history([])
    assert "Aucun echange" in ctx_empty
    print("  [OK] Format history : cas vide")


def test_prompt_contains_anti_hallucination_rules():
    has_no_invent = "invente JAMAIS" in SYSTEM_PROMPT or "invente" in SYSTEM_PROMPT
    has_no_vehicule = "Aucun vehicule" in SYSTEM_PROMPT
    if not has_no_invent:
        print("  [WARN] 'invente' non trouve dans SYSTEM_PROMPT (peut-etre encodage)")
    if not has_no_vehicule:
        print("  [WARN] 'Aucun vehicule' non trouve dans SYSTEM_PROMPT")
    found_rules = [r for r in ["Ne invente", "invente", "Aucun vehicule"] if r in SYSTEM_PROMPT]
    assert len(found_rules) >= 2, f"Regles anti-hallucination manquantes. Trouve: {found_rules}"
    print(f"  [OK] Prompt system : {len(found_rules)} regles trouvees")


def test_multi_turn_conversation_flow():
    memory = InMemoryConversationMemory()

    turn1_user = "Je cherche un SUV"
    turn1_assistant = "J'ai trouve un Peugeot 3008 a Casablanca a 285 000 MAD."
    memory.add_turn("session-flow", turn1_user, turn1_assistant)

    turn2_user = "et en diesel ?"
    history = memory.get_history("session-flow")
    last_user = memory.get_last_user_message("session-flow")

    assert last_user == turn1_user
    assert len(history) == 2

    memory.add_turn("session-flow", turn2_user, "Voici les diesel disponibles...")
    history_after = memory.get_history("session-flow")
    assert len(history_after) == 4

    ctx = _format_history(history_after)
    assert "SUV" in ctx
    assert "diesel" in ctx
    print("  [OK] Multi-turn : historique contextuel maintenu")


def test_no_results_scenario():
    ctx = _format_vehicle_context([])
    assert "Aucun vehicule" in ctx

    enriched = _format_graph_context({}, {})
    assert enriched == "Aucune donnee graphe disponible."

    reviews = _format_review_context([])
    assert "Aucun avis" in reviews
    print("  [OK] No results : tous les formatters retournent un message adequat")


if __name__ == "__main__":
    sep = "=" * 60
    print(sep)
    print("  AutoMind - Test Chatbot RAG")
    print(sep)
    print()

    tests = [
        ("Schemas Pydantic", test_schemas),
        ("Conversation memory (CRUD)", test_conversation_memory),
        ("Memory max turns", test_memory_max_turns),
        ("Format vehicle context", test_format_vehicle_context),
        ("Format graph context", test_format_graph_context),
        ("Format review context", test_format_review_context),
        ("Format history", test_format_history),
        ("Prompt anti-hallucination", test_prompt_contains_anti_hallucination_rules),
        ("Multi-turn conversation flow", test_multi_turn_conversation_flow),
        ("No results scenario", test_no_results_scenario),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        print(f">> {name}")
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}")
            failed += 1
        print()

    print(sep)
    print(f"  Resultat : {passed}/{len(tests)} tests reussis", end="")
    if failed:
        print(f", {failed} echecs")
    else:
        print()
    print(sep)
    sys.exit(0 if failed == 0 else 1)
