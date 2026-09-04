"""
tests/unit/test_consultative_flow.py — Tests unitaires pour le flow consultatif.

Vérifie :
- Le flow pose une seule question à la fois avant toute recommandation
- Pas de recommandation si profil incomplet (budget/usage manquant)
- Recommandation déclenchée une fois profil complet
- Accumulation incrémentale du profil
- Objection budgétaire → alternative moins chère
"""

import pytest

from app.rag.needs_profile_schema import NeedsProfile, PRIORITY_ALIASES, VALID_DIMENSIONS
from app.rag.consultative_flow import (
    ConsultativeFlow,
    extract_profile_fields,
)


# ═══════════════════════════════════════════════════════════════
# Tests extract_profile_fields (extraction déterministe)
# ═══════════════════════════════════════════════════════════════

class TestExtractProfileFields:
    """Tests d'extraction déterministe des champs depuis un message."""

    def test_extract_budget_french(self):
        fields = extract_profile_fields("Mon budget est de 250000 MAD")
        assert fields.get("budget_max") == 250000.0

    def test_extract_budget_with_spaces(self):
        fields = extract_profile_fields("J'ai un budget de 250 000 DH")
        assert fields.get("budget_max") == 250000.0

    def test_extract_budget_k_suffix(self):
        fields = extract_profile_fields("budget 250k")
        assert fields.get("budget_max") == 250000.0

    def test_extract_budget_range_takes_upper(self):
        fields = extract_profile_fields("entre 200000 et 300000 MAD")
        assert fields.get("budget_max") == 300000.0

    def test_extract_budget_max_keyword(self):
        fields = extract_profile_fields("max 180000")
        assert fields.get("budget_max") == 180000.0

    def test_extract_usage_ville(self):
        fields = extract_profile_fields("Je roule surtout en ville")
        assert fields.get("usage") == "ville"

    def test_extract_usage_route(self):
        fields = extract_profile_fields("Je fais beaucoup d'autoroute")
        assert fields.get("usage") == "route"

    def test_extract_fuel_diesel(self):
        fields = extract_profile_fields("Je préfère le diesel")
        assert fields.get("fuel_preference") == "diesel"

    def test_extract_fuel_electric(self):
        fields = extract_profile_fields("Je veux une voiture électrique")
        assert fields.get("fuel_preference") == "electrique"

    def test_extract_body_suv(self):
        fields = extract_profile_fields("Je cherche un SUV")
        assert fields.get("body_type_preference") == "suv"

    def test_extract_passengers(self):
        fields = extract_profile_fields("Nous sommes 5 personnes")
        assert fields.get("nb_passagers") == 5

    def test_extract_brand(self):
        fields = extract_profile_fields("J'adore les Toyota")
        assert fields.get("brand_preference") == "Toyota"

    def test_extract_priorities_securite(self):
        fields = extract_profile_fields("La sécurité est très importante pour moi")
        assert "securite" in fields.get("priorities", [])

    def test_extract_priorities_ecologie(self):
        fields = extract_profile_fields("Je veux un véhicule écologique, faible CO2")
        prios = fields.get("priorities", [])
        assert "ecologie" in prios

    def test_empty_message_returns_empty(self):
        fields = extract_profile_fields("")
        assert fields == {}

    def test_irrelevant_message_returns_empty(self):
        fields = extract_profile_fields("Bonjour, comment allez-vous ?")
        # Should not extract budget, usage, etc.
        assert "budget_max" not in fields
        assert "usage" not in fields

    def test_darija_budget(self):
        fields = extract_profile_fields("3andi ghir 200000")
        assert fields.get("budget_max") == 200000.0


# ═══════════════════════════════════════════════════════════════
# Tests NeedsProfile
# ═══════════════════════════════════════════════════════════════

