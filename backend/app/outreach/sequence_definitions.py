"""
outreach/sequence_definitions.py — Définitions des 6 jalons de la séquence
d'outreach 0-60 jours, conformes au document de référence Wakala.

Chaque jalon a un code, un délai en jours, un objectif, et un canal.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Milestone:
    """Définition d'un jalon dans la séquence d'outreach."""
    code: str
    delay_days: int
    objective: str
    channel: str
    template_key: str
    skippable: bool = False  # Si True, peut être sauté si la condition n'est pas remplie


# Les 6 jalons du document de référence
MILESTONES: list[Milestone] = [
    Milestone(
        code="J0",
        delay_days=0,
        objective="Récapitulatif Top 3 personnalisé",
        channel="email",
        template_key="j0_recap_top3",
    ),
    Milestone(
        code="J2-3",
        delay_days=2,
        objective="Catalogue interactif avec fiches détaillées",
        channel="whatsapp",
        template_key="j2_catalogue_interactif",
    ),
    Milestone(
        code="J7",
        delay_days=7,
        objective="Matrice TCO comparative (coût total de possession)",
        channel="email",
        template_key="j7_matrice_tco",
    ),
    Milestone(
        code="J14",
        delay_days=14,
        objective="Proposition d'essai routier",
        channel="whatsapp",
        template_key="j14_essai_routier",
    ),
    Milestone(
        code="J45",
        delay_days=45,
        objective="Alerte prix si baisse réelle détectée",
        channel="email",
        template_key="j45_alerte_prix",
        skippable=True,  # Sauté si aucune vraie baisse n'est détectée
    ),
    Milestone(
        code="J60",
        delay_days=60,
        objective="Clôture bienveillante de la séquence",
        channel="email",
        template_key="j60_cloture",
    ),
]

# Mapping code → Milestone pour accès rapide
MILESTONE_MAP: dict[str, Milestone] = {m.code: m for m in MILESTONES}


def get_next_milestone(current_code: str | None) -> Milestone | None:
    """Retourne le jalon suivant dans la séquence."""
    if current_code is None:
        return MILESTONES[0] if MILESTONES else None

    for i, m in enumerate(MILESTONES):
        if m.code == current_code and i + 1 < len(MILESTONES):
            return MILESTONES[i + 1]

    return None  # Séquence terminée
