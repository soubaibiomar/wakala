"""
api/routes_users.py — Gestion du profil utilisateur.
"""

from typing import Annotated
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.models.user import User
from app.schemas.user_schema import UserRead, UserUpdate

router = APIRouter()


# ──────────────────────────────────────────────────────────────
# GET /me — Profil de l'utilisateur connecté
# ──────────────────────────────────────────────────────────────

@router.get(
    "/me",
    response_model=UserRead,
    summary="Mon profil",
    description="Retourne le profil de l'utilisateur authentifié.",
)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


# ──────────────────────────────────────────────────────────────
# PUT /me — Mettre à jour son profil
# ──────────────────────────────────────────────────────────────

@router.put(
    "/me",
    response_model=UserRead,
    summary="Modifier mon profil",
)
async def update_me(
    payload: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.flush()
    await db.refresh(current_user)
    return current_user


# ──────────────────────────────────────────────────────────────
# POST /me/avatar — Mettre à jour la photo de profil
# ──────────────────────────────────────────────────────────────

@router.post(
    "/me/avatar",
    response_model=UserRead,
    summary="Uploader une photo de profil",
)
async def upload_avatar(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    file: UploadFile = File(...),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image.")
        
    os.makedirs("uploads/avatars", exist_ok=True)
    ext = file.filename.split(".")[-1]
    filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join("uploads", "avatars", filename)
    
    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    current_user.avatar_url = f"/uploads/avatars/{filename}"
    await db.flush()
    await db.refresh(current_user)
    
    return current_user



# ──────────────────────────────────────────────────────────────
# GET /{user_id} — Profil public d'un utilisateur
# ──────────────────────────────────────────────────────────────

@router.get(
    "/{user_id}",
    response_model=UserRead,
    summary="Profil d'un utilisateur",
    description="Retourne le profil public d'un utilisateur par son ID.",
)
async def get_user(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )

    return user


# ──────────────────────────────────────────────────────────────
# PATCH /{user_id}/verify — Vérifier un vendeur (TrustBadge)
# ──────────────────────────────────────────────────────────────

@router.patch(
    "/{user_id}/verify",
    response_model=UserRead,
    summary="Vérifier un vendeur (admin)",
    description="Active le TrustBadge pour un vendeur. Réservé aux admins.",
)
async def verify_seller(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _admin: Annotated[User, Depends(require_role("admin"))],
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if user.role != "seller":
        raise HTTPException(status_code=400, detail="Seuls les vendeurs peuvent être vérifiés")

    user.is_verified = True
    await db.flush()
    await db.refresh(user)
    return user
