import re
import secrets
import time
from typing import Dict, Tuple, Optional, Any


MOROCCAN_PHONE_REGEX = re.compile(r"^(?:\+212|0)([67]\d{8})$")

# In-memory store for OTPs and rate limits (can be backed by Redis in production)
_OTP_STORE: Dict[str, Dict[str, Any]] = {}
_RATE_LIMIT_STORE: Dict[str, list] = {}

OTP_EXPIRY_SECONDS = 300  # 5 minutes
MAX_REQUESTS_PER_WINDOW = 3
RATE_LIMIT_WINDOW_SECONDS = 900  # 15 minutes


def normalize_moroccan_phone(phone: str) -> Optional[str]:
    """
    Validates and normalizes Moroccan mobile numbers to international E.164 (+2126XXXXXXXX / +2127XXXXXXXX).
    """
    cleaned = re.sub(r"[\s\-\.\(\)]", "", phone.strip())
    match = MOROCCAN_PHONE_REGEX.match(cleaned)
    if not match:
        return None
    national_number = match.group(1)
    return f"+212{national_number}"


def check_rate_limit(phone: str) -> bool:
    """
    Sliding window rate-limiter to protect against SMS toll fraud and spam.
    Allows at most 3 OTP requests per 15 minutes.
    """
    now = time.time()
    history = _RATE_LIMIT_STORE.get(phone, [])
    # Remove timestamps older than window
    valid_history = [t for t in history if now - t < RATE_LIMIT_WINDOW_SECONDS]
    
    if len(valid_history) >= MAX_REQUESTS_PER_WINDOW:
        return False  # Rate limit exceeded
    
    valid_history.append(now)
    _RATE_LIMIT_STORE[phone] = valid_history
    return True


def generate_otp(phone: str) -> Tuple[bool, str, str]:
    """
    Generates a secure 6-digit numeric OTP with 5-minute expiration.
    Returns (success, otp_code_or_error, normalized_phone).
    """
    normalized = normalize_moroccan_phone(phone)
    if not normalized:
        return False, "Numéro de téléphone marocain invalide (doit commencer par 06/07 ou +212)", ""
    
    if not check_rate_limit(normalized):
        return False, "Limite de demandes d'OTP atteinte. Veuillez réessayer dans 15 minutes.", normalized
    
    # 6-digit cryptographically secure PIN
    otp_code = f"{secrets.randbelow(900000) + 100000}"
    _OTP_STORE[normalized] = {
        "code": otp_code,
        "expires_at": time.time() + OTP_EXPIRY_SECONDS,
        "attempts": 0
    }
    
    return True, otp_code, normalized


def verify_otp(phone: str, code: str) -> Tuple[bool, str]:
    """
    Verifies an OTP code for a normalized phone number.
    """
    normalized = normalize_moroccan_phone(phone)
    if not normalized:
        return False, "Numéro de téléphone marocain invalide"
    
    entry = _OTP_STORE.get(normalized)
    if not entry:
        return False, "Aucun code actif trouvé ou code expiré"
    
    if time.time() > entry["expires_at"]:
        _OTP_STORE.pop(normalized, None)
        return False, "Le code de vérification a expiré"
    
    entry["attempts"] += 1
    if entry["attempts"] > 5:
        _OTP_STORE.pop(normalized, None)
        return False, "Nombre maximal de tentatives dépassé. Veuillez demander un nouveau code."
    
    if entry["code"] != code.strip():
        return False, "Code de vérification incorrect"
    
    # Success: consume OTP
    _OTP_STORE.pop(normalized, None)
    return True, "Numéro vérifié avec succès"
