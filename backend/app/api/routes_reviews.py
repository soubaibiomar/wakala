"""
api/routes_reviews.py — CRUD avis (reviews).
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.review import Review
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.review_schema import (
    ReviewCreate,
    ReviewRead,
    ReviewReadWithAuthor,
    ReviewUpdate,
)

router = APIRouter()


# ──────────────────────────────────────────────────────────────
# POST / — Publier un avis
# ──────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    summary="Publier un avis",
    description="Publie un avis sur un véhicule ou un vendeur. "
                "Le champ target_type détermine la cible.",
)
async def create_review(
    payload: ReviewCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    # Validation de la cible
    if payload.target_type == "vehicle":
        if not payload.vehicle_id:
            raise HTTPException(status_code=400, detail="vehicle_id requis pour target_type='vehicle'")
        result = await db.execute(select(Vehicle).where(Vehicle.id == payload.vehicle_id))
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Véhicule non trouvé")

    elif payload.target_type == "seller":
        if not payload.seller_id:
            raise HTTPException(status_code=400, detail="seller_id requis pour target_type='seller'")
        result = await db.execute(
            select(User).where(User.id == payload.seller_id, User.role == "seller")
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Vendeur non trouvé")

    # Empêcher de se noter soi-même
    if payload.seller_id and str(payload.seller_id) == str(current_user.id):
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous noter vous-même")

    # Calculate sentiment score
    sentiment_score = 0.5
    if payload.comment:
        from app.ml.sentiment.sentiment_analyzer import sentiment_analyzer
        sentiment_score = sentiment_analyzer.analyze(payload.comment)

    review_data = payload.model_dump()
    review_data["sentiment_score"] = sentiment_score

    review = Review(
        **review_data,
        author_id=current_user.id,
    )
    db.add(review)
    await db.flush()
    await db.refresh(review)
    return review


# ──────────────────────────────────────────────────────────────
# GET / — Liste des avis (filtrage par véhicule ou vendeur)
# ──────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=list[ReviewReadWithAuthor],
    summary="Lister les avis",
    description="Retourne les avis filtrés par véhicule, vendeur ou auteur.",
)
async def list_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    vehicle_id: Optional[str] = Query(None, description="Filtrer par véhicule"),
    seller_id: Optional[str] = Query(None, description="Filtrer par vendeur"),
    author_id: Optional[str] = Query(None, description="Filtrer par auteur"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Note minimum"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = select(Review).order_by(Review.created_at.desc())

    if vehicle_id:
        query = query.where(Review.vehicle_id == vehicle_id)
    if seller_id:
        query = query.where(Review.seller_id == seller_id)
    if author_id:
        query = query.where(Review.author_id == author_id)
    if min_rating:
        query = query.where(Review.rating >= min_rating)

    # N'afficher que les avis approuvés (sauf si filtrage par auteur)
    if not author_id:
        query = query.where(Review.is_approved == True)  # noqa: E712

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    reviews = result.scalars().all()
    return reviews


# ──────────────────────────────────────────────────────────────
# GET /{review_id} — Détail d'un avis
# ──────────────────────────────────────────────────────────────

@router.get(
    "/{review_id}",
    response_model=ReviewReadWithAuthor,
    summary="Détail d'un avis",
)
async def get_review(
    review_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Avis non trouvé")

    return review


# ──────────────────────────────────────────────────────────────
# PUT /{review_id} — Modifier un avis (auteur uniquement)
# ──────────────────────────────────────────────────────────────

@router.put(
    "/{review_id}",
    response_model=ReviewRead,
    summary="Modifier mon avis",
)
async def update_review(
    review_id: str,
    payload: ReviewUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Avis non trouvé")
    if review.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres avis")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    # Réinitialiser le sentiment car le contenu a changé
    if "comment" in update_data and update_data["comment"]:
        from app.ml.sentiment.sentiment_analyzer import sentiment_analyzer
        review.sentiment_score = sentiment_analyzer.analyze(update_data["comment"])
        review.sentiment_label = None
        review.key_phrases = None

    await db.flush()
    await db.refresh(review)
    return review


# ──────────────────────────────────────────────────────────────
# DELETE /{review_id} — Supprimer un avis
# ──────────────────────────────────────────────────────────────

@router.delete(
    "/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un avis",
)
async def delete_review(
    review_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()

    if not review:
        raise HTTPException(status_code=404, detail="Avis non trouvé")
    if review.author_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Non autorisé")

    await db.delete(review)
