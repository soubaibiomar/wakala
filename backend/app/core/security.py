"""
core/security.py — Hashing de mots de passe + création/vérification JWT.

Fournit :
    - hash_password / verify_password   (bcrypt via passlib)
    - create_access_token / decode_token (JWT via python-jose)
    - get_current_user                  (dépendance FastAPI)
    - require_role                      (dépendance de rôle)
"""

from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
try:
    from jose import JWTError, jwt
except ImportError:
    try:
        import jwt  # type: ignore[no-redef]
        JWTError = jwt.PyJWTError  # type: ignore[assignment]
    except ImportError:
        jwt = None  # type: ignore[assignment]
        JWTError = Exception  # type: ignore[assignment]

try:
    import bcrypt
    from passlib.context import CryptContext
    import passlib.handlers.bcrypt
    passlib.handlers.bcrypt.detect_wrap_bug = lambda ident: False
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except ImportError:
    bcrypt = None
    class DummyCrypt:
        def hash(self, secret: str) -> str: return "hashed_" + secret
        def verify(self, secret: str, hash_val: str) -> bool: return hash_val == "hashed_" + secret
    pwd_context = DummyCrypt()

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash un mot de passe en clair."""
    return pwd_context.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    return pwd_context.verify(plain_password[:72], hashed_password)


# ─── JWT ───────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Crée un JWT signé contenant les claims fournis."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Décode et vérifie un JWT. Lève JWTError si invalide."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


# ─── Dépendance : utilisateur courant ─────────────────────────
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Dépendance FastAPI — Extrait l'utilisateur du JWT.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Import tardif pour éviter les imports circulaires
    from app.models.user import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user

async def get_current_user_optional(
    token: Annotated[Optional[str], Depends(oauth2_scheme_optional)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


# ─── Dépendance : vérification de rôle ────────────────────────
def require_role(*roles: str):
    """
    Factory de dépendance — Vérifie que l'utilisateur a le rôle requis.

    Usage :
        @router.post("/", dependencies=[Depends(require_role("seller"))])
    """
    async def role_checker(
        current_user=Depends(get_current_user),
    ):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rôle requis : {', '.join(roles)}. Votre rôle : {current_user.role}",
            )
        return current_user

    return role_checker
