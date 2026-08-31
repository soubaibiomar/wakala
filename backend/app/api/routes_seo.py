from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.sitemap_generator import generate_sitemap_xml

router = APIRouter(tags=["SEO"])

@router.get("/sitemap.xml", response_class=Response)
@router.get("/api/sitemap.xml", response_class=Response)
async def get_sitemap(db: AsyncSession = Depends(get_db)):
    """
    Génère et retourne le sitemap XML dynamiquement pour l'indexation SEO et GEO.
    """
    sitemap_xml = await generate_sitemap_xml(db)
    return Response(content=sitemap_xml, media_type="application/xml")


@router.get("/robots.txt", response_class=Response)
@router.get("/api/robots.txt", response_class=Response)
async def get_robots():
    """
    Retourne le fichier robots.txt autorisant expressément les crawlers SEO et les robots IA (GEO).
    """
    content = """# robots.txt — Wakala Marketplace Automobile Maroc (100% Véhicules Neufs)

User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

# GEO — Crawlers IA et Moteurs Génératifs autorisés pour indexation et citation
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: Bytespider
Allow: /

User-agent: CCBot
Allow: /

# Règles globales
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /dashboard/
Disallow: /api/v1/admin/
Disallow: /api/auth/

Sitemap: https://wakala.ma/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")
