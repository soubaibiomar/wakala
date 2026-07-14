"""
Tests unitaires pour la conformité CNDP (loi 09-08).
"""

import pytest
from datetime import datetime, timedelta, timezone

from app.core.compliance import (
    CNDPCompliance,
    ComplianceStatus,
    ConsentPurpose,
)


pytestmark = pytest.mark.unit


class TestCNDPCompliance:
    def test_full_consent_is_compliant(self):
        consents = {
            "marketing": True,
            "profiling": True,
            "data_sharing": True,
        }
        status = CNDPCompliance.check_consent(consents)
        assert status == ComplianceStatus.COMPLIANT

    def test_missing_consent_is_non_compliant(self):
        consents = {
            "marketing": True,
            "profiling": False,
        }
        status = CNDPCompliance.check_consent(consents)
        assert status == ComplianceStatus.NON_COMPLIANT

    def test_empty_consents_is_non_compliant(self):
        status = CNDPCompliance.check_consent({})
        assert status == ComplianceStatus.NON_COMPLIANT

    def test_anonymize_pii_returns_hashed_fields(self):
        result = CNDPCompliance.anonymize_pii("test@example.ma", "+212612345678")
        assert "email" in result
        assert "phone" in result
        assert result["email"] != "test@example.ma"
        assert result["phone"] != "+212612345678"
        assert len(result["email"]) == 16
        assert len(result["phone"]) == 16

    def test_breach_notification_within_72h_is_compliant(self):
        breach = datetime.now(timezone.utc) - timedelta(hours=48)
        notified = datetime.now(timezone.utc)
        status = CNDPCompliance.verify_data_breach_notification(breach, notified)
        assert status == ComplianceStatus.COMPLIANT

    def test_breach_notification_exceeding_72h_is_non_compliant(self):
        breach = datetime.now(timezone.utc) - timedelta(hours=96)
        notified = datetime.now(timezone.utc)
        status = CNDPCompliance.verify_data_breach_notification(breach, notified)
        assert status == ComplianceStatus.NON_COMPLIANT

    def test_consent_record_signature_is_deterministic(self):
        sig1 = CNDPCompliance.sign_consent_record("user-1", "marketing", True, "secret123")
        sig2 = CNDPCompliance.sign_consent_record("user-1", "marketing", True, "secret123")
        assert sig1 == sig2

    def test_consent_record_signature_differs_on_input(self):
        sig1 = CNDPCompliance.sign_consent_record("user-1", "marketing", True, "secret123")
        sig2 = CNDPCompliance.sign_consent_record("user-2", "marketing", True, "secret123")
        assert sig1 != sig2
