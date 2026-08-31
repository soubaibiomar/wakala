import time
import pytest
from app.services.ai.chat import detect_language
from app.rag.chatbot_chain import _detect_language
from app.rag.conversation_memory import InMemoryConversationMemory, SESSION_TTL_SECONDS


@pytest.mark.unit
def test_detect_language_preserves_darija_on_numeric_input():
    # User previously spoke Darija
    history = [
        {"role": "user", "content": "Salam bghit chi tomobila mzyana"},
        {"role": "assistant", "content": "Marhaba, chhal le budget dyalek ?"},
    ]
    # Follow-up with purely numeric input
    detected = detect_language("180000", history=history)
    assert detected == "darija_lat"


@pytest.mark.unit
def test_detect_language_preserves_arabic_on_short_input():
    history = [
        {"role": "user", "content": "السلام عليكم أريد سيارة عائلية"},
        {"role": "assistant", "content": "أهلاً بك، ما هو ميزانيتك؟"},
    ]
    detected = detect_language("200000", history=history)
    assert detected in ("arabic", "darija_ar")


@pytest.mark.unit
def test_detect_language_preserves_english_on_short_input():
    history = [
        {"role": "user", "content": "Hi, looking for a family SUV"},
        {"role": "assistant", "content": "Great, what is your budget?"},
    ]
    detected = detect_language("300000", history=history)
    assert detected == "english"


@pytest.mark.unit
def test_rag_detect_language_preserves_darija():
    history = [
        {"role": "user", "content": "bghit tomobila rkhisa"},
        {"role": "assistant", "content": "Chhal budget ?"},
    ]
    detected = _detect_language("120000", history=history)
    assert "darija" in detected


@pytest.mark.unit
def test_memory_ttl_expiration():
    memory = InMemoryConversationMemory()
    memory.add_turn("session-temp", "Bonjour", "Bonjour!")
    assert len(memory.get_history("session-temp")) == 2

    # Simulate expired timestamp
    memory._timestamps["session-temp"] = time.time() - (SESSION_TTL_SECONDS + 10)
    
    # Getting history should detect expiration and clear it
    expired_history = memory.get_history("session-temp")
    assert expired_history == []
