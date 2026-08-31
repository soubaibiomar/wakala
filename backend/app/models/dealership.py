import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Dealership(Base):
    __tablename__ = "dealerships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True, index=True)  # Auto Hall, Renault Commerce Maroc, Sopriam, SMEIA, CAC
    slug: Mapped[str] = mapped_column(String(180), nullable=False, unique=True, index=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    headquarters_city: Mapped[str | None] = mapped_column(String(100), default="Casablanca")

    showrooms: Mapped[list["Showroom"]] = relationship(
        "Showroom", back_populates="dealership", lazy="selectin", cascade="all, delete-orphan"
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Showroom(Base):
    __tablename__ = "showrooms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dealership_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("dealerships.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)  # e.g., Renault Succursale Ain Sebaa
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # Casablanca, Rabat, Marrakech, Tanger, Fès, Agadir...
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 6), nullable=True)
    brand_affiliations: Mapped[list | None] = mapped_column(JSONB, nullable=True)  # ["Dacia", "Renault"]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    dealership: Mapped["Dealership"] = relationship("Dealership", back_populates="showrooms", lazy="selectin")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
