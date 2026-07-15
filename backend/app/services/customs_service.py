from typing import Dict, Any

def calculate_customs(
    purchase_price: float,
    age_years: int,
    fuel_type: str,
    fiscal_power: int,
    origin_eu: bool
) -> Dict[str, Any]:
    """
    Simulateur de calcul des droits et taxes de douane au Maroc (ADII).
    Ceci est un modèle simplifié pour l'MVP.
    
    Règles basiques appliquées:
    - Base taxable : purchase_price
    - Droits d'importation (DI) : 2.5% si origine UE, 17.5% sinon.
    - Taxe Parafiscale (TP) : 0.25% de la base.
    - TVA : 20% calculée sur (Base + DI + TP).
    - Taxe additionnelle (Luxe/Puissance) : Forfaitaire selon puissance fiscale.
    """
    
    # 1. Base taxable
    taxable_base = purchase_price
    
    # 2. Droits d'importation
    import_duty_rate = 0.025 if origin_eu else 0.175
    import_duty_amount = taxable_base * import_duty_rate
    
    # 3. Taxe parafiscale
    parafiscal_tax_rate = 0.0025
    parafiscal_tax_amount = taxable_base * parafiscal_tax_rate
    
    # 4. TVA
    vat_base = taxable_base + import_duty_amount + parafiscal_tax_amount
    vat_rate = 0.20
    vat_amount = vat_base * vat_rate
    
    # 5. Taxe additionnelle (Puissance fiscale)
    # Simple simulation: > 10 CV = 5000 MAD, > 14 CV = 20000 MAD
    additional_tax = 0.0
    if fiscal_power > 14:
        additional_tax = 20000.0
    elif fiscal_power > 10:
        additional_tax = 5000.0
        
    # Total Douane
    total_customs_fees = import_duty_amount + parafiscal_tax_amount + vat_amount + additional_tax
    
    # Prix de revient total (Achat + Douane)
    total_cost = purchase_price + total_customs_fees
    
    return {
        "purchase_price": round(purchase_price, 2),
        "import_duty": round(import_duty_amount, 2),
        "parafiscal_tax": round(parafiscal_tax_amount, 2),
        "vat": round(vat_amount, 2),
        "additional_tax": round(additional_tax, 2),
        "total_customs_fees": round(total_customs_fees, 2),
        "total_cost": round(total_cost, 2),
        "breakdown": [
            {"label": "Prix d'achat", "amount": round(purchase_price, 2), "color": "var(--bg-card)"},
            {"label": "Droits d'importation", "amount": round(import_duty_amount, 2), "color": "var(--accent-blue)"},
            {"label": "TVA (20%)", "amount": round(vat_amount, 2), "color": "var(--accent-gold)"},
            {"label": "Taxes annexes", "amount": round(parafiscal_tax_amount + additional_tax, 2), "color": "var(--accent-red)"},
        ]
    }
