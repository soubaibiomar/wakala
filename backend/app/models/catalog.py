import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint,
    JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class BrandCatalog(Base):
    __tablename__ = "car_brands"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    logo_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country_of_origin: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    models: Mapped[list["ModelCatalog"]] = relationship("ModelCatalog", back_populates="brand", lazy="selectin", cascade="all, delete-orphan")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class ModelCatalog(Base):
    __tablename__ = "car_models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("car_brands.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    body_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    year_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    brand: Mapped["BrandCatalog"] = relationship("BrandCatalog", back_populates="models", lazy="selectin")
    specs: Mapped[list["TechSpecCatalog"]] = relationship("TechSpecCatalog", back_populates="model", lazy="selectin", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('brand_id', 'name', name='uq_brand_model'),
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

class TechSpecCatalog(Base):
    """Fiches techniques exactes des versions"""
    __tablename__ = "car_technical_specs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("car_models.id", ondelete="CASCADE"), nullable=False, index=True)
    version_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    
    # Pricing info (Neuf Maroc)
    price_new_mad: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    
    # Engine & Powertrain
    engine_type: Mapped[str | None] = mapped_column(String(100), nullable=True) # e.g. 1.5 dCi
    fuel_type: Mapped[str | None] = mapped_column(String(50), nullable=True) # essence, diesel, hybride...
    engine_power_hp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fiscal_power_cv: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transmission: Mapped[str | None] = mapped_column(String(50), nullable=True) # Manuelle, Automatique
    
    # Performance & Consumption
    consumption_l_100: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    acceleration_0_100: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    top_speed_kmh: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Dimensions
    trunk_capacity_l: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fuel_tank_capacity_l: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Other features as JSON
    equipment_list: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    model: Mapped["ModelCatalog"] = relationship("ModelCatalog", back_populates="specs", lazy="selectin")

    __table_args__ = (
        UniqueConstraint('model_id', 'version_name', name='uq_model_version'),
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
