# 📖 API Reference — AutoMind Backend

Base URL : `http://localhost:8000/api/v1`

Documentation interactive : [Swagger UI](http://localhost:8000/docs) | [ReDoc](http://localhost:8000/redoc)

---

## Véhicules

### `GET /vehicles`
Liste paginée des véhicules avec filtres.

| Paramètre   | Type   | Description                |
|-------------|--------|----------------------------|
| page        | int    | Page (défaut: 1)           |
| limit       | int    | Résultats par page (max 100)|
| fuel_type   | string | Filtre carburant           |
| body_type   | string | Filtre carrosserie         |
| min_price   | float  | Prix minimum               |
| max_price   | float  | Prix maximum               |

### `GET /vehicles/{id}`
Détail d'un véhicule (inclut `trust_score` et `predicted_price`).

### `POST /vehicles/search`
Recherche en langage naturel.

```json
{ "query": "SUV familial diesel moins de 250 000 MAD" }
```

---

## Recommandations

### `POST /recommendations`
Obtient des recommandations hybrides.

```json
{
  "budget_max": 25000,
  "fuel_type": "diesel",
  "body_type": "suv",
  "usage": "familial"
}
```

---

## Chatbot RAG

### `POST /chatbot/message`

```json
{
  "message": "Je cherche une voiture économique pour la ville",
  "history": []
}
```

---

## Prédiction de prix

### `POST /pricing/predict`

```json
{
  "brand": "Peugeot",
  "model": "3008",
  "year": 2022,
  "mileage": 45000,
  "fuel_type": "diesel",
  "body_type": "suv"
}
```

---

## Analytics

### `GET /analytics/overview`
Métriques globales de la plateforme.

### `GET /analytics/trends`
Tendances de prix et demande.

### `GET /analytics/anomalies`
Anomalies détectées (fraude potentielle).
