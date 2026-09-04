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
    doors: Optional[int] = Query(None, ge=2, le=6, description="Nombre de portes"),
    seats: Optional[int] = Query(None, ge=1, le=9, description="Nombre de places"),
    color: Optional[str] = Query(None, description="Couleur"),
    min_engine_power: Optional[int] = Query(None, ge=0, description="Puissance minimum"),
    is_4x4: Optional[bool] = Query(None, description="Transmission intégrale"),
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
            
        brand_conditions = []
        for b in set(brand_aliases):
            if len(b) <= 3:
                brand_conditions.extend([
                    Vehicle.brand.ilike(b),
                    Vehicle.brand.ilike(f"{b} %"),
                    Vehicle.brand.ilike(f"% {b}"),
                    Vehicle.brand.ilike(f"% {b} %"),
                ])
            else:
                brand_conditions.append(Vehicle.brand.ilike(f"%{b}%"))
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
    if doors is not None:
        query = query.where(Vehicle.doors == doors)
    if seats is not None:
        query = query.where(Vehicle.seats == seats)
    if color:
        query = query.where(Vehicle.color.ilike(f"%{color}%"))
    if min_engine_power is not None:
        query = query.where(Vehicle.engine_power_hp >= min_engine_power)
    if is_4x4 is not None:
        query = query.where(Vehicle.is_4x4 == is_4x4)
    
    # The catalogue must expose only active, new 0 km vehicles with valid pricing.
    # Corrupted scrape entries (e.g. #Avis) and unpriced duplicates (price = 0)
    # are excluded from the showroom.
    query = query.where(
        Vehicle.status == "available",
        Vehicle.condition == "new",
        Vehicle.mileage == 0,
        Vehicle.price > 0,
        Vehicle.model != "#Avis",
        Vehicle.brand != "#Avis",
    )

    if condition == 'occasion':
        query = query.where(1 == 0)

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
# GET /compare — Comparaison factuelle de véhicules
# ──────────────────────────────────────────────────────────────

@router.get(
    "/compare",
    summary="Comparaison factuelle de plusieurs véhicules",
    description="Retourne les données des véhicules sélectionnés sans génération IA.",
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
    
    return {
        "vehicles": [VehicleRead.model_validate(v) for v in vehicles],
        "ai_verdict": ""
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
    from sqlalchemy import cast, String

    # 1. Vérifier si version_slug contient un Short ID (8 hex) ou un UUID (36 chars)
    short_id_match = re.search(r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|[0-9a-f]{8})$', version_slug, re.IGNORECASE)
    if short_id_match:
        matched_id = short_id_match.group(1)
        if len(matched_id) == 8:
            res_id = await db.execute(select(Vehicle).where(cast(Vehicle.id, String).startswith(matched_id)))
            v_id = res_id.scalars().first()
            if v_id:
                return v_id
        else:
            res_id = await db.execute(select(Vehicle).where(Vehicle.id == matched_id))
            v_id = res_id.scalar_one_or_none()
            if v_id:
                return v_id

    # 2. Récupérer tous les véhicules de cette marque et modèle
    clean_brand = brand.strip().replace('-', ' ')
    clean_model = model.strip().replace('-', ' ')
    result = await db.execute(
        select(Vehicle)
        .where(Vehicle.brand.ilike(f"%{clean_brand}%"))
        .where(Vehicle.model.ilike(f"%{clean_model}%"))
        .order_by(Vehicle.price.asc())
    )
    vehicles = result.scalars().all()
    
    if not vehicles:
        # Essayer avec recherche plus souple sur le modèle
        result = await db.execute(
            select(Vehicle)
            .where(Vehicle.brand.ilike(f"%{brand.strip()}%"))
            .order_by(Vehicle.price.asc())
        )
        vehicles = [v for v in result.scalars().all() if clean_model.lower() in v.model.lower() or v.model.lower() in clean_model.lower()]

    if not vehicles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé pour cette marque et modèle",
        )

    # 3. Match par index "finition-X" ou "finition X"
    norm_slug = version_slug.lower().replace('%20', ' ').replace('-', ' ').strip()
    finition_idx_match = re.search(r'finition\s*(\d+)', norm_slug)
    if finition_idx_match:
        idx = int(finition_idx_match.group(1)) - 1
        if 0 <= idx < len(vehicles):
            return vehicles[idx]

    # 4. Match par slug généré
    for v in vehicles:
        parts = []
        if v.version and v.version.lower() != 'fiche technique':
            parts.append(v.version)
        if v.year:
            parts.append(str(v.year))
            
        generated_slug = '-'.join(parts).lower()
        generated_slug = re.sub(r'[^a-z0-9]+', '-', generated_slug).strip('-')
        
        if generated_slug and (generated_slug == version_slug.lower() or version_slug.lower() in generated_slug or generated_slug in version_slug.lower()):
            return v

    # 5. Match par mot-clé de finition ou motorisation (ex: expression, journey, extreme, 115, 155)
    for v in vehicles:
        v_text = f"{v.version or ''} {v.engine_power_hp or ''} {v.fuel_type or ''} {v.transmission or ''}".lower()
        slug_words = [w for w in re.split(r'[^a-z0-9]+', norm_slug) if w and w not in ('finition', 'version', 'neuf', 'dacia', 'renault', 'peugeot')]
        if slug_words and all(w in v_text for w in slug_words):
            return v

    # 6. Fallback vers le premier véhicule disponible du modèle
    return vehicles[0]



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