class TestNeedsProfile:
    """Tests du schéma NeedsProfile."""

    def test_empty_profile_is_not_complete(self):
        profile = NeedsProfile()
        assert not profile.is_complete
        assert profile.filled_fields_count == 0

    def test_budget_only_not_complete(self):
        profile = NeedsProfile(budget_max=200000)
        assert not profile.is_complete
        assert "usage" in profile.missing_essential_fields()

    def test_usage_only_not_complete(self):
        profile = NeedsProfile(usage="ville")
        assert not profile.is_complete
        assert "budget" in profile.missing_essential_fields()

    def test_budget_and_usage_is_complete(self):
        profile = NeedsProfile(budget_max=200000, usage="ville")
        assert profile.is_complete
        assert profile.missing_essential_fields() == []

    def test_merge_update_incremental(self):
        """merge_update ne doit PAS écraser les valeurs existantes."""
        profile = NeedsProfile(budget_max=200000, usage="ville")
        updated = profile.merge_update({"budget_max": 300000, "nb_passagers": 4})
        # Budget should NOT be overwritten
        assert updated.budget_max == 200000
        # Passengers should be added
        assert updated.nb_passagers == 4

    def test_merge_update_adds_priorities(self):
        profile = NeedsProfile(priorities=["securite"])
        updated = profile.merge_update({"priorities": ["ecologie", "espace"]})
        assert "securite" in updated.priorities
        assert "ecologie" in updated.priorities
        assert "espace" in updated.priorities

    def test_merge_update_normalizes_aliases(self):
        """Les alias de priorité doivent être normalisés."""
        profile = NeedsProfile()
        updated = profile.merge_update({"priorities": ["coffre", "sécurité"]})
        assert "espace" in updated.priorities
        assert "securite" in updated.priorities

    def test_filled_fields_count(self):
        profile = NeedsProfile(
            budget_max=200000, usage="ville",
            nb_passagers=4, fuel_preference="diesel",
        )
        assert profile.filled_fields_count == 4


# ═══════════════════════════════════════════════════════════════
# Tests ConsultativeFlow
# ═══════════════════════════════════════════════════════════════

