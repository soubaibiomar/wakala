import re
from typing import Optional


BRAND_KEYWORDS = {
    "renault": "Renault", "peugeot": "Peugeot", "citroen": "Citroën",
    "citroën": "Citroën", "dacia": "Dacia", "toyota": "Toyota",
    "honda": "Honda", "hyundai": "Hyundai", "kia": "Kia",
    "nissan": "Nissan", "volkswagen": "Volkswagen", "vw": "Volkswagen",
    "bmw": "BMW", "mercedes": "Mercedes-Benz", "mercedes-benz": "Mercedes-Benz",
    "audi": "Audi", "ford": "Ford", "fiat": "Fiat", "opel": "Opel",
    "mazda": "Mazda", "suzuki": "Suzuki", "mitsubishi": "Mitsubishi",
    "volvo": "Volvo", "seat": "Seat", "skoda": "Škoda", "škoda": "Škoda",
    "land rover": "Land Rover", "jeep": "Jeep", "porsche": "Porsche",
    "jaguar": "Jaguar", "tesla": "Tesla",
}

FUEL_KEYWORDS = {
    "essence": "essence", "petrol": "essence", "super": "essence", "lisans": "essence", "gasoline": "essence", "gas": "essence",
    "diesel": "diesel", "gazoil": "diesel", "mazot": "diesel", "mazout": "diesel", "nafta": "diesel",
    "hybride": "hybride", "hybrid": "hybride", "hybride rechargeable": "hybride_rechargeable",
    "phev": "hybride_rechargeable", "electrique": "electrique", "electric": "electrique", "ev": "electrique",
    "électrique": "electrique", "gpl": "gpl",
}

BODY_KEYWORDS = {
    "citadine": "citadine", "city car": "citadine", "sghira": "citadine", "sghera": "citadine", "sghir": "citadine", "small": "citadine",
    "berline": "berline", "sedan": "berline",
    "suv": "suv", "4x4": "suv", "tout terrain": "suv", "kbira": "suv", "kbir": "suv", "3alia": "suv",
    "break": "break", "station wagon": "break", "sw": "break", "touring": "break",
    "coupe": "coupe", "coupé": "coupe",
    "cabriolet": "cabriolet", "cabrio": "cabriolet", "convertible": "cabriolet",
    "monospace": "monospace", "minivan": "monospace",
    "utilitaire": "utilitaire", "pick up": "pick_up", "pickup": "pick_up", "truck": "pick_up",
}

# “Family car” describes the use case, not one single body style. Keep all
# practical passenger shapes eligible instead of incorrectly forcing the
# result to monospace/minivans only.
FAMILY_BODY_TYPES = ["monospace", "suv", "break", "berline", "citadine"]
FAMILY_QUERY_TERMS = (
    "family", "famille", "familial", "familiale", "familiaux", "familiales",
    "3aila", "عائلية", "عائلية", "أطفال", "kids", "children", "baby", "bébé",
)


def extract_brand(text: str) -> Optional[str]:
    lower = text.lower()
    for keyword, brand in BRAND_KEYWORDS.items():
        if keyword in lower:
            return brand
    return None


def extract_fuel_type(text: str) -> Optional[str]:
    lower = text.lower()
    for keyword, fuel in FUEL_KEYWORDS.items():
        if keyword in lower:
            return fuel
    return None


def extract_body_type(text: str) -> Optional[str]:
    lower = text.lower()
    for keyword, body in BODY_KEYWORDS.items():
        if keyword in lower:
            return body
    return None


def is_family_query(text: str) -> bool:
    lower = text.lower()
    return any(re.search(rf"\b{re.escape(term)}\b", lower) for term in FAMILY_QUERY_TERMS)


