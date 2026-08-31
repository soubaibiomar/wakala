"""
tests/unit/test_eight_dimension_scorer.py — Tests unitaires du scoreur 8 dimensions.

Vérifie les seuils de scoring conformes au catalogue xlsx :
- Véhicule électrique → Coût réel = 5/5, Écologie = 5/5
- Diesel 8L/100km → Coût réel = 2/5
- NCAP 5★ → Sécurité = 5/5
- SUV 4x4 → Motricité = 5/5
- Citadine <4m → Praticité urbaine = 5/5
"""

import pytest
from unittest.mock import MagicMock

from app.ml.recommendation.eight_dimension_scorer import (
    score_vehicle_8d,
    _score_cout_reel,
    _score_securite,
    _score_espace,
    _score_prix_acces,
    _score_praticite_urbaine,
    _score_performance,
    _score_ecologie,
    _score_motricite,
)


# ═══════════════════════════════════════════════════════════════
# Tests des fonctions de scoring individuelles
# ═══════════════════════════════════════════════════════════════

class TestCoutReel:
    def test_electrique_5_sur_5(self):
        assert _score_cout_reel(None, "electrique") == 5.0

    def test_low_consumption_5(self):
        assert _score_cout_reel(3.5, "essence") == 5.0

    def test_medium_consumption_4(self):
        assert _score_cout_reel(5.0, "diesel") == 4.0

    def test_moderate_consumption_3(self):
        assert _score_cout_reel(7.0, "essence") == 3.0

    def test_high_consumption_2(self):
        assert _score_cout_reel(9.0, "diesel") == 2.0

    def test_very_high_consumption_1(self):
        assert _score_cout_reel(12.0, "essence") == 1.0

    def test_none_defaults_pessimistic(self):
        """Sans conso connue, score pessimiste (7L → 3/5)."""
        score = _score_cout_reel(None, "essence")
        assert score == 3.0


class TestSecurite:
    def test_ncap_5_stars(self):
        assert _score_securite("5 étoiles", 2023) == 5.0

    def test_ncap_4_stars(self):
        assert _score_securite("4★", 2022) == 4.0

    def test_ncap_3_stars(self):
        assert _score_securite("3 étoiles NCAP", 2021) == 3.0

    def test_no_ncap_recent_car(self):
        """Pas de note NCAP mais voiture récente → 3.5."""
        assert _score_securite(None, 2023) == 3.5

    def test_no_ncap_older_car(self):
        """Pas de note NCAP, voiture ancienne → 2.5."""
        assert _score_securite(None, 2018) == 2.5


class TestEspace:
    def test_large_trunk_5(self):
        assert _score_espace(550, 5, "suv") == 5.0

    def test_medium_trunk_4(self):
        assert _score_espace(450, 5, "berline") == 4.0

    def test_small_trunk_2(self):
        assert _score_espace(250, 4, "citadine") == 2.0

    def test_7_seats_bonus(self):
        """7 places → bonus de 0.5."""
        score = _score_espace(350, 7, "monospace")
        assert score == 3.5  # 3 + 0.5

    def test_default_by_body_type(self):
        """Sans volume coffre, estimation par carrosserie."""
        score = _score_espace(None, 5, "utilitaire")
        assert score == 5.0  # default 750L → 5


class TestPrixAcces:
    def test_very_affordable_5(self):
        assert _score_prix_acces(120000) == 5.0

    def test_affordable_4(self):
        assert _score_prix_acces(200000) == 4.0

    def test_moderate_3(self):
        assert _score_prix_acces(350000) == 3.0

    def test_expensive_2(self):
        assert _score_prix_acces(500000) == 2.0

    def test_premium_1(self):
        assert _score_prix_acces(800000) == 1.0


class TestPraticiteUrbaine:
    def test_compact_citadine_5(self):
        assert _score_praticite_urbaine(380, "citadine") == 5.0

    def test_medium_sedan_3(self):
        assert _score_praticite_urbaine(450, "berline") == 3.0

    def test_large_suv_2(self):
        assert _score_praticite_urbaine(470, "suv") == 2.0

    def test_default_by_body(self):
        """Sans longueur, estimation par carrosserie."""
        score = _score_praticite_urbaine(None, "citadine")
        assert score == 5.0  # default 380cm → 5


class TestPerformance:
    def test_sporty_5(self):
        assert _score_performance(300) == 5.0

    def test_powerful_4(self):
        assert _score_performance(200) == 4.0

    def test_normal_3(self):
        assert _score_performance(150) == 3.0

    def test_modest_2(self):
        assert _score_performance(100) == 2.0

    def test_entry_level_1(self):
        assert _score_performance(65) == 1.0


