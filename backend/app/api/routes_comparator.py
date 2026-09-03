import uuid
from typing import List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.catalog import TrimCatalog, ModelCatalog, BrandCatalog, PowertrainCatalog
from app.models.equipment import TrimEquipmentMapping, EquipmentFeature, EquipmentCategory
from app.services.calculator.moroccan_taxes import calculate_on_the_road_price

router = APIRouter(prefix="/v1/comparator", tags=["Matrix Vehicle Comparator"])


class CompareRequest(BaseModel):
    trim_ids_or_slugs: List[str]


@router.post("/compare")
async def compare_vehicles_matrix(
    payload: CompareRequest = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare 2 à 4 finitions côte à côte avec matrice d'équipements normalisée et radar comparatif.
    """
    identifiers = payload.trim_ids_or_slugs
    if len(identifiers) < 2:
        raise HTTPException(status_code=400, detail="Veuillez sélectionner au moins 2 véhicules pour la comparaison.")
    if len(identifiers) > 4:
        raise HTTPException(status_code=400, detail="La comparaison est limitée à 4 véhicules maximum.")

    trims = []
    for item in identifiers:
        try:
            t_uuid = uuid.UUID(item)
            cond = TrimCatalog.id == t_uuid
        except ValueError:
            cond = TrimCatalog.slug == item.lower().strip()

        stmt = (
            select(TrimCatalog)
            .where(cond)
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
        
        # If not found by trim slug, fallback to check if it's a model slug and take its first trim
        if not trim:
            stmt_model = (
                select(TrimCatalog)
                .join(ModelCatalog, TrimCatalog.model_id == ModelCatalog.id)
                .where(ModelCatalog.slug == item.lower().strip())
                .options(
                    selectinload(TrimCatalog.model).selectinload(ModelCatalog.brand),
                    selectinload(TrimCatalog.powertrain),
                    selectinload(TrimCatalog.equipment_mappings)
                    .selectinload(TrimEquipmentMapping.feature)
                    .selectinload(EquipmentFeature.category)
                )
                .order_by(TrimCatalog.price_new_mad.asc())
            )
            res_m = await db.execute(stmt_model)
            trim = res_m.scalars().first()

        if trim:
            trims.append(trim)

    if len(trims) < 2:
        raise HTTPException(status_code=404, detail="Certains véhicules à comparer sont introuvables.")

    # Build Vehicle Summaries & Radar Metrics (normalized 0-100)
    vehicles_data = []
    for t in trims:
        pt = t.powertrain
        model = t.model
        brand = model.brand

        otr = calculate_on_the_road_price(
            base_price_mad=float(t.price_new_mad),
            fiscal_power_cv=pt.fiscal_power_cv if pt else 6,
            fuel_type=pt.fuel_type if pt else "DIESEL",
            promo_price_mad=float(t.promo_price_mad) if t.promo_price_mad else None
        )

        # Radar score heuristics (Economics, Power, Space, Safety, Eco)
        # Power score (e.g. 90-300hp)
        hp = pt.engine_power_hp if (pt and pt.engine_power_hp) else 100
        power_score = min(100, max(20, int((hp / 250) * 100)))

        # Eco / Fuel efficiency (lower L/100 -> higher score)
        cons = float(pt.consumption_l_100) if (pt and pt.consumption_l_100) else 5.0
        eco_score = min(100, max(20, int((1 - (cons - 3.5) / 5.0) * 100)))

        # Space / Boot capacity
        boot = t.trunk_capacity_l or 380
        space_score = min(100, max(20, int((boot / 650) * 100)))

        # Safety EuroNCAP
        stars = t.euro_ncap_stars or 4
        safety_score = stars * 20

        # Price / Budget competitiveness
        effective_p = otr.effective_price_mad
        budget_score = min(100, max(20, int((1 - (effective_p - 140000) / 500000) * 100)))

        # Extract official hyperlinks from descriptions & vehicle records
        import re
        dealer_url = None
        if brand.description:
            m_site = re.search(r'Site\s*:\s*(https?://[^\s|]+)', brand.description)
            if m_site: dealer_url = m_site.group(1).rstrip('.')

        model_url = None
        if model.description:
            m_fiche = re.search(r'Fiche officielle\s*:\s*(https?://[^\s|]+)', model.description)
            if m_fiche: model_url = m_fiche.group(1).rstrip('.')

        # Lookup vehicle & scores for NCAP and Conso source links
        from app.models.vehicle import Vehicle
        from app.models.vehicle_option import VehicleWakalaScore
        stmt_veh = (
            select(Vehicle)
            .where((Vehicle.brand == brand.name) & (Vehicle.model == model.name))
            .limit(1)
        )
        res_v = await db.execute(stmt_veh)
        veh_rec = res_v.scalars().first()

        trim_url = veh_rec.source_url if veh_rec else None
        ncap_report_url = None
        real_conso_url = None

        if veh_rec:
            stmt_sc = select(VehicleWakalaScore).where(VehicleWakalaScore.vehicle_id == veh_rec.id).limit(1)
            res_sc = await db.execute(stmt_sc)
            sc_rec = res_sc.scalars().first()
            if sc_rec and sc_rec.source_note:
                m_ncap = re.search(r'Rapport NCAP\s*:\s*(https?://[^\s|]+)', sc_rec.source_note)
                if m_ncap: ncap_report_url = m_ncap.group(1)
                m_conso = re.search(r'Conso réelle\s*:\s*(https?://[^\s|]+)', sc_rec.source_note)
                if m_conso: real_conso_url = m_conso.group(1)

        vehicles_data.append({
            "id": str(t.id),
            "name": f"{brand.name} {model.name} - {t.name}",
            "slug": t.slug,
            "image_url": t.image_url or model.hero_image_url,
            "brand_name": brand.name,
            "brand_logo": brand.logo_url,
            "brand_url": dealer_url,
            "model_name": model.name,
            "model_url": model_url,
            "trim_name": t.name,
            "trim_url": trim_url,
            "ncap_report_url": ncap_report_url,
            "real_conso_url": real_conso_url,
            "body_type": model.body_type,
            "price_new_mad": float(t.price_new_mad),
            "promo_price_mad": float(t.promo_price_mad) if t.promo_price_mad else None,
            "clef_en_main_mad": otr.total_clef_en_main_mad,
            "vignette_dgi_mad": otr.vignette_dgi_mad,
            "warranty": f"{t.warranty_years} ans / {t.warranty_km:,} km",
            "specs": {
                "fuel_type": pt.fuel_type if pt else "N/A",
                "fiscal_power_cv": f"{pt.fiscal_power_cv} CV" if pt else "N/A",
                "engine_power_hp": f"{pt.engine_power_hp} ch" if (pt and pt.engine_power_hp) else "N/A",
                "torque_nm": f"{pt.torque_nm} Nm" if (pt and pt.torque_nm) else "N/A",
                "transmission": pt.transmission if pt else "N/A",
                "consumption_l_100": f"{pt.consumption_l_100} L/100km" if (pt and pt.consumption_l_100) else "N/A",
                "trunk_capacity_l": f"{t.trunk_capacity_l} L" if t.trunk_capacity_l else "N/A",
                "euro_ncap_stars": f"{t.euro_ncap_stars} / 5" if t.euro_ncap_stars else "N/A",
            },
            "radar_scores": {
                "economie": budget_score,
                "puissance": power_score,
                "espace": space_score,
                "securite": safety_score,
                "ecologie": eco_score
            }
        })

    # Build Unified Equipment Comparison Matrix
    # 1. Collect all distinct features across all compared trims
    all_feature_ids = {}
    for t in trims:
        for em in t.equipment_mappings:
            feat = em.feature
            cat = feat.category
            f_id = str(feat.id)
            if f_id not in all_feature_ids:
                all_feature_ids[f_id] = {
                    "id": f_id,
                    "name": feat.name,
                    "category": cat.name if cat else "Autres",
                    "icon": cat.icon if cat else "check"
                }

    # Group matrix by category
    categories_matrix = {}
    for f_id, f_meta in all_feature_ids.items():
        cat_name = f_meta["category"]
        if cat_name not in categories_matrix:
            categories_matrix[cat_name] = {
                "category_name": cat_name,
                "icon": f_meta["icon"],
                "features": []
            }

        # Status for each vehicle
        veh_statuses = {}
        all_same = True
        first_status = None

        for t in trims:
            t_id = str(t.id)
            mapping = next((em for em in t.equipment_mappings if str(em.feature_id) == f_id), None)
            st = mapping.status if mapping else "NON_DISPO"
            opt_p = float(mapping.option_price_mad) if (mapping and mapping.option_price_mad) else 0.0
            
            veh_statuses[t_id] = {
                "status": st,  # SERIE, OPTION, NON_DISPO
                "option_price_mad": opt_p if st == "OPTION" else 0.0
            }

            if first_status is None:
                first_status = st
            elif first_status != st:
                all_same = False

        categories_matrix[cat_name]["features"].append({
            "feature_id": f_id,
            "feature_name": f_meta["name"],
            "has_difference": not all_same,
            "values_per_vehicle": veh_statuses
        })

    return {
        "vehicles": vehicles_data,
        "equipment_matrix": list(categories_matrix.values())
    }
