import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.recommendation.feature_extraction import (
    extract_filters_from_query,
    PRICE_PATTERNS
)
from app.ml.scoring.wakala_scorer import wakala_scorer
from app.ml.scoring.criteria_ranker import criteria_ranker

def test_feature_extraction_regex():
    print("Testing Regex Price & Features Extraction...")
    
    test_cases = [
        ("Dacia Logan diesel 90000 dh max", 90000),
        ("Clio essence 120 000 MAD maximum", 120000),
        ("voiture plafond 150000", 150000),
        ("budget max: 80 000 dhs", 80000),
        ("SUV automatique 250000 dhs max", 250000),
    ]
    
    for text, exp_price in test_cases:
        res = extract_filters_from_query(text)
        print(f"Text: '{text}' -> Extracted Price: {res.get('price_max')}")
        assert res.get("price_max") == exp_price, f"Failed for '{text}': got {res.get('price_max')}, expected {exp_price}"

    print(">>> All Regex Feature Extraction tests PASSED!")

def test_wakala_scoring_system():
    print("\nTesting Wakala Scoring & Tangible Facts...")
    
    car = {
        "price": 135000,
        "mileage": 0,
        "year": 2024,
        "brand": "Dacia",
        "model": "Duster",
        "reliability_score": 8.8,
        "safety_rating": 5,
        "trunk_capacity": 520,
        "trunk_volume_l": 520,
        "consumption_mixed": 4.5,
        "fuel_consumption": 4.5,
        "engine_power_hp": 115,
        "body_type": "suv",
        "fuel_type": "diesel",
        "description": "Pack Sécurité 6 airbags climatisation carplay camera recul",
    }
    
    user_weights = wakala_scorer.compute_user_weights(usage="famille", priorites=["economie", "securite", "espace_coffre"])
    scored = wakala_scorer.score_single_vehicle(car, user_weights, budget_max=150000, usage="famille")
    criteria_scores = criteria_ranker.compute_criteria_scores(car)
    facts = criteria_ranker.extract_key_facts(car, criteria_scores)
    
    score = scored["final_score"]
    print(f"Vehicle Score: {score}/100")
    print(f"Breakdown: {scored.get('score_breakdown')}")
    print(f"Generated Facts: {facts}")
    
    assert score >= 70, f"Expected high score >= 70, got {score}"
    assert len(facts) > 0, "Expected at least one tangible key fact"
    print(">>> All Wakala Scoring System tests PASSED!")

if __name__ == "__main__":
    test_feature_extraction_regex()
    test_wakala_scoring_system()
