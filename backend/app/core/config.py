"""
core/config.py — Configuration centralisée via variables d'environnement.
Charge automatiquement le fichier .env à la racine du backend.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuration de l'application Wakala."""

    # ─── Application ───────────────────────────────────────────
    APP_NAME: str = "Wakala"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ─── Sécurité / JWT ────────────────────────────────────────
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GOOGLE_CLIENT_ID: str = ""

    # ─── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # ─── Emails (SMTP) ─────────────────────────────────────────
    MAIL_SERVER: str = "mailhog"
    MAIL_PORT: int = 1025
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@wakala.ma"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = False

    # ─── PostgreSQL ────────────────────────────────────────────
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "Wakala"
    POSTGRES_USER: str = "Wakala_user"
    POSTGRES_PASSWORD: str

    @property
    def DATABASE_URL(self) -> str:
        """URL de connexion async pour SQLAlchemy (asyncpg)."""
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """URL de connexion synchrone (pour Alembic ou scripts)."""
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ─── Neo4j ─────────────────────────────────────────────────
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str

    # ─── Qdrant ────────────────────────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "vehicle_embeddings"

    # ─── Kafka ─────────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # ─── Groq — LLM ultra-rapide (Désactivé) ──────────────────
    GROQ_API_KEY: str = ""

    @property
    def groq_api_key(self) -> str:
        if not self.GROQ_API_KEY:
            # We don't raise error since we use Ollama now
            return ""
        return self.GROQ_API_KEY

    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # ─── LLM / RAG (Ollama) ───────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434/v1"
    OLLAMA_MODEL_TEXT: str = "qwen3:8b"
    OLLAMA_MODEL_CODE: str = "qwen2.5-coder:7b"
    
    OPENAI_API_KEY: str = "ollama" # placeholder needed for langchain_openai
    LLM_MODEL: str = "qwen3:8b"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