class TestEcologie:
    def test_electric_5(self):
        assert _score_ecologie(None, "electrique") == 5.0

    def test_very_low_co2_4_5(self):
        assert _score_ecologie(80, "hybride") == 4.5

    def test_moderate_co2_3(self):
        assert _score_ecologie(145, "essence") == 3.0

    def test_high_co2_1(self):
        assert _score_ecologie(220, "diesel") == 1.0

    def test_hybrid_no_co2_estimated_4(self):
        assert _score_ecologie(None, "hybride") == 4.0

    def test_diesel_no_co2_estimated_2_5(self):
        assert _score_ecologie(None, "diesel") == 2.5


class TestMotricite:
    def test_4x4_confirmed_5(self):
        assert _score_motricite(True, "suv") == 5.0

    def test_suv_no_4x4_3(self):
        assert _score_motricite(False, "suv") == 3.0

    def test_pickup_no_4x4_3_5(self):
        assert _score_motricite(False, "pick_up") == 3.5

    def test_citadine_1_5(self):
        assert _score_motricite(False, "citadine") == 1.5


# ═══════════════════════════════════════════════════════════════
# Tests du scoreur intégré (score_vehicle_8d)
# ═══════════════════════════════════════════════════════════════

class TestScoreVehicle8D:
    def _make_vehicle(self, **kwargs):
        """Crée un véhicule mock avec les attributs donnés."""
        v = MagicMock()
        defaults = {
            "id": "test-id-001",
            "fuel_consumption": 6.0,
            "fuel_type": "essence",
            "ncap_rating": None,
            "year": 2023,
            "trunk_volume_l": None,
            "seats": 5,
            "body_type": "berline",
            "price": 250000,
            "length_cm": None,
            "engine_power_hp": 130,
            "co2_emissions": None,
            "is_4x4": False,
            "wakala_scores": None,
        }
        defaults.update(kwargs)
        for k, val in defaults.items():
            setattr(v, k, val)
        return v

    def test_electric_vehicle_scores(self):
        """Véhicule électrique → scores écologie et coût réel élevés."""
        v = self._make_vehicle(
            fuel_type="electrique", fuel_consumption=0, co2_emissions=0,
        )
        result = score_vehicle_8d(v)
        assert result.scores.ecologie == 5.0
        assert result.scores.cout_reel == 5.0
        assert result.source == "computed"

    def test_diesel_8l_consumption(self):
        """Diesel 8L/100km → Coût réel = 2/5."""
        v = self._make_vehicle(fuel_type="diesel", fuel_consumption=9.0)
        result = score_vehicle_8d(v)
        assert result.scores.cout_reel == 2.0

    def test_suv_4x4_motricite(self):
        """SUV 4x4 → Motricité = 5/5."""
        v = self._make_vehicle(body_type="suv", is_4x4=True)
        result = score_vehicle_8d(v)
        assert result.scores.motricite == 5.0

    def test_citadine_praticite(self):
        """Citadine <4m → Praticité urbaine = 5/5."""
        v = self._make_vehicle(body_type="citadine", length_cm=380)
        result = score_vehicle_8d(v)
        assert result.scores.praticite_urbaine == 5.0

    def test_precomputed_scores_used(self):
        """Quand vehicle_wakala_scores est présent, utilise les scores pré-calculés."""
        ws = MagicMock()
        ws.space_score = 4.0
        ws.safety_score = 5.0
        ws.real_cost_score = 3.0
        ws.access_price_score = 4.0
        ws.city_practicality_score = 2.0
        ws.performance_score = 3.0
        ws.ecology_score = 4.0
        ws.offroad_score = 1.5

        v = self._make_vehicle(wakala_scores=ws)
        result = score_vehicle_8d(v)

        assert result.source == "precomputed"
        assert result.scores.espace == 4.0
        assert result.scores.securite == 5.0
        assert result.scores.cout_reel == 3.0

    def test_all_scores_between_1_and_5(self):
        """Tous les scores doivent être entre 1 et 5."""
        v = self._make_vehicle()
        result = score_vehicle_8d(v)
        for dim in ["espace", "securite", "cout_reel", "prix_acces",
                     "praticite_urbaine", "performance", "ecologie", "motricite"]:
            score = getattr(result.scores, dim)
            assert 1.0 <= score <= 5.0, f"{dim} = {score} hors limites"
