"""
Générateur de données véhicules réalistes pour le marché marocain.
Basé sur les parts de marché réelles, prix MAD, villes marocaines.
"""
import random
import uuid
from datetime import datetime, timezone
from typing import Optional

BRANDS_WITH_SHARE = [
    ("Dacia", 0.32), ("Renault", 0.12), ("Peugeot", 0.10),
    ("Citroen", 0.08), ("Hyundai", 0.07), ("Kia", 0.06),
    ("Toyota", 0.05), ("Volkswagen", 0.04), ("BMW", 0.03),
    ("Mercedes", 0.03), ("Audi", 0.02), ("Ford", 0.02),
    ("Nissan", 0.02), ("Fiat", 0.02), ("MG", 0.02),
]

MODELS_MAP = {
    "Dacia": [("Sandero", 130), ("Logan", 100), ("Duster", 110),
              ("Lodgy", 60), ("Stepway", 80), ("Jogger", 50)],
    "Renault": [("Clio", 100), ("Captur", 70), ("Megane", 60),
                ("Arkana", 40), ("Kadjar", 30), ("Talisman", 20)],
    "Peugeot": [("208", 90), ("308", 60), ("301", 50), ("3008", 50),
                ("2008", 40), ("Partner", 30), ("Rifter", 20)],
    "Citroen": [("C3", 70), ("C-Elysée", 40), ("Berlingo", 30),
                ("Jumpy", 20), ("C4", 30), ("C5 Aircross", 20)],
    "Hyundai": [("i10", 50), ("i20", 40), ("Accent", 30),
                ("Tucson", 40), ("Santa Fe", 20), ("Kona", 30)],
    "Kia": [("Picanto", 40), ("Rio", 40), ("Ceed", 30),
            ("Sportage", 40), ("Sorento", 20), ("Stonic", 20)],
    "Toyota": [("Yaris", 40), ("Corolla", 30), ("Hilux", 30),
               ("RAV4", 20), ("Land Cruiser", 10), ("CH-R", 20)],
    "Volkswagen": [("Polo", 30), ("Golf", 25), ("Passat", 15),
                   ("Tiguan", 20), ("T-Cross", 15), ("Amarok", 10)],
    "BMW": [("Serie 1", 20), ("Serie 3", 18), ("X1", 15),
            ("X3", 12), ("X5", 8), ("Serie 5", 10)],
    "Mercedes": [("Classe A", 18), ("Classe C", 15), ("GLA", 12),
                 ("GLC", 10), ("Classe E", 8), ("Vito", 8)],
    "Audi": [("A3", 15), ("A1", 12), ("Q3", 10), ("Q5", 8), ("A4", 10)],
    "Ford": [("Fiesta", 20), ("Focus", 15), ("Kuga", 15), ("Ranger", 15)],
    "Nissan": [("Micra", 20), ("Qashqai", 25), ("Juke", 15), ("Navara", 10)],
    "Fiat": [("500", 25), ("Panda", 20), ("Tipo", 15), ("Doblo", 15)],
    "MG": [("ZS", 20), ("MG5", 15), ("HS", 15), ("Marvel R", 10)],
}

FUEL_DISTRIBUTION = {"diesel": 0.55, "essence": 0.35, "hybride": 0.07, "electrique": 0.03}

BODY_DISTRIBUTION = {
    "berline": 0.30, "citadine": 0.25, "suv": 0.25,
    "break": 0.05, "coupe": 0.03, "cabriolet": 0.02,
    "monospace": 0.07, "utilitaire": 0.03,
}

TRANSMISSION_DISTRIBUTION = {"manuelle": 0.75, "automatique": 0.25}

