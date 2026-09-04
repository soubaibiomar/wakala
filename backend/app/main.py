"""
Wakala Backend — Point d'entrée FastAPI.

Lance le serveur avec :
    uvicorn app.main:app --reload --port 8000

Documentation interactive :
    http://localhost:8000/docs   (Swagger UI)
    http://localhost:8000/redoc  (ReDoc)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    RateLimitExceeded = Exception
    def _rate_limit_exceeded_handler(request, exc): pass

from app.api.middlewares.security import SecurityHeadersMiddleware, AuditLogMiddleware, user_or_ip_key_func

from app.services.health_checker import start_health_checker

# ─── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    import logging
    logger = logging.getLogger(__name__)

    # 1. Vérification PostgreSQL
    try:
        from app.core.database import engine
        from sqlalchemy import text
        if engine is not None:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("PostgreSQL connection successful.")
        else:
            logger.warning("PostgreSQL engine not configured. Skipping startup check.")
    except Exception as e:
        logger.warning(f"PostgreSQL connection check failed (continuing gracefully): {e}")

    # 2. Vérification Qdrant
    try:
        from app.services.ai.qdrant import get_qdrant_client
        qdrant = get_qdrant_client()
        if qdrant is not None:
            await qdrant.get_collections()
            logger.info("Qdrant connection successful.")
        else:
            logger.info("Qdrant client not configured. Skipping startup check.")
    except Exception as e:
        logger.warning(f"Qdrant connection check failed (continuing gracefully): {e}")

    # Démarrage des tâches de fond
    start_health_checker()
    
    yield
    # Cleanup si nécessaire

# ─── Rate Limiter ────────────────────────────────────────────────
from app.core.limiter import limiter

from app.core.config import settings
from app.api.routes_auth import router as auth_router
from app.api.routes_users import router as users_router
from app.api.routes_vehicles import router as vehicles_router
from app.api.routes_listings import router as listings_router
from app.api.routes_reviews import router as reviews_router
from app.api.routes_recommendation import router as recommendation_router
from app.api.routes_chatbot import router as chatbot_router
from app.api.routes_pricing import router as pricing_router
from app.api.routes_vision import router as vision_router
from app.api.routes_admin import router as admin_router
from app.api.routes_customs import router as customs_router
from app.api.routes_transactions import router as transactions_router
from app.api.routes_search import router as search_router
from app.api.routes_messages import router as messages_router
from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.maintenance import router as maintenance_router
from app.api.routes_favorites import router as favorites_router
from app.api.routes_offers import router as offers_router
from app.api.routes_voice import router as voice_router
from app.api.routes_new_catalog import router as new_catalog_router
from app.api.routes_comparator import router as comparator_router
from app.api.routes_test_drives import router as test_drives_router
from app.api.routes_seo import router as seo_router
from app.api.routes_seo_pages import router as seo_pages_router
from app.api.routes_vehicle_options import router as vehicle_options_router
from app.api.routes_consent import router as consent_router

# ─── Application FastAPI ───────────────────────────────────────

app = FastAPI(
    title="Wakala API",
    lifespan=lifespan,
    description=(
        "API REST de la marketplace automobile intelligente Wakala.\n\n"
        "Modules disponibles :\n"
        "- **Auth** : Inscription, connexion JWT\n"
        "- **Users** : Gestion de profil, vérification TrustBadge\n"
        "- **Vehicles** : CRUD véhicules, recherche par filtres\n"
        "- **Listings** : Publication et gestion d'annonces\n"
        "- **Reviews** : Avis avec analyse de sentiment (NLP)\n"
        "- **Pricing** : Prédiction de prix XGBoost\n\n"
        "Modules IA (à venir) :\n"
        "- Détection d'anomalies (Isolation Forest)\n"
        "- Analyse d'images (vision)"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Avatars are intentionally public profile media; receipts and identity
# documents are served through authenticated routes only.
os.makedirs("uploads/avatars", exist_ok=True)
app.mount("/uploads/avatars", StaticFiles(directory="uploads/avatars"), name="avatars")

# ─── Static Files (Uploads) ────────────────────────────────────
# ─── CORS ──────────────────────────────────────────────────────
cors_origins = list(settings.CORS_ORIGINS) if settings.CORS_ORIGINS else []
# Never append a wildcard implicitly: with credentials/auth headers enabled,
# allowing every browser origin would defeat the deployment CORS policy.

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Accept", "Authorization", "Content-Type", "X-Requested-With"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditLogMiddleware)

# ─── Routers ──────────────────────────────────────────────────

app.include_router(auth_router,     prefix="/api/auth",     tags=["Authentification"])
app.include_router(users_router,    prefix="/api/users",    tags=["Utilisateurs"])
app.include_router(vehicles_router, prefix="/api/vehicles", tags=["Véhicules"])
app.include_router(listings_router, prefix="/api/listings", tags=["Annonces"])
app.include_router(reviews_router,  prefix="/api/reviews",  tags=["Avis"])
app.include_router(recommendation_router,  prefix="/api/recommendation",  tags=["Recommandation"])
app.include_router(chatbot_router,  prefix="/api/chat",  tags=["Chatbot"])
app.include_router(search_router,   prefix="/api/search", tags=["Recherche NLP"])
app.include_router(pricing_router, prefix="/api", tags=["Prédiction de prix"])
app.include_router(vision_router, prefix="/api/v1", tags=["Computer Vision"])
app.include_router(admin_router, prefix="/api/v1", tags=["Admin & Modération"])
app.include_router(customs_router, prefix="/api/v1", tags=["Dédouanement"])
app.include_router(transactions_router, prefix="/api/transactions")

app.include_router(messages_router, prefix="/api/messages")
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI Integration"])
app.include_router(maintenance_router, prefix="/api/maintenance", tags=["Maintenance"])
app.include_router(seo_router)
app.include_router(seo_pages_router, prefix="/api", tags=["SEO & GEO Dynamic Pages"])
app.include_router(favorites_router, prefix="/api", tags=["Favorites"])
app.include_router(offers_router, prefix="/api/offers", tags=["Offres et Négociations"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice Transcription"])
app.include_router(new_catalog_router, prefix="/api", tags=["100% New Cars Digital Showroom"])
app.include_router(comparator_router, prefix="/api", tags=["Matrix Vehicle Comparator"])
app.include_router(test_drives_router, prefix="/api", tags=["Showrooms & Test Drives"])
app.include_router(vehicle_options_router, prefix="/api/vehicles", tags=["Options & Configurateur"])
app.include_router(consent_router, prefix="/api/consent", tags=["Consentement CNDP"])

# ─── Gestionnaire d'exceptions Global ─────────────────────────────────────────────
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import sys

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    import logging
    logging.getLogger(__name__).warning(
        "Request validation failed: method=%s path=%s errors=%s",
        request.method, request.url.path, exc.errors(),
    )
    return JSONResponse(status_code=422, content={"detail": jsonable_encoder(exc.errors())})# ─── Health check ─────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    """Vérifie que le service est opérationnel."""
    return {
        "status": "healthy",
        "service": "Wakala-backend",
        "version": "0.1.0",
    }
