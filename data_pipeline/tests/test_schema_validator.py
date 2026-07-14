import pytest
from datetime import datetime
from data_pipeline.kafka.producers.scrapers.schema_validator import SchemaValidator

def test_valid_listing():
    listing = {
        "brand": "dacia",
        "source": "avito",
        "source_url": "http://avito.ma/123",
        "price": 120000,
        "year": 2018,
        "mileage": 50000
    }
    is_valid, errors = SchemaValidator.validate(listing)
    assert is_valid is True
    assert len(errors) == 0

def test_missing_required_fields():
    listing = {
        # Missing brand
        "source": "avito",
        # Missing source_url
        "price": 120000
    }
    is_valid, errors = SchemaValidator.validate(listing)
    assert is_valid is False
    assert any("brand" in err for err in errors)
    assert any("source_url" in err for err in errors)

def test_invalid_price():
    # Price too low
    listing = {
        "brand": "dacia",
        "source": "avito",
        "source_url": "url",
        "price": 100, # Too low
    }
    is_valid, errors = SchemaValidator.validate(listing)
    assert is_valid is False
    assert any("Price" in err for err in errors)

    # Price string
    listing["price"] = "150000"
    is_valid, errors = SchemaValidator.validate(listing)
    assert is_valid is False

def test_invalid_year():
    listing = {
        "brand": "dacia",
        "source": "avito",
        "source_url": "url",
        "price": 100000,
        "year": 3000 # Future year
    }
    is_valid, errors = SchemaValidator.validate(listing)
    assert is_valid is False
    assert any("Year 3000 out of bounds" in err for err in errors)
