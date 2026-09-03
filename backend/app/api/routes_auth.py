"""
api/routes_auth.py — Authentification (inscription + connexion JWT).
"""

import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Request
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.auth import EmailVerification
from app.models.user import User
from app.schemas.user_schema import (
    LoginRequest,
    GoogleLoginRequest,
    OTPVerification,
    ResendOTPRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    TokenResponse,
    UserCreate,
    UserRead,
)
from app.core.security import get_current_user

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.services.mailer import send_otp_email
from app.core.limiter import limiter

router = APIRouter()

def generate_otp() -> str:
    """Génère un code OTP à 6 chiffres."""
    return ''.join(secrets.choice(string.digits) for _ in range(6))


# ──────────────────────────────────────────────────────────────
# POST /register — Inscription
# ──────────────────────────────────────────────────────────────

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Créer un compte utilisateur et envoyer OTP",
    description="Inscrit un nouvel acheteur ou vendeur et envoie un code OTP par email.",
)
@limiter.limit("3/15minutes")
async def register(
    request: Request,
    payload: UserCreate,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Vérifier l'unicité de l'email
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un compte avec cet email existe déjà",
        )

    # Créer l'utilisateur (is_verified = False par défaut)
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        is_verified=False,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Générer OTP et sauvegarder
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    verification = EmailVerification(
        user_id=user.id,
        otp_code=otp_code,
        expires_at=expires_at,
    )
    db.add(verification)
    await db.commit()

    # Déclencher l'envoi de l'e-mail en tâche de fond
    background_tasks.add_task(send_otp_email, user.email, otp_code)

    return {"message": "Utilisateur créé. Code OTP envoyé."}


# ──────────────────────────────────────────────────────────────
# POST /verify-email — Vérification OTP
# ──────────────────────────────────────────────────────────────

@router.post(
    "/verify-email",
    summary="Vérifier l'email via OTP",
    description="Valide le code OTP et active le compte.",
)
@limiter.limit("3/15minutes")
async def verify_email(
    request: Request,
    payload: OTPVerification,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Trouver l'utilisateur
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
    if user.is_verified:
        return {"message": "Compte déjà vérifié"}

    # Vérifier l'OTP
    stmt = select(EmailVerification).where(
        EmailVerification.user_id == user.id,
        EmailVerification.otp_code == payload.otp_code,
    )
    verification_result = await db.execute(stmt)
    verification = verification_result.scalar_one_or_none()

    if not verification:
        raise HTTPException(status_code=400, detail="Code OTP invalide")
        
    if verification.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Le code OTP a expiré")

    # Activer le compte
    user.is_verified = True
    
    # Supprimer l'OTP
    await db.execute(delete(EmailVerification).where(EmailVerification.user_id == user.id))
    
    # Commit transaction
    await db.commit()
    
    return {"message": "Email vérifié avec succès. Vous pouvez maintenant vous connecter."}


# ──────────────────────────────────────────────────────────────
# POST /resend-otp — Renvoyer un OTP
# ──────────────────────────────────────────────────────────────

@router.post(
    "/resend-otp",
    summary="Renvoyer un code OTP",
    description="Génère et envoie un nouveau code OTP si l'utilisateur n'est pas encore vérifié.",
)
@limiter.limit("3/15minutes")
async def resend_otp(
    request: Request,
    payload: ResendOTPRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user:
        return {"message": "Si l'email existe, un code a été envoyé."}

    if user.is_verified:
        return {"message": "Compte déjà vérifié."}

    # Supprimer les anciens OTP
    await db.execute(delete(EmailVerification).where(EmailVerification.user_id == user.id))

    # Générer OTP et sauvegarder
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    verification = EmailVerification(
        user_id=user.id,
        otp_code=otp_code,
        expires_at=expires_at,
    )
    db.add(verification)
    await db.commit()

    # Déclencher l'envoi de l'e-mail en tâche de fond
    background_tasks.add_task(send_otp_email, user.email, otp_code)

    return {"message": "Si l'email existe, un code a été envoyé."}


# ──────────────────────────────────────────────────────────────
# POST /forgot-password — Demander réinitialisation mot de passe
# ──────────────────────────────────────────────────────────────

@router.post(
    "/forgot-password",
    summary="Demander un code OTP pour réinitialiser le mot de passe",
)
@limiter.limit("3/15minutes")
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user:
        return {"message": "Si l'email existe, un code a été envoyé."}

    # Supprimer les anciens OTP
    await db.execute(delete(EmailVerification).where(EmailVerification.user_id == user.id))

    # Générer OTP et sauvegarder
    otp_code = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    verification = EmailVerification(
        user_id=user.id,
        otp_code=otp_code,
        expires_at=expires_at,
    )
    db.add(verification)
    await db.commit()

    # Déclencher l'envoi de l'e-mail
    background_tasks.add_task(send_otp_email, user.email, otp_code)

    return {"message": "Si l'email existe, un code a été envoyé."}


# ──────────────────────────────────────────────────────────────
# POST /reset-password — Réinitialiser le mot de passe
# ──────────────────────────────────────────────────────────────

@router.post(
    "/reset-password",
    summary="Réinitialiser le mot de passe via OTP",
)
@limiter.limit("3/15minutes")
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Requête invalide")

    # Vérifier l'OTP
    stmt = select(EmailVerification).where(
        EmailVerification.user_id == user.id,
        EmailVerification.otp_code == payload.otp_code,
    )
    verification_result = await db.execute(stmt)
    verification = verification_result.scalar_one_or_none()

    if not verification or verification.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Code OTP invalide ou expiré")

    # Mettre à jour le mot de passe
    user.hashed_password = hash_password(payload.new_password)
    
    # Valider l'email en même temps s'il n'était pas vérifié
    if not user.is_verified:
        user.is_verified = True

    # Supprimer l'OTP
    await db.execute(delete(EmailVerification).where(EmailVerification.user_id == user.id))
    
    await db.commit()
    
    return {"message": "Mot de passe réinitialisé avec succès."}


# ──────────────────────────────────────────────────────────────
# POST /change-password — Modifier le mot de passe (Connecté)
# ──────────────────────────────────────────────────────────────

@router.post(
    "/change-password",
    summary="Modifier le mot de passe du compte connecté",
    description="Permet à un utilisateur (admin, concessionnaire, acheteur) authentifié de changer son mot de passe.",
)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Vérifier l'ancien mot de passe
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe actuel est incorrect",
        )

    # Vérifier que la confirmation correspond
    if payload.new_password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La confirmation ne correspond pas au nouveau mot de passe",
        )

    # Vérifier que le nouveau mot de passe n'est pas identique à l'ancien
    if payload.current_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe doit être différent du mot de passe actuel",
        )

    # Mettre à jour et hasher le nouveau mot de passe
    current_user.hashed_password = hash_password(payload.new_password)
    await db.commit()

    return {
        "status": "success",
        "message": "Votre mot de passe a été mis à jour avec succès.",
    }



