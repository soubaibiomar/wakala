from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Annotated

from app.core.database import get_db
from app.core.security import require_role
from app.models.user import User
from app.ml.fraud.broker_detector import broker_detector

router = APIRouter(prefix="/admin", tags=["Admin & Modération"])

@router.post("/detect-brokers", summary="Lancer la détection de courtiers (Neo4j)")
async def run_broker_detection(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_role("admin"))],
):
    """
    Exécute l'algorithme d'analyse de graphe (Neo4j) pour trouver des clusters
    d'utilisateurs partageant des IP ou téléphones.
    Met à jour PostgreSQL (`is_pro = true`) pour les suspects.
    """
    suspect_ids = await broker_detector.detect_brokers()
    
    if not suspect_ids:
        return {"message": "Aucun nouveau courtier détecté.", "count": 0}
    
    # Update Postgres database
    # On met à jour is_pro = True pour les users détectés
    # (Note: En SQL pur on ferait WHERE id IN (suspect_ids) et is_pro = False)
    stmt = (
        update(User)
        .where(User.id.in_(suspect_ids))
        .where(User.is_pro == False)
        .values(is_pro=True)
        .execution_options(synchronize_session="fetch")
    )
    
    result = await db.execute(stmt)
    await db.commit()
    
    updated_count = result.rowcount
    
    return {
        "message": "Détection terminée.",
        "suspects_found": len(suspect_ids),
        "newly_flagged": updated_count
    }

@router.get("/brokers", summary="Lister les utilisateurs flaggés 'Pro'")
async def get_flagged_brokers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_role("admin"))],
):
    """
    Retourne la liste des utilisateurs ayant été flaggés comme potentiels courtiers.
    """
    query = select(User).where(User.is_pro == True)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [
        {
            "id": str(u.id),
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "role": u.role,
            "created_at": u.created_at
        } for u in users
    ]
