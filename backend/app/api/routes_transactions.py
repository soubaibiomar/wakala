import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.listing import Listing
from app.models.user import User
from app.core.security import get_current_user
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
async def initiate_transaction(
    request: InitiateTransactionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initie une transaction Escrow pour sécuriser les fonds."""
    listing = db.query(Listing).filter(Listing.id == request.listing_id).first()
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
    db.commit()
    db.refresh(new_tx)
    
    return {
        "id": str(new_tx.id),
        "listing_id": str(new_tx.listing_id),
        "amount": new_tx.amount,
        "status": new_tx.status,
        "payment_intent_id": new_tx.payment_intent_id
    }

@router.post("/{tx_id}/webhook-pay", summary="Simule le retour de paiement bancaire")
async def webhook_payment_success(
    tx_id: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    # SÉCURITÉ : Validation de la provenance du Webhook (mock)
    webhook_secret = request.headers.get("X-Webhook-Secret")
    if not webhook_secret or webhook_secret != "wakala_mock_secret":
        raise HTTPException(status_code=403, detail="Signature Webhook invalide.")

    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction non trouvée.")
        
    res = await payment_service.simulate_webhook_payment_success(tx.payment_intent_id)
    if res["status"] == "succeeded":
        tx.status = "FUNDS_SECURED"
        db.commit()
        return {"status": "FUNDS_SECURED", "message": "Les fonds sont bloqués sur le compte Wakala."}
    return {"status": tx.status}

@router.post("/{tx_id}/upload-document", summary="Upload et vérification IA de la carte grise")
async def upload_transfer_document(
    tx_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Idéalement, seul l'acheteur ou le vendeur peut faire ça
):
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction non trouvée.")
        
    if str(current_user.id) not in [str(tx.seller_id), str(tx.buyer_id)]:
        raise HTTPException(status_code=403, detail="Vous n'êtes pas autorisé à modifier cette transaction.")
        
    if tx.status != "FUNDS_SECURED":
        raise HTTPException(status_code=400, detail="Les fonds ne sont pas encore sécurisés.")
        
    # On simule l'enregistrement du fichier
    file_content = await file.read()
    
    # OCR Extraction
    document_text = ocr_validator.extract_text(file_content)
    
    # On récupère le nom du vendeur pour validation
    seller = db.query(User).filter(User.id == tx.seller_id).first()
    
    # Validation OCR
    is_valid = ocr_validator.validate_ownership_transfer(document_text, seller.name)
    
    if is_valid:
        # Libération des fonds simulée
        await payment_service.release_funds(tx.payment_intent_id, str(seller.id))
        tx.status = "COMPLETED"
        tx.document_url = "s3://wakala-escrow/doc_" + str(uuid.uuid4())
        db.commit()
        return {"status": "COMPLETED", "message": "Transfert de propriété validé par l'IA. Fonds libérés au vendeur."}
    else:
        tx.status = "DISPUTED"
        db.commit()
        raise HTTPException(status_code=400, detail="Validation OCR échouée. Le document ne correspond pas au vendeur.")
