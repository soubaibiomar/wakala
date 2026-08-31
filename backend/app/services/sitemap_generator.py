from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.vehicle import Vehicle
from app.models.catalog import BrandCatalog, ModelCatalog
from datetime import datetime, timezone

async def generate_sitemap_xml(db: AsyncSession) -> str:
    """
    Génère le contenu XML du sitemap pour les véhicules, marques, villes et grappes SEO/GEO de Wakala.
    """
    base_url = "https://wakala.ma"
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = []

    # 1. Routes piliers et guides SEO/GEO majeurs
    static_routes = [
        ("/", "daily", "1.0"),
        ("/guide-achat-voiture-maroc", "daily", "1.0"),
        ("/catalogue", "daily", "0.95"),
        ("/financement-auto-maroc", "weekly", "0.9"),
        ("/comparateur", "weekly", "0.9"),
        ("/marque", "weekly", "0.85"),
        ("/dedouanement", "monthly", "0.8"),
        ("/chat", "weekly", "0.75"),
        ("/score-de-confiance", "monthly", "0.7"),
        ("/technologie", "monthly", "0.7"),
    ]
    for route, freq, prio in static_routes:
        urls.append(f"""  <url>
    <loc>{base_url}{route}</loc>
    <lastmod>{now_str}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>""")

    # 2. Grappe "Par ville" (/voitures-neuves/{ville})
    moroccan_cities = [
        "casablanca", "rabat", "marrakech", "tanger", "agadir",
        "fes", "meknes", "oujda", "kenitra", "tetouan",
        "temara", "mohammedia", "el-jadida", "nador", "beni-mellal"
    ]
    for city in moroccan_cities:
        urls.append(f"""  <url>
    <loc>{base_url}/voitures-neuves/{city}</loc>
    <lastmod>{now_str}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>""")

    # 3. Grappe "Comparatifs" populaires
    popular_comparisons = [
        "dacia-duster-vs-renault-captur",
        "dacia-sandero-streetway-vs-renault-clio",
        "hyundai-tucson-vs-kia-sportage",
        "peugeot-208-vs-renault-clio",
        "volkswagen-t-roc-vs-hyundai-tucson",
        "toyota-yaris-vs-renault-clio",
    ]
    for comp in popular_comparisons:
        urls.append(f"""  <url>
    <loc>{base_url}/comparer/{comp}</loc>
    <lastmod>{now_str}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.85</priority>
  </url>""")

    # 4. Grappe "Par marque" (/marque/{brand_slug})
    res_brands = await db.execute(select(BrandCatalog).where(BrandCatalog.is_active.is_(True)))
    brands = res_brands.scalars().all()
    for b in brands:
        urls.append(f"""  <url>
    <loc>{base_url}/marque/{b.slug}</loc>
    <lastmod>{now_str}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.85</priority>
  </url>""")

    # 5. Fiches Modèles Neufs (/neuf/{model_slug})
    res_models = await db.execute(select(ModelCatalog))
    models = res_models.scalars().all()
    for m in models:
        urls.append(f"""  <url>
    <loc>{base_url}/neuf/{m.slug}</loc>
    <lastmod>{now_str}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    # 6. Véhicules individuels
    res_vehicles = await db.execute(select(Vehicle).where(Vehicle.status == "available"))
    vehicles = res_vehicles.scalars().all()
    for v in vehicles:
        url = f"{base_url}/vehicule/{v.id}"
        lastmod = v.updated_at.strftime("%Y-%m-%d") if v.updated_at else now_str
        urls.append(f"""  <url>
    <loc>{url}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.75</priority>
  </url>""")

    urls_xml = "\n".join(urls)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_xml}
</urlset>"""
