import uuid

class PaymentService:
    """
    Mock pour simuler un partenaire bancaire marocain (CMI) ou Stripe Connect.
    Pour l'Escrow Wakala.
    """
    
    @staticmethod
    async def create_payment_intent(amount: float, buyer_id: str, seller_id: str, listing_id: str) -> dict:
        """Simule la création d'une session de paiement pour bloquer les fonds."""
        payment_intent_id = f"pi_{uuid.uuid4().hex[:16]}"
        return {
            "payment_intent_id": payment_intent_id,
            "client_secret": f"{payment_intent_id}_secret_{uuid.uuid4().hex[:8]}",
            "amount": amount,
            "status": "requires_payment_method"
        }

    @staticmethod
    async def simulate_webhook_payment_success(payment_intent_id: str) -> dict:
        """Simule la réception du Webhook confirmant que les fonds sont sécurisés."""
        return {
            "payment_intent_id": payment_intent_id,
            "status": "succeeded" # Équivalent de FUNDS_SECURED
        }

    @staticmethod
    async def release_funds(payment_intent_id: str, seller_id: str) -> dict:
        """Simule le déblocage des fonds vers le vendeur après validation OCR."""
        return {
            "status": "transferred",
            "payout_id": f"po_{uuid.uuid4().hex[:16]}"
        }

payment_service = PaymentService()
