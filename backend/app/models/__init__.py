# Models package — Importe tous les modèles pour que SQLAlchemy les enregistre.
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.listing import Listing
from app.models.review import Review

__all__ = ["User", "Vehicle", "Listing", "Review"]
