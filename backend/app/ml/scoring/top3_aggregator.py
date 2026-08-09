"""
app.ml.scoring.top3_aggregator — Agrégation des versions par modèle,
application de la règle de diversité (1 voiture par marque) et restitution du Top 3.
"""

from typing import Optional, Any, Union, Dict, List

try:
    from pydantic import BaseModel, Field
except ImportError:
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__
        def model_dump(self, **kwargs):
            return self.__dict__
    def Field(default=None, **kwargs):
        return default

class Top3VehicleItem(BaseModel):
    vehicle_id: str
    brand: str
    model: str
    version_name: Optional[str] = None
    price: float
    year: int
    match_score: float
    score_breakdown: Dict[str, Any]
    key_facts: List[str]
    budget_margin: Optional[float] = None
    body_type: Optional[str] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    mileage: Optional[int] = None
    image_url: Optional[str] = None


class Top3Response(BaseModel):
    items: List[Top3VehicleItem]
    relaxed_filter: Optional[str] = None
    message: Optional[str] = None



class Top3Aggregator:
    """Agrégateur de résultats pour le Top 3 Wakala."""

    def __init__(self):
        pass

    def _get_val(self, obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def aggregate_top3(
        self,
        scored_vehicles: List[Dict[str, Any]],
        vehicles_map: Dict[str, Any],
        relaxed_filter: Optional[str] = None,
        limit: int = 3
    ) -> Top3Response:
        """
        1. Regroupe par modèle en conservant la meilleure finition/version.
        2. Applique la diversité : max 1 modèle par marque.
        3. Sélectionne les top N résultats (par défaut 3).
        """
        # Tri initial par score décroissant
        sorted_scored = sorted(scored_vehicles, key=lambda x: x["final_score"], reverse=True)

        # 1. Regroupement par modèle (on ne garde que le meilleur véhicule d'un modèle donné)
        best_per_model: Dict[str, Dict[str, Any]] = {}
        for item in sorted_scored:
            vid = item["vehicle_id"]
            vehicle_obj = vehicles_map.get(vid)
            if not vehicle_obj:
                continue

            brand = (self._get_val(vehicle_obj, "brand", "") or "").strip().title()
            model = (self._get_val(vehicle_obj, "model", "") or "").strip().title()
            model_key = f"{brand}::{model}".lower()

            if model_key not in best_per_model:
                best_per_model[model_key] = {
                    "scored": item,
                    "vehicle": vehicle_obj,
                }

        # 2. Règle de diversité : max 1 modèle par marque
        seen_brands = set()
        diverse_selection = []
        overflow_selection = []

        for model_key, data in best_per_model.items():
            brand = (self._get_val(data["vehicle"], "brand", "") or "").strip().lower()
            if brand not in seen_brands:
                seen_brands.add(brand)
                diverse_selection.append(data)
            else:
                overflow_selection.append(data)

        # Si moins de 3 marques disponibles, on complète avec l'overflow
        final_selected = diverse_selection[:limit]
        if len(final_selected) < limit and overflow_selection:
            needed = limit - len(final_selected)
            final_selected.extend(overflow_selection[:needed])

        # 3. Construction des items de restitution
        items: List[Top3VehicleItem] = []
        for entry in final_selected:
            s = entry["scored"]
            v = entry["vehicle"]

            version_name = self._get_val(v, "version")
            if not version_name:
                version_name = f"{self._get_val(v, 'brand', '')} {self._get_val(v, 'model', '')} {self._get_val(v, 'year', '')}"

            # Extraction image si présente
            image_url = None
            images = self._get_val(v, "images", [])
            if images and len(images) > 0:
                first_img = images[0]
                if isinstance(first_img, dict):
                    image_url = first_img.get("file_path")
                elif hasattr(first_img, "file_path"):
                    image_url = getattr(first_img, "file_path")

            items.append(
                Top3VehicleItem(
                    vehicle_id=str(s["vehicle_id"]),
                    brand=self._get_val(v, "brand", ""),
                    model=self._get_val(v, "model", ""),
                    version_name=version_name,
                    price=float(self._get_val(v, "price", 0.0)),
                    year=int(self._get_val(v, "year", 2020)),
                    match_score=float(s["final_score"]),
                    score_breakdown=s["score_breakdown"],
                    key_facts=s["key_facts"],
                    budget_margin=s.get("budget_margin"),
                    body_type=self._get_val(v, "body_type"),
                    fuel_type=self._get_val(v, "fuel_type"),
                    transmission=self._get_val(v, "transmission"),
                    mileage=self._get_val(v, "mileage"),
                    image_url=image_url,
                )
            )

        message = None
        if relaxed_filter:
            messages_map = {
                "puissance": "Nous avons élargi votre critère de puissance minimale pour trouver les meilleures alternatives.",
                "carrosserie": "Nous avons élargi le type de carrosserie pour vous proposer des modèles équivalents.",
                "places": "Nous avons élargi le nombre de places pour trouver des véhicules compatibles.",
                "energie": "Nous avons élargi le choix de motorisation/carburant pour respecter votre budget.",
                "marque": "Nous avons élargi le choix des marques pour vous proposer des véhicules parfaitement adaptés.",
                "budget": "Nous avons légèrement assoupli le budget pour afficher les options les plus pertinentes.",
            }
            message = messages_map.get(relaxed_filter, f"Critère '{relaxed_filter}' élargi pour obtenir au moins 3 candidates.")

        return Top3Response(items=items, relaxed_filter=relaxed_filter, message=message)


top3_aggregator = Top3Aggregator()
