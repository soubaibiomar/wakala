from pathlib import Path

import numpy as np
import pytest

from app.ml.pricing.price_model import PriceModel, FALLBACK_PRICE


pytestmark = pytest.mark.unit


class TestPriceModel:
    def test_predict_without_model_returns_fallback(self, tmp_path: Path):
        model = PriceModel(model_dir=tmp_path)
        result = model.predict({
            "brand": "Renault", "model": "Clio", "year": 2020,
            "mileage": 50000, "fuel_type": "diesel", "body_type": "berline",
            "city": "Casablanca",
        })
        assert result["predicted_price"] > 0
        assert result["method"] == "fallback"
        lo, hi = result["confidence_interval"]
        assert lo < hi

    def test_train_and_predict(self, tmp_path: Path):
        model = PriceModel(model_dir=tmp_path)
        vehicles = _make_fake_vehicles(20)
        model.train(vehicles)
        assert model.model is not None

        result = model.predict({
            "brand": "Renault", "model": "Clio", "year": 2020,
            "mileage": 50000, "fuel_type": "diesel", "body_type": "berline",
            "city": "Casablanca",
        })
        assert result["predicted_price"] > 0
        assert result["method"] == "xgboost"
        lo, hi = result["confidence_interval"]
        assert lo < hi

    def test_predict_returns_features_importance(self, tmp_path: Path):
        model = PriceModel(model_dir=tmp_path)
        vehicles = _make_fake_vehicles(20)
        model.train(vehicles)

        result = model.predict({
            "brand": "Peugeot", "model": "208", "year": 2021,
            "mileage": 30000, "fuel_type": "essence", "body_type": "citadine",
            "city": "Rabat",
        })
        assert "features_importance" in result
        assert len(result["features_importance"]) > 0

    def test_train_raises_on_insufficient_data(self, tmp_path: Path):
        model = PriceModel(model_dir=tmp_path)
        vehicles = _make_fake_vehicles(3)
        with pytest.raises(ValueError, match="Insufficient data"):
            model.train(vehicles)

    def test_predict_clamps_extreme_values(self, tmp_path: Path):
        model = PriceModel(model_dir=tmp_path)
        vehicles = _make_fake_vehicles(20)
        model.train(vehicles)

        result = model.predict({
            "brand": "Bugatti", "model": "Veyron", "year": 2023,
            "mileage": 100, "fuel_type": "essence", "body_type": "coupe",
            "city": "Marrakech",
        })
        assert 10_000 <= result["predicted_price"] <= 1_500_000

    def test_unknown_category_does_not_crash(self, tmp_path: Path):
        model = PriceModel(model_dir=tmp_path)
        vehicles = _make_fake_vehicles(20)
        model.train(vehicles)

        result = model.predict({
            "brand": "MegaRareBrand", "model": "Unknown", "year": 2022,
            "mileage": 10000, "fuel_type": "hydrogene", "body_type": "utilitaire",
            "city": "NowhereCity",
        })
        assert result["predicted_price"] > 0

    def test_save_and_load(self, tmp_path: Path):
        model = PriceModel(model_dir=tmp_path)
        vehicles = _make_fake_vehicles(20)
        model.train(vehicles)

        model2 = PriceModel(model_dir=tmp_path)
        assert model2.model is not None
        result = model2.predict({
            "brand": "Renault", "model": "Clio", "year": 2020,
            "mileage": 50000, "fuel_type": "diesel", "body_type": "berline",
            "city": "Casablanca",
        })
        assert result["method"] == "xgboost"
        assert result["predicted_price"] > 0


def _make_fake_vehicles(n: int):
    import random
    from unittest.mock import MagicMock

    from app.models.vehicle import Vehicle

    brands = ["Renault", "Peugeot", "Toyota", "Dacia", "Hyundai"]
    models = ["Clio", "208", "Corolla", "Sandero", "i10"]
    fuels = ["essence", "diesel", "hybride"]
    bodies = ["citadine", "berline", "suv", "break"]
    trans = ["manuelle", "automatique"]
    cities = ["Casablanca", "Rabat", "Marrakech", "Tanger", "Fès"]

    vehicles = []
    for i in range(n):
        v = MagicMock(spec=Vehicle)
        v.brand = random.choice(brands)
        v.model = random.choice(models)
        v.year = random.randint(2005, 2024)
        v.mileage = random.randint(5000, 200000)
        v.fuel_type = random.choice(fuels)
        v.body_type = random.choice(bodies)
        v.transmission = random.choice(trans)
        v.engine_power_hp = random.choice([60, 75, 90, 110, 130, 150])
        v.doors = 5
        v.seats = 5
        v.city = random.choice(cities)
        base = 40000 + (v.year - 2005) * 3000 - v.mileage * 0.5 + hash(v.brand) % 20000
        v.price = max(20000, min(base + random.randint(-10000, 10000), 400000))
        vehicles.append(v)
    return vehicles
