"""
api/routes_vehicles.py — CRUD véhicules + recherche par filtres.
Pagination offset-based, filtres par query params.
"""

import math
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle_schema import (
    VehicleCreate,
    VehicleListResponse,
    VehicleRead,
    VehicleReadWithSeller,
    VehicleUpdate,
)

router = APIRouter()


# ──────────────────────────────────────────────────────────────
# GET / — Liste paginée avec filtres
# ──────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=VehicleListResponse,
    summary="Lister les véhicules",
    description="Retourne une liste paginée de véhicules avec filtres optionnels.",
)
async def list_vehicles(
    db: Annotated[AsyncSession, Depends(get_db)],
    # Pagination
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Résultats par page"),
    # Filtres
    brand: Optional[str] = Query(None, description="Filtrer par marque"),
    model: Optional[str] = Query(None, description="Filtrer par modèle"),
    city: Optional[str] = Query(None, description="Filtrer par ville"),
    fuel_type: Optional[str] = Query(None, description="Filtrer par carburant"),
    body_type: Optional[str] = Query(None, description="Filtrer par carrosserie"),
    transmission: Optional[str] = Query(None, description="Filtrer par transmission"),
    price_min: Optional[float] = Query(None, ge=0, description="Prix minimum (MAD)"),
    price_max: Optional[float] = Query(None, ge=0, description="Prix maximum (MAD)"),
    year_min: Optional[int] = Query(None, ge=1950, description="Année minimum"),
    year_max: Optional[int] = Query(None, le=2030, description="Année maximum"),
    mileage_max: Optional[int] = Query(None, ge=0, description="Kilométrage maximum"),
    # Tri
    sort_by: str = Query("created_at", description="Champ de tri"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Ordre de tri"),
):
    # Construction de la requête avec filtres
    query = select(Vehicle)

    if brand:
        query = query.where(Vehicle.brand.ilike(f"%{brand}%"))
    if model:
        query = query.where(Vehicle.model.ilike(f"%{model}%"))
    if city:
        query = query.where(Vehicle.city.ilike(f"%{city}%"))
    if fuel_type:
        query = query.where(Vehicle.fuel_type == fuel_type)
    if body_type:
        query = query.where(Vehicle.body_type == body_type)
    if transmission:
        query = query.where(Vehicle.transmission == transmission)
    if price_min is not None:
        query = query.where(Vehicle.price >= price_min)
    if price_max is not None:
        query = query.where(Vehicle.price <= price_max)
    if year_min is not None:
        query = query.where(Vehicle.year >= year_min)
    if year_max is not None:
        query = query.where(Vehicle.year <= year_max)
    if mileage_max is not None:
        query = query.where(Vehicle.mileage <= mileage_max)

    # Compter le total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Tri
    sort_column = getattr(Vehicle, sort_by, Vehicle.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    vehicles = result.scalars().all()

    return VehicleListResponse(
        items=[VehicleRead.model_validate(v) for v in vehicles],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total > 0 else 0,
    )


# ──────────────────────────────────────────────────────────────
# GET /{vehicle_id} — Détail d'un véhicule (avec vendeur)
# ──────────────────────────────────────────────────────────────

@router.get(
    "/{vehicle_id}",
    response_model=VehicleReadWithSeller,
    summary="Détail d'un véhicule",
    description="Retourne le détail complet d'un véhicule avec les infos vendeur.",
)
async def get_vehicle(
    vehicle_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé",
        )

    return vehicle


# ──────────────────────────────────────────────────────────────
# POST / — Créer un véhicule (vendeur authentifié)
# ──────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=VehicleRead,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un véhicule",
    description="Crée un véhicule rattaché au vendeur authentifié.",
)
async def create_vehicle(
    payload: VehicleCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("seller", "admin"))],
):
    vehicle = Vehicle(
        **payload.model_dump(),
        seller_id=current_user.id,
    )
    db.add(vehicle)
    await db.flush()
    await db.refresh(vehicle)
    return vehicle


# ──────────────────────────────────────────────────────────────
# PUT /{vehicle_id} — Modifier un véhicule
# ──────────────────────────────────────────────────────────────

@router.put(
    "/{vehicle_id}",
    response_model=VehicleRead,
    summary="Modifier un véhicule",
    description="Met à jour les champs modifiables d'un véhicule. "
                "Seul le vendeur propriétaire ou un admin peut modifier.",
)
async def update_vehicle(
    vehicle_id: str,
    payload: VehicleUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")

    # Vérification propriétaire ou admin
    if vehicle.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé à modifier ce véhicule")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)

    await db.flush()
    await db.refresh(vehicle)
    return vehicle


# ──────────────────────────────────────────────────────────────
# DELETE /{vehicle_id} — Supprimer un véhicule
# ──────────────────────────────────────────────────────────────

@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un véhicule",
)
async def delete_vehicle(
    vehicle_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")

    if vehicle.seller_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé")

    await db.delete(vehicle)
