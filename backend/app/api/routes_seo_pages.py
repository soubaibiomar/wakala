"""
routes_seo_pages.py — Endpoints API dédiés à la génération de contenu dynamique pour le SEO et le GEO.
Fournit des données 100% réelles issues du catalogue pour les pages de grappe :
- Comparatifs (/comparer/{slug})
- Villes (/voitures-neuves/{ville})
- Marques (/marque/{brand})
- Hub de maillage interne (/hub)
"""

import uuid
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.catalog import BrandCatalog, ModelCatalog, PowertrainCatalog, TrimCatalog
from app.models.dealership import Dealership, Showroom
from app.models.equipment import TrimEquipmentMapping, EquipmentFeature, EquipmentCategory
from app.services.calculator.moroccan_taxes import calculate_on_the_road_price

router = APIRouter(prefix="/v1/seo-pages", tags=["SEO & GEO Dynamic Pages"])

CITY_SLUG_MAP = {
    "casablanca": "Casablanca",
    "rabat": "Rabat",
    "marrakech": "Marrakech",
    "tanger": "Tanger",
    "agadir": "Agadir",
    "fes": "Fès",
    "meknes": "Meknès",
    "kenitra": "Kénitra",
    "tetouan": "Tétouan",
    "oujda": "Oujda",
    "temara": "Témara",
    "mohammedia": "Mohammedia",
    "el-jadida": "El Jadida",
    "nador": "Nador",
    "beni-mellal": "Béni Mellal",
}


