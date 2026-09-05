import hmac
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.listing import Listing
from app.models.user import User
from app.core.security import get_current_user
from app.core.config import settings
from app.core.limiter import limiter
from app.services.payment_service import payment_service
from app.ml.vision.ocr_validator import ocr_validator
from pydantic import BaseModel

router = APIRouter(prefix="/transactions", tags=["Escrow & Séquestre"])

class InitiateTransactionRequest(BaseModel):
    listing_id: str

class TransactionResponse(BaseModel):
    id: str
    listing_id: str
    amount: float
    status: str
    payment_intent_id: str | None

@router.post("/initiate", response_model=TransactionResponse)
@limiter.limit("10/minute")
async def initiate_transaction(
    request: Request,
    payload: InitiateTransactionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initie une transaction Escrow pour sécuriser les fonds."""
    result = await db.execute(select(Listing).where(Listing.id == payload.listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="Annonce introuvable.")
    
    if str(listing.user_id) == str(current_user.id):
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas acheter votre propre véhicule.")

    # Simuler l'appel à Stripe/CMI
    payment_data = await payment_service.create_payment_intent(
        amount=listing.price,
        buyer_id=str(current_user.id),
        seller_id=str(listing.user_id),
        listing_id=str(listing.id)
    )

    new_tx = Transaction(
        listing_id=listing.id,
        buyer_id=current_user.id,
        seller_id=listing.user_id,
        amount=listing.price,
        status="PENDING",
        payment_intent_id=payment_data["payment_intent_id"]
    )
    
    db.add(new_tx)
    await db.commit()
    await db.refresh(new_tx)
    
    return {
        "id": str(new_tx.id),
        "listing_id": str(new_tx.listing_id),
        "amount": new_tx.amount,
        "status": new_tx.status,
        "payment_intent_id": new_tx.payment_intent_id
    }

@router.post("/{tx_id}/webhook-pay", summary="Simule le retour de paiement bancaire")
@limiter.limit("30/minute")
async def webhook_payment_success(
    tx_id: str, 
    request: Request, 
    db: AsyncSession = Depends(get_db)
):
    # SÉCURITÉ : Validation de la provenance du Webhook
    webhook_secret = request.headers.get("X-Webhook-Secret")
    expected_secret = settings.WEBHOOK_SECRET or os.environ.get("WEBHOOK_SECRET")
    if not expected_secret:
        raise HTTPException(
            status_code=500,
            detail="Configuration serveur incomplète : WEBHOOK_SECRET non défini."
        )
    if not webhook_secret or not hmac.compare_digest(webhook_secret, expected_secret):
        raise HTTPException(status_code=403, detail="Signature Webhook invalide.")

    result = await db.execute(select(Transaction).where(Transaction.id == tx_id))
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction non trouvée.")

    # Webhooks are retried by providers; make the state transition idempotent.
    if tx.status == "FUNDS_SECURED":
        return {"status": tx.status}
        
    res = await payment_service.simulate_webhook_payment_success(tx.payment_intent_id)
    if res["status"] == "succeeded":
        tx.status = "FUNDS_SECURED"
        await db.commit()
        return {"status": "FUNDS_SECURED", "message": "Les fonds sont bloqués sur le compte Wakala."}
    return {"status": tx.status}

@router.post("/{tx_id}/upload-document", summary="Upload et vérification IA de la carte grise")
@limiter.limit("5/minute")
async def upload_transfer_document(
    tx_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user) # Idéalement, seul l'acheteur ou le vendeur peut faire ça
):
    result = await db.execute(select(Transaction).where(Transaction.id == tx_id))
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction non trouvée.")
        
    if str(current_user.id) not in [str(tx.seller_id), str(tx.buyer_id)]:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à modifier cette transaction.")
        
    if tx.status != "FUNDS_SECURED":
        raise HTTPException(status_code=400, detail="Les fonds ne sont pas encore sécurisés.")
        
    if not file.content_type in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Le document doit être une image (JPEG/PNG) ou un PDF.")
        
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Le fichier est trop volumineux (maximum 5MB).")
        
    # On simule l'enregistrement du fichier
    file_content = await file.read(5 * 1024 * 1024 + 1)
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Le fichier est trop volumineux (maximum 5MB).")
    
    # OCR Extraction
    document_text = ocr_validator.extract_text(file_content)
    
    # On récupère le nom du vendeur pour validation
    result_seller = await db.execute(select(User).where(User.id == tx.seller_id))
    seller = result_seller.scalar_one_or_none()
    if not seller:
        raise HTTPException(status_code=404, detail="Vendeur non trouvé.")
    
    # Validation OCR
    is_valid = ocr_validator.validate_ownership_transfer(document_text, seller.full_name)
    
    if is_valid:
        # Libération des fonds simulée
        await payment_service.release_funds(tx.payment_intent_id, str(seller.id))
        tx.status = "COMPLETED"
        tx.document_url = "s3://wakala-escrow/doc_" + str(uuid.uuid4())
        await db.commit()
        return {"status": "COMPLETED", "message": "Transfert de propriété validé par l'IA. Fonds libérés au vendeur."}
    else:
        tx.status = "DISPUTED"
        await db.commit()
        raise HTTPException(status_code=400, detail="Validation OCR échouée. Le document ne correspond pas au vendeur.")
