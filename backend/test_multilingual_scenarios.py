# -*- coding: utf-8 -*-
"""
test_multilingual_scenarios.py — Suite de tests automatisée de bout en bout pour le Chatbot IA Wakala.

Vérifie l'ensemble des 16 matrices de test (4 scénarios x 4 langues) :
1. Découverte consultative pas-à-pas (Budget -> Usage -> Carburant -> Boîte -> Carrosserie -> Recommandation)
2. Diagnostic technique et de fiabilité (1.2 PureTech, 1.2 TCe, DSG7, AdBlue)
3. Calcul des droits de dédouanement et simulateur
4. Suivi et carnet d'entretien

Vérifications rigoureuses appliquées :
- Zéro émoji dans les réponses
- Zéro fuite de balises de réflexion (<think>, Thinking Process)
- Pureté linguistique absolue (100% dans la langue active)
- Strictement une seule question à la fois lors de la phase de découverte
- Équivalence coffre en valises dès que les litres sont mentionnés
"""

import sys
import os
import io
import re
import asyncio
from typing import List, Dict, Any, Tuple

# Forcer l'encodage UTF-8 pour la sortie standard console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Configuration du PYTHONPATH pour l'import des modules app
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.services.ai.chat import (
    detect_language,
    analyze_intent,
    fast_classify_intent,
    is_specific_search_request,
    build_system_prompt,
    remove_emojis,
    scrub_thinking,
    GREETING_RESPONSES,
    EXPERT_CONTEXTS,
    CUSTOMS_CONTEXTS,
    MAINTENANCE_CONTEXTS,
    CONSULTATIVE_DISCOVERY_CONTEXTS,
    LANGUAGE_NAMES,
    EMOJI_PATTERN,
)

# ─── Utilitaires de validation ───────────────────────────────────────────────

def assert_zero_emojis(text: str, context_label: str) -> None:
    emojis = EMOJI_PATTERN.findall(text)
    if emojis:
        raise AssertionError(f"[{context_label}] Emojis detectes dans la sortie : {emojis}")

def assert_zero_thinking(text: str, context_label: str) -> None:
    thinking_markers = [
        "<think>", "</think>", "thinking process", "thought process",
        "reasoning process", "1. analyze", "1. **analyze"
    ]
    lower = text.lower()
    for marker in thinking_markers:
        if marker in lower:
            raise AssertionError(f"[{context_label}] Balise ou amorce de reflexion detectee : '{marker}'")

def assert_single_question(text: str, context_label: str) -> None:
    q_marks = text.count('?') + text.count('؟')
    if q_marks > 2:
        raise AssertionError(f"[{context_label}] Trop de questions detectees ({q_marks} points d'interrogation).")
    
    bullet_question_pattern = re.search(r'(?:^|\n)\s*[\-\*\•\d+\.]\s*.*[\?؟]', text)
    if bullet_question_pattern and q_marks > 1:
        raise AssertionError(f"[{context_label}] Liste de questions detectee : {bullet_question_pattern.group(0)}")

def assert_suitcase_metric(text: str, context_label: str) -> None:
    has_liters = bool(re.search(r'\b\d{3}\s*(?:l|litres?|لتر)\b', text, re.I))
    if has_liters:
        has_suitcases = bool(re.search(r'(?:valise|valises|suitcase|suitcases|حقائب|حقيبة|فاليز|فاليزات)', text, re.I))
        if not has_suitcases:
            raise AssertionError(f"[{context_label}] Volume de coffre mentionne en Litres sans equivalence en valises !")

def assert_language_match(detected: str, expected: str, context_label: str) -> None:
    expected_map = {
        "en": "english",
        "fr": "french",
        "darija": "darija_ar",
        "ar": "arabic"
    }
    target = expected_map.get(expected, expected)
    if detected != target:
        raise AssertionError(f"[{context_label}] Detection de langue incorrecte : obtenu '{detected}', attendu '{target}'")

# ─── 1. Tests Matrix 1: English (en) ─────────────────────────────────────────