PRICE_PATTERNS = [
    re.compile(r'(?P<min>\d+(?:\s?\d+)*\s*[kK]?)\s*(?:a|à|–|-|jusqu\'?à?|et)\s*(?P<max>\d+(?:\s?\d+)*\s*[kK]?)\s*(?:€|eur|dh|mad|melyoun|mlyoun|alf)?', re.IGNORECASE),
    re.compile(r'(?P<max>\d+(?:\s?\d+)*\s*[kK]?)\s*(?:€|eur|dh|mad|melyoun|mlyoun|alf)?\s*(?:max|maxi|maximum|au plus|plafond)', re.IGNORECASE),
    re.compile(r'(?P<min>\d+(?:\s?\d+)*\s*[kK]?)\s*(?:€|eur|dh|mad|melyoun|mlyoun|alf)?\s*(?:min|mini|minimum|au moins|plancher)', re.IGNORECASE),
    re.compile(r'(?:moins de|max|maxi|maximum|jusqu\'?à?|under|au plus|plafond de)\s*(?P<max>\d+(?:\s?\d+)*\s*[kK]?)\s*(?:€|eur|dh|mad|melyoun|mlyoun|alf)?', re.IGNORECASE),
    re.compile(r'(?:plus de|min|mini|minimum|à partir de|dès|over|au moins)\s*(?P<min>\d+(?:\s?\d+)*\s*[kK]?)\s*(?:€|eur|dh|mad|melyoun|mlyoun|alf)?', re.IGNORECASE),
    re.compile(r'(?P<exact>\d+(?:\s?\d+)*\s*[kK]?)\s*(?:€|eur|dh|mad|melyoun|mlyoun|alf)', re.IGNORECASE),
    re.compile(r'budget\s*(?:de|:)?\s*(?P<min>\d+(?:\s?\d+)*\s*[kK]?)\s*(?:a|à|–|-)\s*(?P<max>\d+(?:\s?\d+)*\s*[kK]?)', re.IGNORECASE),
]

MILEAGE_PATTERNS = [
    re.compile(r'(?P<max>\d+)\s*(?:km|kms|kilomètres?)\s*(?:max|maxi|maximum)?', re.IGNORECASE),
    re.compile(r'(?:moins de|max|maxi|under)\s*(?P<max>\d+)\s*(?:km|kms|kilomètres?)', re.IGNORECASE),
]

YEAR_PATTERNS = [
    re.compile(r'(?P<min>\d{4})\s*(?:a|à|–|-)\s*(?P<max>\d{4})'),
    re.compile(r'(?:après|depuis|>|>=|after)\s*(?P<min>\d{4})', re.IGNORECASE),
    re.compile(r'(?:avant|avant\s*le|<|<=|before)\s*(?P<max>\d{4})', re.IGNORECASE),
    re.compile(r'(?P<year>\d{4})\s*(?:et\s*plus|plus|(?:\+|et\s*plus\s*)?récent)', re.IGNORECASE),
]

MOROCCAN_CITIES = [
    "Casablanca", "Rabat", "Marrakech", "Fès", "Tanger",
    "Agadir", "Meknès", "Oujda", "Kénitra", "Tétouan",
    "Safi", "El Jadida", "Nador", "Laâyoune", "Khouribga",
    "Béni Mellal", "Taza", "Mohammédia", "El Kelâa des Sraghna", "Témara",
    "Settat", "Berrechid", "Sidi Kacem", "Guelmim", "Dakhla",
    "Ben Guerir", "Sefrou", "Youssoufia", "Fnideq", "Martil",
    "M'diq", "Chefchaouen", "Taounate", "Berkane", "Taroudant",
    "Ouarzazate", "Tiznit", "Essaouira", "El Hajeb", "Ifrane",
]

CITY_KEYWORDS = re.compile(
    r'\b('
    r'casablanca|casa|rabat|marrakech|marrakech|fès|fes|tanger|tanger|'
    r'agadir|meknès|meknes|oujda|kénitra|kenitra|tétouan|tetouan|'
    r'safi|el jadida|nador|laâyoune|laayoune|khouribga|'
    r'béni mellal|beni mellal|taza|mohammédia|mohammedia|'
    r'settat|berrechid|dakhla|essaouira|tiznit|ouarzazate|'
    r'taroudant|chefchaouen|berkane|m\'diq|fnideq|martil'
    r')\b',
    re.IGNORECASE,
)


def _clean_number(raw: str) -> str:
    return raw.replace(" ", "")

def _parse_price_value(raw: str, is_melyoun: bool = False, is_alf: bool = False) -> Optional[float]:
    if not raw:
        return None
    cleaned = _clean_number(raw)
    multiplier = 1.0
    if cleaned.lower().endswith('k'):
        multiplier = 1000.0
        cleaned = cleaned[:-1]
    if is_melyoun:
        multiplier = 10000.0
    elif is_alf:
        multiplier = 1000.0
    return float(cleaned) * multiplier

