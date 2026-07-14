import numpy as np
import pytest

from app.ml.pricing.price_predictor import PricePredictor


pytestmark = pytest.mark.unit


class TestPricePrediction:
    def test_predict_without_model_returns_default(self):
        predictor = PricePredictor()
        result = predictor.predict(np.array([2020, 50000, 150, 5, 0]))
        assert result["predicted_price"] == 0.0
        assert result["confidence_interval"] == (0.0, 0.0)

    def test_train_and_predict(self):
        predictor = PricePredictor()
        X = np.array([
            [2020, 50000, 150, 5, 0],
            [2021, 30000, 130, 4, 1],
            [2022, 15000, 90, 5, 0],
            [2019, 80000, 200, 5, 1],
        ])
        y = np.array([18500, 28500, 32000, 12000])
        predictor.train(X, y)
        assert predictor.model is not None

        result = predictor.predict(np.array([2022, 15000, 90, 5, 0]))
        assert result["predicted_price"] > 0
        lo, hi = result["confidence_interval"]
        assert lo < hi

    def test_predict_returns_features_importance(self):
        predictor = PricePredictor()
        X = np.random.rand(20, 5)
        y = np.random.rand(20) * 50000
        predictor.train(X, y)

        result = predictor.predict(np.random.rand(5))
        assert "features_importance" in result
        assert len(result["features_importance"]) > 0

    def test_save_and_load(self, tmp_path):
        predictor = PricePredictor()
        predictor.MODEL_PATH = tmp_path / "test_model.joblib"

        X = np.random.rand(10, 3)
        y = np.random.rand(10) * 30000
        predictor.train(X, y)
        predictor.save()

        assert predictor.MODEL_PATH.exists()

        predictor2 = PricePredictor()
        predictor2.MODEL_PATH = predictor.MODEL_PATH
        predictor2.load()
        assert predictor2.model is not None

    def test_predict_with_single_sample(self):
        predictor = PricePredictor()
        X = np.array([[2020, 50000, 150]])
        y = np.array([20000])
        predictor.train(X, y)
        result = predictor.predict(np.array([2021, 30000, 130]))
        assert result["predicted_price"] > 0
