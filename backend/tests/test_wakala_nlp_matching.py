import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ml.nlp_pipeline.llm_extractor import _fallback_extraction
from app.ml.recommendation.feature_extraction import extract_price, extract_fuel_type, extract_brand

def test_nlp_extraction():
    print("Testing NLP fallback extraction & regex patterns...")
    
    queries = [
        ("Dacia Logan diesel budget 90000 dh max", 90000, "diesel", "Dacia"),
        ("SUV essence automatique max 250000 MAD Casablanca", 250000, "essence", None),
        ("Voiture familiale grand coffre securite 150000", 150000, None, None),
        ("bghit tomobila diesel economique 80000 dh max", 80000, "diesel", None),
        ("plafond 120000 dh hybride", 120000, "hybride", None),
    ]
    
    for q, exp_price, exp_fuel, exp_brand in queries:
        p_min, p_max = extract_price(q)
        fuel = extract_fuel_type(q)
        brand = extract_brand(q)
        nlp_res = _fallback_extraction(q)
        print(f"\nQuery: '{q}'")
        print(f"Regex Extracted: price_max={p_max}, fuel={fuel}, brand={brand}")
        print(f"NLP Extracted: budget={nlp_res.budget}, usage={nlp_res.usage_prevu}, priorites={nlp_res.priorites}")
        
        if exp_price:
            assert p_max == exp_price or nlp_res.budget == exp_price, f"Expected budget {exp_price}"
        if exp_fuel:
            assert fuel == exp_fuel, f"Expected fuel {exp_fuel}"
        if exp_brand:
            assert brand == exp_brand, f"Expected brand {exp_brand}"
    print("\n>>> All NLP extraction tests PASSED successfully!")

from app.ml.scoring.wakala_scorer import wakala_scorer

def test_wakala_scoring():
    print("\nTesting Wakala 100-point scoring algorithm & 3-ingredient formula...")
    
    car = {
        "price": 140000,
        "mileage": 45000,
        "year": 2021,
        "reliability_score": 8.5,
        "is_first_hand": True,
        "has_service_book": True,
        "safety_rating": 5,
        "trunk_capacity": 510,
        "consumption_mixed": 4.8,
        "warranty_months": 12,
        "body_type": "suv",
        "fuel_type": "diesel",
        "seats": 5
    }
    
    usage = "famille"
    priorities = ["economie_usage", "securite", "espace_coffre"]
    budget_max = 160000.0
    
    weights = wakala_scorer.compute_user_weights(usage=usage, priorites=priorities)
    res = wakala_scorer.score_single_vehicle(
        vehicle=car,
        user_weights=weights,
        budget_max=budget_max,
        usage=usage
    )
    
    print(f"Total Wakala Score: {res['final_score']}/100")
    print(f"Quality Score (57%): {res['score_breakdown']['qualite']}")
    print(f"Budget Score (25%): {res['score_breakdown']['budget']}")
    print(f"Pratique/Usage Score (18%): {res['score_breakdown']['pratique']}")
    print(f"Key Facts: {res['key_facts']}")
    print(f"Criteria Scores: {res['score_breakdown']['criteria']}")
    
    assert res['final_score'] >= 65, f"Expected match score >= 65, got {res['final_score']}"
    assert len(res['key_facts']) >= 2, f"Expected at least 2 tangible facts, got {len(res['key_facts'])}"
    print(">>> All Wakala scoring tests PASSED successfully!")

if __name__ == "__main__":
    test_nlp_extraction()
    test_wakala_scoring()