MOROCCAN_CITIES = [
    ("Casablanca", 0.18), ("Rabat", 0.10), ("Marrakech", 0.09),
    ("Fes", 0.07), ("Tanger", 0.07), ("Agadir", 0.06),
    ("Oujda", 0.04), ("Kenitra", 0.04), ("Tetouan", 0.04),
    ("Safi", 0.03), ("Meknes", 0.03), ("El Jadida", 0.03),
    ("Nador", 0.03), ("Beni Mellal", 0.02), ("Laayoune", 0.02),
    ("Mohammedia", 0.02), ("Khouribga", 0.02), ("Sale", 0.02),
    ("Berrechid", 0.02), ("Settat", 0.02),
]

COLORS = ["Noir", "Blanc", "Gris", "Bleu", "Rouge", "Argent", "Beige",
          "Vert", "Orange", "Marron", "Bordeaux", "Bleu Nuit"]

YEAR_WEIGHTS = {y: max(5, 20 - abs(2026 - y) * 2) for y in range(2010, 2027)}


def _weighted_choice(items_with_weights: list[tuple]) -> any:
    items, weights = zip(*items_with_weights)
    return random.choices(items, weights=weights, k=1)[0]


def _brand_model_price_range(brand: str, model: str, year: int) -> tuple[int, int]:
    base = {
        "Dacia": (80000, 250000), "Renault": (90000, 350000),
        "Peugeot": (100000, 400000), "Citroen": (80000, 300000),
        "Hyundai": (90000, 350000), "Kia": (90000, 350000),
        "Toyota": (120000, 500000), "Volkswagen": (120000, 450000),
        "BMW": (200000, 800000), "Mercedes": (200000, 800000),
        "Audi": (180000, 700000), "Ford": (90000, 300000),
        "Nissan": (100000, 350000), "Fiat": (70000, 250000),
        "MG": (150000, 450000),
    }
    low, high = base.get(brand, (80000, 300000))
    age_factor = 1 + (2026 - year) * 0.04
    premium = 0
    if model in ("X5", "X3", "GLC", "GLA", "Q5", "Q3", "Land Cruiser", "Tucson", "Sportage"):
        premium = 50000
    return int(low / age_factor) + premium, int(high / age_factor) + premium


def generate_vehicle() -> dict:
    brand = _weighted_choice(BRANDS_WITH_SHARE)
    model = _weighted_choice(MODELS_MAP[brand])
    year = _weighted_choice(list(YEAR_WEIGHTS.items()))

    price_low, price_high = _brand_model_price_range(brand, model, year)
    price = random.randint(price_low, price_high)
    price = round(price / 1000) * 1000

    mileage = max(0, int(random.gauss(
        (2026 - year) * 18000,
        (2026 - year) * 8000
    )))

    fuel = _weighted_choice(list(FUEL_DISTRIBUTION.items()))
    body = _weighted_choice(list(BODY_DISTRIBUTION.items()))
    transmission = _weighted_choice(list(TRANSMISSION_DISTRIBUTION.items()))
    city = _weighted_choice(MOROCCAN_CITIES)

    power_map = {"citadine": (60, 100), "berline": (80, 150),
                 "suv": (100, 200), "break": (90, 160),
                 "coupe": (150, 300), "cabriolet": (100, 200),
                 "monospace": (90, 150), "utilitaire": (70, 120)}
    p_low, p_high = power_map.get(body, (75, 150))
    power = random.randint(p_low, p_high)

    description = f"{brand} {model} ({year}) en excellent état, "
    description += f"entretien régulier chez le concessionnaire, "
    description += f"{mileage:,} km, {fuel}, {transmission}. "
    description += f"Première main, carnet d'entretien à jour, "
    description += f"garantie disponible. Prix: {price:,} MAD."

    return {
        "brand": brand,
        "model": model,
        "year": year,
        "price": price,
        "mileage": mileage,
        "fuel_type": fuel,
        "body_type": body,
        "transmission": transmission,
        "engine_power_hp": power,
        "color": random.choice(COLORS),
        "doors": random.choice([3, 5]),
        "seats": random.choice([5, 5, 5, 7]),
        "city": city,
        "description": description,
        "source": "generator",
        "source_url": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def generate_listings(count: int = 50) -> list[dict]:
    return [generate_vehicle() for _ in range(count)]
