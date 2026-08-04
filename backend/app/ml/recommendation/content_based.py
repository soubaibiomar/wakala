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
def _cached_scalers() -> tuple[StandardScaler, MinMaxScaler, MinMaxScaler, MinMaxScaler, MinMaxScaler]:
    return (StandardScaler(), MinMaxScaler(), MinMaxScaler(), MinMaxScaler(), MinMaxScaler())


BODY_TYPE_ORDER = [
    "citadine", "berline", "break", "coupe", "cabriolet",
    "monospace", "suv", "pick_up", "utilitaire",
]

TRANSMISSION_MAP = {"manuelle": 0, "automatique": 1, "semi_auto": 0.5}

FUEL_ORDER = [
    "essence", "diesel", "hybride", "hybride_rechargeable",
    "electrique", "gpl", "hydrogene",
]

FEATURE_COLUMNS = [
    "price_norm", "year_norm", "mileage_norm",
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
        float(vehicle.price),
        float(vehicle.year),
        float(vehicle.mileage),
        _encode_body_type(vehicle.body_type),
        TRANSMISSION_MAP.get(vehicle.transmission, 0),
        _encode_fuel(vehicle.fuel_type),
        float(vehicle.engine_power_hp or 0),
    ]).reshape(1, -1)
    return raw


def candidate_vehicles_from_filters(
    vehicles: list[Vehicle],
    filters: dict,
) -> list[Vehicle]:
    candidates = []
    for v in vehicles:
        if "brand" in filters and v.brand.lower() != filters["brand"].lower():
            continue
        if "city" in filters and v.city.lower() != filters["city"].lower():
            continue
        if "fuel_type" in filters and v.fuel_type != filters["fuel_type"]:
            continue
        if "body_type" in filters and v.body_type != filters["body_type"]:
            continue
        if "body_type_in" in filters and v.body_type not in filters["body_type_in"]:
            continue
        if "price_min" in filters and v.price < filters["price_min"]:
            continue
        if "price_max" in filters and v.price > filters["price_max"]:
            continue
        if "year_min" in filters and v.year < filters["year_min"]:
            continue
        if "year_max" in filters and v.year > filters["year_max"]:
            continue
        if "mileage_max" in filters and v.mileage > filters["mileage_max"]:
            continue
        candidates.append(v)
    return candidates


def build_feature_matrix(vehicles: list[Vehicle]) -> np.ndarray:
    n = len(vehicles)
    if n == 0:
        return np.empty((0, len(FEATURE_COLUMNS)))

    matrix = np.zeros((n, len(FEATURE_COLUMNS)))
    for i, v in enumerate(vehicles):
        matrix[i, 0] = float(v.price)
        matrix[i, 1] = float(v.year)
        matrix[i, 2] = float(v.mileage)
        matrix[i, 3] = _encode_body_type(v.body_type)
        matrix[i, 4] = TRANSMISSION_MAP.get(v.transmission, 0)
        matrix[i, 5] = _encode_fuel(v.fuel_type)
        matrix[i, 6] = float(v.engine_power_hp or 0)

    price_col = matrix[:, 0:1]
    year_col = matrix[:, 1:2]
    mileage_col = matrix[:, 2:3]
    engine_col = matrix[:, 6:7]

    price_scaler, year_scaler, mileage_scaler, engine_scaler, _ = _cached_scalers()
    matrix[:, 0:1] = price_scaler.fit_transform(price_col)
    matrix[:, 1:2] = year_scaler.fit_transform(year_col)
    matrix[:, 2:3] = mileage_scaler.fit_transform(mileage_col)
    matrix[:, 6:7] = engine_scaler.fit_transform(engine_col)

    return matrix


def build_query_vector(filters: dict, reference_vehicles: list[Vehicle]) -> np.ndarray:
    n_features = len(FEATURE_COLUMNS)
    query = np.zeros((1, n_features))
    query[0, 3] = _encode_body_type(filters.get("body_type", ""))
    query[0, 4] = TRANSMISSION_MAP.get(filters.get("transmission", ""), 0)
    query[0, 5] = _encode_fuel(filters.get("fuel_type", ""))

    if filters.get("price_min") is not None and filters.get("price_max") is not None:
        ref_price = (filters["price_min"] + filters["price_max"]) / 2
    elif filters.get("price_max") is not None:
        ref_price = filters["price_max"] * 0.85
    else:
        ref_price = float(np.mean([v.price for v in reference_vehicles])) if reference_vehicles else 30000

    if filters.get("year_min") is not None:
        ref_year = float(filters["year_min"])
    elif filters.get("year_max") is not None:
        ref_year = float(filters["year_max"])
    else:
        ref_year = float(np.mean([v.year for v in reference_vehicles])) if reference_vehicles else 2020

    if filters.get("mileage_max") is not None:
        ref_mileage = float(filters["mileage_max"]) * 0.5
    else:
        ref_mileage = float(np.mean([v.mileage for v in reference_vehicles])) if reference_vehicles else 50000

    ref_engine = float(np.mean([(v.engine_power_hp or 0) for v in reference_vehicles])) if reference_vehicles else 100

    query[0, 0] = ref_price
    query[0, 1] = ref_year
    query[0, 2] = ref_mileage
    query[0, 6] = ref_engine

    price_scaler, year_scaler, mileage_scaler, engine_scaler, _ = _cached_scalers()
    query[:, 0:1] = price_scaler.transform(query[:, 0:1])
    query[:, 1:2] = year_scaler.transform(query[:, 1:2])
    query[:, 2:3] = mileage_scaler.transform(query[:, 2:3])
    query[:, 6:7] = engine_scaler.transform(query[:, 6:7])

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