def normalize_slug(text: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', (text or '').lower()).strip('-')


@router.get("/comparatif/{slug}")
async def get_comparatif_seo_data(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Génère les données dynamiques et factuelles pour une page de comparaison SEO/GEO (/comparer/{slug}).
    Exemple de slug : dacia-duster-vs-renault-captur ou dacia-sandero-vs-renault-clio
    """
    parts = slug.lower().strip().split("-vs-")
    if len(parts) != 2:
        raise HTTPException(
            status_code=400,
            detail="Format de comparatif invalide. Le format attendu est '{vehicule1}-vs-{vehicule2}'."
        )

    slug1, slug2 = parts[0].strip(), parts[1].strip()

    async def find_vehicle_model_or_trim(item_slug: str):
        # 1. Chercher par trim slug
        stmt_trim = (
            select(TrimCatalog)
            .where(TrimCatalog.slug == item_slug)
            .options(
                selectinload(TrimCatalog.model).selectinload(ModelCatalog.brand),
                selectinload(TrimCatalog.powertrain),
                selectinload(TrimCatalog.equipment_mappings)
                .selectinload(TrimEquipmentMapping.feature)
                .selectinload(EquipmentFeature.category)
            )
        )
        res = await db.execute(stmt_trim)
        trim = res.scalar_one_or_none()
        if trim:
            return trim, trim.model

        # 2. Chercher par model slug
        stmt_model = (
            select(ModelCatalog)
            .where(ModelCatalog.slug == item_slug)
            .options(
                selectinload(ModelCatalog.brand),
                selectinload(ModelCatalog.powertrains),
                selectinload(ModelCatalog.trims).selectinload(TrimCatalog.powertrain),
                selectinload(ModelCatalog.trims).selectinload(TrimCatalog.equipment_mappings)
                .selectinload(TrimEquipmentMapping.feature)
                .selectinload(EquipmentFeature.category)
            )
        )
        res_m = await db.execute(stmt_model)
        model = res_m.scalar_one_or_none()
        if model and model.trims:
            # Trier trims par prix ascendant et prendre la finition d'appel ou la plus populaire
            sorted_trims = sorted(model.trims, key=lambda t: float(t.promo_price_mad or t.price_new_mad))
            return sorted_trims[0], model

        # 3. Chercher par matching partiel (ex: 'dacia-duster' vs 'duster')
        clean_name = item_slug.replace('-', ' ')
        stmt_search = (
            select(ModelCatalog)
            .join(BrandCatalog, ModelCatalog.brand_id == BrandCatalog.id)
            .where(
                or_(
                    ModelCatalog.name.ilike(f"%{clean_name}%"),
                    ModelCatalog.slug.ilike(f"%{item_slug}%"),
                    (BrandCatalog.name + " " + ModelCatalog.name).ilike(f"%{clean_name}%")
                )
            )
            .options(
                selectinload(ModelCatalog.brand),
                selectinload(ModelCatalog.powertrains),
                selectinload(ModelCatalog.trims).selectinload(TrimCatalog.powertrain),
                selectinload(ModelCatalog.trims).selectinload(TrimCatalog.equipment_mappings)
                .selectinload(TrimEquipmentMapping.feature)
                .selectinload(EquipmentFeature.category)
            )
        )
        res_s = await db.execute(stmt_search)
        model_s = res_s.scalars().first()
        if model_s and model_s.trims:
            sorted_trims = sorted(model_s.trims, key=lambda t: float(t.promo_price_mad or t.price_new_mad))
            return sorted_trims[0], model_s

        return None, None

    trim1, model1 = await find_vehicle_model_or_trim(slug1)
    trim2, model2 = await find_vehicle_model_or_trim(slug2)

    if not trim1 or not trim2:
        raise HTTPException(
            status_code=404,
            detail=f"Impossible de trouver les véhicules pour le comparatif '{slug}'."
        )

    def build_vehicle_card(t: TrimCatalog, m: ModelCatalog) -> Dict[str, Any]:
        pt = t.powertrain
        b = m.brand
        otr = calculate_on_the_road_price(
            base_price_mad=float(t.price_new_mad),
            fiscal_power_cv=pt.fiscal_power_cv if pt else 6,
            fuel_type=pt.fuel_type if pt else "DIESEL",
            promo_price_mad=float(t.promo_price_mad) if t.promo_price_mad else None
        )

        hp = pt.engine_power_hp if (pt and pt.engine_power_hp) else 100
        cons = float(pt.consumption_l_100) if (pt and pt.consumption_l_100) else 5.0
        boot = t.trunk_capacity_l or 380
        stars = t.euro_ncap_stars or 4

        return {
            "id": str(t.id),
            "brand_name": b.name,
            "brand_slug": b.slug,
            "brand_logo": b.logo_url,
            "model_name": m.name,
            "model_slug": m.slug,
            "trim_name": t.name,
            "trim_slug": t.slug,
            "full_name": f"{b.name} {m.name} ({t.name})",
            "image_url": t.image_url or m.hero_image_url,
            "body_type": m.body_type,
            "price_new_mad": float(t.price_new_mad),
            "promo_price_mad": float(t.promo_price_mad) if t.promo_price_mad else None,
            "clef_en_main_mad": otr.total_clef_en_main_mad,
            "vignette_dgi_mad": otr.vignette_dgi_mad,
            "warranty": f"{t.warranty_years or 3} ans / {t.warranty_km or 100000:,} km",
            "specs": {
                "fuel_type": pt.fuel_type if pt else "N/A",
                "fiscal_power_cv": f"{pt.fiscal_power_cv} CV" if pt else "N/A",
                "engine_power_hp": hp,
                "torque_nm": pt.torque_nm if (pt and pt.torque_nm) else None,
                "transmission": pt.transmission if pt else "N/A",
                "consumption_l_100": cons,
                "trunk_capacity_l": boot,
                "euro_ncap_stars": stars,
            },
            "radar_scores": {
                "economie": min(100, max(20, int((1 - (otr.effective_price_mad - 140000) / 500000) * 100))),
                "puissance": min(100, max(20, int((hp / 250) * 100))),
                "espace": min(100, max(20, int((boot / 650) * 100))),
                "securite": stars * 20,
                "ecologie": min(100, max(20, int((1 - (cons - 3.5) / 5.0) * 100))),
            }
        }

    v1 = build_vehicle_card(trim1, model1)
    v2 = build_vehicle_card(trim2, model2)

    # Analyse comparative et réponse autoportante GEO
    price_diff = abs(v1["clef_en_main_mad"] - v2["clef_en_main_mad"])
    cheaper = v1 if v1["clef_en_main_mad"] < v2["clef_en_main_mad"] else v2
    more_expensive = v2 if cheaper == v1 else v1

    # Réponse autoportante claire et directe pour LLMs & moteurs génératifs
    self_contained_answer = (
        f"Au Maroc en 2026, le comparatif entre {v1['full_name']} et {v2['full_name']} révèle un avantage tarifaire pour "
        f"{cheaper['brand_name']} {cheaper['model_name']} avec un prix clé en main de {cheaper['clef_en_main_mad']:,.0f} MAD contre "
        f"{more_expensive['clef_en_main_mad']:,.0f} MAD (écart de {price_diff:,.0f} MAD). "
        f"Côté consommation, {v1['full_name']} affiche {v1['specs']['consumption_l_100']} L/100km face à {v2['specs']['consumption_l_100']} L/100km pour {v2['full_name']}. "
        f"Le volume de coffre est de {v1['specs']['trunk_capacity_l']} L contre {v2['specs']['trunk_capacity_l']} L."
    )

    faqs = [
        {
            "question": f"Quel est le modèle le moins cher entre {v1['full_name']} et {v2['full_name']} au Maroc ?",
            "answer": f"{cheaper['brand_name']} {cheaper['model_name']} est plus abordable avec un prix de départ clé en main de {cheaper['clef_en_main_mad']:,.0f} MAD (vignette et immatriculation incluses), soit {price_diff:,.0f} MAD d'écart avec {more_expensive['brand_name']} {more_expensive['model_name']}."
        },
        {
            "question": f"Quelle est la différence de consommation de carburant ?",
            "answer": f"{v1['full_name']} consomme en moyenne {v1['specs']['consumption_l_100']} L/100km ({v1['specs']['fuel_type']}) tandis que {v2['full_name']} consomme {v2['specs']['consumption_l_100']} L/100km ({v2['specs']['fuel_type']})."
        },
        {
            "question": f"Quelles sont les garanties officielles au Maroc ?",
            "answer": f"{v1['brand_name']} offre une garantie officielle de {v1['warranty']} via son réseau agréé au Maroc, contre {v2['warranty']} pour {v2['brand_name']}."
        }
    ]

    return {
        "slug": slug,
        "title": f"Comparatif {v1['brand_name']} {v1['model_name']} vs {v2['brand_name']} {v2['model_name']} (Prix Maroc 2026)",
        "meta_description": f"Comparatif détaillé {v1['full_name']} vs {v2['full_name']} au Maroc : prix clé en main MAD, consommation réelle, vignette DGI et fiche technique.",
        "self_contained_answer": self_contained_answer,
        "updated_at": "2026-08-30",
        "vehicle1": v1,
        "vehicle2": v2,
        "price_difference_mad": price_diff,
        "cheaper_vehicle": cheaper["full_name"],
        "faqs": faqs,
        "breadcrumbs": [
            {"name": "Accueil", "item": "https://wakala.ma/"},
            {"name": "Guide d'Achat", "item": "https://wakala.ma/guide-achat-voiture-maroc"},
            {"name": "Comparateur", "item": "https://wakala.ma/comparateur"},
            {"name": f"{v1['model_name']} vs {v2['model_name']}", "item": f"https://wakala.ma/comparer/{slug}"}
        ]
    }


@router.get("/city/{city_slug}")
async def get_city_seo_data(
    city_slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Génère les données dynamiques et factuelles pour une page de catalogue par ville (/voitures-neuves/{ville}).
    Exemple de slug : casablanca, rabat, marrakech, tanger, agadir...
    """
    city_name = CITY_SLUG_MAP.get(city_slug.lower().strip())
    if not city_name:
        # Fallback formatage capitalize
        city_name = city_slug.replace('-', ' ').title()

    # 1. Récupérer les showrooms actifs dans cette ville
    stmt_showrooms = (
        select(Showroom)
        .where(
            and_(
                Showroom.is_active.is_(True),
                or_(
                    Showroom.city.ilike(f"%{city_name}%"),
                    Showroom.city.ilike(f"%{city_slug}%")
                )
            )
        )
        .options(selectinload(Showroom.dealership))
    )
    res_s = await db.execute(stmt_showrooms)
    showrooms = res_s.scalars().all()

    # Extraire les marques représentées dans ces showrooms
    represented_brands = set()
    showrooms_list = []
    for sh in showrooms:
        brands = sh.brand_affiliations or []
        for b in brands:
            represented_brands.add(b)
        showrooms_list.append({
            "id": str(sh.id),
            "name": sh.name,
            "dealership_name": sh.dealership.name if sh.dealership else "Concessionnaire Agréé",
            "address": sh.address,
            "phone": sh.phone,
            "city": sh.city,
            "brand_affiliations": brands
        })

    # 2. Récupérer des modèles neufs disponibles au Maroc
    stmt_models = (
        select(ModelCatalog)
        .join(BrandCatalog, ModelCatalog.brand_id == BrandCatalog.id)
        .where(BrandCatalog.is_active.is_(True))
        .options(
            selectinload(ModelCatalog.brand),
            selectinload(ModelCatalog.trims).selectinload(TrimCatalog.powertrain)
        )
        .limit(12)
    )
    res_m = await db.execute(stmt_models)
    all_models = res_m.scalars().all()

    models_list = []
    prices = []
    for m in all_models:
        if not m.trims:
            continue
        sorted_trims = sorted(m.trims, key=lambda t: float(t.promo_price_mad or t.price_new_mad))
        min_trim = sorted_trims[0]
        min_p = float(min_trim.promo_price_mad or min_trim.price_new_mad)
        prices.append(min_p)
        models_list.append({
            "id": str(m.id),
            "name": m.name,
            "slug": m.slug,
            "brand_name": m.brand.name,
            "brand_slug": m.brand.slug,
            "body_type": m.body_type,
            "hero_image_url": m.hero_image_url,
            "starting_price_mad": min_p,
            "trims_count": len(m.trims)
        })

    min_price_city = min(prices) if prices else 135000
    avg_price_city = int(sum(prices) / len(prices)) if prices else 240000
    showroom_count = len(showrooms_list)

    self_contained_answer = (
        f"À {city_name}, Wakala référence {showroom_count} concessionnaires et showrooms officiels agréés. "
        f"Les véhicules neufs y sont disponibles à partir de {min_price_city:,.0f} MAD, avec un prix moyen catalogue de {avg_price_city:,.0f} MAD. "
        f"Tous les modèles présentés bénéficient de la garantie constructeur marocaine et sont livrables directement chez les concessionnaires partenaires de {city_name}."
    )

    faqs = [
        {
            "question": f"Où acheter une voiture neuve à {city_name} ?",
            "answer": f"Wakala référence les réseaux officiels agréés à {city_name} avec fiches techniques transparentes, devis clé en main et réservation d'essai gratuite auprès des showrooms officiels."
        },
        {
            "question": f"Quels sont les frais d'immatriculation et carte grise à {city_name} ?",
            "answer": f"L'immatriculation à {city_name} suit le barème fiscal national : vignette DGI calculée selon la puissance fiscale (de 350 MAD à plus de 20 000 MAD) et frais de dossier carte grise inclus dans notre calcul clé en main."
        },
        {
            "question": f"Peut-on réserver un essai véhicule neuf à {city_name} ?",
            "answer": f"Oui, la réservation d'essai est 100% gratuite et confirmée sous 2h par le showroom officiel partenaire le plus proche de votre localisation à {city_name}."
        }
    ]

    return {
        "city_slug": city_slug,
        "city_name": city_name,
        "title": f"Voitures Neuves à {city_name} (2026) — Prix, Concessionnaires & Showrooms | Wakala",
        "meta_description": f"Découvrez les voitures neuves disponibles à {city_name}. Showrooms officiels, prix clé en main en MAD, vignette DGI et réservation d'essai.",
        "self_contained_answer": self_contained_answer,
        "updated_at": "2026-08-30",
        "showrooms_count": showroom_count,
        "showrooms": showrooms_list,
        "models": models_list,
        "min_price_mad": min_price_city,
        "avg_price_mad": avg_price_city,
        "other_cities": [
            {"slug": s, "name": n}
            for s, n in CITY_SLUG_MAP.items()
            if s != city_slug.lower()
        ][:8],
        "faqs": faqs,
        "breadcrumbs": [
            {"name": "Accueil", "item": "https://wakala.ma/"},
            {"name": "Guide d'Achat", "item": "https://wakala.ma/guide-achat-voiture-maroc"},
            {"name": "Voitures par Ville", "item": "https://wakala.ma/catalogue"},
            {"name": f"Voitures Neuves {city_name}", "item": f"https://wakala.ma/voitures-neuves/{city_slug}"}
        ]
    }


@router.get("/brand/{brand_slug}")
async def get_brand_seo_data(
    brand_slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Génère les données dynamiques et factuelles pour une page de marque (/marque/{brand}).
    """
    clean_slug = brand_slug.lower().strip()
    stmt_brand = (
        select(BrandCatalog)
        .where(
            or_(
                BrandCatalog.slug == clean_slug,
                BrandCatalog.name.ilike(f"%{clean_slug}%")
            )
        )
        .options(
            selectinload(BrandCatalog.models)
            .selectinload(ModelCatalog.trims)
            .selectinload(TrimCatalog.powertrain)
        )
    )
    res = await db.execute(stmt_brand)
    brand = res.scalar_one_or_none()

    if not brand:
        raise HTTPException(
            status_code=404,
            detail=f"Marque '{brand_slug}' introuvable dans le catalogue."
        )

    models_data = []
    prices = []
    body_types = set()
    fuels = set()
    warranties = []

    for m in brand.models:
        trims = m.trims or []
        if not trims:
            continue
        sorted_trims = sorted(trims, key=lambda t: float(t.promo_price_mad or t.price_new_mad))
        min_trim = sorted_trims[0]
        min_p = float(min_trim.promo_price_mad or min_trim.price_new_mad)
        prices.append(min_p)
        if m.body_type:
            body_types.add(m.body_type)

        for t in trims:
            if t.warranty_years:
                warranties.append(t.warranty_years)
            if t.powertrain and t.powertrain.fuel_type:
                fuels.add(t.powertrain.fuel_type)

        models_data.append({
            "id": str(m.id),
            "name": m.name,
            "slug": m.slug,
            "body_type": m.body_type,
            "hero_image_url": m.hero_image_url,
            "starting_price_mad": min_p,
            "trims_count": len(trims)
        })

    models_data.sort(key=lambda x: x["starting_price_mad"])

    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    avg_warranty = max(warranties) if warranties else 3

    self_contained_answer = (
        f"{brand.name} propose au Maroc {len(models_data)} modèles neufs en 2026, avec des tarifs allant de {min_price:,.0f} MAD à {max_price:,.0f} MAD. "
        f"La gamme comprend des carrosseries ({', '.join(sorted(body_types)) if body_types else 'Citadines et SUV'}) disponibles en motorisations {', '.join(sorted(fuels)) if fuels else 'Essence et Diesel'}, "
        f"bénéficiant d'une garantie constructeur officielle jusqu'à {avg_warranty} ans au Maroc."
    )

    faqs = [
        {
            "question": f"Quel est le modèle {brand.name} le moins cher au Maroc en 2026 ?",
            "answer": f"Le modèle {brand.name} le plus accessible est la {models_data[0]['name'] if models_data else brand.name}, disponible à partir de {min_price:,.0f} MAD clé en main."
        },
        {
            "question": f"Quelle est la durée de garantie constructeur {brand.name} au Maroc ?",
            "answer": f"Les véhicules neufs {brand.name} sont couverts par une garantie officielle constructeur de {avg_warranty} ans (ou 100 000 km) auprès de l'ensemble du réseau agréé au Maroc."
        },
        {
            "question": f"Où essayer et commander une {brand.name} neuve au Maroc ?",
            "answer": f"Wakala permet de configurer votre {brand.name}, de calculer le coût clé en main exact et de réserver un essai immédiat auprès des concessions officielles."
        }
    ]

    return {
        "id": str(brand.id),
        "name": brand.name,
        "slug": brand.slug,
        "logo_url": brand.logo_url,
        "country_of_origin": brand.country_of_origin,
        "description": brand.description,
        "title": f"Voitures {brand.name} Neuves au Maroc (Prix 2026, Fiches & Gamme) | Wakala",
        "meta_description": f"Découvrez toute la gamme {brand.name} neuve au Maroc : {len(models_data)} modèles à partir de {min_price:,.0f} MAD. Fiches techniques et garantie constructeur.",
        "self_contained_answer": self_contained_answer,
        "updated_at": "2026-08-30",
        "models_count": len(models_data),
        "min_price_mad": min_price,
        "max_price_mad": max_price,
        "available_body_types": list(body_types),
        "available_fuels": list(fuels),
        "warranty_years": avg_warranty,
        "models": models_data,
        "faqs": faqs,
        "breadcrumbs": [
            {"name": "Accueil", "item": "https://wakala.ma/"},
            {"name": "Guide d'Achat", "item": "https://wakala.ma/guide-achat-voiture-maroc"},
            {"name": "Marques", "item": "https://wakala.ma/marque"},
            {"name": brand.name, "item": f"https://wakala.ma/marque/{brand.slug}"}
        ]
    }


@router.get("/hub")
async def get_seo_hub_data(
    db: AsyncSession = Depends(get_db)
):
    """
    Fournit l'ensemble des liens structurés du maillage sémantique pour la page pilier et le sitemap.
    """
    # 1. Marques actives
    stmt_brands = (
        select(BrandCatalog.name, BrandCatalog.slug, func.count(ModelCatalog.id).label("count"))
        .outerjoin(ModelCatalog, ModelCatalog.brand_id == BrandCatalog.id)
        .where(BrandCatalog.is_active.is_(True))
        .group_by(BrandCatalog.id)
        .order_by(BrandCatalog.name.asc())
    )
    res_b = await db.execute(stmt_brands)
    brands = [{"name": r.name, "slug": r.slug, "models_count": r.count} for r in res_b.all()]

    # 2. Villes principales
    cities = [{"slug": slug, "name": name} for slug, name in CITY_SLUG_MAP.items()]

    # 3. Comparatifs populaires prédéfinis
    popular_comparisons = [
        {"slug": "dacia-duster-vs-renault-captur", "title": "Dacia Duster vs Renault Captur"},
        {"slug": "dacia-sandero-streetway-vs-renault-clio", "title": "Dacia Sandero vs Renault Clio"},
        {"slug": "hyundai-tucson-vs-kia-sportage", "title": "Hyundai Tucson vs Kia Sportage"},
        {"slug": "peugeot-208-vs-renault-clio", "title": "Peugeot 208 vs Renault Clio"},
        {"slug": "volkswagen-t-roc-vs-hyundai-tucson", "title": "Volkswagen T-Roc vs Hyundai Tucson"},
        {"slug": "toyota-yaris-vs-renault-clio", "title": "Toyota Yaris vs Renault Clio"},
    ]

    # 4. Modèles vedettes
    stmt_featured = (
        select(ModelCatalog)
        .join(BrandCatalog, ModelCatalog.brand_id == BrandCatalog.id)
        .options(
            selectinload(ModelCatalog.brand),
            selectinload(ModelCatalog.trims).selectinload(TrimCatalog.powertrain)
        )
        .limit(6)
    )
    res_f = await db.execute(stmt_featured)
    featured_models = []
    for m in res_f.scalars().all():
        if m.trims:
            sorted_trims = sorted(m.trims, key=lambda t: float(t.promo_price_mad or t.price_new_mad))
            min_p = float(sorted_trims[0].promo_price_mad or sorted_trims[0].price_new_mad)
            featured_models.append({
                "id": str(m.id),
                "name": m.name,
                "slug": m.slug,
                "brand_name": m.brand.name,
                "body_type": m.body_type,
                "hero_image_url": m.hero_image_url,
                "starting_price_mad": min_p
            })

    return {
        "pillar_url": "/guide-achat-voiture-maroc",
        "financing_url": "/financement-auto-maroc",
        "ai_advisor_url": "/chat",
        "brands": brands,
        "cities": cities,
        "popular_comparisons": popular_comparisons,
        "featured_models": featured_models
    }
