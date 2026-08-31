"""
models/vehicle.py — Modèle ORM Vehicle.
Correspond à la migration 002_create_vehicles.sql.
Champs IA (condition_score, predicted_price, popularity_score) nullable
pour l'instant — seront remplis par les modules vision, pricing, graphe.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Enum, Integer, Numeric, SmallInteger, String, Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # ─── Identité ──────────────────────────────────────────────
    brand: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str | None] = mapped_column(String(200), nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    mileage: Mapped[int] = mapped_column(Integer, nullable=False)
    fuel_type: Mapped[str] = mapped_column(
        Enum(
            "essence", "diesel", "hybride", "hybride_rechargeable",
            "electrique", "gpl", "hydrogene",
            name="fuel_type", create_type=False,
        ),
        nullable=False,
    )
    body_type: Mapped[str] = mapped_column(
        Enum(
            "citadine", "berline", "suv", "break", "coupe",
            "cabriolet", "monospace", "utilitaire", "pick_up",
            name="body_type", create_type=False,
        ),
        nullable=False,
    )
    transmission: Mapped[str] = mapped_column(
        Enum("manuelle", "automatique", "semi_auto", name="transmission_type", create_type=False),
        nullable=False,
        default="manuelle",
    )
    engine_power_hp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    color: Mapped[str | None] = mapped_column(String(50), nullable=True)
    doors: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=5)
    seats: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=5)

    # ─── Caractéristiques Techniques Catalogue & Neuf ──────────
    trunk_volume_l: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ncap_rating: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fuel_consumption: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    co2_emissions: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    length_cm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_4x4: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    engine_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    condition: Mapped[str] = mapped_column(String(50), nullable=False, default="new")
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="wakala_catalogue")

    # ─── Statut (Soft Delete) ──────────────────────────────────
    status: Mapped[str] = mapped_column(
        Enum("available", "sold", "deleted", name="vehicle_status", create_type=False),
        nullable=False,
        default="available",
    )
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ─── Localisation ──────────────────────────────────────────
    city: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)

    # ─── Prix ──────────────────────────────────────────────────
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    predicted_price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    price_confidence: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)

    # ─── Scores IA (nullable — remplis par les modules ML) ────
    condition_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    popularity_score: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)

    # ─── Description ───────────────────────────────────────────
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ─── Timestamps ────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # ─── Relations ─────────────────────────────────────────────
    seller: Mapped["User"] = relationship("User", back_populates="vehicles", lazy="selectin")  # noqa: F821
    listings: Mapped[list["Listing"]] = relationship(  # noqa: F821
        "Listing", back_populates="vehicle", lazy="selectin"
    )

    saved_by_users: Mapped[list["User"]] = relationship(  # noqa: F821
        "User", secondary="saved_vehicles", back_populates="saved_vehicles", lazy="selectin"
    )
    reviews: Mapped[list["Review"]] = relationship(  # noqa: F821
        "Review", back_populates="vehicle", lazy="selectin"
    )
    services: Mapped[list["VehicleService"]] = relationship( # noqa: F821
        "VehicleService", back_populates="vehicle", lazy="selectin"
    )
    reminders: Mapped[list["ServiceReminder"]] = relationship( # noqa: F821
        "ServiceReminder", back_populates="vehicle", lazy="selectin"
    )
    options: Mapped[list["VehicleOption"]] = relationship(  # noqa: F821
        "VehicleOption", back_populates="vehicle", lazy="selectin", cascade="all, delete-orphan"
    )
    colors: Mapped[list["VehicleColor"]] = relationship(  # noqa: F821
        "VehicleColor", back_populates="vehicle", lazy="selectin", cascade="all, delete-orphan"
    )
    wakala_scores: Mapped["VehicleWakalaScore | None"] = relationship(  # noqa: F821
        "VehicleWakalaScore", back_populates="vehicle", uselist=False, lazy="selectin", cascade="all, delete-orphan"
    )

    @property
    def images(self) -> list[dict]:
        active_listing = next((l for l in self.listings if l.status == "active"), None)
        # Fallback to draft/any listing if no active listing
        if not active_listing and self.listings:
            active_listing = self.listings[0]
            
        if active_listing and active_listing.images_urls:
            return [{"file_path": url} for url in active_listing.images_urls]
        return []

    def __repr__(self) -> str:
        return f"<Vehicle {self.brand} {self.model} ({self.year}) — {self.price} MAD>"
