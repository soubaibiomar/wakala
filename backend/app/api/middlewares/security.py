import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injecte les headers de sécurité HTTP de niveau production.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # CSP simplifiée pour l'API (bloque presque tout HTML since it's an API)
        response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        return response

class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Enregistre les requêtes échouées (401/403) pour la détection des attaques.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        if response.status_code in [401, 403]:
            ip = get_remote_address(request)
            logger.warning(
                f"SECURITY AUDIT: Access Denied | IP: {ip} | Status: {response.status_code} | Path: {request.url.path}"
            )
        return response

def user_or_ip_key_func(request: Request) -> str:
    """
    Retourne l'ID de l'utilisateur si connecté, sinon l'adresse IP.
    Utilisé par le Rate Limiter de slowapi.
    """
    if hasattr(request.state, "user") and request.state.user:
        return str(request.state.user.id)
    return get_remote_address(request)
