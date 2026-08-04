from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.sitemap_generator import generate_sitemap_xml

router = APIRouter(tags=["SEO"])

@router.get("/sitemap.xml", response_class=Response)
async def get_sitemap(db: AsyncSession = Depends(get_db)):
    """
    Génère et retourne le sitemap XML dynamiquement.
    """
    sitemap_xml = await generate_sitemap_xml(db)
    return Response(content=sitemap_xml, media_type="application/xml")
