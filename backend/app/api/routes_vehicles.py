"""
api/routes_vehicles.py — CRUD véhicules + recherche par filtres.
Pagination offset-based, filtres par query params.
"""

import math
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, or_

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
from app.rag.compare_chain import compare_chain
from app.services.ai.sync import upsert_vehicle_to_qdrant, delete_vehicle_from_qdrant
from fastapi import BackgroundTasks

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
    condition: Optional[str] = Query(None, description="Condition (neuf/occasion)"),
    group_by_model: Optional[bool] = Query(False, description="Grouper par marque et modèle (renvoie le moins cher)"),
    # Tri
    sort_by: str = Query("created_at", description="Champ de tri"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Ordre de tri"),
):
    # Construction de la requête avec filtres
    query = select(Vehicle)

    if group_by_model:
        query = query.distinct(Vehicle.brand, Vehicle.model)

    if brand:
        import re
        # Remove accents for a broader search
        brand_norm = brand.replace('ë', 'e').replace('é', 'e').replace('è', 'e').replace('Ë', 'E')
        
        # We check both the original brand name and the normalized one.
        # Also, if the normalized one has 'e', we also try 'ë' and 'é' to be safe since DB might have them.
        brand_e1 = brand_norm.replace('e', 'ë').replace('E', 'Ë')
        brand_e2 = brand_norm.replace('e', 'é').replace('E', 'É')
        # Handle space vs hyphen mismatches (e.g. "Land Rover" vs "Land-rover")
        brand_hyphen = brand.replace(' ', '-')
        brand_space = brand.replace('-', ' ')
        
        # Brand alias mappings (e.g. Haval <-> GWM, Mercedes <-> Mercedes-Benz, BAIC, Seres, Maserati)
        brand_lower = brand.lower().strip()
        brand_aliases = [brand, brand_norm, brand_e1, brand_e2, brand_hyphen, brand_space]
        
        if "haval" in brand_lower or "gwm" in brand_lower:
            brand_aliases.extend(["GWM", "Haval", "Great Wall", "gwm", "haval"])
        elif "mercedes" in brand_lower:
            brand_aliases.extend(["Mercedes-Benz", "Mercedes", "MERCEDES", "mercedes-benz", "mercedes"])
        elif "alfa" in brand_lower:
            brand_aliases.extend(["Alfa Romeo", "Alfa-romeo", "ALFA-ROMEO", "Alfa", "alfa"])
        elif "land" in brand_lower and "rover" in brand_lower:
            brand_aliases.extend(["Land Rover", "Land-rover", "LAND-ROVER", "Land-Rover"])
        elif "baic" in brand_lower:
            brand_aliases.extend(["BAIC", "Baic", "baic"])
        elif "seres" in brand_lower:
            brand_aliases.extend(["SERES", "Seres", "seres"])
        elif "maserati" in brand_lower:
            brand_aliases.extend(["Maserati", "MASERATI", "maserati"])
        elif "citroen" in brand_lower or "citroën" in brand_lower:
            brand_aliases.extend(["Citroën", "Citroen", "CITROEN", "citroen", "citroën"])
        elif "bmw" in brand_lower:
            brand_aliases.extend(["BMW", "Bmw", "bmw"])
        elif "dfsk" in brand_lower:
            brand_aliases.extend(["DFSK", "Dfsk", "dfsk"])
        elif "byd" in brand_lower:
            brand_aliases.extend(["BYD", "Byd", "byd"])
        elif "mg" == brand_lower:
            brand_aliases.extend(["MG", "Mg", "mg"])
        elif "ds" == brand_lower:
            brand_aliases.extend(["DS", "Ds", "ds"])
            
        brand_conditions = [Vehicle.brand.ilike(f"%{b}%") for b in set(brand_aliases)]
        query = query.where(or_(*brand_conditions))
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
    
    if condition == 'neuf':
        query = query.where(Vehicle.description.ilike('%Véhicule Neuf Officiel%'))
    elif condition == 'occasion':
        query = query.where(
            or_(
                Vehicle.description.is_(None),
                Vehicle.description.notilike('%Véhicule Neuf Officiel%')
            )
        )

    # Compter le total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Tri
    allowed_sort_fields = {"price", "year", "mileage", "created_at"}
    if sort_by not in allowed_sort_fields:
        sort_by = "created_at"
    sort_column = getattr(Vehicle, sort_by)
    
    order_clause = sort_column.desc() if sort_order == "desc" else sort_column.asc()
    
    if group_by_model:
        query = query.order_by(Vehicle.brand, Vehicle.model, Vehicle.price.asc())
    else:
        query = query.order_by(order_clause)

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
# GET /compare — Comparaison IA de véhicules
# ──────────────────────────────────────────────────────────────

