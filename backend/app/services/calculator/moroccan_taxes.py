from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MoroccanTaxBreakdown:
    base_price_mad: float
    promo_price_mad: Optional[float]
    effective_price_mad: float
    fiscal_power_cv: int
    fuel_type: str
    vignette_dgi_mad: float
    immatriculation_carte_grise_mad: float
    luxury_tax_mad: float
    frais_dossier_plaques_mad: float
    total_taxes_and_fees_mad: float
    total_clef_en_main_mad: float  # Total On-The-Road (OTR) in MAD
    is_hybrid_or_ev_exempt: bool
    luxury_tax_applied: bool


def calculate_vignette_dgi(fiscal_power_cv: int, fuel_type: str) -> float:
    """
    Calcul de la Taxe Spéciale Annuelle sur les Véhicules Automobiles (TSAVA / Vignette DGI)
    selon le Code Général des Impôts marocain (CGI Art. 262).
    
    Règles fiscales :
    - Véhicules Hybrides & Électriques : EXONÉRÉS (0 MAD).
    - Moteur DIESEL :
        - <= 7 CV   : 700 MAD
        - 8 - 10 CV : 1 500 MAD
        - 11 - 14 CV: 6 000 MAD
        - >= 15 CV  : 20 000 MAD
    - Moteur ESSENCE (ou assimilé GPL) :
        - <= 7 CV   : 350 MAD
        - 8 - 10 CV : 650 MAD
        - 11 - 14 CV: 3 000 MAD
        - >= 15 CV  : 8 000 MAD
    """
    if fiscal_power_cv < 1:
        fiscal_power_cv = 1

    fuel = fuel_type.upper().strip()

    # Exonération Hybride / Électrique (Loi de Finances)
    if fuel in ("HYBRIDE", "HYBRID", "ELECTRIQUE", "ELECTRIC", "PHEV", "MHEV"):
        return 0.0

    if fuel in ("DIESEL", "GASOIL", "MAZOT"):
        if fiscal_power_cv <= 7:
            return 700.0
        elif fiscal_power_cv <= 10:
            return 1500.0
        elif fiscal_power_cv <= 14:
            return 6000.0
        else:
            return 20000.0
    else:
        # Essence, GPL, Autres
        if fiscal_power_cv <= 7:
            return 350.0
        elif fiscal_power_cv <= 10:
            return 650.0
        elif fiscal_power_cv <= 14:
            return 3000.0
        else:
            return 8000.0


def calculate_luxury_tax(price_ttc_mad: float) -> float:
    """
    Taxe sur les véhicules de luxe au Maroc (Loi de finances).
    Calcul par tranches sur le montant Hors Taxe estimé (TVA 20% standard) :
    - Tranche <= 400 000 DH HT : 0%
    - Tranche 400 001 - 600 000 DH HT : 5%
    - Tranche 600 001 - 800 000 DH HT : 10%
    - Tranche 800 001 - 1 000 000 DH HT : 15%
    - Tranche > 1 000 000 DH HT : 20%
    """
    if price_ttc_mad <= 0:
        return 0.0

    price_ht = price_ttc_mad / 1.20

    if price_ht <= 400000.0:
        return 0.0

    tax = 0.0

    # Tranche 400k - 600k (5%)
    if price_ht > 400000.0:
        taxable_chunk = min(price_ht, 600000.0) - 400000.0
        tax += taxable_chunk * 0.05

    # Tranche 600k - 800k (10%)
    if price_ht > 600000.0:
        taxable_chunk = min(price_ht, 800000.0) - 600000.0
        tax += taxable_chunk * 0.10

    # Tranche 800k - 1M (15%)
    if price_ht > 800000.0:
        taxable_chunk = min(price_ht, 1000000.0) - 800000.0
        tax += taxable_chunk * 0.15

    # Tranche > 1M (20%)
    if price_ht > 1000000.0:
        taxable_chunk = price_ht - 1000000.0
        tax += taxable_chunk * 0.20

    return round(tax, 2)


def calculate_immatriculation_fee(fiscal_power_cv: int) -> float:
    """
    Droits d'immatriculation et frais de carte grise initiale (Morocco NARSA / Ministère du Transport) :
    - <= 7 CV   : 1 200 MAD
    - 8 - 10 CV : 2 400 MAD
    - 11 - 14 CV: 4 800 MAD
    - >= 15 CV  : 9 500 MAD
    """
    if fiscal_power_cv <= 7:
        return 1200.0
    elif fiscal_power_cv <= 10:
        return 2400.0
    elif fiscal_power_cv <= 14:
        return 4800.0
    else:
        return 9500.0


def calculate_on_the_road_price(
    base_price_mad: float,
    fiscal_power_cv: int,
    fuel_type: str,
    promo_price_mad: Optional[float] = None,
    frais_dossier_plaques_mad: float = 1500.0,
) -> MoroccanTaxBreakdown:
    """
    Calcule le prix 'Clé en Main' (On-The-Road) complet pour un véhicule neuf au Maroc.
    """
    effective_price = promo_price_mad if (promo_price_mad is not None and promo_price_mad > 0) else base_price_mad
    vignette = calculate_vignette_dgi(fiscal_power_cv, fuel_type)
    immatriculation = calculate_immatriculation_fee(fiscal_power_cv)
    luxury_tax = calculate_luxury_tax(effective_price)

    fuel_upper = fuel_type.upper().strip()
    is_hybrid_ev = fuel_upper in ("HYBRIDE", "HYBRID", "ELECTRIQUE", "ELECTRIC", "PHEV", "MHEV")

    total_taxes = vignette + immatriculation + luxury_tax + frais_dossier_plaques_mad
    total_otr = effective_price + total_taxes

    return MoroccanTaxBreakdown(
        base_price_mad=round(base_price_mad, 2),
        promo_price_mad=round(promo_price_mad, 2) if promo_price_mad else None,
        effective_price_mad=round(effective_price, 2),
        fiscal_power_cv=fiscal_power_cv,
        fuel_type=fuel_upper,
        vignette_dgi_mad=round(vignette, 2),
        immatriculation_carte_grise_mad=round(immatriculation, 2),
        luxury_tax_mad=round(luxury_tax, 2),
        frais_dossier_plaques_mad=round(frais_dossier_plaques_mad, 2),
        total_taxes_and_fees_mad=round(total_taxes, 2),
        total_clef_en_main_mad=round(total_otr, 2),
        is_hybrid_or_ev_exempt=is_hybrid_ev,
        luxury_tax_applied=(luxury_tax > 0),
    )
