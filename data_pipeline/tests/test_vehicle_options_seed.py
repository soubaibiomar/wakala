"""
tests/test_vehicle_options_seed.py — Tests unitaires pour la génération des options & couleurs.
===============================================================================================

Vérifie :
1. La cohérence des options générées par catégorie de véhicule (SUV, Citadine, Électrique, Berline).
2. La présence obligatoire d'au moins une couleur de série incluse (price_delta = 0 MAD).
3. Le respect strict de la règle de plausibilité (aucun accessoire/option > 15% du prix de base).
"""

import unittest
import uuid
from data_pipeline.scripts.seed_default_options import (
    generate_options_for_vehicle,
    MAX_OPTION_PRICE_RATIO,
)


class TestVehicleOptionsSeed(unittest.TestCase):

    def test_suv_options_generation(self):
        """Vérifie que les SUV reçoivent les barres latérales, barres de toit, attelage, sabots."""
        suv_vehicle = {
            "id": str(uuid.uuid4()),
            "brand": "Dacia",
            "model": "Duster",
            "version": "Journey 1.5 dCi 115 4x4",
            "price": 240000.0,
            "body_type": "suv",
            "fuel_type": "diesel",
            "engine_type": "Thermique",
            "is_4x4": True,
        }

        options, colors, warnings = generate_options_for_vehicle(suv_vehicle)
        opt_names = [o["name"] for o in options]

        self.assertTrue(any("Barres latérales" in name for name in opt_names))
        self.assertTrue(any("Barres de toit" in name for name in opt_names))
        self.assertTrue(any("Attelage" in name for name in opt_names))
        self.assertTrue(any("Sabots de protection" in name for name in opt_names))

    def test_citadine_options_generation(self):
        """Vérifie que les citadines reçoivent les jantes 16'' et le Pack City."""
        citadine_vehicle = {
            "id": str(uuid.uuid4()),
            "brand": "Renault",
            "model": "Clio",
            "version": "Evolution TCe 90",
            "price": 175000.0,
            "body_type": "citadine",
            "fuel_type": "essence",
            "engine_type": "Thermique",
            "is_4x4": False,
        }

        options, colors, warnings = generate_options_for_vehicle(citadine_vehicle)
        opt_names = [o["name"] for o in options]

        self.assertTrue(any("Jantes alliage 16" in name for name in opt_names))
        self.assertTrue(any("Pack City" in name for name in opt_names))

    def test_electric_options_generation(self):
        """Vérifie que les véhicules électriques reçoivent le pack recharge et pompe à chaleur."""
        ev_vehicle = {
            "id": str(uuid.uuid4()),
            "brand": "BYD",
            "model": "Atto 3",
            "version": "Design 60.4 kWh",
            "price": 379000.0,
            "body_type": "suv",
            "fuel_type": "electrique",
            "engine_type": "Électrique",
            "is_4x4": False,
        }

        options, colors, warnings = generate_options_for_vehicle(ev_vehicle)
        opt_names = [o["name"] for o in options]

        self.assertTrue(any("Recharge Rapide" in name for name in opt_names))
        self.assertTrue(any("Pompe à chaleur" in name for name in opt_names))

    def test_colors_palette_and_default_included(self):
        """Vérifie qu'il y a toujours au moins 1 couleur de série (price_delta = 0 MAD et is_default = True)."""
        vehicle = {
            "id": str(uuid.uuid4()),
            "brand": "Peugeot",
            "model": "208",
            "price": 190000.0,
            "body_type": "citadine",
            "fuel_type": "essence",
        }

        options, colors, warnings = generate_options_for_vehicle(vehicle)
        
        self.assertGreaterEqual(len(colors), 3)
        default_colors = [c for c in colors if c["is_default"]]
        self.assertEqual(len(default_colors), 1)
        self.assertEqual(default_colors[0]["price_delta"], 0.0)

    def test_strict_plausibility_rule(self):
        """Vérifie qu'aucune option individuelle ne dépasse 15% du prix de base du véhicule."""
        # Cas extrême : véhicule d'entrée de gamme à bas prix
        low_cost_vehicle = {
            "id": str(uuid.uuid4()),
            "brand": "Dacia",
            "model": "Sandero",
            "price": 115000.0,  # 15% = 17 250 MAD max
            "body_type": "citadine",
            "fuel_type": "essence",
        }

        options, colors, warnings = generate_options_for_vehicle(low_cost_vehicle)
        base_price = low_cost_vehicle["price"]
        max_allowed = base_price * MAX_OPTION_PRICE_RATIO

        for opt in options:
            self.assertLessEqual(
                opt["price_delta"],
                max_allowed,
                f"L'option '{opt['name']}' ({opt['price_delta']} MAD) dépasse 15% du prix du véhicule ({max_allowed} MAD)"
            )

        for col in colors:
            self.assertLessEqual(
                col["price_delta"],
                max_allowed,
                f"La couleur '{col['color_name']}' ({col['price_delta']} MAD) dépasse 15% du prix du véhicule ({max_allowed} MAD)"
            )


if __name__ == "__main__":
    unittest.main()
