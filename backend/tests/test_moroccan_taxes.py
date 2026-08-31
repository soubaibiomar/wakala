import pytest
from app.services.calculator.moroccan_taxes import (
    calculate_vignette_dgi,
    calculate_luxury_tax,
    calculate_immatriculation_fee,
    calculate_on_the_road_price,
)


def test_vignette_dgi_diesel_scales():
    # <= 7 CV Diesel -> 700 MAD
    assert calculate_vignette_dgi(6, "DIESEL") == 700.0
    assert calculate_vignette_dgi(7, "diesel") == 700.0

    # 8 - 10 CV Diesel -> 1500 MAD
    assert calculate_vignette_dgi(8, "DIESEL") == 1500.0
    assert calculate_vignette_dgi(10, "DIESEL") == 1500.0

    # 11 - 14 CV Diesel -> 6000 MAD
    assert calculate_vignette_dgi(11, "DIESEL") == 6000.0
    assert calculate_vignette_dgi(14, "DIESEL") == 6000.0

    # >= 15 CV Diesel -> 20000 MAD
    assert calculate_vignette_dgi(15, "DIESEL") == 20000.0
    assert calculate_vignette_dgi(20, "DIESEL") == 20000.0


def test_vignette_dgi_essence_scales():
    # <= 7 CV Essence -> 350 MAD
    assert calculate_vignette_dgi(5, "ESSENCE") == 350.0
    assert calculate_vignette_dgi(7, "essence") == 350.0

    # 8 - 10 CV Essence -> 650 MAD
    assert calculate_vignette_dgi(8, "ESSENCE") == 650.0
    assert calculate_vignette_dgi(10, "ESSENCE") == 650.0

    # 11 - 14 CV Essence -> 3000 MAD
    assert calculate_vignette_dgi(11, "ESSENCE") == 3000.0
    assert calculate_vignette_dgi(14, "ESSENCE") == 3000.0

    # >= 15 CV Essence -> 8000 MAD
    assert calculate_vignette_dgi(15, "ESSENCE") == 8000.0
    assert calculate_vignette_dgi(22, "ESSENCE") == 8000.0


def test_vignette_dgi_hybrid_ev_exemption():
    # Hybride & EV should be 0 MAD regardless of CV
    assert calculate_vignette_dgi(6, "HYBRIDE") == 0.0
    assert calculate_vignette_dgi(10, "Hybrid") == 0.0
    assert calculate_vignette_dgi(15, "ELECTRIQUE") == 0.0
    assert calculate_vignette_dgi(20, "PHEV") == 0.0


def test_luxury_tax_brackets():
    # Under 400k HT (~480k TTC) -> 0 MAD
    assert calculate_luxury_tax(300000.0) == 0.0
    assert calculate_luxury_tax(450000.0) == 0.0  # 450k / 1.2 = 375k HT <= 400k

    # 600k TTC -> 500k HT -> 100k taxable @ 5% = 5000 MAD
    tax_600k = calculate_luxury_tax(600000.0)
    assert tax_600k == 5000.0

    # 1.2M TTC -> 1M HT -> (200k @ 5%) + (200k @ 10%) + (200k @ 15%) = 10k + 20k + 30k = 60k MAD
    tax_1_2m = calculate_luxury_tax(1200000.0)
    assert tax_1_2m == 600000.0 / 1.2 * 0.0 + (200000.0 * 0.05 + 200000.0 * 0.10 + 200000.0 * 0.15)


def test_on_the_road_calculation():
    # Dacia Duster Diesel 6 CV, 240 000 MAD
    breakdown = calculate_on_the_road_price(
        base_price_mad=240000.0,
        fiscal_power_cv=6,
        fuel_type="DIESEL",
        promo_price_mad=230000.0,
        frais_dossier_plaques_mad=1500.0,
    )

    assert breakdown.effective_price_mad == 230000.0
    assert breakdown.vignette_dgi_mad == 700.0
    assert breakdown.immatriculation_carte_grise_mad == 1200.0
    assert breakdown.luxury_tax_mad == 0.0
    assert breakdown.frais_dossier_plaques_mad == 1500.0
    assert breakdown.total_taxes_and_fees_mad == 3400.0
    assert breakdown.total_clef_en_main_mad == 233400.0
    assert breakdown.is_hybrid_or_ev_exempt is False
    assert breakdown.luxury_tax_applied is False
