# 🏗️ Architecture Wakala

## Vue d'ensemble

```mermaid
graph TB
    subgraph Frontend
        UI[React 18 + TypeScript]
        Hero[Hero animé]
        Search[Barre de recherche IA]
        Chat[Chatbot Widget]
    end

    subgraph Backend
        API[FastAPI REST API]
        ML[Modules ML]
        RAG[RAG Pipeline]
    end

    subgraph ML Modules
        REC[Recommandation Hybride]
        PRICE[Prédiction Prix - XGBoost]
        ANOMALY[Détection Anomalies - IF]
        NLP_MOD[NLP - Sentiment + Search]
        GRAPH[Graphe Similarité - Neo4j]
    end

    subgraph Data Pipeline
        KAFKA[Apache Kafka]
        SPARK[Apache Spark]
        AIRFLOW[Apache Airflow]
    end

    subgraph Storage
        PG[(PostgreSQL)]
        NEO[(Neo4j)]
        QD[(Qdrant)]
        LAKE[Data Lake Medallion]
    end

    UI --> API
    Search --> API
    Chat --> RAG
    API --> ML
    ML --> REC & PRICE & ANOMALY & NLP_MOD & GRAPH
    REC --> PG & QD
    GRAPH --> NEO
    RAG --> QD
    KAFKA --> SPARK
    SPARK --> LAKE
    AIRFLOW --> SPARK
    LAKE --> PG
```

## Architecture Medallion

| Couche   | Format  | Contenu                           |
|----------|---------|-----------------------------------|
| Bronze   | JSON    | Données brutes depuis Kafka       |
| Silver   | Parquet | Données nettoyées, typées         |
| Gold     | Parquet | Agrégations, features pour ML     |

## Flux de données

1. **Ingestion** : Sources d'annonces → Kafka → Bronze
2. **Transformation** : Spark Streaming → Silver (temps réel)
3. **Agrégation** : Spark Batch (Airflow) → Gold
4. **ML Training** : Gold → XGBoost, Isolation Forest, Embeddings
5. **Serving** : FastAPI expose les prédictions en temps réel
6. **RAG** : Qdrant + LangChain → Chatbot contextuel
