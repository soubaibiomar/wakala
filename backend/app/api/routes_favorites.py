from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, saved_vehicles_table
from app.models.vehicle import Vehicle
from app.schemas.vehicle_schema import VehicleRead

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("/{vehicle_id}", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ajoute un véhicule aux favoris de l'utilisateur connecté.
    """
    # Vérifier que le véhicule existe
    vehicle_result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    vehicle = vehicle_result.scalars().first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")

    # Vérifier si déjà en favori
    check_stmt = select(saved_vehicles_table).where(
        (saved_vehicles_table.c.user_id == current_user.id) &
        (saved_vehicles_table.c.vehicle_id == vehicle_id)
    )
    result = await db.execute(check_stmt)
    if result.first():
        return {"message": "Véhicule déjà dans les favoris"}

    # Insérer dans la table d'association
    insert_stmt = saved_vehicles_table.insert().values(
        user_id=current_user.id,
        vehicle_id=vehicle_id
    )
    await db.execute(insert_stmt)
    await db.commit()
    
    return {"message": "Véhicule ajouté aux favoris"}


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    vehicle_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retire un véhicule des favoris de l'utilisateur connecté.
    """
    delete_stmt = saved_vehicles_table.delete().where(
        (saved_vehicles_table.c.user_id == current_user.id) &
        (saved_vehicles_table.c.vehicle_id == vehicle_id)
    )
    result = await db.execute(delete_stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Favori non trouvé")
        
    await db.commit()


@router.get("/", response_model=List[VehicleRead])
async def get_favorites(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Récupère la liste des véhicules favoris de l'utilisateur connecté.
    """
    stmt = (
        select(Vehicle)
        .join(saved_vehicles_table, Vehicle.id == saved_vehicles_table.c.vehicle_id)
        .where(saved_vehicles_table.c.user_id == current_user.id)
        .order_by(saved_vehicles_table.c.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()
