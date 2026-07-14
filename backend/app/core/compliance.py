"""
core/compliance.py — Conformité CNDP (loi 09-08).
Vérifications RGPD-likes pour le marché marocain :
- Consentement utilisateur pour le traitement des données
- Droit à l'oubli (anonymisation des données personnelles)
- Notification en cas de violation de données
- Floutage obligatoire des plaques d'immatriculation
"""

import hashlib
import hmac
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class ConsentPurpose(str, Enum):
    MARKETING = "marketing"
    PROFILING = "profiling"
    DATA_SHARING = "data_sharing"
    GEOLOCATION = "geolocation"


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"


class CNDPCompliance:
    """Vérifications de conformité selon la loi 09-08 relative à la
    protection des personnes physiques à l'égard du traitement des
    données à caractère personnel."""

    REQUIRED_CONSENTS = [
        ConsentPurpose.MARKETING,
        ConsentPurpose.PROFILING,
        ConsentPurpose.DATA_SHARING,
    ]

    @staticmethod
    def check_consent(user_consents: Dict[str, bool]) -> ComplianceStatus:
        """Vérifie que tous les consentements obligatoires sont donnés."""
        missing = [
            p.value for p in CNDPCompliance.REQUIRED_CONSENTS
            if not user_consents.get(p.value, False)
        ]
        if missing:
            logger.warning(f"Consentements manquants : {missing}")
            return ComplianceStatus.NON_COMPLIANT
        return ComplianceStatus.COMPLIANT

    @staticmethod
    def anonymize_pii(email: str, phone: str) -> Dict[str, str]:
        """Anonymise les identifiants personnels (droit à l'oubli)."""
        salt = datetime.now(timezone.utc).isoformat()
        return {
            "email": hashlib.sha256(f"{email}::{salt}".encode()).hexdigest()[:16],
            "phone": hashlib.sha256(f"{phone}::{salt}".encode()).hexdigest()[:16],
        }

    @staticmethod
    def verify_data_breach_notification(
        breach_time: datetime,
        notification_time: datetime,
    ) -> ComplianceStatus:
        """Vérifie que la notification de violation a eu lieu dans
        les 72h (standard RGPD, adopté par la CNDP)."""
        delay_hours = (notification_time - breach_time).total_seconds() / 3600
        if delay_hours <= 72:
            return ComplianceStatus.COMPLIANT
        logger.error(f"Notification trop tardive : {delay_hours:.1f}h (max 72h)")
        return ComplianceStatus.NON_COMPLIANT

    @staticmethod
    def sign_consent_record(user_id: str, purpose: str, consent_given: bool, secret: str) -> str:
        """Signe un enregistrement de consentement (non-répudiation)."""
        message = f"{user_id}:{purpose}:{consent_given}"
        return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
