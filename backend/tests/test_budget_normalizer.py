"""
tests/test_budget_normalizer.py — Tests unitaires pour la normalisation du budget.

Dataset de 20+ phrases annotées couvrant tous les formats :
  - Nombres purs, avec séparateurs
  - Abréviations (k, K)
  - Mots (mille, million)
  - Suffixes monétaires (dh, dirhams, MAD)
  - Edge cases (None, chaînes vides, hors plage)
  - Valeurs numériques directes (int, float)
"""

import pytest
from app.services.budget_normalizer import normalize_budget


class TestNormalizeBudget:
    """Tests pour normalize_budget() — fonction pure regex."""

    # ─── Formats numériques purs ──────────────────────────────

    def test_integer_direct(self):
        """Nombre entier direct."""
        assert normalize_budget(200000) == 200000

    def test_float_direct(self):
        """Nombre flottant direct → arrondi entier."""
        assert normalize_budget(200000.0) == 200000

    def test_string_number_plain(self):
        """Chaîne numérique simple."""
        assert normalize_budget("200000") == 200000

    def test_string_number_with_spaces(self):
        """Nombre avec séparateurs espaces : '200 000'."""
        assert normalize_budget("200 000") == 200000

    def test_string_number_with_commas(self):
        """Nombre avec séparateurs virgules : '200,000'."""
        assert normalize_budget("200,000") == 200000

    # ─── Abréviations k/K ────────────────────────────────────

    def test_200k_lowercase(self):
        """Abréviation '200k'."""
        assert normalize_budget("200k") == 200000

    def test_150K_uppercase(self):
        """Abréviation '150K'."""
        assert normalize_budget("150K") == 150000

    def test_80k_with_space(self):
        """Abréviation avec espace : '80 k'."""
        assert normalize_budget("80 k") == 80000

    # ─── Mots multiplicateurs ────────────────────────────────

    def test_200_mille(self):
        """Format texte : '200 mille'."""
        assert normalize_budget("200 mille") == 200000

    def test_1_point_5_million(self):
        """Format décimal + million : '1.5 million'."""
        assert normalize_budget("1.5 million") == 1500000

    def test_1_comma_5_millions(self):
        """Format décimal virgule : '1,5 millions'."""
        assert normalize_budget("1,5 millions") == 1500000

    def test_2_millions(self):
        """Format texte : '2 millions'."""
        assert normalize_budget("2 millions") == 2000000

    # ─── Suffixes monétaires ─────────────────────────────────

    def test_200000_dh(self):
        """Suffixe 'dh' : '200000 dh'."""
        assert normalize_budget("200000 dh") == 200000

    def test_200_000_dirhams(self):
        """Suffixe 'dirhams' avec espaces : '200 000 dirhams'."""
        assert normalize_budget("200 000 dirhams") == 200000

    def test_300k_mad(self):
        """Abréviation + suffixe : '300k MAD'."""
        assert normalize_budget("300k MAD") == 300000

    def test_150_mille_dh(self):
        """Multiplicateur + suffixe : '150 mille dh'."""
        assert normalize_budget("150 mille dh") == 150000

    def test_250000_DH(self):
        """Suffixe majuscule : '250000 DH'."""
        assert normalize_budget("250000 DH") == 250000

    # ─── Hors plage (trop bas) ───────────────────────────────

    def test_below_minimum_5000(self):
        """Budget trop bas (< 10 000) → None."""
        assert normalize_budget(5000) is None

    def test_below_minimum_9999(self):
        """Budget juste sous le minimum → None."""
        assert normalize_budget(9999) is None

    def test_below_minimum_string(self):
        """Chaîne budget trop bas → None."""
        assert normalize_budget("5000 dh") is None

    # ─── Hors plage (trop haut) ──────────────────────────────

    def test_above_maximum_10m(self):
        """Budget trop élevé (> 5 000 000) → None."""
        assert normalize_budget(10000000) is None

    def test_above_maximum_string(self):
        """Chaîne budget trop élevé → None."""
        assert normalize_budget("10 millions") is None

    def test_above_maximum_6m(self):
        """Juste au-dessus du max → None."""
        assert normalize_budget("6 millions") is None

    # ─── Limites exactes ─────────────────────────────────────

    def test_exact_minimum(self):
        """Limite basse exacte : 10 000 → valide."""
        assert normalize_budget(10000) == 10000

    def test_exact_maximum(self):
        """Limite haute exacte : 5 000 000 → valide."""
        assert normalize_budget(5000000) == 5000000

    # ─── Edge cases ──────────────────────────────────────────

    def test_none(self):
        """None → None."""
        assert normalize_budget(None) is None

    def test_empty_string(self):
        """Chaîne vide → None."""
        assert normalize_budget("") is None

    def test_whitespace_only(self):
        """Espaces seuls → None."""
        assert normalize_budget("   ") is None

    def test_non_numeric_text(self):
        """Texte sans nombre → None."""
        assert normalize_budget("pas de budget") is None

    def test_zero(self):
        """Zéro → None (hors plage)."""
        assert normalize_budget(0) is None

    def test_negative(self):
        """Négatif → None (hors plage)."""
        assert normalize_budget(-100000) is None


class TestNormalizeBudgetPhrasesReelles:
    """Tests avec des phrases réelles que le LLM pourrait renvoyer."""

    def test_autour_de_200000(self):
        """Le LLM peut renvoyer un nombre pur."""
        assert normalize_budget(200000) == 200000

    def test_budget_string_from_llm(self):
        """Le LLM pourrait renvoyer '350000' comme string."""
        assert normalize_budget("350000") == 350000

    def test_llm_returns_float_string(self):
        """Le LLM pourrait renvoyer '200000.0'."""
        assert normalize_budget("200000.0") == 200000
