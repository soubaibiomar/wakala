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
    "essence": "essence", "petrol": "essence", "super": "essence",
    "diesel": "diesel", "gazoil": "diesel",
    "hybride": "hybride", "hybrid": "hybride", "hybride rechargeable": "hybride_rechargeable",
    "phev": "hybride_rechargeable", "electrique": "electrique", "electric": "electrique",
    "électrique": "electrique", "gpl": "gpl",
}

BODY_KEYWORDS = {
    "citadine": "citadine", "city car": "citadine",
    "berline": "berline", "sedan": "berline",
    "suv": "suv", "4x4": "suv", "tout terrain": "suv",
    "break": "break", "station wagon": "break", "sw": "break",
    "coupe": "coupe", "coupé": "coupe",
    "cabriolet": "cabriolet", "cabrio": "cabriolet", "convertible": "cabriolet",
    "monospace": "monospace", "minivan": "monospace",
    "utilitaire": "utilitaire", "pick up": "pick_up", "pickup": "pick_up",
}


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


PRICE_PATTERNS = [
    re.compile(r'(?P<min>\d+(?:\s?\d+)*)\s*(?:a|à|–|-|jusqu\'?à?|et)\s*(?P<max>\d+(?:\s?\d+)*)\s*(?:€|eur|dh|mad)?', re.IGNORECASE),
    re.compile(r'(?:moins de|max|maxi|maximum|jusqu\'?à?)\s*(?P<max>\d+(?:\s?\d+)*)\s*(?:€|eur|dh|mad)?', re.IGNORECASE),
    re.compile(r'(?:plus de|min|mini|minimum|à partir de|dès)\s*(?P<min>\d+(?:\s?\d+)*)\s*(?:€|eur|dh|mad)?', re.IGNORECASE),
    re.compile(r'(?P<exact>\d+(?:\s?\d+)*)\s*(?:€|eur|dh|mad)', re.IGNORECASE),
    re.compile(r'budget\s*(?:de|:)?\s*(?P<min>\d+(?:\s?\d+)*)\s*(?:a|à|–|-)\s*(?P<max>\d+(?:\s?\d+)*)', re.IGNORECASE),
]

MILEAGE_PATTERNS = [
    re.compile(r'(?P<max>\d+)\s*(?:km|kms|kilomètres?)\s*(?:max|maxi|maximum)?', re.IGNORECASE),
    re.compile(r'(?:moins de|max|maxi)\s*(?P<max>\d+)\s*(?:km|kms|kilomètres?)', re.IGNORECASE),
]

YEAR_PATTERNS = [
    re.compile(r'(?P<min>\d{4})\s*(?:a|à|–|-)\s*(?P<max>\d{4})'),
    re.compile(r'(?:après|depuis|>|>=)\s*(?P<min>\d{4})', re.IGNORECASE),
    re.compile(r'(?:avant|avant\s*le|<|<=)\s*(?P<max>\d{4})', re.IGNORECASE),
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

def extract_price(text: str) -> tuple[Optional[float], Optional[float]]:
    for pattern in PRICE_PATTERNS:
        m = pattern.search(text)
        if m:
            d = m.groupdict()
            if d.get("exact"):
                val = float(_clean_number(d["exact"]))
                return (val * 0.85, val * 1.15)
            p_min = float(_clean_number(d["min"])) if d.get("min") else None
            p_max = float(_clean_number(d["max"])) if d.get("max") else None
            return (p_min, p_max)
    return (None, None)


def extract_mileage(text: str) -> Optional[int]:
    for pattern in MILEAGE_PATTERNS:
        m = pattern.search(text)
        if m:
            return int(m.group("max"))
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


def semantic_search(query: str, limit: int = 50) -> list[str]:
    try:
        from app.rag.embeddings import embedding_service
        from app.rag.vector_store import vector_store
        embedding = embedding_service.embed_text(query)
        results = vector_store.search(embedding, limit=limit)
        return [r["vehicle_id"] for r in results if r.get("vehicle_id")]
    except Exception:
        return []
