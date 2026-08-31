"""
models/vehicle_option.py — Modèles ORM pour les options, couleurs et notes Wakala.
Correspond à la migration 018_create_vehicle_options.sql.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Numeric, String, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VehicleOption(Base):
    __tablename__ = "vehicle_options"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # 'accessoire', 'couleur', 'jante', 'sellerie', 'pack'
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price_delta: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0.00
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    image_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="options")  # noqa: F821

    def __repr__(self) -> str:
        return f"<VehicleOption {self.category} '{self.name}' (+{self.price_delta} MAD)>"


class VehicleColor(Base):
    __tablename__ = "vehicle_colors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True
    )
    color_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hex_code: Mapped[str] = mapped_column(String(20), nullable=False)
    price_delta: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, default=0.00
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="colors")  # noqa: F821

    def __repr__(self) -> str:
        return f"<VehicleColor '{self.color_name}' ({self.hex_code}) +{self.price_delta} MAD>"


class VehicleWakalaScore(Base):
    __tablename__ = "vehicle_wakala_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )

    # Notes Wakala 1-5
    space_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    safety_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    real_cost_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    access_price_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    city_practicality_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    performance_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    ecology_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)
    offroad_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True)

    overall_score: Mapped[float | None] = mapped_column(Numeric(3, 1), nullable=True, index=True)
    data_reliability: Mapped[str | None] = mapped_column(String(255), nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="wakala_scores")  # noqa: F821

    def __repr__(self) -> str:
        return f"<VehicleWakalaScore Vehicle={self.vehicle_id} Score={self.overall_score}/5>"
