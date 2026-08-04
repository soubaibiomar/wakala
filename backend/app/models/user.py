"""
models/user.py — Modèle ORM User (acheteurs et vendeurs).
Correspond à la migration 001_create_users.sql.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String, Text, Table, ForeignKey, Column
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

saved_vehicles_table = Table(
    "saved_vehicles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("vehicle_id", UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False),
)



class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("buyer", "seller", "admin", name="user_role", create_type=False),
        nullable=False,
        default="buyer",
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_pro: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    preferences: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # ─── Relations ─────────────────────────────────────────────
    vehicles: Mapped[list["Vehicle"]] = relationship(  # noqa: F821
        "Vehicle", back_populates="seller", lazy="selectin"
    )
    authored_reviews: Mapped[list["Review"]] = relationship(  # noqa: F821
        "Review", foreign_keys="Review.author_id", back_populates="author", lazy="selectin"
    )
    received_reviews: Mapped[list["Review"]] = relationship(  # noqa: F821
        "Review", foreign_keys="Review.seller_id", back_populates="seller", lazy="selectin"
    )
    services: Mapped[list["VehicleService"]] = relationship(  # noqa: F821
        "VehicleService", back_populates="user", lazy="selectin"
    )
    saved_vehicles: Mapped[list["Vehicle"]] = relationship(  # noqa: F821
        "Vehicle", secondary="saved_vehicles", back_populates="saved_by_users", lazy="selectin"
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(  # noqa: F821
        "ChatSession", back_populates="user", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
