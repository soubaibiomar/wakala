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
    DEBUG: bool = False

    # ─── Sécurité / JWT ────────────────────────────────────────
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GOOGLE_CLIENT_ID: str = ""

    # ─── CORS ──────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://wakala-jzdd.vercel.app", 
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
    POSTGRES_PASSWORD: str = ""

    # Optional direct cloud URL (Neon). When set, it takes precedence over
    # the split POSTGRES_* settings below.
    DATABASE_URL: str | None = None

    @property
    def database_url(self) -> str:
        """URL de connexion async pour SQLAlchemy (asyncpg)."""
        if self.DATABASE_URL:
            if self.DATABASE_URL.startswith("postgresql+asyncpg://"):
                return self.DATABASE_URL
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """URL de connexion synchrone (pour Alembic ou scripts)."""
        if self.DATABASE_URL:
            return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1).replace("postgresql://", "postgresql+psycopg2://", 1)
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ─── Neo4j ─────────────────────────────────────────────────
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""

    # ─── Qdrant ────────────────────────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None
    QDRANT_COLLECTION: str = "vehicle_embeddings"

    # ─── Kafka ─────────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    # ─── OpenRouter cloud LLMs with native provider fallback ────────────────
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "liquid/lfm-2.5-2.6b:free"
    OPENROUTER_MODELS: list[str] = [
        "liquid/lfm-2.5-2.6b:free",
        "minimax/minimax-m3:free",
        "openrouter/free",
    ]

    # ─── Groq — LLM ultra-rapide (Désactivé) ──────────────────
    GROQ_API_KEY: str = ""

    @property
    def groq_api_key(self) -> str:
        if not self.GROQ_API_KEY:
            return ""
        return self.GROQ_API_KEY

    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # ─── LLM / RAG ────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = ""
    EMBEDDING_MODEL: str = "hash-1024"

    # ─── Hugging Face / Cohere ────────────────────────────────
    HF_TOKEN: str = ""
    HUGGINGFACE_API_KEY: str = ""
    COHERE_API_KEY: str = ""

    # ─── Voice AI (server-side only) ──────────────────────────
    # Credentials are intentionally never exposed to the frontend bundle.
    ELEVENLABS_API_KEY: str = ""
    TTS_VOICE_FR: str = ""
    TTS_VOICE_DARIJA: str = ""
    TTS_VOICE_AR: str = ""
    TTS_VOICE_EN: str = ""
    VOICE_MAX_SECONDS: int = 90


    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.APP_ENV != "development" and self.DEBUG:
            raise ValueError("DEBUG must be false outside development")
        # ─── CRITICAL: Reject known placeholder SECRET_KEY values ──
        _KNOWN_PLACEHOLDERS = {
            "change-me-in-production-use-openssl-rand-hex-32",
            "changeme",
            "secret",
            "your-secret-key-here",
        }
        if self.SECRET_KEY in _KNOWN_PLACEHOLDERS:
            import warnings
            warnings.warn(
                "\n"
                "╔══════════════════════════════════════════════════════════╗\n"
                "║  ⚠️  SECURITY WARNING: SECRET_KEY is a placeholder!     ║\n"
                "║  Generate a real key:                                    ║\n"
                "║  python -c \"import secrets; print(secrets.token_hex(32))\"║\n"
                "╚══════════════════════════════════════════════════════════╝\n",
                stacklevel=2,
            )
            if self.APP_ENV != "development":
                raise ValueError(
                    "FATAL: SECRET_KEY must not be a placeholder in non-development environments. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
                )


settings = Settings()
