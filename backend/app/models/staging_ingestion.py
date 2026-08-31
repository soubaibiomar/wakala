import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base


class StagedCatalogScrape(Base):
    """
    Quarantine staging area for incoming scraper feeds and importer price sheets.
    Data is reviewed or automatically verified before promotion to the live catalog.
    """
    __tablename__ = "staged_catalog_scrapes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_platform = Column(String(50), nullable=False)  # 'WANDALOO', 'MOTEUR_MA', 'OFFICIAL_IMPORTER'
    brand_name = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    trim_name = Column(String(150), nullable=False)
    
    scraped_price_mad = Column(Float, nullable=False)
    scraped_promo_price_mad = Column(Float, nullable=True)
    fuel_type = Column(String(50), nullable=True)
    fiscal_power_cv = Column(Integer, nullable=True)
    transmission = Column(String(50), nullable=True)
    
    raw_specs = Column(JSON, nullable=True)
    raw_equipment = Column(JSON, nullable=True)
    
    status = Column(String(30), default="PENDING_REVIEW")  # PENDING_REVIEW, AUTO_APPROVED, PROMOTED, REJECTED
    anomaly_flag = Column(Boolean, default=False)
    anomaly_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    promoted_at = Column(DateTime, nullable=True)


class CatalogIngestAnomaly(Base):
    """
    Log of pricing or spec discrepancies detected during ingestion.
    """
    __tablename__ = "catalog_ingest_anomalies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staged_scrape_id = Column(UUID(as_uuid=True), ForeignKey("staged_catalog_scrapes.id", ondelete="CASCADE"), nullable=True)
    brand_name = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    trim_name = Column(String(150), nullable=False)
    
    anomaly_type = Column(String(50), nullable=False)  # 'PRICE_SPIKE', 'PRICE_DROP', 'MISSING_EQUIPMENT', 'CV_MISMATCH'
    severity = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, CRITICAL
    old_value = Column(String(100), nullable=True)
    new_value = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
