"""
models/outreach.py — Modèles ORM pour le consentement prospect et les séquences d'outreach.
Correspond aux migrations 019_create_consent_table.sql et 020_create_outreach_sequences.sql.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProspectConsent(Base):
    """Enregistrement du consentement explicite d'un prospect (loi 09-08/CNDP)."""
    __tablename__ = "prospect_consents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    prospect_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    channel: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )
    purpose: Mapped[str] = mapped_column(
        String(50), nullable=False, default="recommendation_outreach"
    )
    consented_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    opt_out_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consent_source: Mapped[str] = mapped_column(
        String(20), nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint(
            "channel IN ('whatsapp', 'email', 'sms')",
            name="ck_consent_channel",
        ),
        CheckConstraint(
            "consent_source IN ('web', 'whatsapp', 'chatbot')",
            name="ck_consent_source",
        ),
    )

    @property
    def is_active(self) -> bool:
        """Le consentement est actif s'il n'a pas été retiré."""
        return self.opt_out_at is None

    def __repr__(self) -> str:
        status = "active" if self.is_active else f"opted-out@{self.opt_out_at}"
        return f"<ProspectConsent {self.prospect_id} {self.channel} {status}>"


class OutreachSequence(Base):
    """Séquence d'outreach 0-60 jours pour un prospect consentant."""
    __tablename__ = "outreach_sequences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    prospect_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    top3_vehicle_ids: Mapped[dict] = mapped_column(
        JSONB, nullable=False
    )
    sequence_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    current_milestone: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )
    next_scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )
    stop_reason: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'stopped', 'completed')",
            name="ck_outreach_status",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<OutreachSequence {self.prospect_id} "
            f"milestone={self.current_milestone} status={self.status}>"
        )
