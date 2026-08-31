import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, Boolean
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BrandCatalog(Base):
    __tablename__ = "car_brands"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    country_of_origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    models: Mapped[list["ModelCatalog"]] = relationship(
        "ModelCatalog", back_populates="brand", lazy="selectin", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )


class ModelCatalog(Base):
    __tablename__ = "car_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("car_brands.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    body_type: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)  # SUV, Citadine, Berline, Break, Monospace, Utilitaire
    year_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hero_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    brand: Mapped["BrandCatalog"] = relationship("BrandCatalog", back_populates="models", lazy="selectin")
    powertrains: Mapped[list["PowertrainCatalog"]] = relationship(
        "PowertrainCatalog", back_populates="model", lazy="selectin", cascade="all, delete-orphan"
    )
    trims: Mapped[list["TrimCatalog"]] = relationship(
        "TrimCatalog", back_populates="model", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint('brand_id', 'slug', name='uq_brand_model_slug'),
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )


class PowertrainCatalog(Base):
    __tablename__ = "car_powertrains"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("car_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)  # e.g., 1.5 dCi 115, 1.2 PureTech 130, TCe 100 ECO-G, Hybrid 140
    fuel_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # DIESEL, ESSENCE, HYBRIDE, ELECTRIQUE, GPL
    fiscal_power_cv: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # Fiscal horsepower (CV) for Vignette DGI
    engine_power_hp: Mapped[int | None] = mapped_column(Integer, nullable=True)  # Ch DIN
    torque_nm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    engine_displacement_cc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transmission: Mapped[str] = mapped_column(String(50), nullable=False)  # MANUELLE, AUTOMATIQUE, EDC, E-CVT, BVA8
    drivetrain: Mapped[str | None] = mapped_column(String(50), default="FWD")  # FWD, RWD, AWD, 4x4
    consumption_l_100: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    co2_emissions_g_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    battery_capacity_kwh: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    electric_range_km: Mapped[int | None] = mapped_column(Integer, nullable=True)

    model: Mapped["ModelCatalog"] = relationship("ModelCatalog", back_populates="powertrains", lazy="selectin")
    trims: Mapped[list["TrimCatalog"]] = relationship("TrimCatalog", back_populates="powertrain", lazy="selectin")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )


class TrimCatalog(Base):
    __tablename__ = "car_trims"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("car_models.id", ondelete="CASCADE"), nullable=False, index=True
    )
    powertrain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("car_powertrains.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., Essential, Expression, Journey, Extreme, GT Line
    slug: Mapped[str] = mapped_column(String(150), nullable=False, index=True)

    # Moroccan Pricing & Promotions (MAD)
    price_new_mad: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, index=True)
    promo_price_mad: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    is_promo: Mapped[bool] = mapped_column(Boolean, default=False)

    # Warranty & Specs
    warranty_years: Mapped[int | None] = mapped_column(Integer, default=3)
    warranty_km: Mapped[int | None] = mapped_column(Integer, default=100000)
    trunk_capacity_l: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel_tank_capacity_l: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seats_count: Mapped[int | None] = mapped_column(Integer, default=5)
    doors_count: Mapped[int | None] = mapped_column(Integer, default=5)
    euro_ncap_stars: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Media & Colors
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    gallery_urls: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    available_colors: Mapped[list | None] = mapped_column(JSONB, nullable=True)  # [{"name": "Gris Schiste", "hex": "#4A4F55", "price_mad": 0}]

    is_available_in_morocco: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    model: Mapped["ModelCatalog"] = relationship("ModelCatalog", back_populates="trims", lazy="selectin")
    powertrain: Mapped["PowertrainCatalog"] = relationship("PowertrainCatalog", back_populates="trims", lazy="selectin")
    equipment_mappings: Mapped[list["TrimEquipmentMapping"]] = relationship(
        "TrimEquipmentMapping", back_populates="trim", lazy="selectin", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )


# Alias for backwards compatibility if needed
TechSpecCatalog = TrimCatalog
