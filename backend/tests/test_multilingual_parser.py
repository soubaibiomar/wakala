import pytest
from app.services.ai.multilingual_parser import (
    sanitize_pii_zero_leak,
    parse_moroccan_currency_and_numbers,
    parse_multilingual_car_intent
)


def test_pii_sanitization_morocco():
    # Phone number and Moroccan CIN sanitization
    raw_query = "Bghit nchouf Dacia Sandero, contactez-moi au 0661234567 ou cin AB123456 email karim@gmail.com"
    sanitized = sanitize_pii_zero_leak(raw_query)
    
    assert "0661234567" not in sanitized
    assert "[PHONE_REDACTED]" in sanitized
    assert "karim@gmail.com" not in sanitized
    assert "[EMAIL_REDACTED]" in sanitized
    assert "AB123456" not in sanitized
    assert "[CIN_REDACTED]" in sanitized


def test_moroccan_currency_parsing():
    # 25 melyoun -> 250,000 MAD
    assert parse_moroccan_currency_and_numbers("bghit tomobil b 25 melyoun") == 250000.0
    assert parse_moroccan_currency_and_numbers("budget dyali 18 mlyon") == 180000.0
    assert parse_moroccan_currency_and_numbers("عندي ميزانية ديال 20 مليون") == 200000.0
    
    # 180k / 180 alf dh
    assert parse_moroccan_currency_and_numbers("180k dh") == 180000.0
    assert parse_moroccan_currency_and_numbers("220 alf dirham") == 220000.0
    
    # Direct numbers
    assert parse_moroccan_currency_and_numbers("prix 300000 MAD") == 300000.0


def test_multilingual_intent_extraction():
    # Darija query with mazot + SUV + brand
    res = parse_multilingual_car_intent("bghit chi SUV Dacia mazot b 25 melyoun")
    assert res["detected_brand"] == "dacia"
    assert res["body_type"] == "SUV"
    assert res["fuel_type"] == "DIESEL"
    assert res["max_budget_mad"] == 250000.0

    # Hybrid + Auto query
    res2 = parse_multilingual_car_intent("cherche Toyota hybride automatique neuve budget 350000 dh")
    assert res2["detected_brand"] == "toyota"
    assert res2["fuel_type"] == "HYBRIDE"
    assert res2["transmission"] == "AUTOMATIQUE"
    assert res2["max_budget_mad"] == 350000.0
