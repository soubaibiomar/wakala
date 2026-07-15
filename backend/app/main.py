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
from contextlib import asynccontextmanager

from app.services.health_checker import start_health_checker

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
from app.api.v1.endpoints.ai import router as ai_router

# ─── Lifespan ──────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrage des tâches de fond
    start_health_checker()
    yield
    # Cleanup si nécessaire

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

# ─── CORS ──────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────

app.include_router(auth_router,     prefix="/api/auth",     tags=["Authentification"])
app.include_router(users_router,    prefix="/api/users",    tags=["Utilisateurs"])
app.include_router(vehicles_router, prefix="/api/vehicles", tags=["Véhicules"])
app.include_router(listings_router, prefix="/api/listings", tags=["Annonces"])
app.include_router(reviews_router,  prefix="/api/reviews",  tags=["Avis"])
app.include_router(recommendation_router,  prefix="/api/recommendation",  tags=["Recommandation"])
app.include_router(chatbot_router,  prefix="/api/chat",  tags=["Chatbot"])
app.include_router(pricing_router, prefix="/api", tags=["Prédiction de prix"])
app.include_router(vision_router, prefix="/api/v1", tags=["Computer Vision"])
app.include_router(admin_router, prefix="/api/v1", tags=["Admin & Modération"])
app.include_router(customs_router, prefix="/api/v1", tags=["Dédouanement"])
app.include_router(transactions_router, prefix="/api/v1", tags=["Escrow & Séquestre"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["IA & RAG"])

# ─── Health check ─────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def health_check():
    """Vérifie que le service est opérationnel."""
    return {
        "status": "healthy",
        "service": "Wakala-backend",
        "version": "0.1.0",
    }
