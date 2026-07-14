import pytest


pytestmark = pytest.mark.unit


class TestDamageDetector:
    def test_detector_imports(self):
        try:
            from app.ml.vision.detector import DamageDetector
            assert DamageDetector is not None
        except ImportError:
            pytest.skip("Module vision pas encore implemente")

    def test_detect_no_damage(self):
        pytest.skip("Necessite un modele YOLO entraîne")

    def test_detect_damage_on_test_image(self):
        pytest.skip("Necessite une image de test et un modele charge")

    def test_returns_structured_output(self):
        pytest.skip("Module vision pas encore implemente")
