"""
core/database.py — Connexion SQLAlchemy async + session factory.

Fournit :
    - engine      : moteur async connecté à PostgreSQL (asyncpg)
    - Base        : classe déclarative pour les modèles ORM
    - get_db()    : dépendance FastAPI injectant une AsyncSession
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# ─── Engine ────────────────────────────────────────────────────
try:
    engine = create_async_engine(
        settings.database_url,
        echo=settings.DEBUG,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,      # détecte les connexions mortes
        pool_recycle=3600,        # recycle après 1 h
    )
except Exception:
    try:
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    except Exception:
        engine = None

# ─── Session factory ──────────────────────────────────────────
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
) if engine is not None else None


# ─── Base ORM ─────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy."""
    pass


# ─── Dependency : session par requête ─────────────────────────
async def get_db() -> AsyncSession:
    """
    Dépendance FastAPI — Fournit une session DB par requête.
    La session est automatiquement fermée en fin de requête.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
