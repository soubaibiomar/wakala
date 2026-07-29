# Models package — Importe tous les modèles pour que SQLAlchemy les enregistre.
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from app.models.review import Review
from app.models.auth import EmailVerification
from app.models.maintenance import VehicleService
from app.models.catalog import BrandCatalog, ModelCatalog, TechSpecCatalog
from app.models.message import Message

__all__ = ["User", "Vehicle", "Listing", "Review", "EmailVerification", "VehicleService", "BrandCatalog", "ModelCatalog", "TechSpecCatalog", "Message"]
