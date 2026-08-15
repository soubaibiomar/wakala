"""
content_based.py — Content-based recommendation engine.

PIVOT: Removed mileage as a feature dimension. New-car recommendations
are based on: price, year, body_type, transmission, fuel_type, engine_power.
Mileage is meaningless for new vehicles (always 0).
"""

import math
from functools import lru_cache
from typing import Any, TYPE_CHECKING, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler, StandardScaler

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
else:
    Vehicle = Any


@lru_cache(maxsize=1)
def _cached_scalers() -> tuple[StandardScaler, MinMaxScaler, MinMaxScaler]:
    return (StandardScaler(), MinMaxScaler(), MinMaxScaler())


BODY_TYPE_ORDER = [
    "citadine", "berline", "break", "coupe", "cabriolet",
    "monospace", "suv", "pick_up", "utilitaire",
]

TRANSMISSION_MAP = {"manuelle": 0, "automatique": 1, "semi_auto": 0.5}

FUEL_ORDER = [
    "essence", "diesel", "hybride", "hybride_rechargeable",
    "electrique", "gpl", "hydrogene",
]

# ── PIVOT: Removed mileage_norm ──────────────────────────────────
FEATURE_COLUMNS = [
    "price_norm", "year_norm",
    "body_type_encoded", "transmission_encoded",
    "fuel_encoded", "engine_power_norm",
]


def _encode_body_type(body_type: str) -> float:
    try:
        return BODY_TYPE_ORDER.index(body_type) / (len(BODY_TYPE_ORDER) - 1)
    except (ValueError, IndexError):
        return 0.5


def _encode_fuel(fuel_type: str) -> float:
    try:
        return FUEL_ORDER.index(fuel_type) / (len(FUEL_ORDER) - 1)
    except (ValueError, IndexError):
        return 0.5


def vehicle_to_feature_vector(vehicle: Vehicle) -> np.ndarray:
    raw = np.array([
        float(vehicle.price or 0),
        float(vehicle.year or 2020),
        _encode_body_type(vehicle.body_type or ""),
        TRANSMISSION_MAP.get(vehicle.transmission or "", 0),
        _encode_fuel(vehicle.fuel_type or ""),
        float(vehicle.engine_power_hp or 0),
    ]).reshape(1, -1)
    return raw


def candidate_vehicles_from_filters(
    vehicles: list[Vehicle],
    filters: dict,
) -> list[Vehicle]:
    candidates = []
    for v in vehicles:
        if "brand" in filters and (not v.brand or v.brand.lower() != filters["brand"].lower()):
            continue
        if "city" in filters and (not v.city or v.city.lower() != filters["city"].lower()):
            continue
        if "fuel_type" in filters and v.fuel_type != filters["fuel_type"]:
            continue
        if "body_type" in filters and v.body_type != filters["body_type"]:
            continue
        if "body_type_in" in filters and v.body_type not in filters["body_type_in"]:
            continue
        if "price_min" in filters and (v.price is None or v.price < filters["price_min"]):
            continue
        if "price_max" in filters and (v.price is None or v.price > filters["price_max"]):
            continue
        if "year_min" in filters and (v.year is None or v.year < filters["year_min"]):
            continue
        if "year_max" in filters and (v.year is None or v.year > filters["year_max"]):
            continue
        # ── PIVOT: Removed mileage_max filter (irrelevant for new cars) ──
        candidates.append(v)
    return candidates


def build_feature_matrix(vehicles: list[Vehicle]) -> np.ndarray:
    n = len(vehicles)
    if n == 0:
        return np.empty((0, len(FEATURE_COLUMNS)))

    matrix = np.zeros((n, len(FEATURE_COLUMNS)))
    for i, v in enumerate(vehicles):
        matrix[i, 0] = float(v.price or 0)
        matrix[i, 1] = float(v.year or 2020)
        matrix[i, 2] = _encode_body_type(v.body_type or "")
        matrix[i, 3] = TRANSMISSION_MAP.get(v.transmission or "", 0)
        matrix[i, 4] = _encode_fuel(v.fuel_type or "")
        matrix[i, 5] = float(v.engine_power_hp or 0)

    price_col = matrix[:, 0:1]
    year_col = matrix[:, 1:2]
    engine_col = matrix[:, 5:6]

    price_scaler, year_scaler, engine_scaler = _cached_scalers()
    matrix[:, 0:1] = price_scaler.fit_transform(price_col)
    matrix[:, 1:2] = year_scaler.fit_transform(year_col)
    matrix[:, 5:6] = engine_scaler.fit_transform(engine_col)

    return matrix


def build_query_vector(filters: dict, reference_vehicles: list[Vehicle]) -> np.ndarray:
    n_features = len(FEATURE_COLUMNS)
    query = np.zeros((1, n_features))
    query[0, 2] = _encode_body_type(filters.get("body_type", ""))
    query[0, 3] = TRANSMISSION_MAP.get(filters.get("transmission", ""), 0)
    query[0, 4] = _encode_fuel(filters.get("fuel_type", ""))

    prices = [v.price for v in reference_vehicles if v.price is not None]
    years = [v.year for v in reference_vehicles if v.year is not None]
    powers = [(v.engine_power_hp or 0) for v in reference_vehicles]

    if filters.get("price_min") is not None and filters.get("price_max") is not None:
        ref_price = (filters["price_min"] + filters["price_max"]) / 2
    elif filters.get("price_max") is not None:
        ref_price = filters["price_max"] * 0.85
    else:
        ref_price = float(np.mean(prices)) if prices else 30000.0

    if filters.get("year_min") is not None:
        ref_year = float(filters["year_min"])
    elif filters.get("year_max") is not None:
        ref_year = float(filters["year_max"])
    else:
        ref_year = float(np.mean(years)) if years else 2020.0

    ref_engine = float(np.mean(powers)) if powers else 100.0

    query[0, 0] = ref_price
    query[0, 1] = ref_year
    query[0, 5] = ref_engine

    price_scaler, year_scaler, engine_scaler = _cached_scalers()
    query[:, 0:1] = price_scaler.transform(query[:, 0:1])
    query[:, 1:2] = year_scaler.transform(query[:, 1:2])
    query[:, 5:6] = engine_scaler.transform(query[:, 5:6])

    return query


def compute_content_scores(
    vehicles: list[Vehicle],
    filters: dict,
) -> list[dict]:
    if not vehicles:
        return []

    candidates = candidate_vehicles_from_filters(vehicles, filters)

    if not candidates:
        candidates = vehicles

    matrix = build_feature_matrix(candidates)
    if matrix.shape[0] == 0:
        return []

    query = build_query_vector(filters, candidates)

    similarities = cosine_similarity(query, matrix).flatten()
    sim_min, sim_max = similarities.min(), similarities.max()
    if sim_max > sim_min:
        normalized = (similarities - sim_min) / (sim_max - sim_min)
    else:
        normalized = np.ones_like(similarities)

    results = []
    for i, v in enumerate(candidates):
        results.append({
            "vehicle_id": str(v.id),
            "content_score": float(normalized[i]),
        })

    results.sort(key=lambda x: x["content_score"], reverse=True)
    return results
