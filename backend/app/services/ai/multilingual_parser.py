import re
from typing import Dict, Any, Optional, Tuple


# Regex PII Sanitization for Moroccan Data (Phones, Emails, Moroccan CIN e.g. AB123456, BK78901)
PHONE_REGEX = re.compile(r'(?:\+212|0)[5-7]\d{8}|\b(?:\+212|0)\s?[5-7](?:[\s.-]?\d{2}){4}\b')
EMAIL_REGEX = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
CIN_REGEX = re.compile(r'\b[A-Z]{1,2}\d{5,7}\b', re.IGNORECASE)


def sanitize_pii_zero_leak(text: str) -> str:
    """
    Supprime toutes les données personnelles (PII) avant transmission au LLM ou vector store.
    Conforme CNDP (Loi 09-08).
    """
    if not text:
        return ""
    sanitized = PHONE_REGEX.sub("[PHONE_REDACTED]", text)
    sanitized = EMAIL_REGEX.sub("[EMAIL_REDACTED]", sanitized)
    sanitized = CIN_REGEX.sub("[CIN_REDACTED]", sanitized)
    return sanitized


def parse_moroccan_currency_and_numbers(text: str) -> Optional[float]:
    """
    Normalise les expressions de monnaie et d'argot financier marocain :
    - "25 melyoun" / "25 مليون" / "25 mlyon" -> 250,000 MAD
    - "180 alf dh" / "180 000 dh" / "180k" -> 180,000 MAD
    - "500 alf ryal" -> 25,000 MAD
    - "30 d million" -> 300,000 MAD
    """
    if not text:
        return None

    cleaned = text.lower().replace(",", ".").strip()

    # 1. "X melyoun / million / mlyon / مليون" -> X * 10,000 MAD
    melyoun_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:melyoun|mlyon|mlyen|million|milion|ملايين|مليون)', cleaned)
    if melyoun_match:
        val = float(melyoun_match.group(1))
        return val * 10000.0

    # 2. "X k / X alf / X ألف / X mille" -> X * 1,000 MAD
    alf_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:k|alf|elf|mille|ألف|الف)(?:\s*(?:dh|mad|dirham|درهم))?', cleaned)
    if alf_match:
        val = float(alf_match.group(1))
        return val * 1000.0

    # 3. Direct MAD / DH number e.g. "250000 dh" or "250 000 MAD"
    dh_match = re.search(r'(\d[\d\s]*\d|\d+)\s*(?:dh|mad|dhs|dirham|dirhams|درهم)', cleaned)
    if dh_match:
        num_str = dh_match.group(1).replace(" ", "")
        try:
            return float(num_str)
        except ValueError:
            pass

    # 4. Fallback: 5 or 6 digit number (e.g. 250000)
    standalone_num = re.search(r'\b(1[0-9]{5}|2[0-9]{5}|3[0-9]{5}|4[0-9]{5}|5[0-9]{5}|6[0-9]{5}|7[0-9]{5}|8[0-9]{5}|9[0-9]{5})\b', cleaned)
    if standalone_num:
        try:
            return float(standalone_num.group(1))
        except ValueError:
            pass

    return None


def parse_multilingual_car_intent(query: str) -> Dict[str, Any]:
    """
    Extrait les contraintes structurées à partir de requêtes multilingues
    avec code-switching (Darija, Français, Anglais, Arabe).
    """
    sanitized = sanitize_pii_zero_leak(query)
    q_lower = sanitized.lower()

    params: Dict[str, Any] = {
        "raw_query": query,
        "sanitized_query": sanitized,
        "max_budget_mad": parse_moroccan_currency_and_numbers(q_lower),
        "fuel_type": None,
        "transmission": None,
        "body_type": None,
        "detected_brand": None,
        "is_new_car_query": True
    }

    # Fuel Detection
    if any(k in q_lower for k in ["diesel", "mazot", "gasoil", "مازوط", "مازوت", "ديزل"]):
        params["fuel_type"] = "DIESEL"
    elif any(k in q_lower for k in ["hybride", "hybrid", "phev", "mhev", "هايبرد", "هجين"]):
        params["fuel_type"] = "HYBRIDE"
    elif any(k in q_lower for k in ["electrique", "electric", "ev", "كهربائي", "تريسينتي"]):
        params["fuel_type"] = "ELECTRIQUE"
    elif any(k in q_lower for k in ["essence", "petrol", "gasoline", "lisans", "lisanse", "بنزين", "ليصانص"]):
        params["fuel_type"] = "ESSENCE"

    # Transmission Detection
    if any(k in q_lower for k in ["automatique", "auto", "bva", "edc", "dsg", "dct", "أوتوماتيك", "اوتوماتيك"]):
        params["transmission"] = "AUTOMATIQUE"
    elif any(k in q_lower for k in ["manuelle", "bvm", "manual", "3adi", "aadi", "عادي", "يدوي"]):
        params["transmission"] = "MANUELLE"

    # Body Type Detection
    if any(k in q_lower for k in ["suv", "crossover", "4x4", "baroudeur"]):
        params["body_type"] = "SUV"
    elif any(k in q_lower for k in ["citadine", "petite voiture", "hatchback", "compacte", "city car", "صغيرة"]):
        params["body_type"] = "Citadine"
    elif any(k in q_lower for k in ["berline", "sedan", "saloon"]):
        params["body_type"] = "Berline"
    elif any(k in q_lower for k in ["utilitaire", "fourgon", "pickup", "pick-up"]):
        params["body_type"] = "Utilitaire"

    # Brand Detection
    brands_map = {
        "dacia": ["dacia", "داسيا"],
        "renault": ["renault", "رونو", "رينو"],
        "peugeot": ["peugeot", "بيجو"],
        "hyundai": ["hyundai", "هيونداي"],
        "toyota": ["toyota", "تويوتا"],
        "volkswagen": ["volkswagen", "vw", "golf", "تيكوان", "فولكس"],
        "kia": ["kia", "كيا"],
        "citroen": ["citroen", "citroën", "سيتروين"],
    }
    for b_key, aliases in brands_map.items():
        if any(alias in q_lower for alias in aliases):
            params["detected_brand"] = b_key
            break

    return params
