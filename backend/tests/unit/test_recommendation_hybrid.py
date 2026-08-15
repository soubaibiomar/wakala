import uuid
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pytest

from app.ml.recommendation.content_based import (
    build_feature_matrix,
    candidate_vehicles_from_filters,
    compute_content_scores,
)
from app.ml.recommendation.hybrid_engine import HybridEngine
from app.ml.recommendation.schemas import RecommendationFilters
from app.ml.recommendation.feature_extraction import extract_filters_from_query


pytestmark = pytest.mark.unit


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


@pytest.fixture
def vehicles() -> list[FakeVehicle]:
    return [
        FakeVehicle(brand="Renault", model="Clio", year=2022, mileage=15000,
                    fuel_type="diesel", body_type="citadine", transmission="manuelle",
                    engine_power_hp=90, city="Casablanca", price=18500),
        FakeVehicle(brand="Peugeot", model="3008", year=2021, mileage=35000,
                    fuel_type="diesel", body_type="suv", transmission="automatique",
                    engine_power_hp=130, city="Rabat", price=28500),
        FakeVehicle(brand="Toyota", model="Corolla", year=2023, mileage=8000,
                    fuel_type="hybride", body_type="berline", transmission="automatique",
                    engine_power_hp=140, city="Casablanca", price=32000),
        FakeVehicle(brand="Dacia", model="Sandero", year=2020, mileage=45000,
                    fuel_type="essence", body_type="citadine", transmission="manuelle",
                    engine_power_hp=75, city="Tanger", price=12000),
        FakeVehicle(brand="BMW", model="X5", year=2022, mileage=25000,
                    fuel_type="diesel", body_type="suv", transmission="automatique",
                    engine_power_hp=265, city="Casablanca", price=55000),
        FakeVehicle(brand="Mercedes-Benz", model="Classe C", year=2021, mileage=30000,
                    fuel_type="diesel", body_type="berline", transmission="automatique",
                    engine_power_hp=200, city="Rabat", price=45000),
        FakeVehicle(brand="Renault", model="Megane", year=2022, mileage=20000,
                    fuel_type="essence", body_type="berline", transmission="manuelle",
                    engine_power_hp=115, city="Casablanca", price=22000),
        FakeVehicle(brand="Volkswagen", model="Golf", year=2023, mileage=5000,
                    fuel_type="essence", body_type="berline", transmission="automatique",
                    engine_power_hp=150, city="Marrakech", price=30000),
    ]


class TestContentBased:
    def test_feature_matrix_shape(self, vehicles):
        matrix = build_feature_matrix(vehicles)
        assert matrix.shape[0] == len(vehicles)
        assert matrix.shape[1] == 6
        assert not np.any(np.isnan(matrix))

    def test_feature_matrix_normalized(self, vehicles):
        matrix = build_feature_matrix(vehicles)
        assert np.allclose(matrix.mean(axis=0)[:3], 0, atol=1)

    def test_candidate_filtering_fuel_and_body(self, vehicles):
        filters = {"fuel_type": "diesel", "body_type": "suv"}
        candidates = candidate_vehicles_from_filters(vehicles, filters)
        assert len(candidates) >= 2
        assert all(v.fuel_type == "diesel" for v in candidates)
        assert all(v.body_type == "suv" for v in candidates)

    def test_candidate_filtering_brand(self, vehicles):
        filters = {"brand": "Renault"}
        candidates = candidate_vehicles_from_filters(vehicles, filters)
        assert len(candidates) == 2
        assert all(v.brand == "Renault" for v in candidates)

    def test_candidate_filtering_price_range(self, vehicles):
        filters = {"price_min": 20000, "price_max": 35000}
        candidates = candidate_vehicles_from_filters(vehicles, filters)
        assert all(20000 <= v.price <= 35000 for v in candidates)

    def test_content_scores_sorted(self, vehicles):
        filters = {"fuel_type": "diesel"}
        scores = compute_content_scores(vehicles, filters)
        assert len(scores) > 0
        for i in range(len(scores) - 1):
            assert scores[i]["content_score"] >= scores[i + 1]["content_score"]

    def test_content_scores_normalized(self, vehicles):
        filters = {"city": "Casablanca"}
        scores = compute_content_scores(vehicles, filters)
        assert all(0 <= s["content_score"] <= 1 for s in scores)


class TestFeatureExtraction:
    def test_extract_suv_diesel_casablanca(self):
        q = "SUV diesel entre 200 000 et 300 000 MAD a Casablanca"
        f = extract_filters_from_query(q)
        assert f.get("body_type") == "suv"
        assert f.get("fuel_type") == "diesel"
        assert f.get("city") == "Casablanca"
        assert f.get("price_min") == 200000
        assert f.get("price_max") == 300000

    def test_extract_brand_mileage(self):
        q = "Peugeot 3008 essence moins de 50000km"
        f = extract_filters_from_query(q)
        assert f.get("brand") == "Peugeot"
        assert f.get("fuel_type") == "essence"
        assert f.get("mileage_max") == 50000

    def test_extract_empty_query(self):
        f = extract_filters_from_query("")
        assert isinstance(f, dict)

    def test_extract_no_match(self):
        f = extract_filters_from_query("bonjour")
        assert f == {}


class TestHybridEngine:
    def test_hybrid_fusion(self):
        engine = HybridEngine(alpha=0.6)
        content = [
            {"vehicle_id": "v1", "content_score": 0.9},
            {"vehicle_id": "v2", "content_score": 0.7},
        ]
        collab = [
            {"vehicle_id": "v1", "collaborative_score": 0.3},
            {"vehicle_id": "v2", "collaborative_score": 0.8},
        ]
        response = engine.combine(content, collab, cold_start=False)
        assert response.method == "hybrid"
        assert response.total == 2
        v2 = next(i for i in response.items if i.vehicle_id == "v2")
        expected = round((0.6 * 0.7 + 0.4 * 0.8) * 100, 1)
        assert abs(v2.match_score - expected) < 0.1

    def test_cold_start(self):
        engine = HybridEngine(alpha=0.6)
        content = [
            {"vehicle_id": "v1", "content_score": 0.9},
            {"vehicle_id": "v2", "content_score": 0.7},
        ]
        collab = [
            {"vehicle_id": "v1", "collaborative_score": 0.0},
            {"vehicle_id": "v2", "collaborative_score": 0.0},
        ]
        response = engine.combine(content, collab, cold_start=True)
        assert response.method == "cold-start"
        assert response.cold_start is True
        assert response.items[0].score_breakdown.collaborative == 0.0
        assert abs(response.items[0].match_score - 90.0) < 0.1

    def test_pagination(self):
        engine = HybridEngine(alpha=0.6)
        content = [{"vehicle_id": f"v{i}", "content_score": 1.0 - i * 0.1} for i in range(10)]
        collab = [{"vehicle_id": f"v{i}", "collaborative_score": i * 0.1} for i in range(10)]
        response = engine.combine(content, collab, page=1, page_size=3, cold_start=False)
        assert len(response.items) == 3
        assert response.total == 10
        assert response.page == 1
