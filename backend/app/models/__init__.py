# Models package — Importe tous les modèles pour que SQLAlchemy les enregistre.
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from app.models.review import Review
from app.models.auth import EmailVerification
from app.models.maintenance import VehicleService
from app.models.catalog import BrandCatalog, ModelCatalog, TechSpecCatalog
from app.models.message import Message
from app.models.offer import Offer
from app.models.chat_history import ChatSession, ChatMessage

__all__ = ["User", "Vehicle", "Listing", "Review", "EmailVerification", "VehicleService", "BrandCatalog", "ModelCatalog", "TechSpecCatalog", "Message", "Offer", "ChatSession", "ChatMessage"]
