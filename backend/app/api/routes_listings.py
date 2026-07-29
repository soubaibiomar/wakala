"""
api/routes_listings.py — CRUD annonces (listings).
"""

from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.listing import Listing
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.listing_schema import (
    ListingCreate,
    ListingRead,
    ListingReadWithVehicle,
    ListingUpdate,
)
from app.ml.anomaly.detector import anomaly_detector
from app.ml.fraud.broker_detector import broker_detector
import numpy as np

router = APIRouter()


# ──────────────────────────────────────────────────────────────
# POST / — Créer une annonce
# ──────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=ListingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une annonce",
    description="Publie une annonce liée à un véhicule existant. "
                "Le véhicule doit appartenir au vendeur authentifié.",
)
async def create_listing(
    request: Request,
    payload: ListingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("seller", "admin"))],
):
    # Vérifier que le véhicule existe et appartient au seller
    result = await db.execute(select(Vehicle).where(Vehicle.id == payload.vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
    if vehicle.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Ce véhicule ne vous appartient pas")

    # Evaluation du score de fraude via Isolation Forest
    # Utilisation de features basiques pour la démo
    features = np.array([vehicle.year or 2020, vehicle.mileage or 50000])
    trust_score = anomaly_detector.compute_trust_score(features)
    fraud_score = 100.0 - trust_score

    listing_data = payload.model_dump()
    listing_data["fraud_score"] = fraud_score
    listing = Listing(**listing_data)

    # Si le statut est directement "active", mettre published_at
    if listing.status == "active":
        listing.published_at = datetime.now(timezone.utc)

    db.add(listing)
    await db.flush()
    await db.refresh(listing)

    # Ingestion dans le graphe (Neo4j) pour la détection de courtiers
    # Si localhost, simuler des IPs pour générer des clusters artificiels pour les tests
    client_ip = request.client.host if request.client else "unknown"
    if client_ip in ("127.0.0.1", "::1", "localhost"):
        import random
        # Pour forcer des partages d'IP en dev (1 chance sur 3 de retomber sur une IP "suspecte" commune)
        test_ips = ["192.168.1.100", "192.168.1.200", f"192.168.1.{random.randint(10,99)}"]
        client_ip = random.choice(test_ips)

    # Lancement asynchrone non-bloquant
    import asyncio
    asyncio.create_task(
        broker_detector.ingest_user_listing_activity(
            user_id=str(current_user.id),
            phone=current_user.phone or "UNKNOWN_PHONE",
            ip_address=client_ip,
            vehicle_id=str(vehicle.id),
            brand=vehicle.brand,
            city=vehicle.city
        )
    )

    return listing


# ──────────────────────────────────────────────────────────────
# GET / — Liste des annonces (publiques, statut active)
# ──────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[ListingReadWithVehicle],
    summary="Lister les annonces actives",
)
async def list_listings(
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: Optional[str] = Query("active", alias="status", description="Filtrer par statut"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = select(Listing).order_by(Listing.created_at.desc())

    if status_filter:
        query = query.where(Listing.status == status_filter)

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    listings = result.scalars().all()
    return listings


# ──────────────────────────────────────────────────────────────
# GET /me — Mes annonces (vendeur)
# ──────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=list[ListingReadWithVehicle],
    summary="Mes annonces",
    description="Retourne la liste des annonces appartenant à l'utilisateur connecté via ses véhicules.",
)
async def get_my_listings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("seller", "admin"))],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = (
        select(Listing)
        .join(Vehicle, Listing.vehicle_id == Vehicle.id)
        .where(Vehicle.seller_id == current_user.id)
        .order_by(Listing.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    result = await db.execute(query)
    listings = result.scalars().all()
    return listings

# ──────────────────────────────────────────────────────────────
# GET /{listing_id} — Détail d'une annonce
# ──────────────────────────────────────────────────────────────

@router.get(
    "/{listing_id}",
    response_model=ListingReadWithVehicle,
    summary="Détail d'une annonce",
)
async def get_listing(
    listing_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=404, detail="Annonce non trouvée")

    # Incrémenter le compteur de vues
    listing.view_count += 1
    await db.flush()

    return listing


# ──────────────────────────────────────────────────────────────
# PATCH /{listing_id} — Mettre à jour une annonce
# ──────────────────────────────────────────────────────────────

@router.patch(
    "/{listing_id}",
    response_model=ListingRead,
    summary="Modifier une annonce",
    description="Met à jour le statut, les images, etc. "
                "La transition draft→active déclenche la mise à jour de published_at.",
)
async def update_listing(
    listing_id: str,
    payload: ListingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()

    if not listing:
        raise HTTPException(status_code=404, detail="Annonce non trouvée")

    # Vérification propriétaire via le véhicule
    vehicle_result = await db.execute(select(Vehicle).where(Vehicle.id == listing.vehicle_id))
    vehicle = vehicle_result.scalar_one_or_none()

    if vehicle and vehicle.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé")

    update_data = payload.model_dump(exclude_unset=True)

    # Gestion des transitions de statut
    new_status = update_data.get("status")
    if new_status:
        old_status = listing.status
        if new_status == "active" and old_status == "draft" and not listing.published_at:
            listing.published_at = datetime.now(timezone.utc)
        if new_status == "sold" and old_status != "sold":
            listing.sold_at = datetime.now(timezone.utc)

    for field, value in update_data.items():
        setattr(listing, field, value)

    await db.flush()
    await db.refresh(listing)
    return listing
