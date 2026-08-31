"""
official_brand_catalog_data.py — Base de référence des couleurs, options et équipements
officiels des marques distribuées au Maroc (2026).
"""

from typing import Any, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# 1. NUANCIERS OFFICIELS DES CONSTRUCTEURS (TEINTES EXACTES + HEX + PRIX MAD)
# ═══════════════════════════════════════════════════════════════════════════════

OFFICIAL_BRAND_COLORS: Dict[str, List[Dict[str, Any]]] = {
    "dacia": [
        {"name": "Blanc Glacier (Opaque)", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Gris Schiste (Métallisé)", "hex": "#4A4F55", "price_mad": 3800, "is_default": False},
        {"name": "Noir Nacré (Métallisé)", "hex": "#141414", "price_mad": 3800, "is_default": False},
        {"name": "Kaki Lichen (Opaque)", "hex": "#4E5442", "price_mad": 3800, "is_default": False},
        {"name": "Vert Cèdre (Métallisé)", "hex": "#294038", "price_mad": 4200, "is_default": False},
        {"name": "Brun Terracotta (Métallisé)", "hex": "#944E38", "price_mad": 4200, "is_default": False},
        {"name": "Gris Comète (Métallisé)", "hex": "#585B62", "price_mad": 3800, "is_default": False},
    ],
    "renault": [
        {"name": "Blanc Glacier", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Noir Étoilé", "hex": "#111111", "price_mad": 4500, "is_default": False},
        {"name": "Gris Rafale", "hex": "#8A919A", "price_mad": 5000, "is_default": False},
        {"name": "Gris Schiste", "hex": "#484D53", "price_mad": 5000, "is_default": False},
        {"name": "Bleu Iron", "hex": "#0D357A", "price_mad": 5500, "is_default": False},
        {"name": "Rouge Flamme", "hex": "#9E1020", "price_mad": 6000, "is_default": False},
        {"name": "Orange Valencia", "hex": "#D65000", "price_mad": 6000, "is_default": False},
    ],
    "peugeot": [
        {"name": "Blanc Banquise", "hex": "#F7F7F7", "price_mad": 0, "is_default": True},
        {"name": "Noir Perla Nera", "hex": "#181818", "price_mad": 4800, "is_default": False},
        {"name": "Gris Artense", "hex": "#76797D", "price_mad": 4800, "is_default": False},
        {"name": "Gris Selenium", "hex": "#4C5257", "price_mad": 5200, "is_default": False},
        {"name": "Bleu Vertigo (Nacré)", "hex": "#005EB8", "price_mad": 6500, "is_default": False},
        {"name": "Rouge Elixir (Nacré)", "hex": "#8C0D1C", "price_mad": 6500, "is_default": False},
        {"name": "Jaune Agueda", "hex": "#CCA01D", "price_mad": 5200, "is_default": False},
    ],
    "citroen": [
        {"name": "Blanc Banquise", "hex": "#FAFAFA", "price_mad": 0, "is_default": True},
        {"name": "Noir Perla Nera", "hex": "#191919", "price_mad": 4500, "is_default": False},
        {"name": "Gris Acier", "hex": "#6C7176", "price_mad": 4500, "is_default": False},
        {"name": "Gris Platinium", "hex": "#484B50", "price_mad": 4500, "is_default": False},
        {"name": "Bleu Eclipse", "hex": "#11263F", "price_mad": 5200, "is_default": False},
        {"name": "Rouge Elixir", "hex": "#8A0E1F", "price_mad": 5800, "is_default": False},
    ],
    "volkswagen": [
        {"name": "Blanc Pur", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Noir Intense (Nacré)", "hex": "#0E0E0E", "price_mad": 5500, "is_default": False},
        {"name": "Gris Indium (Métallisé)", "hex": "#4B4E54", "price_mad": 5500, "is_default": False},
        {"name": "Gris Dauphin", "hex": "#6E747B", "price_mad": 5500, "is_default": False},
        {"name": "Reflet d'Argent", "hex": "#B5B8BC", "price_mad": 5500, "is_default": False},
        {"name": "Bleu Atlantique", "hex": "#102C4E", "price_mad": 6000, "is_default": False},
        {"name": "Rouge Roi", "hex": "#7B141E", "price_mad": 6500, "is_default": False},
    ],
    "hyundai": [
        {"name": "Atlas White", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Phantom Black (Pearl)", "hex": "#121212", "price_mad": 4600, "is_default": False},
        {"name": "Cyber Gray (Metallic)", "hex": "#7E8388", "price_mad": 4600, "is_default": False},
        {"name": "Titan Gray", "hex": "#46484D", "price_mad": 4600, "is_default": False},
        {"name": "Intense Blue", "hex": "#14376F", "price_mad": 5200, "is_default": False},
        {"name": "Dragon Red", "hex": "#8B192A", "price_mad": 5500, "is_default": False},
        {"name": "Jungle Green", "hex": "#2D4439", "price_mad": 5200, "is_default": False},
    ],
    "toyota": [
        {"name": "Blanc Pur", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Noir Attitude", "hex": "#111111", "price_mad": 4800, "is_default": False},
        {"name": "Gris Minéral", "hex": "#555A5F", "price_mad": 4800, "is_default": False},
        {"name": "Gris Argent", "hex": "#B2B5B8", "price_mad": 4800, "is_default": False},
        {"name": "Bleu Nebula", "hex": "#1A3B65", "price_mad": 5500, "is_default": False},
        {"name": "Rouge Allure", "hex": "#931120", "price_mad": 6000, "is_default": False},
        {"name": "Bronze Impérial", "hex": "#54463A", "price_mad": 5500, "is_default": False},
    ],
    "kia": [
        {"name": "Clear White", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Aurora Black Pearl", "hex": "#121212", "price_mad": 4500, "is_default": False},
        {"name": "Steel Gray", "hex": "#5E636A", "price_mad": 4500, "is_default": False},
        {"name": "Gravity Gray", "hex": "#3F4349", "price_mad": 4500, "is_default": False},
        {"name": "Mineral Blue", "hex": "#173A66", "price_mad": 5200, "is_default": False},
        {"name": "Runway Red", "hex": "#8F1626", "price_mad": 5500, "is_default": False},
    ],
    "mercedes": [
        {"name": "Blanc Polaire", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Noir Obsidienne (Métallisé)", "hex": "#131314", "price_mad": 11000, "is_default": False},
        {"name": "Gris Montagne (Métallisé)", "hex": "#54595E", "price_mad": 11000, "is_default": False},
        {"name": "Argent Iridium", "hex": "#C2C4C4", "price_mad": 11000, "is_default": False},
        {"name": "Bleu Spectral", "hex": "#122A4E", "price_mad": 12500, "is_default": False},
        {"name": "Rouge Patagonie MANUFAKTUR", "hex": "#7A0F1B", "price_mad": 19500, "is_default": False},
        {"name": "Gris Montagne Magno (Mat)", "hex": "#44484E", "price_mad": 26000, "is_default": False},
    ],
    "bmw": [
        {"name": "Alpinweiss uni", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Saphirschwarz métallisé", "hex": "#111213", "price_mad": 11500, "is_default": False},
        {"name": "Skyscraper Grau métallisé", "hex": "#6C7178", "price_mad": 11500, "is_default": False},
        {"name": "M Portimao Blau", "hex": "#153B82", "price_mad": 13000, "is_default": False},
        {"name": "Sanremo Grün", "hex": "#254C37", "price_mad": 13000, "is_default": False},
        {"name": "Isle of Man Grün M", "hex": "#195641", "price_mad": 18000, "is_default": False},
        {"name": "Dravitgrau BMW Individual", "hex": "#404347", "price_mad": 24000, "is_default": False},
    ],
    "audi": [
        {"name": "Blanc Ibis uni", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Noir Mythic métallisé", "hex": "#101112", "price_mad": 10500, "is_default": False},
        {"name": "Gris Daytona nacré (Pack S Line)", "hex": "#4A4F55", "price_mad": 12000, "is_default": False},
        {"name": "Gris Chronos métallisé", "hex": "#62676D", "price_mad": 10500, "is_default": False},
        {"name": "Bleu Navarre métallisé", "hex": "#13294C", "price_mad": 11500, "is_default": False},
        {"name": "Rouge Tango métallisé", "hex": "#8C1824", "price_mad": 12500, "is_default": False},
        {"name": "Gris Nardo Audi Exclusive", "hex": "#74787D", "price_mad": 25000, "is_default": False},
    ],
    "byd": [
        {"name": "Skiing White", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Time Grey", "hex": "#656A71", "price_mad": 5000, "is_default": False},
        {"name": "Delan Black", "hex": "#131313", "price_mad": 5000, "is_default": False},
        {"name": "Surf Blue", "hex": "#1A4E8C", "price_mad": 6000, "is_default": False},
        {"name": "Atlantis Grey", "hex": "#43484F", "price_mad": 5500, "is_default": False},
        {"name": "Emerald Green", "hex": "#204638", "price_mad": 6500, "is_default": False},
    ],
    "mg": [
        {"name": "Dover White", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Pebble Black", "hex": "#141414", "price_mad": 4200, "is_default": False},
        {"name": "Medal Silver", "hex": "#B5B8BB", "price_mad": 4200, "is_default": False},
        {"name": "Cosmic Silver", "hex": "#61666D", "price_mad": 4200, "is_default": False},
        {"name": "Brighton Blue", "hex": "#16447F", "price_mad": 5000, "is_default": False},
        {"name": "Diamond Red", "hex": "#8E1727", "price_mad": 5500, "is_default": False},
    ],
    "chery": [
        {"name": "White Pearl", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Carbon Black", "hex": "#151515", "price_mad": 4000, "is_default": False},
        {"name": "Quantum Gray", "hex": "#5D6268", "price_mad": 4000, "is_default": False},
        {"name": "Techno Blue", "hex": "#1C3F73", "price_mad": 4500, "is_default": False},
        {"name": "Ruby Red", "hex": "#8B1828", "price_mad": 4500, "is_default": False},
    ],
    "geely": [
        {"name": "Alpine White", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
        {"name": "Ink Black", "hex": "#121212", "price_mad": 4000, "is_default": False},
        {"name": "Magnetic Gray", "hex": "#575B61", "price_mad": 4000, "is_default": False},
        {"name": "Galaxy Blue", "hex": "#18396B", "price_mad": 4800, "is_default": False},
        {"name": "Passion Red", "hex": "#8F1829", "price_mad": 4800, "is_default": False},
    ],
}

DEFAULT_UNIVERSAL_COLORS = [
    {"name": "Blanc Glacier Métallisé", "hex": "#FFFFFF", "price_mad": 0, "is_default": True},
    {"name": "Gris Anthracite Métallisé", "hex": "#484D53", "price_mad": 4500, "is_default": False},
    {"name": "Noir Ébène Nacré", "hex": "#131313", "price_mad": 4500, "is_default": False},
    {"name": "Bleu Saphir Profond", "hex": "#143768", "price_mad": 5500, "is_default": False},
    {"name": "Gris Argent Lunaire", "hex": "#B5B8BC", "price_mad": 4500, "is_default": False},
    {"name": "Rouge Rubis Nacré", "hex": "#8A1422", "price_mad": 6000, "is_default": False},
]


def get_official_colors_for_vehicle(brand_name: str, model_name: str) -> List[Dict[str, Any]]:
    clean_brand = brand_name.lower().replace("-", "").replace(" ", "").strip()
    for key, colors in OFFICIAL_BRAND_COLORS.items():
        if key in clean_brand:
            return colors
    return DEFAULT_UNIVERSAL_COLORS


# ═══════════════════════════════════════════════════════════════════════════════
# 2. OPTIONS ET PACKS D'ÉQUIPEMENTS OFFICIELS PAR SEGMENT DE VÉHICULE
# ═══════════════════════════════════════════════════════════════════════════════

def get_official_options_for_vehicle(
    brand_name: str,
    model_name: str,
    body_type: str,
    price_mad: float,
    is_electric_or_hybrid: bool = False
) -> List[Dict[str, Any]]:
    is_premium = any(b in brand_name.lower() for b in ["mercedes", "bmw", "audi", "porsche", "lexus", "land rover", "bentley", "jaguar", "volvo"])
    is_suv = body_type in ["suv", "pick_up"] or "duster" in model_name.lower() or "tucson" in model_name.lower()
    
    options = []
    
    # 1. JANTES
    if is_premium:
        options.append({"category": "jante", "name": "Jantes alliage 18 pouces multibranches", "price_delta": 0, "is_default": True})
        options.append({"category": "jante", "name": "Jantes forgées 19/20 pouces Sport bicolores", "price_delta": 14500, "is_default": False})
    elif is_suv:
        options.append({"category": "jante", "name": "Jantes alliage 17 pouces Tergan", "price_delta": 0, "is_default": True})
        options.append({"category": "jante", "name": "Jantes diamantées 18 pouces tout-terrain", "price_delta": 5500, "is_default": False})
    else:
        options.append({"category": "jante", "name": "Jantes alliage 16 pouces diamantées", "price_delta": 0, "is_default": True})
        options.append({"category": "jante", "name": "Jantes alliage 17 pouces Sport design", "price_delta": 4200, "is_default": False})

    # 2. SELLERIE & INTÉRIEUR
    if is_premium:
        options.append({"category": "sellerie", "name": "Cuir synthétique Artico / Tissu technique", "price_delta": 0, "is_default": True})
        options.append({"category": "sellerie", "name": "Cuir Nappa véritable surpiqué avec sièges ventilés", "price_delta": 22000, "is_default": False})
    else:
        options.append({"category": "sellerie", "name": "Tissu Confort renforcé avec surpiqûres", "price_delta": 0, "is_default": True})
        options.append({"category": "sellerie", "name": "Sellerie mixte Tissu / TEP Premium hydrofuge", "price_delta": 4500, "is_default": False})

    # 3. ACCESSOIRES
    if is_suv:
        options.append({"category": "accessoire", "name": "Barres de toit longitudinales modulables aluminium", "price_delta": 2400, "is_default": False})
        options.append({"category": "accessoire", "name": "Marchepieds latéraux inox brossé et pack protection caisse", "price_delta": 4800, "is_default": False})
        options.append({"category": "accessoire", "name": "Attelage amovible sans outil avec faisceau 13 broches", "price_delta": 5900, "is_default": False})
    else:
        options.append({"category": "accessoire", "name": "Pack Tapis velours haute protection & bac de coffre", "price_delta": 1400, "is_default": False})
        options.append({"category": "accessoire", "name": "Seuils de portes rétro-éclairés et coques de rétroviseurs noires", "price_delta": 2200, "is_default": False})

    # 4. PACKS TECHNOLOGIQUES & SÉCURITÉ
    if is_premium:
        options.append({"category": "pack", "name": "Pack Conduite Semi-Autonome Niveau 2 (ACC + maintien de voie actif)", "price_delta": 18500, "is_default": False})
        options.append({"category": "pack", "name": "Toit panoramique ouvrant avec store électrique", "price_delta": 15000, "is_default": False})
        options.append({"category": "pack", "name": "Système audio Surround Premium Hi-Fi 12 haut-parleurs", "price_delta": 12000, "is_default": False})
    else:
        options.append({"category": "pack", "name": "Pack Sécurité Active & Caméra 360° (Radars AV/AR + angle mort)", "price_delta": 6500, "is_default": False})
        options.append({"category": "pack", "name": "Pack Navigation Connectée (Écran tactile 10 pouces sans fil + chargeur induction)", "price_delta": 5500, "is_default": False})
        options.append({"category": "pack", "name": "Toit ouvrant électrique vitré", "price_delta": 7500, "is_default": False})

    if is_electric_or_hybrid:
        options.append({"category": "accessoire", "name": "Câble de recharge rapide Mode 3 Type 2 (32A - 22kW) + sacoche", "price_delta": 3200, "is_default": False})
        options.append({"category": "pack", "name": "Pompe à chaleur haute efficacité & pré-conditionnement thermique", "price_delta": 8500, "is_default": False})

    return options
