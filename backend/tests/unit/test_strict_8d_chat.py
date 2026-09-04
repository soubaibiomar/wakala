import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from app.services.ai.chat import (
    get_fallback_discovery_question,
    CONSULTATIVE_DISCOVERY_CONTEXTS,
)


def test_consultative_discovery_contexts_strictly_8d():
    """Verify that all consultative discovery contexts explicitly require the 8 Wakala Dimensions."""
    for lang in ["french", "english", "arabic", "darija_ar", "darija_lat"]:
        prompt = CONSULTATIVE_DISCOVERY_CONTEXTS[lang]
        assert "8 Dimensions" in prompt or "8D" in prompt or "الأبعاد الثمانية" in prompt
        # Verify non-8D isolated gearbox question is not present in steps
        assert "Etape 4 (Boîte" not in prompt
        assert "Turn 4 (Transmission" not in prompt


def test_fallback_progression_strictly_8d():
    """Verify that the discovery fallback strictly evaluates the 8 dimensions in order."""
    # 1. Budget missing -> asks for Budget (prix_acces)
    q1 = get_fallback_discovery_question("french", "Je cherche une voiture")
    assert "budget maximum" in q1.lower()

    # 2. Budget provided -> asks for Urban Practicality (praticite_urbaine)
    q2 = get_fallback_discovery_question("french", "Budget 200 000 MAD")
    assert "format compact" in q2.lower() or "garer en ville" in q2.lower()

    # 3. Usage provided -> asks for Space / Luggage (espace)
    q3 = get_fallback_discovery_question("french", "Budget 200 000 MAD pour la ville")
    assert "valises" in q3.lower() or "places" in q3.lower() or "coffre" in q3.lower()

    # 4. Space provided -> asks for Clean Ecology / Running costs (ecologie / cout_reel)
    q4 = get_fallback_discovery_question("french", "Budget 200 000 MAD pour la ville, coffre 3 valises")
    assert "hybride" in q4.lower() or "électrique" in q4.lower() or "consommation" in q4.lower()

    # 5. Eco provided -> asks for Safety NCAP (securite)
    q5 = get_fallback_discovery_question("french", "Budget 200 000 MAD pour la ville, coffre 3 valises, moteur hybride propre")
    assert "sécurité" in q5.lower() or "ncap" in q5.lower()

    # 6. Safety provided -> asks for Motricity / 4x4 (motricite)
    q6 = get_fallback_discovery_question("french", "Budget 200 000 MAD pour la ville, coffre 3 valises, moteur hybride propre, sécurité 5 étoiles")
    assert "4x4" in q6.lower() or "intégrale" in q6.lower() or "motricité" in q6.lower()

    # 7. Motricity provided -> asks for Performance (performance)
    q7 = get_fallback_discovery_question("french", "Budget 200 000 MAD pour la ville, coffre 3 valises, hybride propre, sécurité 5 étoiles, 2 roues motrices")
    assert "puissance" in q7.lower() or "reprises" in q7.lower() or "accélération" in q7.lower()

    # 8. All 8D covered -> Final recommendations
    q8 = get_fallback_discovery_question("french", "Budget 200 000 MAD pour la ville, coffre 3 valises, hybride propre, sécurité 5 étoiles, 2 roues motrices, puissance modérée")
    assert "8 dimensions" in q8.lower()


def test_fallback_progression_in_all_languages():
    """Verify fallback discovery questions in english, arabic and darija."""
    en_q = get_fallback_discovery_question("english", "I want to buy a car")
    assert "budget" in en_q.lower()

    ar_q = get_fallback_discovery_question("arabic", "أبحث عن سيارة")
    assert "ميزانيتك" in ar_q

    darija_q = get_fallback_discovery_question("darija_ar", "بغيت نشري طوموبيل")
    assert "الميزانية" in darija_q