def extract_price(text: str) -> tuple[Optional[float], Optional[float]]:
    # Remove mileage substrings before matching price to prevent '50000km' matching as price
    sanitized_text = re.sub(r'\d+\s*(?:km|kms|kilomètres?)', '', text, flags=re.IGNORECASE)
    # Moroccan users commonly write Dhs; normalize it to the accepted Dh
    # suffix before applying the catalogue price patterns.
    sanitized_text = re.sub(r'\bdhs?\b', 'dh', sanitized_text, flags=re.IGNORECASE)
    for pattern in PRICE_PATTERNS:
        m = pattern.search(sanitized_text)
        if m:
            d = m.groupdict()
            matched_str = m.group(0).lower()
            is_melyoun = 'melyoun' in matched_str or 'mlyoun' in matched_str
            is_alf = 'alf' in matched_str

            if d.get("exact"):
                val = _parse_price_value(d["exact"], is_melyoun, is_alf)
                # An exact stated budget is a hard maximum for catalogue
                # requests: never recommend a vehicle above the user's MAD
                # limit.
                return (None, val) if val is not None else (None, None)
            p_min = _parse_price_value(d["min"], is_melyoun, is_alf) if d.get("min") else None
            p_max = _parse_price_value(d["max"], is_melyoun, is_alf) if d.get("max") else None
            return (p_min, p_max)
    return (None, None)


def extract_mileage(text: str) -> Optional[int]:
    for pattern in MILEAGE_PATTERNS:
        m = pattern.search(text)
        if m:
            d = m.groupdict()
            if d.get("max"):
                return int(_clean_number(d["max"]))
    return None


def extract_year(text: str) -> tuple[Optional[int], Optional[int]]:
    for pattern in YEAR_PATTERNS:
        m = pattern.search(text)
        if m:
            d = m.groupdict()
            if d.get("year"):
                y = int(d["year"])
                return (y, None)
            p_min = int(d["min"]) if d.get("min") else None
            p_max = int(d["max"]) if d.get("max") else None
            return (p_min, p_max)
    return (None, None)


def extract_city(text: str) -> Optional[str]:
    m = CITY_KEYWORDS.search(text)
    if m:
        raw = m.group(0).lower()
        mapping = {
            "casa": "Casablanca", "casablanca": "Casablanca",
            "rabat": "Rabat", "marrakech": "Marrakech", "marrakech": "Marrakech",
            "fès": "Fès", "fes": "Fès", "tanger": "Tanger", "tanger": "Tanger",
            "agadir": "Agadir", "meknès": "Meknès", "meknes": "Meknès",
            "oujda": "Oujda", "kénitra": "Kénitra", "kenitra": "Kénitra",
            "tétouan": "Tétouan", "tetouan": "Tétouan", "safi": "Safi",
            "el jadida": "El Jadida", "nador": "Nador",
            "paris": "Paris", "lyon": "Lyon", "marseille": "Marseille",
            "toulouse": "Toulouse", "bordeaux": "Bordeaux", "lille": "Lille",
        }
        return mapping.get(raw, raw.capitalize())
    return None


def extract_filters_from_query(query: str) -> dict:
    filters = {}
    brand = extract_brand(query)
    if brand:
        filters["brand"] = brand
    fuel = extract_fuel_type(query)
    if fuel:
        filters["fuel_type"] = fuel
    body = extract_body_type(query)
    if body:
        filters["body_type"] = body
    elif is_family_query(query):
        filters["body_type_in"] = FAMILY_BODY_TYPES.copy()
    city = extract_city(query)
    if city:
        filters["city"] = city
    price_min, price_max = extract_price(query)
    if price_min is not None:
        filters["price_min"] = price_min
    if price_max is not None:
        filters["price_max"] = price_max
    mileage_max = extract_mileage(query)
    if mileage_max is not None:
        filters["mileage_max"] = mileage_max
    year_min, year_max = extract_year(query)
    if year_min is not None:
        filters["year_min"] = year_min
    if year_max is not None:
        filters["year_max"] = year_max
    return filters


def semantic_search(query: str, limit: int = 50, precomputed_embedding: list[float] | None = None) -> list[str]:
    try:
        from app.rag.vector_search import compute_query_embedding
        from app.rag.vector_store import vector_store
        embedding = precomputed_embedding or compute_query_embedding(query)
        results = vector_store.search(embedding, limit=limit)
        return [r["vehicle_id"] for r in results if r.get("vehicle_id")]
    except Exception:
        return []
