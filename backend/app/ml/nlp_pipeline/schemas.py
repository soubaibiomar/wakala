from pydantic import BaseModel, Field, validator
from typing import Optional, Literal

class ExtractedCriteria(BaseModel):
    budget: Optional[int] = Field(None, description="Budget en MAD (entier), ou null si non mentionné / hors plage")
    usage_prevu: Optional[Literal["familial", "urbain", "longue_distance", "professionnel", "loisir"]] = Field(None, description="Usage principal du véhicule")
    priorites: list[str] = Field(default_factory=list, description="Liste des priorités de l'utilisateur")
    profil_passagers: Optional[str] = Field(None, description="Profil des passagers / type d'acheteur")
    erreur: bool = Field(False, description="True si l'extraction a échoué")
    
    # Nouveaux champs pour le multilinguisme et la clarification
    confiance_langue: Optional[str] = Field(None, description="Niveau de confiance de la détection de langue: haute, moyenne, basse")
    confiance_extraction: Optional[str] = Field(None, description="Niveau de confiance de l'extraction des critères: haute, moyenne, basse")
    
    langue_principale: Optional[str] = Field(None, description="fr, ar, darija, ou en")
    langues_presentes: list[str] = Field(default_factory=list, description="Liste des langues détectées dans la phrase")
    melange_langues: bool = Field(False, description="True si la phrase mélange plusieurs langues")
    
    statut: Optional[str] = Field(None, description="Statut de l'extraction, ex: 'clarification_requise'")
    question: Optional[str] = Field(None, description="Question de clarification si confiance basse")

    @validator('usage_prevu', pre=True)
    def validate_usage(cls, v):
        valid_usages = {"familial", "urbain", "longue_distance", "professionnel", "loisir"}
        if v not in valid_usages:
            return None
        return v
