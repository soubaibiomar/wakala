import re

def clean_price(price_str: str) -> int:
    """
    Extract integer price from string (e.g. '140 000 MAD', '140,000.00').
    """
    if not price_str:
        return 0
    digits = re.sub(r'[^\d]', '', price_str)
    return int(digits) if digits else 0

def clean_mileage(mileage_str: str) -> int:
    """
    Extract integer mileage.
    """
    if not mileage_str:
        return -1
    if str(mileage_str).lower() in ['neuf', '0']:
        return 0
    digits = "".join(filter(str.isdigit, str(mileage_str)))
    return int(digits) if digits else -1

def normalize_fuel(fuel_str: str) -> str:
    """
    Normalize fuel types to: essence, diesel, hybride, electrique, gpl, hydrogene
    """
    if not fuel_str:
        return "essence" # fallback
    
    f = fuel_str.lower()
    if 'diesel' in f or 'mazout' in f:
        return 'diesel'
    if 'hybride' in f or 'hybrid' in f:
        return 'hybride'
    if 'electrique' in f or 'électrique' in f:
        return 'electrique'
    if 'gpl' in f:
        return 'gpl'
    return 'essence'

def normalize_transmission(trans_str: str) -> str:
    """
    Normalize transmission to: manuelle, automatique, semi_auto
    """
    if not trans_str:
        return "manuelle"
    
    t = trans_str.lower()
    if 'auto' in t:
        return 'automatique'
    if 'semi' in t or 'tiptronic' in t:
        return 'semi_auto'
    return 'manuelle'

def normalize_condition(cond_str: str, mileage: int = None) -> str:
    """
    Normalize to 'new' or 'used'.
    """
    if mileage == 0:
        return "new"
        
    if not cond_str:
        return "used"
        
    c = cond_str.lower()
    if 'neuf' in c or 'new' in c:
        return 'new'
    return 'used'