# ──────────────────────────────────────────────────────────────
# POST /login — Connexion (retourne un JWT)
# ──────────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Se connecter",
    description="Authentifie un utilisateur et retourne un access token JWT.",
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    payload: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Veuillez vérifier votre adresse email avant de vous connecter",
        )

    # Si remember_me est True, le token expire dans 30 jours, sinon la valeur par défaut (1h)
    expires_delta = timedelta(days=30) if getattr(payload, 'remember_me', False) else None
    token = create_access_token(data={"sub": str(user.id), "role": user.role}, expires_delta=expires_delta)

    return TokenResponse(
        access_token=token,
        user=UserRead.model_validate(user),
    )


# ──────────────────────────────────────────────────────────────
# POST /google-login — Connexion avec Google
# ──────────────────────────────────────────────────────────────

@router.post(
    "/google-login",
    response_model=TokenResponse,
    summary="Se connecter avec Google",
    description="Vérifie un token Google OAuth et authentifie l'utilisateur.",
)
async def google_login(
    payload: GoogleLoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        if not settings.GOOGLE_CLIENT_ID and settings.APP_ENV != "development":
            raise RuntimeError("Google OAuth client is not configured")
        idinfo = id_token.verify_oauth2_token(
            payload.token,
            google_requests.Request(),
            audience=settings.GOOGLE_CLIENT_ID or None,
        )
        
        email = idinfo.get("email")
        full_name = idinfo.get("name", "Utilisateur Google")
        avatar_url = idinfo.get("picture")

        if not email:
            raise ValueError("Email non fourni par Google")
    except (ValueError, RuntimeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Google invalide.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Chercher l'utilisateur par email
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user:
        # Créer l'utilisateur automatiquement
        user = User(
            full_name=full_name,
            email=email,
            avatar_url=avatar_url,
            # Mot de passe aléatoire car géré par Google
            hashed_password=hash_password(secrets.token_urlsafe(32)),
            role="buyer", # par défaut
            is_verified=True, # Google a déjà vérifié l'email
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Si remember_me est True, le token expire dans 30 jours, sinon la valeur par défaut (1h)
    expires_delta = timedelta(days=30) if getattr(payload, 'remember_me', False) else None
    token = create_access_token(data={"sub": str(user.id), "role": user.role}, expires_delta=expires_delta)

    return TokenResponse(
        access_token=token,
        user=UserRead.model_validate(user),
    )
