# Models package — Importe tous les modèles pour que SQLAlchemy les enregistre.
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from app.models.review import Review
from app.models.auth import EmailVerification
from app.models.maintenance import VehicleService
from app.models.catalog import BrandCatalog, ModelCatalog, PowertrainCatalog, TrimCatalog, TechSpecCatalog
from app.models.equipment import EquipmentCategory, EquipmentFeature, TrimEquipmentMapping
from app.models.dealership import Dealership, Showroom
from app.models.lead_inquiry import LeadInquiry
from app.models.staging_ingestion import StagedCatalogScrape, CatalogIngestAnomaly
from app.models.message import Message
from app.models.offer import Offer
from app.models.chat_history import ChatSession, ChatMessage
from app.models.vehicle_option import VehicleOption, VehicleColor, VehicleWakalaScore

__all__ = [
    "User",
    "Vehicle",
    "Listing",
    "Review",
    "EmailVerification",
    "VehicleService",
    "BrandCatalog",
    "ModelCatalog",
    "PowertrainCatalog",
    "TrimCatalog",
    "TechSpecCatalog",
    "EquipmentCategory",
    "EquipmentFeature",
    "TrimEquipmentMapping",
    "Dealership",
    "Showroom",
    "LeadInquiry",
    "StagedCatalogScrape",
    "CatalogIngestAnomaly",
    "Message",
    "Offer",
    "ChatSession",
    "ChatMessage",
    "VehicleOption",
    "VehicleColor",
    "VehicleWakalaScore",
]
