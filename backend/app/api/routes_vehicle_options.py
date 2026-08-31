"""
api/routes_vehicle_options.py — Endpoint pour les options et couleurs configurables d'un véhicule.
"""

from typing import Annotated, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import cast, String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.vehicle import Vehicle
from app.models.vehicle_option import VehicleOption, VehicleColor, VehicleWakalaScore
from app.schemas.vehicle_option_schema import (
    VehicleColorRead,
    VehicleConfiguratorOptionsResponse,
    VehicleOptionRead,
    VehicleWakalaScoreRead,
)

router = APIRouter()


@router.get(
    "/{vehicle_id}/options",
    response_model=VehicleConfiguratorOptionsResponse,
    summary="Options et couleurs d'un véhicule pour le configurateur",
    description="Retourne les couleurs et la liste des options/accessoires configurables pour un véhicule donné.",
)
async def get_vehicle_options(
    vehicle_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Support UUID complet ou Short ID (8 premiers caractères)
    if len(vehicle_id) == 8:
        stmt = (
            select(Vehicle)
            .where(cast(Vehicle.id, String).startswith(vehicle_id))
            .options(
                selectinload(Vehicle.options),
                selectinload(Vehicle.colors),
                selectinload(Vehicle.wakala_scores),
            )
        )
        res = await db.execute(stmt)
        vehicle = res.scalars().first()
    else:
        try:
            val_uuid = UUID(vehicle_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identifiant de véhicule invalide",
            )
        stmt = (
            select(Vehicle)
            .where(Vehicle.id == val_uuid)
            .options(
                selectinload(Vehicle.options),
                selectinload(Vehicle.colors),
                selectinload(Vehicle.wakala_scores),
            )
        )
        res = await db.execute(stmt)
        vehicle = res.scalar_one_or_none()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Véhicule non trouvé",
        )

    # Regroupement par catégorie
    options_by_cat: Dict[str, List[VehicleOptionRead]] = {}
    options_list = [VehicleOptionRead.model_validate(opt) for opt in (vehicle.options or [])]
    
    for opt in options_list:
        options_by_cat.setdefault(opt.category, []).append(opt)

    colors_list = [VehicleColorRead.model_validate(col) for col in (vehicle.colors or [])]

    wakala_scores_read = None
    if vehicle.wakala_scores:
        wakala_scores_read = VehicleWakalaScoreRead.model_validate(vehicle.wakala_scores)

    return VehicleConfiguratorOptionsResponse(
        vehicle_id=vehicle.id,
        brand=vehicle.brand,
        model=vehicle.model,
        version=vehicle.version,
        base_price=float(vehicle.price),
        colors=colors_list,
        options=options_list,
        options_by_category=options_by_cat,
        wakala_scores=wakala_scores_read,
    )