class TestConsultativeFlow:
    """Tests du flow consultatif."""

    def setup_method(self):
        self.flow = ConsultativeFlow()
        self.session_id = "test-session-001"

    def test_initial_phase_is_discovery(self):
        """Au démarrage, la phase doit être 'discovery'."""
        phase = self.flow.get_phase(self.session_id)
        assert phase == "discovery"

    def test_no_recommendation_without_budget(self):
        """Pas de recommandation si budget manquant."""
        self.flow.update_profile(self.session_id, "Je cherche une voiture pour la ville")
        phase = self.flow.get_phase(self.session_id)
        assert phase == "discovery"

    def test_no_recommendation_without_usage(self):
        """Pas de recommandation si usage manquant."""
        self.flow.update_profile(self.session_id, "Mon budget est de 250000 MAD")
        phase = self.flow.get_phase(self.session_id)
        assert phase == "discovery"

    def test_recommendation_when_complete(self):
        """Recommandation déclenchée une fois budget + usage renseignés."""
        self.flow.update_profile(
            self.session_id,
            "Mon budget est de 250000 MAD et je roule en ville"
        )
        phase = self.flow.get_phase(self.session_id)
        assert phase == "restitution"

    def test_incremental_accumulation(self):
        """Le profil s'enrichit à chaque message."""
        self.flow.update_profile(self.session_id, "Mon budget est 200000 DH")
        profile = self.flow.get_profile(self.session_id)
        assert profile.budget_max == 200000
        assert not profile.is_complete

        self.flow.update_profile(self.session_id, "Je roule surtout en ville")
        profile = self.flow.get_profile(self.session_id)
        assert profile.usage == "ville"
        assert profile.is_complete

    def test_discovery_context_shows_missing(self):
        """Le contexte de découverte affiche les champs manquants."""
        self.flow.update_profile(self.session_id, "Bonjour")
        context = self.flow.get_discovery_context(self.session_id)
        assert "MANQUANTS" in context
        assert "budget" in context.lower()
        assert "usage" in context.lower()

    def test_discovery_context_shows_filled(self):
        """Le contexte affiche les champs remplis."""
        self.flow.update_profile(
            self.session_id, "Budget 300000 MAD, usage ville, je veux un diesel"
        )
        context = self.flow.get_discovery_context(self.session_id)
        assert "300" in context
        assert "ville" in context
        assert "diesel" in context.lower()

    def test_question_plan_contains_one_question_only(self):
        """Même avec plusieurs dimensions manquantes, une seule question sort."""
        self.flow.update_profile(self.session_id, "Budget 250000 MAD et je roule en ville")
        plan = self.flow.get_next_question_plan(self.session_id, [
            {"body_type": "SUV", "fuel_type": "diesel", "ncap_rating": "5/5"},
            {"body_type": "Berline", "fuel_type": "essence", "ncap_rating": "4/5"},
        ])
        assert len(plan["questions"]) == 1
        assert len(plan["dimensions"]) == 1

    def test_build_recommendation_query(self):
        """La requête de recommandation est correctement construite."""
        self.flow.update_profile(
            self.session_id,
            "Budget 250000 MAD, je roule en ville, 4 personnes, je veux un diesel"
        )
        query = self.flow.build_recommendation_query(self.session_id)
        assert query["budget_max"] == 250000
        assert query["usage"] == "ville"
        assert query["nb_passagers"] == 4
        assert query["fuel_type"] == "diesel"

    def test_build_query_raises_if_incomplete(self):
        """La construction échoue si le profil est incomplet."""
        self.flow.update_profile(self.session_id, "Bonjour")
        with pytest.raises(ValueError, match="not complete"):
            self.flow.build_recommendation_query(self.session_id)

    def test_budget_objection_reduces_budget(self):
        """L'objection budgétaire réduit le budget de 20%."""
        self.flow.update_profile(
            self.session_id, "Budget 250000 MAD, je roule en ville"
        )
        query = self.flow.handle_budget_objection(self.session_id)
        assert query["budget_max"] == 200000.0  # 250000 * 0.8

    def test_budget_objection_with_new_budget(self):
        """L'objection avec un nouveau budget explicite le remplace."""
        self.flow.update_profile(
            self.session_id, "Budget 250000 MAD, je roule en ville"
        )
        query = self.flow.handle_budget_objection(self.session_id, new_budget=180000)
        assert query["budget_max"] == 180000

    def test_clear_session(self):
        """clear_session remet le profil à zéro."""
        self.flow.update_profile(
            self.session_id, "Budget 250000 MAD, ville"
        )
        self.flow.clear_session(self.session_id)
        profile = self.flow.get_profile(self.session_id)
        assert not profile.is_complete
        assert profile.budget_max is None

    def test_one_question_at_a_time_context(self):
        """Le contexte de découverte impose une seule question à la fois."""
        context = self.flow.get_discovery_context(self.session_id)
        assert "exactement une seule question" in context

    def test_extract_arabic_and_slider_budget_formats(self):
        """Vérifie l'extraction des budgets arabes, darija et issus de la barre de préférences."""
        assert extract_profile_fields("ميزانيتي المستهدفة هي 200 000 درهم").get("budget_max") == 200000.0
        assert extract_profile_fields("البودجي ديالي هو 200 000 درهم").get("budget_max") == 200000.0
        assert extract_profile_fields("200000 درهم").get("budget_max") == 200000.0
        assert extract_profile_fields("200 ألف درهم").get("budget_max") == 200000.0
        assert extract_profile_fields("200 ألف").get("budget_max") == 200000.0
        assert extract_profile_fields("15 مليون").get("budget_max") == 150000.0
        assert extract_profile_fields("ميزانيتي 200000").get("budget_max") == 200000.0
        assert extract_profile_fields("أقل من 200000").get("budget_max") == 200000.0
        assert extract_profile_fields("بين 150000 و 200000").get("budget_max") == 200000.0
        assert extract_profile_fields("عندي غير 180000").get("budget_max") == 180000.0

    def test_extract_arabic_passengers_and_constraints(self):
        """Vérifie l'extraction des passagers en darija/arabe et des contraintes négatives."""
        res_passengers = extract_profile_fields("كنقلب على طوموبيل ديال 7 بلايص")
        assert res_passengers.get("nb_passagers") == 7

        res_constraints = extract_profile_fields("ما بغيتش محرك ديزل وبدون علبة يدوية")
        assert len(res_constraints.get("constraints", [])) >= 1
