import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.catalog import BrandCatalog, ModelCatalog, PowertrainCatalog, TrimCatalog
from app.models.equipment import EquipmentCategory, EquipmentFeature, TrimEquipmentMapping
from app.services.calculator.moroccan_taxes import calculate_on_the_road_price

router = APIRouter(prefix="/v1/new-cars", tags=["100% New Cars Digital Showroom"])


@router.get("/brands")
async def list_new_car_brands(
    db: AsyncSession = Depends(get_db)
):
    """
    Liste toutes les marques automobiles avec nombre de modèles neufs disponibles.
    """
    stmt = (
        select(
            BrandCatalog.id,
            BrandCatalog.name,
            BrandCatalog.slug,
            BrandCatalog.logo_url,
            BrandCatalog.country_of_origin,
            func.count(func.distinct(TrimCatalog.model_id)).label("models_count"),
            func.min(TrimCatalog.price_new_mad).label("min_price_mad")
        )
        .outerjoin(ModelCatalog, ModelCatalog.brand_id == BrandCatalog.id)
        .outerjoin(TrimCatalog, and_(TrimCatalog.model_id == ModelCatalog.id, TrimCatalog.is_available_in_morocco.is_(True)))
        .where(BrandCatalog.is_active.is_(True))
        .group_by(BrandCatalog.id)
        .order_by(BrandCatalog.name.asc())
    )
    res = await db.execute(stmt)
    rows = res.all()

    return [
        {
            "id": str(r.id),
            "name": r.name,
            "slug": r.slug,
            "logo_url": r.logo_url,
            "country_of_origin": r.country_of_origin,
            "models_count": r.models_count or 0,
            "min_price_mad": float(r.min_price_mad) if r.min_price_mad else None,
        }
        for r in rows
    ]


@router.get("/models")
async def list_new_car_models(
    brand_slug: Optional[str] = Query(None, description="Filtrer par marque (slug)"),
    body_type: Optional[str] = Query(None, description="Filtrer par carrosserie (SUV, Citadine, Berline...)"),
    fuel_type: Optional[str] = Query(None, description="DIESEL, ESSENCE, HYBRIDE, ELECTRIQUE"),
    transmission: Optional[str] = Query(None, description="MANUELLE, AUTOMATIQUE"),
    max_price: Optional[float] = Query(None, description="Budget max en MAD"),
    min_price: Optional[float] = Query(None, description="Budget min en MAD"),
    db: AsyncSession = Depends(get_db)
):
    """
    Catalogue des véhicules neufs avec prix d'appel 'À partir de XXX MAD' et fiches modèles.
    """
    stmt = (
        select(ModelCatalog)
        .join(BrandCatalog, BrandCatalog.id == ModelCatalog.brand_id)
        .where(BrandCatalog.is_active.is_(True))
        .options(
            selectinload(ModelCatalog.brand),
            selectinload(ModelCatalog.powertrains),
        selectinload(ModelCatalog.trims.and_(TrimCatalog.is_available_in_morocco.is_(True)))
        )
    )

    if brand_slug:
        stmt = stmt.where(BrandCatalog.slug == brand_slug.lower().strip())
    if body_type:
        stmt = stmt.where(ModelCatalog.body_type.ilike(f"%{body_type}%"))

    res = await db.execute(stmt)
    models = res.scalars().all()

    results = []
    for m in models:
        trims = m.trims or []
        if not trims:
            continue

        # Filter trims by criteria
        matching_trims = []
        for t in trims:
            pt = t.powertrain
            if fuel_type and pt and pt.fuel_type.upper() != fuel_type.upper():
                continue
            if transmission and pt and transmission.upper() not in pt.transmission.upper():
                continue
            price = t.promo_price_mad or t.price_new_mad
            if max_price and price > max_price:
                continue
            if min_price and price < min_price:
                continue
            matching_trims.append(t)

        if (fuel_type or transmission or max_price or min_price) and not matching_trims:
            continue

        valid_trims = matching_trims if (fuel_type or transmission or max_price or min_price) else trims
        prices = [float(t.promo_price_mad or t.price_new_mad) for t in valid_trims]
        min_p = min(prices) if prices else None
        max_p = max(prices) if prices else None
        has_promo = any(t.is_promo for t in valid_trims)

        # Fuels available
        fuels = list(set([t.powertrain.fuel_type for t in valid_trims if t.powertrain]))

        results.append({
            "id": str(m.id),
            "name": m.name,
            "slug": m.slug,
            "brand": {
                "id": str(m.brand.id),
                "name": m.brand.name,
                "slug": m.brand.slug,
                "logo_url": m.brand.logo_url
            },
            "body_type": m.body_type,
            "year_start": m.year_start,
            "hero_image_url": m.hero_image_url,
            "starting_price_mad": min_p,
            "max_price_mad": max_p,
            "has_promo": has_promo,
            "available_fuels": fuels,
            "trims_count": len(valid_trims),
        })

    # Sort by starting price asc
    results.sort(key=lambda x: x["starting_price_mad"] or 999999999)
    return results


