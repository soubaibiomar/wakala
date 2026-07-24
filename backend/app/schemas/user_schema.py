"""
schemas/user_schema.py — Schémas Pydantic pour les utilisateurs.
Create ≠ Read ≠ Update : validation stricte et surface d'API contrôlée.
Validation marocaine : téléphone +212, CIN format XX-NNNNNN.
"""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

MOROCCAN_PHONE_RE = re.compile(r'^\+212[5-7]\d{8}$')
CIN_RE = re.compile(r'^[A-Za-z]{2}\d{5,6}$')


# ─── Création ──────────────────────────────────────────────────

class UserCreate(BaseModel):
    """Schéma de création d'un compte utilisateur."""
    full_name: str = Field(..., min_length=2, max_length=255, examples=["Jean Dupont"])
    email: EmailStr = Field(..., examples=["jean@example.ma"])
    phone: str = Field(..., max_length=30, examples=["+212612345678"])
    cin: Optional[str] = Field(None, min_length=7, max_length=8, examples=["AB123456"])
    password: str = Field(..., min_length=8, max_length=128, examples=["MonMotDePasse123!"])
    role: str = Field("buyer", pattern="^(buyer|seller)$", examples=["buyer"])

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not MOROCCAN_PHONE_RE.match(v):
            raise ValueError("Le téléphone doit être au format +2126XXXXXXXX ou +2125XXXXXXXX")
        return v

    @field_validator("cin")
    @classmethod
    def validate_cin(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not CIN_RE.match(v):
            raise ValueError("La CIN doit être au format XX999999 (2 lettres + 5-6 chiffres)")
        return v

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        return v


# ─── Lecture ───────────────────────────────────────────────────

class UserRead(BaseModel):
    """Schéma de lecture — renvoyé par l'API (jamais le hash)."""
    id: UUID
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    is_verified: bool
    preferences: dict = {}
    avatar_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserReadBrief(BaseModel):
    """Version allégée pour les listings/reviews (pas d'email)."""
    id: UUID
    full_name: str
    role: str
    is_verified: bool

    model_config = {"from_attributes": True}


# ─── Mise à jour ──────────────────────────────────────────────

class UserUpdate(BaseModel):
    """Schéma de mise à jour — tous les champs optionnels."""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=30)
    preferences: Optional[dict] = None
    avatar_url: Optional[str] = None


# ─── Auth ──────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Schéma de connexion."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Réponse de connexion avec JWT."""
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class OTPVerification(BaseModel):
    """Schéma de vérification OTP."""
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)


class ResendOTPRequest(BaseModel):
    """Schéma pour renvoyer un OTP."""
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    """Schéma pour demander une réinitialisation de mot de passe."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schéma pour réinitialiser le mot de passe après validation OTP."""
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not any(c.isdigit() for c in v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        return v