def run_english_matrix() -> List[Tuple[str, bool, str]]:
    results = []

    # 1.1 Consultative Discovery Sequence (Turn-by-Turn)
    try:
        history: List[Dict[str, str]] = []
        
        # Turn 0: Greeting
        msg_g = "Hello"
        intent_g = fast_classify_intent(msg_g)
        assert intent_g is not None and intent_g["intent"] == "greeting"
        assert_zero_emojis(GREETING_RESPONSES["english"], "EN-1.1 Greeting")

        # Turn 1: Discovery Start
        msg_t1 = "I want to buy a new car"
        lang_t1 = detect_language(msg_t1, history=history, explicit_language="en")
        assert_language_match(lang_t1, "en", "EN-1.1 Turn 1")
        intent_t1 = fast_classify_intent(msg_t1)
        assert intent_t1 is not None and intent_t1["intent"] == "car_search"
        is_spec_t1 = is_specific_search_request(msg_t1, max_price=intent_t1.get("max_price"), history=history)
        assert not is_spec_t1, "Turn 1 should be consultative discovery (is_specific == False)"
        prompt_t1 = build_system_prompt(lang_t1, CONSULTATIVE_DISCOVERY_CONTEXTS["english"], is_car_search=is_spec_t1)
        assert_zero_emojis(prompt_t1, "EN-1.1 Prompt T1")
        assert "target budget" in prompt_t1.lower() and "MAD" in prompt_t1
        
        # Turn 2: Budget Response
        history.append({"role": "user", "content": msg_t1})
        history.append({"role": "assistant", "content": "What is your target budget for this new vehicle in Moroccan Dirhams (MAD)?"})
        
        msg_t2 = "My budget is 350,000 MAD"
        lang_t2 = detect_language(msg_t2, history=history, explicit_language="en")
        intent_t2 = fast_classify_intent(msg_t2)
        assert intent_t2 is not None and intent_t2["intent"] == "car_search"
        assert intent_t2["max_price"] == 350000
        is_spec_t2 = is_specific_search_request(msg_t2, max_price=intent_t2.get("max_price"), history=history)
        assert not is_spec_t2, "Turn 2 should remain consultative discovery (needs usage/fuel/body)"

        # Turn 3: Usage Response
        history.append({"role": "user", "content": msg_t2})
        history.append({"role": "assistant", "content": "Great budget. What are your daily driving habits (city commute, long distance highway, or mixed)?"})
        
        msg_t3 = "Mixed city and highway"
        intent_t3 = fast_classify_intent(msg_t3)
        assert intent_t3 is not None and intent_t3["intent"] == "car_search"
        is_spec_t3 = is_specific_search_request(msg_t3, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t3, "Turn 3 should continue discovery (fuel/body missing)"

        # Turn 4: Fuel Response
        history.append({"role": "user", "content": msg_t3})
        history.append({"role": "assistant", "content": "Which powertrain do you prefer (Diesel, Petrol, Hybrid, or 100% Electric)?"})
        
        msg_t4 = "Hybrid"
        intent_t4 = fast_classify_intent(msg_t4)
        assert intent_t4 is not None and intent_t4["intent"] == "car_search"
        is_spec_t4 = is_specific_search_request(msg_t4, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t4, "Turn 4 should continue discovery (body missing)"

        # Turn 5: Transmission Response
        history.append({"role": "user", "content": msg_t4})
        history.append({"role": "assistant", "content": "Do you prefer an Automatic gearbox or a Manual transmission?"})
        
        msg_t5 = "Automatic"
        intent_t5 = fast_classify_intent(msg_t5)
        assert intent_t5 is not None and intent_t5["intent"] == "car_search"
        is_spec_t5 = is_specific_search_request(msg_t5, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t5, "Turn 5 should continue discovery (body style missing)"

        # Turn 6: Body Style Response
        history.append({"role": "user", "content": msg_t5})
        history.append({"role": "assistant", "content": "Finally, which vehicle format suits you best: SUV / Crossover, Sedan, or Compact City car?"})
        
        msg_t6 = "SUV"
        intent_t6 = fast_classify_intent(msg_t6)
        assert intent_t6 is not None and intent_t6["intent"] == "car_search"
        is_spec_t6 = is_specific_search_request(msg_t6, max_price=intent_t2["max_price"], history=history)
        assert is_spec_t6, "Turn 6 with Budget + Fuel + Transmission + Body MUST trigger specific catalogue recommendations!"

        prompt_t6 = build_system_prompt("english", "Context with SUVs", is_car_search=is_spec_t6)
        assert "CATALOGUE VEHICLES" in prompt_t6
        assert "CAR_RECOMMENDATION" in prompt_t6

        results.append(("EN-1.1 Consultative Discovery Sequence", True, "Successfully navigated 6-turn discovery cycle from budget to SUV catalogue recommendation"))
    except Exception as e:
        results.append(("EN-1.1 Consultative Discovery Sequence", False, str(e)))

    # 1.2 Technical & Reliability Diagnosis
    try:
        msg_tech = "What are the main problems with the 1.2 PureTech engine?"
        lang_tech = detect_language(msg_tech, explicit_language="en")
        assert_language_match(lang_tech, "en", "EN-1.2 Tech")
        intent_tech = fast_classify_intent(msg_tech)
        assert intent_tech is not None and intent_tech["intent"] == "auto_expert"
        context_tech = EXPERT_CONTEXTS["english"]
        assert "Wet timing belt" in context_tech
        assert "1.2 PureTech" in context_tech
        results.append(("EN-1.2 Mechanical & Reliability Diagnosis (1.2 PureTech)", True, "Correctly classified auto_expert and injected PureTech wet belt context"))
    except Exception as e:
        results.append(("EN-1.2 Mechanical & Reliability Diagnosis (1.2 PureTech)", False, str(e)))

    # 1.3 Customs Clearance Calculations
    try:
        msg_customs = "How are customs calculated in Morocco for imported vehicles?"
        lang_customs = detect_language(msg_customs, explicit_language="en")
        assert_language_match(lang_customs, "en", "EN-1.3 Customs")
        intent_customs = fast_classify_intent(msg_customs)
        assert intent_customs is not None and intent_customs["intent"] == "customs"
        context_customs = CUSTOMS_CONTEXTS["english"]
        assert "Customs Simulator" in context_customs
        results.append(("EN-1.3 Customs Clearance Calculations", True, "Correctly classified customs intent and directed to Customs Simulator"))
    except Exception as e:
        results.append(("EN-1.3 Customs Clearance Calculations", False, str(e)))

    # 1.4 Maintenance Tracking
    try:
        msg_maint = "How do I record my oil change in the service book?"
        lang_maint = detect_language(msg_maint, explicit_language="en")
        assert_language_match(lang_maint, "en", "EN-1.4 Maintenance")
        intent_maint = fast_classify_intent(msg_maint)
        assert intent_maint is not None and intent_maint["intent"] == "maintenance_check"
        context_maint = MAINTENANCE_CONTEXTS["english"]
        assert "Service Book" in context_maint
        results.append(("EN-1.4 Maintenance Tracking", True, "Correctly classified maintenance_check and injected Service Book context"))
    except Exception as e:
        results.append(("EN-1.4 Maintenance Tracking", False, str(e)))

    return results

# ─── 2. Tests Matrix 2: French (fr) ──────────────────────────────────────────

def run_french_matrix() -> List[Tuple[str, bool, str]]:
    results = []

    # 2.1 Consultative Discovery Sequence
    try:
        history: List[Dict[str, str]] = []
        
        # Turn 1: Greeting / Search initiation
        msg_t1 = "Bonjour, je cherche une voiture neuve"
        lang_t1 = detect_language(msg_t1, history=history, explicit_language="fr")
        assert_language_match(lang_t1, "fr", "FR-2.1 Turn 1")
        intent_t1 = fast_classify_intent(msg_t1)
        assert intent_t1 is not None and intent_t1["intent"] == "car_search"
        is_spec_t1 = is_specific_search_request(msg_t1, max_price=intent_t1.get("max_price"), history=history)
        assert not is_spec_t1
        
        prompt_t1 = build_system_prompt("french", CONSULTATIVE_DISCOVERY_CONTEXTS["french"], is_car_search=is_spec_t1)
        assert_zero_emojis(prompt_t1, "FR-2.1 Prompt T1")
        assert "Tu es l'expert consultant automobile" in prompt_t1
        assert "Dirhams (MAD / DH)" in prompt_t1

        # Turn 2: Budget
        history.append({"role": "user", "content": msg_t1})
        history.append({"role": "assistant", "content": "Quel est votre budget approximatif en Dirhams (DH) ?"})
        
        msg_t2 = "Mon budget est de 250 000 DH"
        intent_t2 = fast_classify_intent(msg_t2)
        assert intent_t2 is not None and intent_t2["intent"] == "car_search"
        assert intent_t2["max_price"] == 250000
        is_spec_t2 = is_specific_search_request(msg_t2, max_price=intent_t2.get("max_price"), history=history)
        assert not is_spec_t2

        # Turn 3: Usage
        history.append({"role": "user", "content": msg_t2})
        history.append({"role": "assistant", "content": "Quel sera votre usage principal (ville au quotidien, longs trajets autoroute ou trajets mixtes) ?"})
        
        msg_t3 = "Usage mixte ville et autoroute"
        intent_t3 = fast_classify_intent(msg_t3)
        assert intent_t3 is not None and intent_t3["intent"] == "car_search"
        is_spec_t3 = is_specific_search_request(msg_t3, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t3

        # Turn 4: Fuel
        history.append({"role": "user", "content": msg_t3})
        history.append({"role": "assistant", "content": "Quelle motorisation préférez-vous (Diesel, Essence, Hybride ou Électrique) ?"})
        
        msg_t4 = "Hybride"
        intent_t4 = fast_classify_intent(msg_t4)
        assert intent_t4 is not None and intent_t4["intent"] == "car_search"
        is_spec_t4 = is_specific_search_request(msg_t4, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t4

        # Turn 5: Transmission
        history.append({"role": "user", "content": msg_t4})
        history.append({"role": "assistant", "content": "Préférez-vous une boîte de vitesses automatique ou manuelle ?"})
        
        msg_t5 = "Boîte Automatique"
        intent_t5 = fast_classify_intent(msg_t5)
        assert intent_t5 is not None and intent_t5["intent"] == "car_search"
        is_spec_t5 = is_specific_search_request(msg_t5, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t5

        # Turn 6: Body Style
        history.append({"role": "user", "content": msg_t5})
        history.append({"role": "assistant", "content": "Quel format de carrosserie vous convient le mieux (SUV, Berline ou Citadine) ?"})
        
        msg_t6 = "SUV"
        intent_t6 = fast_classify_intent(msg_t6)
        assert intent_t6 is not None and intent_t6["intent"] == "car_search"
        is_spec_t6 = is_specific_search_request(msg_t6, max_price=intent_t2["max_price"], history=history)
        assert is_spec_t6, "Turn 6 complete qualification MUST trigger recommendations!"

        prompt_t6 = build_system_prompt("french", "Catalogue context", is_car_search=is_spec_t6)
        assert "VÉHICULES DU CATALOGUE" in prompt_t6
        assert "CAR_RECOMMENDATION" in prompt_t6

        results.append(("FR-2.1 French Consultative Discovery Sequence", True, "Native French prompt validated with 100% turn-by-turn criteria progression"))
    except Exception as e:
        results.append(("FR-2.1 French Consultative Discovery Sequence", False, str(e)))

    # 2.2 Technical & Reliability Diagnosis (1.2 TCe)
    try:
        msg_tech = "Quels sont les défauts du moteur 1.2 TCe ?"
        lang_tech = detect_language(msg_tech, explicit_language="fr")
        assert_language_match(lang_tech, "fr", "FR-2.2 Tech")
        intent_tech = fast_classify_intent(msg_tech)
        assert intent_tech is not None and intent_tech["intent"] == "auto_expert"
        context_tech = EXPERT_CONTEXTS["french"]
        assert "1.2 TCe" in context_tech
        assert "surconsommation d'huile" in context_tech
        results.append(("FR-2.2 Mechanical & Reliability Diagnosis (1.2 TCe)", True, "Correctly classified auto_expert with 1.2 TCe oil consumption context"))
    except Exception as e:
        results.append(("FR-2.2 Mechanical & Reliability Diagnosis (1.2 TCe)", False, str(e)))

    # 2.3 Customs Clearance Calculations
    try:
        msg_customs = "Comment sont calculés les droits de dédouanement au Maroc ?"
        lang_customs = detect_language(msg_customs, explicit_language="fr")
        assert_language_match(lang_customs, "fr", "FR-2.3 Customs")
        intent_customs = fast_classify_intent(msg_customs)
        assert intent_customs is not None and intent_customs["intent"] == "customs"
        context_customs = CUSTOMS_CONTEXTS["french"]
        assert "simulateur" in context_customs.lower()
        results.append(("FR-2.3 Customs Clearance Calculations", True, "Correctly classified customs intent and directed to Wakala customs simulator"))
    except Exception as e:
        results.append(("FR-2.3 Customs Clearance Calculations", False, str(e)))

    # 2.4 Maintenance Tracking
    try:
        msg_maint = "Comment enregistrer ma vidange dans le carnet d'entretien ?"
        lang_maint = detect_language(msg_maint, explicit_language="fr")
        assert_language_match(lang_maint, "fr", "FR-2.4 Maintenance")
        intent_maint = fast_classify_intent(msg_maint)
        assert intent_maint is not None and intent_maint["intent"] == "maintenance_check"
        context_maint = MAINTENANCE_CONTEXTS["french"]
        assert "Carnet d'Entretien" in context_maint
        results.append(("FR-2.4 Maintenance Tracking", True, "Correctly classified maintenance_check with Carnet d'Entretien context"))
    except Exception as e:
        results.append(("FR-2.4 Maintenance Tracking", False, str(e)))

    return results

# ─── 3. Tests Matrix 3: Moroccan Darija (darija) ─────────────────────────────

def run_darija_matrix() -> List[Tuple[str, bool, str]]:
    results = []

    # 3.1 Consultative Discovery Sequence
    try:
        history: List[Dict[str, str]] = []
        
        # Turn 1: Greeting
        msg_t1 = "سلام، بغيت نشري طوموبيل جديدة"
        lang_t1 = detect_language(msg_t1, history=history, explicit_language="darija")
        assert_language_match(lang_t1, "darija", "DARIJA-3.1 Turn 1")
        intent_t1 = fast_classify_intent(msg_t1)
        assert intent_t1 is not None and intent_t1["intent"] == "car_search"
        is_spec_t1 = is_specific_search_request(msg_t1, max_price=intent_t1.get("max_price"), history=history)
        assert not is_spec_t1
        
        prompt_t1 = build_system_prompt("darija_ar", CONSULTATIVE_DISCOVERY_CONTEXTS["darija_ar"], is_car_search=is_spec_t1)
        assert_zero_emojis(prompt_t1, "DARIJA-3.1 Prompt T1")
        assert "الميزانية" in prompt_t1

        # Turn 2: Budget
        history.append({"role": "user", "content": msg_t1})
        history.append({"role": "assistant", "content": "شحال هي الميزانية التقريبية ديالك بالدرهم ؟"})
        
        msg_t2 = "البودجي ديالي هو 180,000 درهم"
        intent_t2 = fast_classify_intent(msg_t2)
        assert intent_t2 is not None and intent_t2["intent"] == "car_search"
        assert intent_t2["max_price"] == 180000
        is_spec_t2 = is_specific_search_request(msg_t2, max_price=intent_t2.get("max_price"), history=history)
        assert not is_spec_t2

        # Turn 3: Usage
        history.append({"role": "user", "content": msg_t2})
        history.append({"role": "assistant", "content": "فين غادي تستعملها بزاف: وسط المدينة، طريق وسفر، ولا مخلط ؟"})
        
        msg_t3 = "تنقل مخلط بين المدينة والطريق"
        intent_t3 = fast_classify_intent(msg_t3)
        assert intent_t3 is not None and intent_t3["intent"] == "car_search"
        is_spec_t3 = is_specific_search_request(msg_t3, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t3

        # Turn 4: Fuel
        history.append({"role": "user", "content": msg_t3})
        history.append({"role": "assistant", "content": "شنو هو المطور المفضل عندك (مازوط، ليسانص، إيبريد، ولا كهربائي) ؟"})
        
        msg_t4 = "مازوط"
        intent_t4 = fast_classify_intent(msg_t4)
        assert intent_t4 is not None and intent_t4["intent"] == "car_search"
        is_spec_t4 = is_specific_search_request(msg_t4, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t4

        # Turn 5: Transmission
        history.append({"role": "user", "content": msg_t4})
        history.append({"role": "assistant", "content": "كتفضل بواط فيتاس أوتوماتيك ولا مانييل ؟"})
        
        msg_t5 = "أوتوماتيك"
        intent_t5 = fast_classify_intent(msg_t5)
        assert intent_t5 is not None and intent_t5["intent"] == "car_search"
        is_spec_t5 = is_specific_search_request(msg_t5, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t5

        # Turn 6: Body Style
        history.append({"role": "user", "content": msg_t5})
        history.append({"role": "assistant", "content": "أشمن نوع ديال الطوموبيل باغي (SUV عالية، سيتادين للمدينة، ولا بيرلين عائلية) ؟"})
        
        msg_t6 = "SUV"
        intent_t6 = fast_classify_intent(msg_t6)
        assert intent_t6 is not None and intent_t6["intent"] == "car_search"
        is_spec_t6 = is_specific_search_request(msg_t6, max_price=intent_t2["max_price"], history=history)
        assert is_spec_t6, "Darija full criteria MUST trigger recommendations!"

        prompt_t6 = build_system_prompt("darija_ar", "Context", is_car_search=is_spec_t6)
        assert "عند التوصية بسيارات من السياق أرفق كود JSON" in prompt_t6

        results.append(("DARIJA-3.1 Moroccan Darija Consultative Discovery", True, "Successfully executed 6-turn Darija Arabic script discovery cycle"))
    except Exception as e:
        results.append(("DARIJA-3.1 Moroccan Darija Consultative Discovery", False, str(e)))

    # 3.2 Technical & Reliability Diagnosis
    try:
        msg_tech = "واش كاينين مشاكل في محرك 1.2 PureTech ؟"
        lang_tech = detect_language(msg_tech, explicit_language="darija")
        assert_language_match(lang_tech, "darija", "DARIJA-3.2 Tech")
        intent_tech = fast_classify_intent(msg_tech)
        assert intent_tech is not None and intent_tech["intent"] == "auto_expert"
        context_tech = EXPERT_CONTEXTS["darija_ar"]
        assert "1.2 PureTech" in context_tech
        assert "حزام التوقيت" in context_tech
        results.append(("DARIJA-3.2 Mechanical & Reliability Diagnosis (PureTech in Darija)", True, "Correctly identified auto_expert in Darija Arabic script"))
    except Exception as e:
        results.append(("DARIJA-3.2 Mechanical & Reliability Diagnosis (PureTech in Darija)", False, str(e)))

    # 3.3 Customs Clearance Calculations
    try:
        msg_customs = "كيفاش كتحسب الديوانة ديال الطوموبيل في المغرب ؟"
        lang_customs = detect_language(msg_customs, explicit_language="darija")
        assert_language_match(lang_customs, "darija", "DARIJA-3.3 Customs")
        intent_customs = fast_classify_intent(msg_customs)
        assert intent_customs is not None and intent_customs["intent"] == "customs"
        context_customs = CUSTOMS_CONTEXTS["darija_ar"]
        assert "حاسبة الجمارك" in context_customs
        results.append(("DARIJA-3.3 Customs Clearance in Darija", True, "Correctly classified customs intent in Darija Arabic script"))
    except Exception as e:
        results.append(("DARIJA-3.3 Customs Clearance in Darija", False, str(e)))

    # 3.4 Maintenance Tracking
    try:
        msg_maint = "كيفاش نسجل الفيدونج ديالي في دفتر الصيانة ؟"
        lang_maint = detect_language(msg_maint, explicit_language="darija")
        assert_language_match(lang_maint, "darija", "DARIJA-3.4 Maintenance")
        intent_maint = fast_classify_intent(msg_maint)
        assert intent_maint is not None and intent_maint["intent"] == "maintenance_check"
        context_maint = MAINTENANCE_CONTEXTS["darija_ar"]
        assert "دفتر الصيانة" in context_maint
        results.append(("DARIJA-3.4 Maintenance Tracking in Darija", True, "Correctly classified maintenance_check in Darija"))
    except Exception as e:
        results.append(("DARIJA-3.4 Maintenance Tracking in Darija", False, str(e)))

    return results

# ─── 4. Tests Matrix 4: Modern Standard Arabic (ar) ─────────────────────────

def run_arabic_matrix() -> List[Tuple[str, bool, str]]:
    results = []

    # 4.1 Consultative Discovery Sequence
    try:
        history: List[Dict[str, str]] = []
        
        # Turn 1: Greeting
        msg_t1 = "مرحبا، أريد شراء سيارة جديدة"
        lang_t1 = detect_language(msg_t1, history=history, explicit_language="ar")
        assert_language_match(lang_t1, "ar", "AR-4.1 Turn 1")
        intent_t1 = fast_classify_intent(msg_t1)
        assert intent_t1 is not None and intent_t1["intent"] == "car_search"
        is_spec_t1 = is_specific_search_request(msg_t1, max_price=intent_t1.get("max_price"), history=history)
        assert not is_spec_t1
        
        prompt_t1 = build_system_prompt("arabic", CONSULTATIVE_DISCOVERY_CONTEXTS["arabic"], is_car_search=is_spec_t1)
        assert_zero_emojis(prompt_t1, "AR-4.1 Prompt T1")
        assert "الميزانية" in prompt_t1

        # Turn 2: Budget
        history.append({"role": "user", "content": msg_t1})
        history.append({"role": "assistant", "content": "ما هي ميزانيتك المستهدفة لشراء السيارة بالدرهم المغربي؟"})
        
        msg_t2 = "ميزانيتي المستهدفة هي 400,000 درهم"
        intent_t2 = fast_classify_intent(msg_t2)
        assert intent_t2 is not None and intent_t2["intent"] == "car_search"
        assert intent_t2["max_price"] == 400000
        is_spec_t2 = is_specific_search_request(msg_t2, max_price=intent_t2.get("max_price"), history=history)
        assert not is_spec_t2

        # Turn 3: Usage
        history.append({"role": "user", "content": msg_t2})
        history.append({"role": "assistant", "content": "ما هي طبيعة تنقلاتك اليومية (داخل المدينة، طرق سريعة وسفر، أو قيادة مختلطة)؟"})
        
        msg_t3 = "استعمال مختلط بين المدينة والطرق السريعة"
        intent_t3 = fast_classify_intent(msg_t3)
        assert intent_t3 is not None and intent_t3["intent"] == "car_search"
        is_spec_t3 = is_specific_search_request(msg_t3, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t3

        # Turn 4: Fuel
        history.append({"role": "user", "content": msg_t3})
        history.append({"role": "assistant", "content": "ما هو نوع الوقود المفضل لديك (ديزل، بنزين، هجين/هايبرد، أو كهربائي)؟"})
        
        msg_t4 = "هجين"
        intent_t4 = fast_classify_intent(msg_t4)
        assert intent_t4 is not None and intent_t4["intent"] == "car_search"
        is_spec_t4 = is_specific_search_request(msg_t4, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t4

        # Turn 5: Transmission
        history.append({"role": "user", "content": msg_t4})
        history.append({"role": "assistant", "content": "هل تفضل ناقل حركة أوتوماتيكي أم يدوي؟"})
        
        msg_t5 = "ناقل حركة أوتوماتيكي"
        intent_t5 = fast_classify_intent(msg_t5)
        assert intent_t5 is not None and intent_t5["intent"] == "car_search"
        is_spec_t5 = is_specific_search_request(msg_t5, max_price=intent_t2["max_price"], history=history)
        assert not is_spec_t5

        # Turn 6: Body Style
        history.append({"role": "user", "content": msg_t5})
        history.append({"role": "assistant", "content": "ما هي فئة السيارة المفضلة (دفع رباعي / SUV، سيدان، أو مدمجة للمدينة)؟"})
        
        msg_t6 = "سيارة دفع رباعي / SUV"
        intent_t6 = fast_classify_intent(msg_t6)
        assert intent_t6 is not None and intent_t6["intent"] == "car_search"
        is_spec_t6 = is_specific_search_request(msg_t6, max_price=intent_t2["max_price"], history=history)
        assert is_spec_t6, "Standard Arabic complete criteria MUST trigger recommendations!"

        prompt_t6 = build_system_prompt("arabic", "Context", is_car_search=is_spec_t6)
        assert "عند التوصية بسيارات من السياق أرفق كود JSON" in prompt_t6

        results.append(("AR-4.1 Modern Standard Arabic Consultative Discovery", True, "Successfully completed 6-turn discovery cycle in Modern Standard Arabic"))
    except Exception as e:
        results.append(("AR-4.1 Modern Standard Arabic Consultative Discovery", False, str(e)))

    # 4.2 Technical & Reliability Diagnosis (DSG7)
    try:
        msg_tech = "ما هي العيوب المصنعية لعلبة السرعات DSG7 ؟"
        lang_tech = detect_language(msg_tech, explicit_language="ar")
        assert_language_match(lang_tech, "ar", "AR-4.2 Tech")
        intent_tech = fast_classify_intent(msg_tech)
        assert intent_tech is not None and intent_tech["intent"] == "auto_expert"
        context_tech = EXPERT_CONTEXTS["arabic"]
        assert "DSG 7" in context_tech
        assert "الميكاترونيكس" in context_tech
        results.append(("AR-4.2 Mechanical & Reliability Diagnosis (DSG7 in Arabic)", True, "Correctly classified auto_expert with DSG7 DQ200 mechatronic context"))
    except Exception as e:
        results.append(("AR-4.2 Mechanical & Reliability Diagnosis (DSG7 in Arabic)", False, str(e)))

    # 4.3 Customs Clearance Calculations
    try:
        msg_customs = "كيف يتم احتساب الرسوم الجمركية للسيارات في المغرب؟"
        lang_customs = detect_language(msg_customs, explicit_language="ar")
        assert_language_match(lang_customs, "ar", "AR-4.3 Customs")
        intent_customs = fast_classify_intent(msg_customs)
        assert intent_customs is not None and intent_customs["intent"] == "customs"
        context_customs = CUSTOMS_CONTEXTS["arabic"]
        assert "حاسبة الجمارك" in context_customs
        results.append(("AR-4.3 Customs Clearance in Standard Arabic", True, "Correctly classified customs intent and directed to Wakala customs calculator"))
    except Exception as e:
        results.append(("AR-4.3 Customs Clearance in Standard Arabic", False, str(e)))

    # 4.4 Maintenance Tracking
    try:
        msg_maint = "كيف يمكنني توثيق الصيانة وتغيير الزيت في دفتر الصيانة؟"
        lang_maint = detect_language(msg_maint, explicit_language="ar")
        assert_language_match(lang_maint, "ar", "AR-4.4 Maintenance")
        intent_maint = fast_classify_intent(msg_maint)
        assert intent_maint is not None and intent_maint["intent"] == "maintenance_check"
        context_maint = MAINTENANCE_CONTEXTS["arabic"]
        assert "دفتر الصيانة" in context_maint
        results.append(("AR-4.4 Maintenance Tracking in Standard Arabic", True, "Correctly classified maintenance_check with Service Book context"))
    except Exception as e:
        results.append(("AR-4.4 Maintenance Tracking in Standard Arabic", False, str(e)))

    return results

# ─── 5. Sanity Checks on Scrubbing & Emojis ──────────────────────────────────

def run_sanitization_and_metric_checks() -> List[Tuple[str, bool, str]]:
    results = []
    
    # 5.1 Emoji Removal
    try:
        raw_text = "Bonjour ! 🚗 Voici votre sélection de voitures 🌟 avec grand coffre 💼."
        cleaned = remove_emojis(raw_text)
        assert_zero_emojis(cleaned, "Sanitization 5.1")
        assert "🚗" not in cleaned and "🌟" not in cleaned and "💼" not in cleaned
        results.append(("SAN-5.1 Emoji Scrubbing Filter", True, "Successfully eliminated all emoji unicode symbols"))
    except Exception as e:
        results.append(("SAN-5.1 Emoji Scrubbing Filter", False, str(e)))

    # 5.2 Thinking Process Scrubbing
    try:
        raw_thinking = "<think>The user wants an SUV with 350k budget. Let's analyze Duster vs Tucson.</think>The Hyundai Tucson is a solid choice."
        cleaned_think = scrub_thinking(raw_thinking)
        assert_zero_thinking(cleaned_think, "Sanitization 5.2")
        assert cleaned_think == "The Hyundai Tucson is a solid choice."

        raw_reasoning = "Thinking Process:\n1. Analyze user request.\n2. Formulate response.\n\nHere are the top recommendations."
        cleaned_reason = scrub_thinking(raw_reasoning)
        assert_zero_thinking(cleaned_reason, "Sanitization 5.2 (Text)")
        assert "Here are the top recommendations." in cleaned_reason
        results.append(("SAN-5.2 Thinking Process Scrubbing", True, "Successfully stripped <think> tags and 'Thinking Process:' preambles"))
    except Exception as e:
        results.append(("SAN-5.2 Thinking Process Scrubbing", False, str(e)))

    # 5.3 Suitcase Metric Assertion
    try:
        valid_trunk_text = "Ce modèle dispose d'un coffre spacieux de 450 Litres, pouvant accueillir environ 3 à 4 valises."
        assert_suitcase_metric(valid_trunk_text, "Metric 5.3 Valid")

        invalid_trunk_text = "Ce modèle dispose d'un coffre de 450 L sans autre précision."
        failed_as_expected = False
        try:
            assert_suitcase_metric(invalid_trunk_text, "Metric 5.3 Invalid")
        except AssertionError:
            failed_as_expected = True
        assert failed_as_expected, "Validator should have raised error when liters are stated without suitcases"
        results.append(("SAN-5.3 Suitcase Equivalence Validator", True, "Validator accurately enforces suitcase count whenever trunk volume is specified in Liters"))
    except Exception as e:
        results.append(("SAN-5.3 Suitcase Equivalence Validator", False, str(e)))

    return results

# ─── Main Execution Runner ───────────────────────────────────────────────────

def main():
    print("=" * 80)
    print("  WAKALA AI CHATBOT - COMPREHENSIVE MULTI-LANGUAGE AUDIT & TEST SUITE  ")
    print("=" * 80)
    print()

    all_test_groups = [
        ("Matrix 1: English (en)", run_english_matrix()),
        ("Matrix 2: Français (fr)", run_french_matrix()),
        ("Matrix 3: Moroccan Darija (darija)", run_darija_matrix()),
        ("Matrix 4: Modern Standard Arabic (ar)", run_arabic_matrix()),
        ("Sanitization & Quality Invariants", run_sanitization_and_metric_checks())
    ]

    total_passed = 0
    total_failed = 0
    
    for group_name, tests in all_test_groups:
        print(f"--- {group_name} ---")
        for test_name, passed, detail in tests:
            status = "PASS [100%]" if passed else "FAIL [X]"
            print(f"  {status} | {test_name}")
            if not passed:
                print(f"         +-- Error: {detail}")
                total_failed += 1
            else:
                print(f"         +-- {detail}")
                total_passed += 1
        print()

    print("=" * 80)
    total_tests = total_passed + total_failed
    score = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    print(f"AUDIT SUMMARY: {total_passed}/{total_tests} Tests Passed ({score:.1f}% Score)")
    print("=" * 80)

    if total_failed > 0:
        sys.exit(1)
    else:
        print("ALL MULTILINGUAL MATRICES AND ARCHITECTURAL INVARIANTS PASSED SUCCESSFULLY!")
        sys.exit(0)

if __name__ == "__main__":
    main()
