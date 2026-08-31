"""
tests/test_import_wakala_catalogue.py — Tests unitaires pour l'import du catalogue Wakala.
========================================================================================

Vérifie :
1. Le mapping exact des colonnes Excel vers le schéma PostgreSQL 'vehicles' et 'vehicle_wakala_scores'.
2. La préservation stricte du texte brut EuroNCAP / GlobalNCAP (pas d'écrasement par la note 1-5).
3. La génération déterministe de l'UUID (idempotence).
4. Le rejet propre et explicite des lignes corrompues ou incomplètes.
"""

import unittest
import uuid
from data_pipeline.scripts.catalogue_mapping import (
    map_excel_row_to_vehicle_data,
    parse_ncap_rating,
    parse_price,
    parse_4x4,
    infer_fuel_type,
    infer_body_type,
    infer_transmission,
)
from data_pipeline.scripts.import_wakala_catalogue import (
    generate_deterministic_vehicle_id,
    validate_and_transform_row,
)


class TestImportWakalaCatalogue(unittest.TestCase):

    def setUp(self):
        self.sample_valid_row = {
            "Marque": "Dacia",
            "Modèle": "Sandero",
            "Variante": "Streetway Essential - 1.5 Blue dCi 95 diesel",
            "Prix DH": 152000,
            "Coffre (L)": 328,
            "Sécu NCAP ★": "2★",
            "Conso L/100km": 5.3,
            "Puissance ch": 95,
            "CO2 g/km": 119,
            "Longueur cm": 407,
            "4x4": "Non",
            "Autonomie km": "Thermique",
            "Espace": 2,
            "Sécurité": 1,
            "Coût réel": 4,
            "Prix accès": 4,
            "Pratique ville": 4,
            "Performance": 2,
            "Écologie": 4,
            "Tout terrain": 1,
            "Score /5": 2.8,
            "Fiabilité données": "✅ Données certifiées conformes aux catalogues officiels",
            "Constat (prix officiel / disponibilité)": "Sandero démarre à 132.000 DH",
            "Source": "dacia.ma + euroncap.com",
            "_excel_row_num": 4,
        }

    def test_mapping_correct_and_complete(self):
        """Vérifie que les colonnes sont correctement mappées vers le dictionnaire véhicule."""
        v_data, s_data = map_excel_row_to_vehicle_data(self.sample_valid_row)

        # Champs vehicles
        self.assertEqual(v_data["brand"], "Dacia")
        self.assertEqual(v_data["model"], "Sandero")
        self.assertEqual(v_data["version"], "Streetway Essential - 1.5 Blue dCi 95 diesel")
        self.assertEqual(v_data["price"], 152000.0)
        self.assertEqual(v_data["trunk_volume_l"], 328)
        self.assertEqual(v_data["fuel_consumption"], 5.3)
        self.assertEqual(v_data["engine_power_hp"], 95)
        self.assertEqual(v_data["co2_emissions"], 119.0)
        self.assertEqual(v_data["length_cm"], 407)
        self.assertFalse(v_data["is_4x4"])
        self.assertEqual(v_data["condition"], "new")
        self.assertEqual(v_data["source"], "wakala_catalogue")
        self.assertEqual(v_data["fuel_type"], "diesel")
        self.assertEqual(v_data["body_type"], "citadine")

        # Champs vehicle_wakala_scores
        self.assertEqual(s_data["space_score"], 2.0)
        self.assertEqual(s_data["safety_score"], 1.0)
        self.assertEqual(s_data["overall_score"], 2.8)
        self.assertEqual(s_data["data_reliability"], "✅ Données certifiées conformes aux catalogues officiels")

    def test_ncap_rating_raw_text_preserved(self):
        """Vérifie que le texte NCAP source ('2★', '5★ (GlobalNCAP)', etc.) est préservé sans conversion."""
        test_cases = [
            ("2★", "2★"),
            ("5★ (GlobalNCAP)", "5★ (GlobalNCAP)"),
            ("5★ (C-NCAP)", "5★ (C-NCAP)"),
            ("NT (source faible)", "NT (source faible)"),
            ("Non testé", "Non testé"),
            (None, "Non testé"),
            ("", "Non testé"),
        ]
        for raw_val, expected in test_cases:
            res = parse_ncap_rating(raw_val)
            self.assertEqual(res, expected)

    def test_idempotence_and_deterministic_uuid(self):
        """Vérifie que le même triplet marque+modèle+variante produit toujours le même UUID."""
        id1 = generate_deterministic_vehicle_id("Peugeot", "208", "GT Line 1.2 PureTech 130")
        id2 = generate_deterministic_vehicle_id("peugeot", "208 ", "GT Line 1.2 PureTech 130")
        id3 = generate_deterministic_vehicle_id("Peugeot", "208", "Allure 1.2 PureTech 100")

        # Normalisation insensible à la casse et aux espaces
        self.assertEqual(id1, id2)
        # Deux variantes différentes produisent des UUIDs distincts
        self.assertNotEqual(id1, id3)
        self.assertIsInstance(id1, uuid.UUID)

    def test_rejection_of_invalid_rows(self):
        """Vérifie que les lignes invalides sont rejetées avec un message d'erreur clair."""
        # 1. Ligne sans marque
        row_no_brand = dict(self.sample_valid_row, Marque="")
        v, s, errs = validate_and_transform_row(row_no_brand)
        self.assertIsNone(v)
        self.assertTrue(any("Marque" in e for e in errs))

        # 2. Ligne avec prix négatif ou nul
        row_bad_price = dict(self.sample_valid_row, **{"Prix DH": 0})
        v, s, errs = validate_and_transform_row(row_bad_price)
        self.assertIsNone(v)
        self.assertTrue(any("Price" in e or "Prix" in e for e in errs))

        # 3. Ligne sans variante
        row_no_version = dict(self.sample_valid_row, Variante="")
        v, s, errs = validate_and_transform_row(row_no_version)
        self.assertIsNone(v)
        self.assertTrue(any("Variante" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
