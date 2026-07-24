from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db
from app.models.vehicle import Vehicle
from app.ml.trust_engine.trust_score_combiner import compute_trust_score
from app.ml.trust_engine.schemas import TrustScoreResult

router = APIRouter()

class ChecklistResponse(BaseModel):
    vehicle_id: str
    trust_score: float
    confidence: str
    checklist: list[str]

@router.get("/checklist/{vehicle_id}", response_model=ChecklistResponse)
async def generate_checklist(vehicle_id: str, db: AsyncSession = Depends(get_db)):
    """
    Génère une checklist de visite basée sur le score de confiance d'un véhicule.
    Le Trust Engine identifie les faiblesses spécifiques (ex: prix anormal, photos douteuses)
    qui sont transformées en points de vigilance pour l'acheteur.
    """
    try:
        vid = uuid.UUID(vehicle_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de véhicule invalide")

    result = await db.execute(select(Vehicle).filter(Vehicle.id == vid))
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")
        
    trust_result: TrustScoreResult = await compute_trust_score(vehicle)
    
    checklist = [
        "Vérifier la concordance entre la carte grise et le numéro de châssis (VIN).",
        "Demander le carnet d'entretien et les dernières factures de réparation."
    ]
    
    # Points de vigilance dynamiques
    if trust_result.price_anomaly_score is not None and trust_result.price_anomaly_score < 70:
        checklist.append("⚠️ Le prix est inhabituellement bas pour ce modèle. Inspectez minutieusement le moteur et demandez s'il y a des défauts cachés.")
        
    if trust_result.seller_pattern_score is not None and trust_result.seller_pattern_score < 70:
        checklist.append("⚠️ Le vendeur pourrait être un courtier non déclaré. Assurez-vous qu'il est bien le propriétaire légal sur la carte grise.")
        
    if trust_result.photo_damage_score is not None and trust_result.photo_damage_score < 70:
        checklist.append("⚠️ L'IA a détecté de possibles rayures ou irrégularités sur la carrosserie. Vérifiez l'état de la peinture à la lumière du jour.")
        
    if trust_result.confidence == "low":
        checklist.append("⚠️ Les informations de l'annonce sont limitées. Posez un maximum de questions avant de vous engager.")
        
    # Test de conduite toujours suggéré
    checklist.append("Faire un essai routier d'au moins 15 minutes (ville et voie rapide).")

    return ChecklistResponse(
        vehicle_id=vehicle_id,
        trust_score=trust_result.trust_score,
        confidence=trust_result.confidence,
        checklist=checklist
    )
