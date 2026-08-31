"""
ml/recommendation/compliance_guard.py — GARDE-FOU CRITIQUE.

Avant de retourner un résultat au chatbot, vérifie que chaque véhicule
proposé existe bel et bien dans la table `vehicles` avec un prix
PostgreSQL à jour et un statut "available".

Si un véhicule référencé n'a pas de correspondance exacte en base,
il est écarté silencieusement du résultat plutôt que transmis au LLM.

Ce module est le SEUL rempart contre une hallucination qui filtrerait
jusqu'à l'utilisateur.
"""

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vehicle import Vehicle

logger = logging.getLogger(__name__)


async def verify_vehicles_exist(
    vehicle_ids: list[str],
    db: AsyncSession,
) -> list[str]:
    """
    Retourne uniquement les IDs qui existent en base avec :
    - status = 'available'
    - price IS NOT NULL et price > 0

    Tous les véhicules non vérifiés sont écartés silencieusement
    avec un warning loggé pour traçabilité.
    """
    if not vehicle_ids:
        return []

    # Convert to UUID, filtering out invalid formats
    valid_uuids = []
    for vid in vehicle_ids:
        try:
            valid_uuids.append(uuid.UUID(str(vid)))
        except (ValueError, AttributeError):
            logger.warning(
                "COMPLIANCE_GUARD: Invalid vehicle ID format rejected: %s", vid
            )

    if not valid_uuids:
        return []

    result = await db.execute(
        select(Vehicle.id).where(
            Vehicle.id.in_(valid_uuids),
            Vehicle.status == "available",
            Vehicle.price.isnot(None),
            Vehicle.price > 0,
        )
    )
    verified_ids = {str(row[0]) for row in result.all()}

    # Log any rejected vehicles
    for vid in vehicle_ids:
        if vid not in verified_ids:
            logger.warning(
                "COMPLIANCE_GUARD: Vehicle %s rejected — "
                "not found in DB, not available, or missing price",
                vid,
            )

    return [vid for vid in vehicle_ids if vid in verified_ids]


async def filter_recommendations(
    recommendations: list[dict[str, Any]],
    db: AsyncSession,
) -> list[dict[str, Any]]:
    """
    Filtre une liste de recommandations structurées, ne conservant que
    celles dont le vehicle_id est vérifié en base.

    Utilisé comme dernier filtre avant de transmettre au LLM.
    """
    if not recommendations:
        return []

    vehicle_ids = [
        r.get("vehicle_id") or r.get("id", "")
        for r in recommendations
    ]

    verified = set(await verify_vehicles_exist(vehicle_ids, db))

    filtered = [
        r for r in recommendations
        if (r.get("vehicle_id") or r.get("id", "")) in verified
    ]

    if len(filtered) < len(recommendations):
        logger.warning(
            "COMPLIANCE_GUARD: %d/%d vehicles rejected from recommendations",
            len(recommendations) - len(filtered),
            len(recommendations),
        )

    return filtered


async def verify_single_vehicle(
    vehicle_id: str,
    db: AsyncSession,
) -> bool:
    """Vérifie qu'un seul véhicule existe et est valide en base."""
    result = await verify_vehicles_exist([vehicle_id], db)
    return len(result) == 1
