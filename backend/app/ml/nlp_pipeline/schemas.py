from pydantic import BaseModel, Field
from typing import Optional

class ExtractedCriteria(BaseModel):
    budget: Optional[int] = Field(None, description="Budget en MAD (entier), ou null si non mentionné / hors plage")
    usage: Optional[str] = Field(None, description="Usage principal du véhicule")
    priorites: list[str] = Field(default_factory=list, description="Liste des priorités de l'utilisateur")
    profil_passagers: Optional[str] = Field(None, description="Profil des passagers / type d'acheteur")
    erreur: bool = Field(False, description="True si l'extraction a échoué")
