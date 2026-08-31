import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EquipmentCategory(Base):
    __tablename__ = "equipment_categories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)  # Sécurité, Confort, Multimédia, Extérieur
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)  # shield, user, wifi, eye
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    features: Mapped[list["EquipmentFeature"]] = relationship(
        "EquipmentFeature", back_populates="category", lazy="selectin", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class EquipmentFeature(Base):
    __tablename__ = "equipment_features"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment_categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)  # e.g., Régulateur adaptatif, Caméra 360°, Apple CarPlay sans fil
    slug: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    category: Mapped["EquipmentCategory"] = relationship("EquipmentCategory", back_populates="features", lazy="selectin")
    trim_mappings: Mapped[list["TrimEquipmentMapping"]] = relationship(
        "TrimEquipmentMapping", back_populates="feature", lazy="selectin", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint('category_id', 'slug', name='uq_category_feature_slug'),
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TrimEquipmentMapping(Base):
    __tablename__ = "trim_equipment_mappings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("car_trims.id", ondelete="CASCADE"), nullable=False, index=True
    )
    feature_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("equipment_features.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="SERIE")  # SERIE, OPTION, NON_DISPO
    option_price_mad: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True, default=0.0)

    trim: Mapped["TrimCatalog"] = relationship("TrimCatalog", back_populates="equipment_mappings", lazy="selectin")
    feature: Mapped["EquipmentFeature"] = relationship("EquipmentFeature", back_populates="trim_mappings", lazy="selectin")

    __table_args__ = (
        UniqueConstraint('trim_id', 'feature_id', name='uq_trim_feature'),
    )
