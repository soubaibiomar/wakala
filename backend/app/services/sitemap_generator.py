from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.vehicle import Vehicle
from datetime import datetime

async def generate_sitemap_xml(db: AsyncSession) -> str:
    """
    Génère le contenu XML du sitemap pour les véhicules de Wakala.
    """
    # Fetch all active vehicles to build their URLs
    result = await db.execute(select(Vehicle).where(Vehicle.is_active == True))
    vehicles = result.scalars().all()

    base_url = "https://wakala.ma/voitures-occasion"
    
    urls = []
    # Static routes
    urls.append(f"""  <url>
    <loc>https://wakala.ma/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")
    urls.append(f"""  <url>
    <loc>{base_url}</loc>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>""")

    # Dynamic routes for vehicles
    for v in vehicles:
        # Example dynamic URL: /voitures-occasion/casablanca/dacia-logan-2019-95000dh
        city_slug = (v.location or "maroc").lower().replace(" ", "-")
        brand_slug = (v.make or "marque").lower().replace(" ", "-")
        model_slug = (v.model or "modele").lower().replace(" ", "-")
        year = v.year or 2000
        price = v.price or 0
        
        # Build slug
        slug = f"{brand_slug}-{model_slug}-{year}-{price}dh"
        url = f"{base_url}/{city_slug}/{slug}"
        
        lastmod = v.updated_at.strftime("%Y-%m-%d") if v.updated_at else datetime.now().strftime("%Y-%m-%d")

        urls.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    urls_xml = "\n".join(urls)
    
    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_xml}
</urlset>"""

    return sitemap