@router.get(
    "/compare",
    summary="Comparaison IA de plusieurs véhicules",
    description="Retourne les données brutes des véhicules et un verdict IA comparatif.",
)
async def compare_vehicles(
    db: Annotated[AsyncSession, Depends(get_db)],
    vehicle_ids: list[str] = Query(..., description="Liste des IDs des véhicules à comparer (max 4)"),
):
    if not vehicle_ids or len(vehicle_ids) > 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veuillez fournir entre 1 et 4 IDs de véhicules.",
        )
    
    result = await db.execute(select(Vehicle).where(Vehicle.id.in_(vehicle_ids)))
    vehicles = result.scalars().all()
    
    if not vehicles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun véhicule trouvé.",
        )
    
    vehicles_data = []
    for v in vehicles:
        vehicles_data.append({
            "id": str(v.id),
            "brand": v.brand,
            "model": v.model,
            "year": v.year,
            "price": float(v.price),
            "mileage": v.mileage,
            "fuel_type": v.fuel_type,
            "condition_score": float(v.condition_score) if v.condition_score else None,
            "description": v.description,
        })
    
    ai_verdict = await compare_chain.generate_comparison(vehicles_data)
    
    return {
        "vehicles": [VehicleRead.model_validate(v) for v in vehicles],
        "ai_verdict": ai_verdict
    }


# ──────────────────────────────────────────────────────────────
# GET /me — Mes véhicules (vendeur authentifié)
# ──────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=list[VehicleRead],
    summary="Mes véhicules",
    description="Retourne la liste des véhicules appartenant à l'utilisateur connecté.",
)
async def get_my_vehicles(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_role("seller", "admin", "buyer"))],
    limit: int = Query(100, ge=1, le=1000, description="Limite du nombre de résultats"),
    offset: int = Query(0, ge=0, description="Décalage (skip)"),
):
    result = await db.execute(select(Vehicle).where(Vehicle.seller_id == current_user.id).limit(limit).offset(offset))
    vehicles = result.scalars().all()
    return vehicles

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
    from sqlalchemy import cast, String

    if len(vehicle_id) == 8:
        # Recherche par Short ID (les 8 premiers caractères de l'UUID)
        result = await db.execute(select(Vehicle).where(cast(Vehicle.id, String).startswith(vehicle_id)))
        vehicle = result.scalars().first()
    else:
        # Recherche classique par UUID complet
        result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
        vehicle = result.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé",
        )

    return vehicle

# ──────────────────────────────────────────────────────────────
# GET /by-slug/{brand}/{model}/{version_slug} — Détail d'un véhicule par Slug (Neuf)
# ──────────────────────────────────────────────────────────────

@router.get(
    "/by-slug/{brand}/{model}/{version_slug}",
    response_model=VehicleReadWithSeller,
    summary="Détail d'un véhicule par slug",
    description="Recherche un véhicule par marque, modèle et slug de version.",
)
async def get_vehicle_by_slug(
    brand: str,
    model: str,
    version_slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    import re
    # Récupérer tous les véhicules de cette marque et modèle
    result = await db.execute(
        select(Vehicle)
        .where(Vehicle.brand.ilike(brand))
        .where(Vehicle.model.ilike(model))
    )
    vehicles = result.scalars().all()
    
    for v in vehicles:
        # On génère le slug pour chaque véhicule
        # Note: on utilise la même logique que côté frontend: "version-annee" (ou juste version si pas d'année)
        parts = []
        if v.version and v.version != 'Fiche Technique':
            parts.append(v.version)
        if v.year:
            parts.append(str(v.year))
            
        generated_slug = '-'.join(parts).lower()
        generated_slug = re.sub(r'[^a-z0-9]+', '-', generated_slug).strip('-')
        
        if generated_slug == version_slug:
            return v
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Véhicule non trouvé pour ce slug",
    )



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
    background_tasks: BackgroundTasks,
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
    
    # Synchronisation IA en tâche de fond
    background_tasks.add_task(upsert_vehicle_to_qdrant, vehicle)
    
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
    background_tasks: BackgroundTasks,
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
    
    # Synchronisation IA en tâche de fond
    background_tasks.add_task(upsert_vehicle_to_qdrant, vehicle)
    
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
    background_tasks: BackgroundTasks,
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
    await db.commit()
    
    # Synchronisation IA en tâche de fond
    background_tasks.add_task(delete_vehicle_from_qdrant, vehicle_id)
