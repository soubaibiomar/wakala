import numpy as np
import pytest

from app.ml.anomaly.detector import AnomalyDetector


pytestmark = pytest.mark.unit


class TestAnomalyDetector:
    def test_initial_state(self):
        detector = AnomalyDetector()
        assert not detector.is_fitted

    def test_fit_and_predict_no_anomalies(self):
        detector = AnomalyDetector(contamination=0.01)
        X = np.random.rand(100, 4)
        detector.fit(X)
        assert detector.is_fitted

        results = detector.predict(X)
        assert len(results) == 100
        anomalies = [r for r in results if r["is_anomaly"]]
        assert len(anomalies) <= 5

    def test_predict_before_fit_returns_empty(self):
        detector = AnomalyDetector()
        results = detector.predict(np.random.rand(5, 3))
        assert results == []

    def test_trust_score_neutral_before_fit(self):
        detector = AnomalyDetector()
        score = detector.compute_trust_score(np.random.rand(4))
        assert score == 50.0

    def test_trust_score_after_fit(self):
        detector = AnomalyDetector()
        X = np.random.rand(100, 4)
        detector.fit(X)

        normal = np.random.rand(4)
        score = detector.compute_trust_score(normal)
        assert 0 <= score <= 100

    def test_results_format(self):
        detector = AnomalyDetector()
        detector.fit(np.random.rand(50, 3))
        results = detector.predict(np.random.rand(10, 3))
        for r in results:
            assert "index" in r
            assert "is_anomaly" in r
            assert "anomaly_score" in r
