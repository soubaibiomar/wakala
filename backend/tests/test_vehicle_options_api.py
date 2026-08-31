import unittest
import uuid
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.schemas.vehicle_option_schema import (
    VehicleOptionRead,
    VehicleColorRead,
    VehicleWakalaScoreRead,
    VehicleConfiguratorOptionsResponse,
)


class TestVehicleOptionsSchemas(unittest.TestCase):

    def test_vehicle_option_read_schema(self):
        v_id = uuid.uuid4()
        opt_id = uuid.uuid4()
        data = {
            "id": opt_id,
            "vehicle_id": v_id,
            "category": "accessoire",
            "name": "Barres de toit transversales",
            "price_delta": 2500.0,
            "is_default": False,
            "image_reference": "acc_roof_bars.png",
        }
        opt = VehicleOptionRead.model_validate(data)
        self.assertEqual(opt.name, "Barres de toit transversales")
        self.assertEqual(opt.price_delta, 2500.0)
        self.assertEqual(opt.category, "accessoire")

    def test_vehicle_color_read_schema(self):
        v_id = uuid.uuid4()
        col_id = uuid.uuid4()
        data = {
            "id": col_id,
            "vehicle_id": v_id,
            "color_name": "Bleu Océan Métallisé",
            "hex_code": "#1B3B6F",
            "price_delta": 5500.0,
            "is_default": False,
        }
        col = VehicleColorRead.model_validate(data)
        self.assertEqual(col.color_name, "Bleu Océan Métallisé")
        self.assertEqual(col.hex_code, "#1B3B6F")
        self.assertEqual(col.price_delta, 5500.0)

    def test_vehicle_configurator_response_schema(self):
        v_id = uuid.uuid4()
        response_data = {
            "vehicle_id": v_id,
            "brand": "Dacia",
            "model": "Duster",
            "version": "Journey 1.5 dCi 115 4x4",
            "base_price": 240000.0,
            "colors": [
                {
                    "id": uuid.uuid4(),
                    "vehicle_id": v_id,
                    "color_name": "Blanc Glacier",
                    "hex_code": "#F2F4F7",
                    "price_delta": 0.0,
                    "is_default": True,
                }
            ],
            "options": [
                {
                    "id": uuid.uuid4(),
                    "vehicle_id": v_id,
                    "category": "accessoire",
                    "name": "Barres de toit",
                    "price_delta": 2500.0,
                    "is_default": False,
                    "image_reference": "acc_roof_bars.png",
                }
            ],
            "options_by_category": {
                "accessoire": [
                    {
                        "id": uuid.uuid4(),
                        "vehicle_id": v_id,
                        "category": "accessoire",
                        "name": "Barres de toit",
                        "price_delta": 2500.0,
                        "is_default": False,
                        "image_reference": "acc_roof_bars.png",
                    }
                ]
            },
            "wakala_scores": {
                "space_score": 4.0,
                "safety_score": 3.0,
                "real_cost_score": 4.5,
                "access_price_score": 4.0,
                "city_practicality_score": 3.5,
                "performance_score": 3.0,
                "ecology_score": 3.5,
                "offroad_score": 4.5,
                "overall_score": 3.8,
                "data_reliability": "✅ Données certifiées conformes aux catalogues officiels",
                "observations": "Duster démarre à 199.000 DH",
                "source_note": "dacia.ma",
            }
        }
        res = VehicleConfiguratorOptionsResponse.model_validate(response_data)
        self.assertEqual(res.brand, "Dacia")
        self.assertEqual(res.base_price, 240000.0)
        self.assertEqual(len(res.colors), 1)
        self.assertEqual(len(res.options), 1)
        self.assertIsNotNone(res.wakala_scores)
        self.assertEqual(res.wakala_scores.overall_score, 3.8)


if __name__ == "__main__":
    unittest.main()
