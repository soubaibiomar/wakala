"""
price_model.py — XGBoost price predictor with proper feature engineering.

Features:
  - Numeric: year, mileage, engine_power_hp, doors, seats
  - Categorical: brand, model, fuel_type, body_type, transmission, city
  - Target: price (MAD)

Handles cold start: if model file missing, returns fallback estimate.
Market range: 40 000 - 400 000 MAD (Moroccan used cars).
"""

import json
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder, StandardScaler

from app.models.vehicle import Vehicle

MODEL_DIR = Path(__file__).parent / "model"
MODEL_PATH = MODEL_DIR / "price_model.ubj"
ENCODERS_PATH = MODEL_DIR / "encoders.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
FEATURES_PATH = MODEL_DIR / "feature_columns.json"

NUMERIC_FEATURES = ["year", "mileage", "engine_power_hp", "doors", "seats"]
CATEGORICAL_FEATURES = ["brand", "model", "fuel_type", "body_type", "transmission", "city"]

ALL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

FALLBACK_PRICE = 150_000.0


class PriceModel:
    def __init__(self, model_dir: Optional[Path] = None):
        self.model: Optional[xgb.XGBRegressor] = None
        self.encoders: dict[str, LabelEncoder] = {}
        self.scaler: Optional[StandardScaler] = None
        self.feature_columns: list[str] = []
        self._model_dir = model_dir or MODEL_DIR
        self._load()

    def _load(self):
        model_path = self._model_dir / "price_model.ubj"
        encoders_path = self._model_dir / "encoders.pkl"
        scaler_path = self._model_dir / "scaler.pkl"
        features_path = self._model_dir / "feature_columns.json"
        if model_path.exists():
            self.model = xgb.XGBRegressor()
            self.model.load_model(str(model_path))
        if encoders_path.exists():
            with open(encoders_path, "rb") as f:
                self.encoders = pickle.load(f)
        if scaler_path.exists():
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
        if features_path.exists():
            with open(features_path) as f:
                self.feature_columns = json.load(f)

    def _encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in CATEGORICAL_FEATURES:
            if col in df.columns and col in self.encoders:
                le = self.encoders[col]
                df[col] = df[col].astype(str)
                known = set(le.classes_)
                df[col] = df[col].apply(
                    lambda v: le.transform([v])[0] if v in known else -1
                )
            elif col in df.columns:
                df[col] = -1
        return df

    def _scale_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.scaler is not None:
            cols = [c for c in NUMERIC_FEATURES if c in df.columns]
            if cols:
                df[cols] = self.scaler.transform(df[cols])
        return df

    def _build_features(self, vehicle: dict) -> pd.DataFrame:
        row = {
            "year": vehicle.get("year", 2020),
            "mileage": vehicle.get("mileage", 50_000),
            "engine_power_hp": vehicle.get("engine_power_hp") or 100,
            "doors": vehicle.get("doors", 5),
            "seats": vehicle.get("seats", 5),
            "brand": vehicle.get("brand", "Inconnu"),
            "model": vehicle.get("model", "Inconnu"),
            "fuel_type": vehicle.get("fuel_type", "essence"),
            "body_type": vehicle.get("body_type", "berline"),
            "transmission": vehicle.get("transmission", "manuelle"),
            "city": vehicle.get("city", "Casablanca"),
        }
        df = pd.DataFrame([row])
        df = self._encode_categorical(df)
        df = self._scale_numeric(df)
        return df[self.feature_columns] if self.feature_columns else df

    def predict(self, vehicle: dict) -> dict:
        if self.model is None:
            return {
                "predicted_price": FALLBACK_PRICE,
                "confidence_interval": (FALLBACK_PRICE * 0.85, FALLBACK_PRICE * 1.15),
                "method": "fallback",
                "features_importance": {},
            }
        X = self._build_features(vehicle)
        pred = float(self.model.predict(X)[0])
        pred = max(10_000, min(pred, 1_500_000))
        margin = pred * 0.10
        importance = {}
        if hasattr(self.model, "feature_importances_"):
            cols = self.feature_columns or ALL_FEATURES
            importance = dict(zip(cols, self.model.feature_importances_.tolist()))
        return {
            "predicted_price": round(pred, 2),
            "confidence_interval": (
                round(max(0, pred - margin), 2),
                round(pred + margin, 2),
            ),
            "method": "xgboost",
            "features_importance": importance,
        }

    def train(self, vehicles: list[Vehicle]):
        if len(vehicles) < 10:
            raise ValueError(f"Insufficient data: need >= 10 vehicles, got {len(vehicles)}")

        records = []
        for v in vehicles:
            records.append({
                "year": v.year,
                "mileage": v.mileage,
                "engine_power_hp": v.engine_power_hp or 100,
                "doors": v.doors,
                "seats": v.seats,
                "brand": v.brand,
                "model": v.model,
                "fuel_type": v.fuel_type,
                "body_type": v.body_type,
                "transmission": v.transmission,
                "city": v.city,
                "price": v.price,
            })

        df = pd.DataFrame(records)
        y = df["price"].values
        X = df.drop(columns=["price"])

        for col in CATEGORICAL_FEATURES:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.encoders[col] = le

        self.scaler = StandardScaler()
        X[NUMERIC_FEATURES] = self.scaler.fit_transform(X[NUMERIC_FEATURES])

        self.feature_columns = list(X.columns)
        self.model = xgb.XGBRegressor(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
        )
        self.model.fit(X, y)

        self.save()

    def save(self):
        self._model_dir.mkdir(parents=True, exist_ok=True)
        model_path = self._model_dir / "price_model.ubj"
        encoders_path = self._model_dir / "encoders.pkl"
        scaler_path = self._model_dir / "scaler.pkl"
        features_path = self._model_dir / "feature_columns.json"
        if self.model:
            self.model.save_model(str(model_path))
        with open(encoders_path, "wb") as f:
            pickle.dump(self.encoders, f)
        with open(scaler_path, "wb") as f:
            pickle.dump(self.scaler, f)
        with open(features_path, "w") as f:
            json.dump(self.feature_columns, f)


price_model = PriceModel()
