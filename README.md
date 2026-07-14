# 🚗 Wakala — Marketplace Automobile Intelligente

> Plateforme de vente automobile en ligne combinant **Big Data** et **Intelligence Artificielle** (chatbot RAG, recommandation hybride, graphe de similarité) avec une couche décisionnelle marketing/économique.

---

## 🏗️ Architecture

```
vente-auto-platform/
├── frontend/          → React 18 + TypeScript (UI premium, hero animé)
├── backend/           → FastAPI (API REST, ML, RAG chatbot)
├── data-pipeline/     → Kafka · Spark · Airflow (Medallion architecture)
├── database/          → PostgreSQL · Neo4j · Qdrant (vector store)
├── analytics/         → dbt · Dashboards · Notebooks
└── docs/              → Documentation technique
```

### Stack Technique

| Couche         | Technologies                                    |
| -------------- | ----------------------------------------------- |
| Frontend       | React 18, TypeScript, Vite, Design system clair |
| Backend API    | FastAPI, Pydantic, uvicorn                       |
| IA / ML        | LangChain, scikit-learn, XGBoost, sentence-transformers |
| Big Data       | Apache Kafka, Apache Spark, Apache Airflow       |
| Bases de données | PostgreSQL, Neo4j, Qdrant (pgvector)           |
| Orchestration  | Docker Compose                                   |

### Architecture Medallion (Data Lake)

```
Bronze (brut)  →  Silver (nettoyé)  →  Gold (agrégé / prêt ML)
```

---

## 🚀 Démarrage rapide

### Prérequis

- Docker & Docker Compose v2+
- Node.js 18+ (dev frontend)
- Python 3.11+ (dev backend)

### Lancement complet

```bash
# Cloner et configurer
cp .env.example .env

# Lancer tous les services
docker compose up -d

# Vérifier les services
docker compose ps
```

### Services exposés

| Service       | URL                          |
| ------------- | ---------------------------- |
| Frontend      | http://localhost:3000         |
| Backend API   | http://localhost:8000/docs    |
| Neo4j Browser | http://localhost:7474         |
| Kafka UI      | http://localhost:9021         |
| PostgreSQL    | localhost:5432                |
| Qdrant        | http://localhost:6333         |

---

## 📂 Modules IA

- **Recommandation hybride** : Content-based + Collaborative Filtering
- **Chatbot RAG** : LangChain + LLM + Qdrant vector store
- **Graphe de similarité** : Neo4j + PageRank véhicules/marques
- **Prédiction de prix** : XGBoost sur features véhicule
- **Détection d'anomalies** : Isolation Forest (fraude vendeur)
- **NLP** : Analyse de sentiment avis, recherche sémantique

---

## 📄 Licence

Projet propriétaire — Tous droits réservés.
