"""
models/listing.py — Modèle ORM Listing (annonces).
Correspond à la migration 003_create_listings.sql.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Enum, Integer, Numeric, String, Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.core.database import Base


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False
    )

    # ─── Statut ────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        Enum("draft", "active", "sold", "expired", "flagged", name="listing_status", create_type=False),
        nullable=False,
        default="draft",
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sold_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ─── Anti-fraude ───────────────────────────────────────────
    fraud_score: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    fraud_flags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_manually_reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ─── Média ─────────────────────────────────────────────────
    images_urls: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Statistiques ──────────────────────────────────────────
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    contact_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    favorite_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ─── Promotion ─────────────────────────────────────────────
    is_boosted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    boost_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ─── Timestamps ────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # ─── Relations ─────────────────────────────────────────────
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="listings", lazy="selectin")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Listing {self.id} — {self.status}>"
