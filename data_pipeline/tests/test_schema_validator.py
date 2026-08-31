"""
tests/test_schema_validator.py — Tests unitaires pour la validation des annonces et véhicules.
"""

import unittest
from datetime import datetime
from data_pipeline.kafka.producers.scrapers.schema_validator import SchemaValidator


class TestSchemaValidator(unittest.TestCase):

    def test_valid_listing(self):
        listing = {
            "brand": "dacia",
            "source": "avito",
            "source_url": "http://avito.ma/123",
            "price": 120000,
            "year": 2018,
            "mileage": 50000
        }
        is_valid, errors = SchemaValidator.validate(listing)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_required_fields(self):
        listing = {
            # Missing brand
            "source": "avito",
            # Missing source_url
            "price": 120000
        }
        is_valid, errors = SchemaValidator.validate(listing)
        self.assertFalse(is_valid)
        self.assertTrue(any("brand" in err for err in errors))
        self.assertTrue(any("source_url" in err for err in errors))

    def test_invalid_price(self):
        # Price too low
        listing = {
            "brand": "dacia",
            "source": "avito",
            "source_url": "url",
            "price": 100,  # Too low
        }
        is_valid, errors = SchemaValidator.validate(listing)
        self.assertFalse(is_valid)
        self.assertTrue(any("Price" in err for err in errors))

        # Price string
        listing["price"] = "150000"
        is_valid, errors = SchemaValidator.validate(listing)
        self.assertFalse(is_valid)

    def test_invalid_year(self):
        listing = {
            "brand": "dacia",
            "source": "avito",
            "source_url": "url",
            "price": 100000,
            "year": 3000  # Future year
        }
        is_valid, errors = SchemaValidator.validate(listing)
        self.assertFalse(is_valid)
        self.assertTrue(any("Year 3000 out of bounds" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
