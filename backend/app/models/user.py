"""
models/user.py — Modèle ORM User (acheteurs et vendeurs).
Correspond à la migration 001_create_users.sql.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("buyer", "seller", "admin", name="user_role", create_type=False),
        nullable=False,
        default="buyer",
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
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
    reviews_authored: Mapped[list["Review"]] = relationship(  # noqa: F821
        "Review", back_populates="author", foreign_keys="Review.author_id", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"
