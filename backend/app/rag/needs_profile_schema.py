"""
rag/needs_profile_schema.py — Schéma structuré du "profil de besoin" accumulé
pendant la phase de découverte consultative.

Ce profil est construit incrémentalement à chaque échange avec le prospect.
Il n'est jamais complété par le LLM — chaque champ provient d'une extraction
déterministe ou d'une extraction LLM validée à partir du message utilisateur.
"""

from typing import Optional
from pydantic import BaseModel, Field


# Les 8 dimensions du document de référence Wakala
VALID_DIMENSIONS = frozenset({
    "espace",
    "securite",
    "cout_reel",
    "prix_acces",
    "praticite_urbaine",
    "performance",
    "ecologie",
    "motricite",
})

# Mapping des expressions utilisateur courantes vers les dimensions
PRIORITY_ALIASES: dict[str, str] = {
    # Espace
    "espace": "espace", "coffre": "espace", "place": "espace",
    "grand": "espace", "spacieux": "espace", "famille": "espace",
    "bagages": "espace",
    # Sécurité
    "securite": "securite", "sécurité": "securite", "airbag": "securite",
    "ncap": "securite", "sûr": "securite", "safe": "securite",
    "enfant": "securite", "bebe": "securite", "bébé": "securite",
    # Coût réel
    "economique": "cout_reel", "économique": "cout_reel",
    "consommation": "cout_reel", "conso": "cout_reel",
    "pas cher à l'usage": "cout_reel", "entretien": "cout_reel",
    "économie": "cout_reel",
    # Prix d'accès
    "prix": "prix_acces", "budget": "prix_acces", "abordable": "prix_acces",
    "rkhis": "prix_acces", "pas cher": "prix_acces",
    # Praticité urbaine
    "ville": "praticite_urbaine", "urbain": "praticite_urbaine",
    "parking": "praticite_urbaine", "manoeuvre": "praticite_urbaine",
    "mdina": "praticite_urbaine", "citadine": "praticite_urbaine",
    # Performance
    "performance": "performance", "puissance": "performance",
    "rapide": "performance", "sportif": "performance",
    "chevaux": "performance", "moteur": "performance",
    # Écologie
    "ecologique": "ecologie", "écologique": "ecologie",
    "electrique": "ecologie", "électrique": "ecologie",
    "vert": "ecologie", "co2": "ecologie", "hybride": "ecologie",
    "environnement": "ecologie",
    # Motricité
    "4x4": "motricite", "tout terrain": "motricite",
    "offroad": "motricite", "piste": "motricite",
    "montagne": "motricite", "boue": "motricite",
    "traction": "motricite",
}


class NeedsProfile(BaseModel):
    """Profil de besoin du prospect, construit incrémentalement."""

    usage: Optional[str] = Field(
        None,
        description="Usage principal : ville, route, mixte, offroad",
    )
    budget_max: Optional[float] = Field(
        None, ge=0,
        description="Budget maximum en MAD",
    )
    nb_passagers: Optional[int] = Field(
        None, ge=1, le=9,
        description="Nombre de passagers habituel",
    )
    priorities: list[str] = Field(
        default_factory=list,
        description="Dimensions prioritaires parmi les 8 dimensions Wakala",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Contraintes exprimées en texte libre (ex: 'pas trop de consommation')",
    )
    fuel_preference: Optional[str] = Field(
        None,
        description="Préférence carburant : essence, diesel, hybride, electrique",
    )
    body_type_preference: Optional[str] = Field(
        None,
        description="Préférence carrosserie si exprimée",
    )
    brand_preference: Optional[str] = Field(
        None,
        description="Préférence marque si exprimée",
    )

    @property
    def is_complete(self) -> bool:
        """Le profil est complet si au moins budget ET usage sont renseignés."""
        return self.budget_max is not None and self.usage is not None

    @property
    def filled_fields_count(self) -> int:
        """Nombre de champs renseignés (hors listes vides)."""
        count = 0
        if self.usage is not None:
            count += 1
        if self.budget_max is not None:
            count += 1
        if self.nb_passagers is not None:
            count += 1
        if self.priorities:
            count += 1
        if self.constraints:
            count += 1
        if self.fuel_preference is not None:
            count += 1
        if self.body_type_preference is not None:
            count += 1
        if self.brand_preference is not None:
            count += 1
        return count

    def missing_essential_fields(self) -> list[str]:
        """Retourne les champs essentiels encore manquants."""
        missing = []
        if self.budget_max is None:
            missing.append("budget")
        if self.usage is None:
            missing.append("usage")
        return missing

    def merge_update(self, partial: dict) -> "NeedsProfile":
        """Met à jour le profil incrémentalement sans écraser les valeurs existantes."""
        data = self.model_dump()
        for key, value in partial.items():
            if value is None:
                continue
            if key == "priorities" and isinstance(value, list):
                existing = set(data.get("priorities", []))
                # Normalise les priorités via les alias
                for p in value:
                    normalized = PRIORITY_ALIASES.get(p.lower().strip(), p.lower().strip())
                    if normalized in VALID_DIMENSIONS:
                        existing.add(normalized)
                data["priorities"] = list(existing)
            elif key == "constraints" and isinstance(value, list):
                existing = set(data.get("constraints", []))
                existing.update(value)
                data["constraints"] = list(existing)
            elif data.get(key) is None:
                # Ne pas écraser une valeur existante
                data[key] = value
        return NeedsProfile(**data)
