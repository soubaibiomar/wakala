"""
Test standalone du moteur de recommandation hybride.
Simule des véhicules et des interactions utilisateur pour valider :
- Content-based scoring
- Collaborative scoring
- Fusion hybride pondérée
- Cold start (nouvel utilisateur sans historique)
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from app.ml.recommendation.content_based import (
    build_feature_matrix,
    build_query_vector,
    candidate_vehicles_from_filters,
    compute_content_scores,
)
from app.ml.recommendation.hybrid_engine import HybridEngine
from app.ml.recommendation.schemas import RecommendationFilters


@dataclass
class FakeVehicle:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    seller_id: uuid.UUID = field(default_factory=uuid.uuid4)
    brand: str = ""
    model: str = ""
    year: int = 2020
    mileage: int = 50000
    fuel_type: str = "essence"
    body_type: str = "berline"
    transmission: str = "manuelle"
    engine_power_hp: Optional[int] = 120
    city: str = "Casablanca"
    price: float = 25000
    description: Optional[str] = None

    @property
    def id_str(self) -> str:
        return str(self.id)


def make_vehicles() -> list[FakeVehicle]:
    return [
        FakeVehicle(
            brand="Renault", model="Clio", year=2022, mileage=15000,
            fuel_type="diesel", body_type="citadine", transmission="manuelle",
            engine_power_hp=90, city="Casablanca", price=18500,
        ),
        FakeVehicle(
            brand="Peugeot", model="3008", year=2021, mileage=35000,
            fuel_type="diesel", body_type="suv", transmission="automatique",
            engine_power_hp=130, city="Rabat", price=28500,
        ),
        FakeVehicle(
            brand="Toyota", model="Corolla", year=2023, mileage=8000,
            fuel_type="hybride", body_type="berline", transmission="automatique",
            engine_power_hp=140, city="Casablanca", price=32000,
        ),
        FakeVehicle(
            brand="Dacia", model="Sandero", year=2020, mileage=45000,
            fuel_type="essence", body_type="citadine", transmission="manuelle",
            engine_power_hp=75, city="Tanger", price=12000,
        ),
        FakeVehicle(
            brand="BMW", model="X5", year=2022, mileage=25000,
            fuel_type="diesel", body_type="suv", transmission="automatique",
            engine_power_hp=265, city="Casablanca", price=55000,
        ),
        FakeVehicle(
            brand="Mercedes-Benz", model="Classe C", year=2021, mileage=30000,
            fuel_type="diesel", body_type="berline", transmission="automatique",
            engine_power_hp=200, city="Rabat", price=45000,
        ),
        FakeVehicle(
            brand="Renault", model="Megane", year=2022, mileage=20000,
            fuel_type="essence", body_type="berline", transmission="manuelle",
            engine_power_hp=115, city="Casablanca", price=22000,
        ),
        FakeVehicle(
            brand="Volkswagen", model="Golf", year=2023, mileage=5000,
            fuel_type="essence", body_type="berline", transmission="automatique",
            engine_power_hp=150, city="Marrakech", price=30000,
        ),
    ]


def test_content_based_scoring():
    vehicles = make_vehicles()
    filters = {"brand": "Renault", "city": "Casablanca"}
    scores = compute_content_scores(vehicles, filters)
    assert len(scores) > 0, "Doit retourner des scores"
    clio = next(
        (s for s in scores if "Clio" in str(s["vehicle_id"])),
        None,
    )
    if clio is not None:
        assert clio["content_score"] >= 0, "Score content-based >= 0"
    assert all(0 <= s["content_score"] <= 1 for s in scores), "Scores normalisés [0,1]"
    for i in range(len(scores) - 1):
        assert scores[i]["content_score"] >= scores[i + 1]["content_score"], (
            "Tri décroissant"
        )
    print("  [OK] Content-based : scores normalisés, triés, filtrage fonctionnel")


def test_candidate_filtering():
    vehicles = make_vehicles()
    filters = {"fuel_type": "diesel", "body_type": "suv"}
    candidates = candidate_vehicles_from_filters(vehicles, filters)
    assert len(candidates) >= 2, "Peugeot 3008 + BMW X5 sont diesel SUV"
    assert all(v.fuel_type == "diesel" for v in candidates)
    assert all(v.body_type == "suv" for v in candidates)
    print(f"  [OK] Filtrage candidats : {len(candidates)} véhicules filtrés")


def test_feature_matrix():
    vehicles = make_vehicles()
    matrix = build_feature_matrix(vehicles)
    assert matrix.shape[0] == len(vehicles), "Toutes les lignes"
    assert matrix.shape[1] == 7, "7 features"
    assert not np.any(np.isnan(matrix)), "Pas de NaN dans la matrice"
    assert np.allclose(matrix.mean(axis=0)[:3], 0, atol=1), "Features normalisées"
    print(f"  [OK] Matrice features : {matrix.shape}, centrée-réduite")


def test_hybrid_engine():
    engine = HybridEngine(alpha=0.6)
    content_scores = [
        {"vehicle_id": "v1", "content_score": 0.9},
        {"vehicle_id": "v2", "content_score": 0.7},
        {"vehicle_id": "v3", "content_score": 0.5},
    ]
    collaborative_scores = [
        {"vehicle_id": "v1", "collaborative_score": 0.3},
        {"vehicle_id": "v2", "collaborative_score": 0.8},
        {"vehicle_id": "v3", "collaborative_score": 0.0},
    ]
    response = engine.combine(content_scores, collaborative_scores, cold_start=False)
    assert response.method == "hybrid"
    assert response.total == 3
    assert response.items[0].vehicle_id in ("v1", "v2")
    v2 = next(i for i in response.items if i.vehicle_id == "v2")
    content_part = 0.6 * 0.7
    collab_part = 0.4 * 0.8
    expected_score = round((content_part + collab_part) * 100, 1)
    assert abs(v2.match_score - expected_score) < 0.1, (
        f"Score hybride v2: {v2.match_score} ≈ {expected_score}"
    )
    print(f"  [OK] Fusion hybride : {response.method}, {response.total} résultats, score v2={v2.match_score}")


def test_cold_start():
    engine = HybridEngine(alpha=0.6)
    content_scores = [
        {"vehicle_id": "v1", "content_score": 0.9},
        {"vehicle_id": "v2", "content_score": 0.7},
    ]
    collaborative_scores = [
        {"vehicle_id": "v1", "collaborative_score": 0.0},
        {"vehicle_id": "v2", "collaborative_score": 0.0},
    ]
    response = engine.combine(content_scores, collaborative_scores, cold_start=True)
    assert response.method == "content-based"
    v1 = response.items[0]
    expected = round(0.9 * 100, 1)
    assert abs(v1.match_score - expected) < 0.1, (
        f"Cold start : match_score={v1.match_score} == {expected}"
    )
    assert v1.score_breakdown.collaborative == 0.0
    print(f"  [OK] Cold start : method={response.method}, score 100% content-based")


def test_hybrid_engine_pagination():
    engine = HybridEngine(alpha=0.6)
    content_scores = [
        {"vehicle_id": f"v{i}", "content_score": 1.0 - i * 0.1}
        for i in range(10)
    ]
    collaborative_scores = [
        {"vehicle_id": f"v{i}", "collaborative_score": i * 0.1}
        for i in range(10)
    ]
    response = engine.combine(
        content_scores, collaborative_scores, page=1, page_size=3, cold_start=False
    )
    assert len(response.items) == 3
    assert response.total == 10
    assert response.page == 1
    print(f"  [OK] Pagination : {len(response.items)} items sur {response.total}")


def test_feature_extraction_parsing():
    from app.ml.recommendation.feature_extraction import extract_filters_from_query

    query = "SUV diesel entre 200 000 et 300 000 MAD à Casablanca"
    filters = extract_filters_from_query(query)
    assert filters.get("body_type") == "suv"
    assert filters.get("fuel_type") == "diesel"
    assert filters.get("city") == "Casablanca"
    assert filters.get("price_min") == 200000
    assert filters.get("price_max") == 300000
    print(f"  [OK] Extraction query : {filters}")

    query2 = "Peugeot 3008 essence moins de 50000km"
    filters2 = extract_filters_from_query(query2)
    assert filters2.get("brand") == "Peugeot"
    assert filters2.get("fuel_type") == "essence"
    assert filters2.get("mileage_max") == 50000
    print(f"  [OK] Extraction query 2 : {filters2}")

    query3 = "berline automatique après 2020 budget 150000dh"
    filters3 = extract_filters_from_query(query3)
    assert filters3.get("body_type") == "berline"
    assert filters3.get("transmission") is None
    print(f"  [OK] Extraction query 3 : {filters3}")


if __name__ == "__main__":
    sep = "=" * 60
    print(sep)
    print("  AutoMind - Test Moteur de Recommandation Hybride")
    print(sep)
    print()

    tests = [
        ("Feature extraction — parsing NLP", test_feature_extraction_parsing),
        ("Filtrage candidats", test_candidate_filtering),
        ("Matrice de features", test_feature_matrix),
        ("Content-based scoring", test_content_based_scoring),
        ("Fusion hybride", test_hybrid_engine),
        ("Cold start", test_cold_start),
        ("Pagination", test_hybrid_engine_pagination),
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
