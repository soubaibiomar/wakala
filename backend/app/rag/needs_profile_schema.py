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
    "espace": "espace", "space": "espace", "coffre": "espace", "luggage": "espace",
    "place": "espace", "grand": "espace", "spacieux": "espace", "famille": "espace",
    "bagages": "espace", "مساحة": "espace", "صندوق": "espace", "أمتعة": "espace",
    "حقائب": "espace", "فاليزات": "espace", "عائلة": "espace", "العائلة": "espace",
    "واسعة": "espace", "كبير": "espace",
    # Sécurité
    "securite": "securite", "sécurité": "securite", "safety": "securite", "airbag": "securite",
    "ncap": "securite", "sûr": "securite", "safe": "securite",
    "enfant": "securite", "bebe": "securite", "bébé": "securite",
    "سلامة": "securite", "السلامة": "securite", "أمان": "securite", "الامان": "securite",
    "حماية": "securite", "أطفال": "securite",
    # Coût réel
    "economique": "cout_reel", "économique": "cout_reel",
    "consommation": "cout_reel", "consumption": "cout_reel", "conso": "cout_reel",
    "low consumption": "cout_reel", "fuel economy": "cout_reel",
    "pas cher à l'usage": "cout_reel", "entretien": "cout_reel",
    "économie": "cout_reel", "استهلاك": "cout_reel", "توفير": "cout_reel",
    "تكاليف": "cout_reel", "مصاريف": "cout_reel", "اقتصادية": "cout_reel", "صيانة": "cout_reel",
    # Prix d'accès
    "prix": "prix_acces", "budget": "prix_acces", "abordable": "prix_acces",
    "rkhis": "prix_acces", "pas cher": "prix_acces",
    "ثمن": "prix_acces", "سعر": "prix_acces", "ميزانية": "prix_acces", "رخيص": "prix_acces", "مناسب": "prix_acces",
    # Praticité urbaine
    "ville": "praticite_urbaine", "city": "praticite_urbaine", "urban": "praticite_urbaine", "urbain": "praticite_urbaine",
    "parking": "praticite_urbaine", "manoeuvre": "praticite_urbaine",
    "mdina": "praticite_urbaine", "citadine": "praticite_urbaine",
    "مدينة": "praticite_urbaine", "المدينة": "praticite_urbaine", "وسط المدينة": "praticite_urbaine",
    "صغيرة": "praticite_urbaine", "سيتادين": "praticite_urbaine",
    # Performance
    "performance": "performance", "puissance": "performance",
    "rapide": "performance", "sportif": "performance",
    "chevaux": "performance", "moteur": "performance",
    "قوة": "performance", "سرعة": "performance", "تسارع": "performance", "محرك": "performance", "رياضية": "performance",
    # Écologie
    "ecologique": "ecologie", "écologique": "ecologie",
    "electrique": "ecologie", "électrique": "ecologie", "electric": "ecologie",
    "vert": "ecologie", "co2": "ecologie", "hybride": "ecologie",
    "environnement": "ecologie",
    "بيئة": "ecologie", "بيئي": "ecologie", "كهربائي": "ecologie", "كهربائية": "ecologie", "هجين": "ecologie",
    # Motricité
    "4x4": "motricite", "tout terrain": "motricite",
    "offroad": "motricite", "piste": "motricite",
    "montagne": "motricite", "boue": "motricite",
    "traction": "motricite",
    "دفع رباعي": "motricite", "وعرة": "motricite", "طرق وعرة": "motricite", "جبلية": "motricite", "مسالك": "motricite",
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
    # État explicite de la boucle de découverte. Ces champs ne sont jamais
    # inventés par le LLM : ils sont alimentés par l'extraction déterministe
    # et par le flow qui enregistre la question effectivement envoyée.
    covered_dimensions: list[str] = Field(
        default_factory=list,
        description="Dimensions 8D explicitement couvertes par le client",
    )
    asked_dimensions: list[str] = Field(
        default_factory=list,
        description="Dimensions déjà demandées dans une question précédente",
    )
    pending_dimensions: list[str] = Field(
        default_factory=list,
        description="Dimensions de la dernière question encore en attente de réponse",
    )
    weight_deltas: dict[str, float] = Field(
        default_factory=dict,
        description="Ajustements de poids issus des arbitrages explicites",
    )

    @property
    def missing_dimensions(self) -> list[str]:
        """Dimensions 8D non encore couvertes, dans l'ordre contractuel."""
        covered = set(self.covered_dimensions)
        return [dimension for dimension in DIMENSION_ORDER if dimension not in covered]

    @property
    def ready_for_recommendation(self) -> bool:
        """Indique si les filtres durs et un minimum de préférences sont connus.

        Budget + usage restent nécessaires pour interroger le catalogue. Trois
        dimensions couvertes suffisent ensuite pour éviter de bloquer le client
        dans un questionnaire sans fin ; les filtres durs (marque, carburant,
        carrosserie) peuvent également déclencher la restitution.
        """
        return self.is_complete and (
            len(self.covered_dimensions) >= 3
            or bool(self.brand_preference and self.body_type_preference)
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
            if key in {"priorities", "covered_dimensions", "asked_dimensions", "pending_dimensions"} and isinstance(value, list):
                existing = set(data.get("priorities", []))
                if key != "priorities":
                    existing = set(data.get(key, []))
                for p in value:
                    normalized = PRIORITY_ALIASES.get(p.lower().strip(), p.lower().strip())
                    if normalized in VALID_DIMENSIONS:
                        existing.add(normalized)
                data[key] = [dimension for dimension in DIMENSION_ORDER if dimension in existing]
            elif key == "weight_deltas" and isinstance(value, dict):
                deltas = dict(data.get("weight_deltas", {}))
                for dimension, delta in value.items():
                    normalized = PRIORITY_ALIASES.get(str(dimension).lower().strip(), str(dimension).lower().strip())
                    if normalized in VALID_DIMENSIONS:
                        deltas[normalized] = float(delta)
                data[key] = deltas
            elif key == "constraints" and isinstance(value, list):
                existing = set(data.get("constraints", []))
                existing.update(value)
                data["constraints"] = list(existing)
            elif data.get(key) is None:
                # Ne pas écraser une valeur existante
                data[key] = value
        return NeedsProfile(**data)


# Keep the canonical order in one place for serialization and deterministic
# missing-dimension calculation. It is deliberately defined after the model so
# existing imports remain backward compatible.
DIMENSION_ORDER = (
    "espace",
    "securite",
    "cout_reel",
    "prix_acces",
    "praticite_urbaine",
    "performance",
    "ecologie",
    "motricite",
)
