"""
models/review.py — Modèle ORM Review (avis).
Correspond à la migration 004_create_reviews.sql.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Enum, Numeric, SmallInteger, String, Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # ─── Cible polymorphe ──────────────────────────────────────
    target_type: Mapped[str] = mapped_column(
        Enum("vehicle", "seller", name="review_target_type", create_type=False),
        nullable=False,
    )
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True
    )
    seller_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # ─── Contenu ───────────────────────────────────────────────
    rating: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)

    # ─── NLP Sentiment (rempli plus tard par le module NLP) ───
    sentiment_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    sentiment_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    key_phrases: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)

    # ─── Modération ────────────────────────────────────────────
    is_approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_flagged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ─── Timestamps ────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # ─── Relations ─────────────────────────────────────────────
    author: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="authored_reviews", foreign_keys=[author_id], lazy="selectin"
    )
    seller: Mapped["User | None"] = relationship(  # noqa: F821
        "User", back_populates="received_reviews", foreign_keys=[seller_id], lazy="selectin"
    )
    vehicle: Mapped["Vehicle | None"] = relationship(  # noqa: F821
        "Vehicle", back_populates="reviews", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Review {self.target_type} — ★{self.rating}>"
