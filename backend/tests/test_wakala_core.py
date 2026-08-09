import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.recommendation.feature_extraction import (
    extract_filters_from_query,
    PRICE_PATTERNS
)
from app.ml.matching.wakala_scoring import (
    calculate_wakala_breakdown,
    calculate_wakala_score,
    WAKALA_MAX_SCORE
)

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
        "mileage": 42000,
        "year": 2021,
        "reliability_score": 8.8,
        "is_first_hand": True,
        "has_service_book": True,
        "safety_rating": 5,
        "trunk_capacity": 520,
        "consumption_mixed": 4.5,
        "warranty_months": 12,
        "body_type": "suv",
        "fuel_type": "diesel"
    }
    
    criteria = {
        "budget_max": 150000,
        "priorities": ["economie", "securite", "coffre"],
        "body_type": "suv",
        "fuel_type": "diesel"
    }
    
    score = calculate_wakala_score(car, criteria)
    breakdown, facts = calculate_wakala_breakdown(car, criteria)
    
    print(f"Vehicle Score: {score}/{WAKALA_MAX_SCORE}")
    print(f"Breakdown: {breakdown}")
    print(f"Generated Facts: {facts}")
    
    assert score >= 75, f"Expected high score >= 75, got {score}"
    assert any("économie" in f.lower() or "consommation" in f.lower() or "coffre" in f.lower() for f in facts)
    print(">>> All Wakala Scoring System tests PASSED!")

if __name__ == "__main__":
    test_feature_extraction_regex()
    test_wakala_scoring_system()
