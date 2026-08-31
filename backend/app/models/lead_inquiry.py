import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class LeadInquiry(Base):
    """
    Demandes d'essai et devis proforma pour véhicules neufs.
    Conforme CNDP (Loi n° 09-08 relative à la protection des personnes physiques
    à l'égard du traitement des données à caractère personnel).
    """
    __tablename__ = "lead_inquiries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trim_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("car_trims.id", ondelete="CASCADE"), nullable=False, index=True
    )
    showroom_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("showrooms.id", ondelete="SET NULL"), nullable=True, index=True
    )
    
    inquiry_type: Mapped[str] = mapped_column(String(50), nullable=False, default="TEST_DRIVE")  # TEST_DRIVE, QUOTE_PROFORMA
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # E.164 +212XXXXXXXXX
    email: Mapped[str | None] = mapped_column(String(150), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    preferred_date: Mapped[str | None] = mapped_column(String(50), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Verification & Anti-Fraud
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    otp_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ip_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # CNDP Moroccan Privacy Compliance
    cndp_consent_accepted: Mapped[bool] = mapped_column(Boolean, default=True)
    cndp_consent_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    cndp_privacy_version: Mapped[str] = mapped_column(String(20), default="2026-v1")

    # Dealer Dispatch Status
    dispatch_status: Mapped[str] = mapped_column(
        String(50), default="PENDING_VERIFICATION", index=True
    )  # PENDING_VERIFICATION, VERIFIED_PENDING_DISPATCH, DISPATCHED, DISPATCH_FAILED_DLQ

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
