"""
Test de validation end-to-end du moteur de recommandation hybride Wakala.

Scénario de référence (issu du spec) :
  Utilisateur : Karim, persona "Famille_Pragmatique"
  Requête : "Je cherche une voiture robuste pour ma famille de 5 personnes, budget max 140 000 DH"
  Extraction NLP : hard_filters={budget_max: 140000, places_min: 5}, soft_features=["familiale","robuste"]
  W1=0.65, W2=0.35 (historique modéré, 421 interactions)
  Score contenu (Dacia Lodgy) : 0.94
  Score collaboratif brut : (3×0.95) + (1×1.0) = 3.85, normalisé sur max=5.0 → 0.77
  Score_final = 0.65×0.94 + 0.35×0.77 = 0.8805
  Tolérance : ±0.01
"""
import math
import unittest
from unittest.mock import patch, MagicMock
from apps.api.services.orchestrator import run_recommendation_pipeline
from apps.api.services.scoring_fusion import compute_weights, compute_final_score
from apps.api.config import K, MAX_W2, MIN_W2


class TestWeightCalibration(unittest.TestCase):
    """Vérifie le calendrier de référence W1/W2 du spec."""

    def test_cold_start(self):
        """Lancement (cold start) : W1=0.95, W2=0.05"""
        w1, w2 = compute_weights(0)
        self.assertAlmostEqual(w1, 0.95, places=2)
        self.assertAlmostEqual(w2, 0.05, places=2)

    def test_1000_interactions(self):
        """Après ~1000 interactions : W1=0.60, W2=0.40"""
        w1, w2 = compute_weights(1000)
        self.assertAlmostEqual(w1, 0.60, places=2)
        self.assertAlmostEqual(w2, 0.40, places=2)

    def test_equilibrium(self):
        """Régime établi : W1=0.50, W2=0.50 (jamais dépassé)"""
        w1, w2 = compute_weights(100_000)
        self.assertAlmostEqual(w1, 0.50, places=2)
        self.assertAlmostEqual(w2, 0.50, places=2)

    def test_karim_weights(self):
        """Karim (421 interactions) : W1=0.65, W2=0.35"""
        w1, w2 = compute_weights(421)
        self.assertAlmostEqual(w1, 0.65, places=2)
        self.assertAlmostEqual(w2, 0.35, places=2)

    def test_w2_never_exceeds_max(self):
        """W2 ne doit JAMAIS dépasser MAX_W2 (0.50)."""
        for n in [0, 100, 1000, 10_000, 1_000_000]:
            _, w2 = compute_weights(n)
            self.assertLessEqual(w2, MAX_W2)


class TestFusionFormula(unittest.TestCase):
    """Vérifie la formule de fusion pondérée."""

    def test_fusion_formula(self):
        """Score_final = W1 × sim(V_user, V_annonce) + W2 × Score_graphe"""
        score = compute_final_score(w1=0.65, w2=0.35, score_content=0.94, score_collab=0.77)
        self.assertAlmostEqual(score, 0.8805, places=4)


class TestKarimEndToEnd(unittest.TestCase):
    """Test end-to-end complet du scénario Karim."""

    @patch("apps.api.services.orchestrator.extract_constraints")
    @patch("apps.api.services.orchestrator.get_content_scores")
    @patch("apps.api.services.orchestrator.generate_explanation")
    def test_karim_scenario(self, mock_explanation, mock_content, mock_nlp):
        """
        Reproduit exactement le scénario de validation du spec.
        Tolérance : ±0.01.
        """
        # ── Mock PostgreSQL ────────────────────────────────────
        mock_pg_client = MagicMock()
        mock_pg_client.get_user.return_value = {
            "id": "Karim",
            "persona_id": "Famille_Pragmatique",
            "n_interactions": 421,  # → W1=0.65, W2=0.35
        }
        # Hard filters retournent Lodgy + Kangoo + une voiture populaire
        # (pour que le max_collab_score = 5.0)
        mock_pg_client.get_cars_by_hard_filters.return_value = [
            "Dacia_Lodgy",
            "Renault_Kangoo",
            "Voiture_Populaire",
        ]
        mock_pg_client.get_car_details.return_value = {
            "titre": "Dacia Lodgy",
            "id": "Dacia_Lodgy",
        }

        # ── Mock NLP (Qwen 2.5 Coder) ─────────────────────────
        mock_nlp.return_value = {
            "hard_filters": {"budget_max": 140000, "places_min": 5},
            "soft_features": ["familiale", "robuste"],
        }

        # ── Mock Qdrant (contenu bge-m3) ──────────────────────
        mock_qdrant_client = MagicMock()
        mock_content.return_value = {
            "Dacia_Lodgy": 0.94,
            "Renault_Kangoo": 0.71,
            "Voiture_Populaire": 0.10,
        }

        # ── Mock Neo4j (collaboratif) ─────────────────────────
        mock_neo4j_client = MagicMock()
        # Scores bruts :
        #   Lodgy : (SAVED:3 × recency:0.95) + (VIEWED:1 × recency:1.0) = 3.85
        #   Voiture_Populaire : 5.0 (pour normalisation max=5.0)
        mock_neo4j_client.get_collaborative_scores.return_value = {
            "Dacia_Lodgy": 3.85,
            "Voiture_Populaire": 5.0,
            "Renault_Kangoo": 1.0,
        }

        # ── Mock Explicabilité ────────────────────────────────
        mock_explanation.return_value = (
            "Ce Dacia Lodgy correspond parfaitement à vos critères de famille nombreuse "
            "avec un budget de 140 000 DH."
        )

        # ── EXÉCUTION ─────────────────────────────────────────
        results = run_recommendation_pipeline(
            user_id="Karim",
            query="Je cherche une voiture robuste pour ma famille de 5 personnes, budget max 140 000 DH",
            pg_client=mock_pg_client,
            qdrant_client=mock_qdrant_client,
            neo4j_client=mock_neo4j_client,
        )

        # ── VALIDATION ────────────────────────────────────────
        lodgy = next((r for r in results if r["car_id"] == "Dacia_Lodgy"), None)
        self.assertIsNotNone(lodgy, "Le Dacia Lodgy doit être dans les recommandations.")

        score_final = lodgy["score_final"]
        score_attendu = 0.8805

        print(f"\n{'='*50}")
        print(f"[TEST END-TO-END] Scénario Karim")
        print(f"{'='*50}")
        print(f"  Persona       : {lodgy.get('w1', '?')} / {lodgy.get('w2', '?')}")
        print(f"  Score contenu  : {lodgy['score_contenu']}")
        print(f"  Score collab   : {lodgy['score_collab']}")
        print(f"  Score final    : {score_final:.4f}")
        print(f"  Score attendu  : {score_attendu:.4f}")
        print(f"  Écart          : {abs(score_final - score_attendu):.4f}")

        self.assertAlmostEqual(
            score_final,
            score_attendu,
            delta=0.01,
            msg=f"Score final {score_final:.4f} hors tolérance ±0.01 de {score_attendu:.4f}",
        )
        print(f"\n  [OK] SUCCES - fusion hybride validee (tolerance +/-0.01)")


if __name__ == "__main__":
    unittest.main()