@router.get("/models/{model_id_or_slug}")
async def get_model_detail(
    model_id_or_slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Fiche détaillée complète d'un modèle neuf avec toutes ses finitions et motorisations.
    """
    try:
        m_uuid = uuid.UUID(model_id_or_slug)
        cond = ModelCatalog.id == m_uuid
    except ValueError:
        cond = ModelCatalog.slug == model_id_or_slug.lower().strip()

    stmt = (
        select(ModelCatalog)
        .where(cond)
        .where(ModelCatalog.brand.has(BrandCatalog.is_active.is_(True)))
        .options(
            selectinload(ModelCatalog.brand),
            selectinload(ModelCatalog.powertrains),
            selectinload(ModelCatalog.trims.and_(TrimCatalog.is_available_in_morocco.is_(True))).selectinload(TrimCatalog.powertrain)
        )
    )
    res = await db.execute(stmt)
    model = res.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Modèle introuvable")

    trims_payload = []
    for t in model.trims:
        pt = t.powertrain
        otr_tax = calculate_on_the_road_price(
            base_price_mad=float(t.price_new_mad),
            fiscal_power_cv=pt.fiscal_power_cv if pt else 6,
            fuel_type=pt.fuel_type if pt else "DIESEL",
            promo_price_mad=float(t.promo_price_mad) if t.promo_price_mad else None
        )

        trims_payload.append({
            "id": str(t.id),
            "name": t.name,
            "slug": t.slug,
            "price_new_mad": float(t.price_new_mad),
            "promo_price_mad": float(t.promo_price_mad) if t.promo_price_mad else None,
            "is_promo": t.is_promo,
            "warranty_years": t.warranty_years,
            "warranty_km": t.warranty_km,
            "trunk_capacity_l": t.trunk_capacity_l,
            "euro_ncap_stars": t.euro_ncap_stars,
            "image_url": t.image_url or model.hero_image_url,
            "available_colors": t.available_colors or [],
            "powertrain": {
                "id": str(pt.id) if pt else None,
                "name": pt.name if pt else None,
                "fuel_type": pt.fuel_type if pt else None,
                "fiscal_power_cv": pt.fiscal_power_cv if pt else None,
                "engine_power_hp": pt.engine_power_hp if pt else None,
                "torque_nm": pt.torque_nm if pt else None,
                "transmission": pt.transmission if pt else None,
                "consumption_l_100": float(pt.consumption_l_100) if (pt and pt.consumption_l_100) else None,
                "co2_emissions_g_km": pt.co2_emissions_g_km if pt else None,
            } if pt else None,
            "on_the_road_breakdown": {
                "vignette_mad": otr_tax.vignette_dgi_mad,
                "immatriculation_mad": otr_tax.immatriculation_carte_grise_mad,
                "luxury_tax_mad": otr_tax.luxury_tax_mad,
                "frais_dossier_mad": otr_tax.frais_dossier_plaques_mad,
                "total_clef_en_main_mad": otr_tax.total_clef_en_main_mad,
            }
        })

    # Sort trims by price
    trims_payload.sort(key=lambda x: x["promo_price_mad"] or x["price_new_mad"])

    return {
        "id": str(model.id),
        "name": model.name,
        "slug": model.slug,
        "body_type": model.body_type,
        "year_start": model.year_start,
        "hero_image_url": model.hero_image_url,
        "brand": {
            "id": str(model.brand.id),
            "name": model.brand.name,
            "slug": model.brand.slug,
            "logo_url": model.brand.logo_url,
            "country_of_origin": model.brand.country_of_origin,
        },
        "starting_price_mad": trims_payload[0]["promo_price_mad"] or trims_payload[0]["price_new_mad"] if trims_payload else None,
        "trims": trims_payload
    }


@router.get("/trims/{trim_id_or_slug}")
async def get_trim_full_sheet(
    trim_id_or_slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Fiche technique et équipement intégrale d'une finition avec ventilation fiscale marocaine.
    """
    try:
        t_uuid = uuid.UUID(trim_id_or_slug)
        cond = TrimCatalog.id == t_uuid
    except ValueError:
        cond = TrimCatalog.slug == trim_id_or_slug.lower().strip()

    stmt = (
        select(TrimCatalog)
        .where(cond, TrimCatalog.is_available_in_morocco.is_(True))
        .options(
            selectinload(TrimCatalog.model).selectinload(ModelCatalog.brand),
            selectinload(TrimCatalog.powertrain),
            selectinload(TrimCatalog.equipment_mappings)
            .selectinload(TrimEquipmentMapping.feature)
            .selectinload(EquipmentFeature.category)
        )
    )
    res = await db.execute(stmt)
    trim = res.scalar_one_or_none()

    if not trim:
        raise HTTPException(status_code=404, detail="Finition introuvable")

    pt = trim.powertrain
    model = trim.model
    brand = model.brand

    otr = calculate_on_the_road_price(
        base_price_mad=float(trim.price_new_mad),
        fiscal_power_cv=pt.fiscal_power_cv if pt else 6,
        fuel_type=pt.fuel_type if pt else "DIESEL",
        promo_price_mad=float(trim.promo_price_mad) if trim.promo_price_mad else None,
    )

    # Group equipment by category
    categorized_equip: dict = {}
    for em in trim.equipment_mappings:
        feat = em.feature
        cat = feat.category
        c_name = cat.name if cat else "Autres"
        if c_name not in categorized_equip:
            categorized_equip[c_name] = {
                "category_name": c_name,
                "icon": cat.icon if cat else "check",
                "features": []
            }
        categorized_equip[c_name]["features"].append({
            "feature_id": str(feat.id),
            "name": feat.name,
            "description": feat.description,
            "status": em.status,  # SERIE, OPTION, NON_DISPO
            "option_price_mad": float(em.option_price_mad) if em.option_price_mad else 0.0
        })

    return {
        "id": str(trim.id),
        "name": trim.name,
        "slug": trim.slug,
        "price_new_mad": float(trim.price_new_mad),
        "promo_price_mad": float(trim.promo_price_mad) if trim.promo_price_mad else None,
        "is_promo": trim.is_promo,
        "warranty_years": trim.warranty_years,
        "warranty_km": trim.warranty_km,
        "trunk_capacity_l": trim.trunk_capacity_l,
        "euro_ncap_stars": trim.euro_ncap_stars,
        "image_url": trim.image_url or model.hero_image_url,
        "available_colors": trim.available_colors or [],
        "model": {
            "id": str(model.id),
            "name": model.name,
            "slug": model.slug,
            "body_type": model.body_type,
            "year_start": model.year_start,
        },
        "brand": {
            "id": str(brand.id),
            "name": brand.name,
            "slug": brand.slug,
            "logo_url": brand.logo_url,
            "country_of_origin": brand.country_of_origin,
        },
        "powertrain": {
            "id": str(pt.id) if pt else None,
            "name": pt.name if pt else None,
            "fuel_type": pt.fuel_type if pt else None,
            "fiscal_power_cv": pt.fiscal_power_cv if pt else None,
            "engine_power_hp": pt.engine_power_hp if pt else None,
            "torque_nm": pt.torque_nm if pt else None,
            "transmission": pt.transmission if pt else None,
            "drivetrain": pt.drivetrain if pt else "FWD",
            "consumption_l_100": float(pt.consumption_l_100) if (pt and pt.consumption_l_100) else None,
            "co2_emissions_g_km": pt.co2_emissions_g_km if pt else None,
        } if pt else None,
        "on_the_road_breakdown": {
            "base_price_mad": otr.base_price_mad,
            "promo_price_mad": otr.promo_price_mad,
            "effective_price_mad": otr.effective_price_mad,
            "vignette_dgi_mad": otr.vignette_dgi_mad,
            "immatriculation_carte_grise_mad": otr.immatriculation_carte_grise_mad,
            "luxury_tax_mad": otr.luxury_tax_mad,
            "frais_dossier_plaques_mad": otr.frais_dossier_plaques_mad,
            "total_taxes_and_fees_mad": otr.total_taxes_and_fees_mad,
            "total_clef_en_main_mad": otr.total_clef_en_main_mad,
            "is_hybrid_or_ev_exempt": otr.is_hybrid_or_ev_exempt,
            "luxury_tax_applied": otr.luxury_tax_applied,
        },
        "equipment_by_category": list(categorized_equip.values())
    }
