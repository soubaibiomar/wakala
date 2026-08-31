#!/usr/bin/env python3
"""
seed_default_options.py — Génération d'options & accessoires configurables par véhicule.
========================================================================================

Génère un jeu d'options réalistes par catégorie de véhicule (SUV, Citadines, Électriques,
Berlines, etc.) et insère les options dans 'vehicle_options' et 'vehicle_colors'.

Applique strictement la règle de plausibilité :
- Aucune option individuelle ne peut dépasser 15% du prix de base du véhicule.
- Les options qui dépasseraient cette règle sont automatiquement flaguées/ajustées.
- 100% idempotent via UUIDv5 déterministes.

Usage :
    python -m data_pipeline.scripts.seed_default_options
    python -m data_pipeline.scripts.seed_default_options --dry-run
"""

import argparse
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Configuration du PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("WakalaOptionsSeeder")

WAKALA_OPTIONS_NAMESPACE = uuid.UUID("a9143890-4829-45d2-b05b-80dfa7b97e20")
MAX_OPTION_PRICE_RATIO = 0.15  # Règle : max 15% du prix du véhicule


# ═══════════════════════════════════════════════════════════════════════════
# MODÈLES DE PALETTES COULEURS ET D'OPTIONS PAR CATÉGORIE
# ═══════════════════════════════════════════════════════════════════════════

STANDARD_COLORS = [
    {"name": "Blanc Glacier", "hex": "#F2F4F7", "price": 0.0, "is_default": True},
    {"name": "Gris Artense Métallisé", "hex": "#5A6065", "price": 4500.0, "is_default": False},
    {"name": "Noir Nacré Perla Nera", "hex": "#14171A", "price": 5000.0, "is_default": False},
    {"name": "Bleu Océan Profond", "hex": "#1B3B6F", "price": 5500.0, "is_default": False},
    {"name": "Rouge Flamme Verni", "hex": "#8C1D24", "price": 6000.0, "is_default": False},
]

PREMIUM_COLORS = [
    {"name": "Blanc Pur Nacré", "hex": "#FAFAFA", "price": 0.0, "is_default": True},
    {"name": "Gris Daytona Mat", "hex": "#3E444A", "price": 9500.0, "is_default": False},
    {"name": "Noir Mythic Métallisé", "hex": "#0D0E11", "price": 8000.0, "is_default": False},
    {"name": "Bleu Navarre Intense", "hex": "#0F2B5C", "price": 9000.0, "is_default": False},
    {"name": "Vert Émeraude Métallisé", "hex": "#1C3B2B", "price": 10000.0, "is_default": False},
]


def generate_options_for_vehicle(vehicle: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    """
    Génère la liste des options et des couleurs pour un véhicule donné.
    Retourne (options_list, colors_list, warnings).
    """
    v_id = str(vehicle["id"])
    base_price = float(vehicle["price"])
    body_type = str(vehicle.get("body_type") or "").lower()
    fuel_type = str(vehicle.get("fuel_type") or "").lower()
    engine_type = str(vehicle.get("engine_type") or "").lower()
    brand = str(vehicle.get("brand") or "").lower()
    
    max_allowed_option_price = base_price * MAX_OPTION_PRICE_RATIO
    warnings = []

    # ─── 1. Couleurs ──────────────────────────────────────────────────────────
    is_luxury = base_price >= 500000 or brand in ["bentley", "porsche", "audi", "bmw", "mercedes-benz", "jaguar", "land rover", "maserati"]
    color_palette = PREMIUM_COLORS if is_luxury else STANDARD_COLORS
    
    colors_data = []
    for c in color_palette:
        price_delta = c["price"]
        # Vérification règle 15%
        if price_delta > max_allowed_option_price:
            price_delta = round(max_allowed_option_price * 0.5, 0)
            warnings.append(
                f"Véhicule {v_id} ({base_price} MAD) : Prix couleur '{c['name']}' ajusté à {price_delta} MAD (règle 15%)."
            )

        col_uuid = uuid.uuid5(WAKALA_OPTIONS_NAMESPACE, f"col::{v_id}::{c['name']}")
        colors_data.append({
            "id": str(col_uuid),
            "vehicle_id": v_id,
            "color_name": c["name"],
            "hex_code": c["hex"],
            "price_delta": price_delta if not c["is_default"] else 0.0,
            "is_default": c["is_default"],
        })

    # ─── 2. Options de base universelles ──────────────────────────────────────
    raw_options = []

    # Sellerie de série
    raw_options.append({
        "category": "sellerie",
        "name": "Sellerie Tissu Confort de série",
        "price_delta": 0.0,
        "is_default": True,
        "image_reference": "seat_fabric_standard.png",
    })

    # Sellerie Optionnelle (Cuir / Alcantara)
    leather_price = 8500.0 if not is_luxury else 18000.0
    raw_options.append({
        "category": "sellerie",
        "name": "Sellerie Cuir Premium & Sièges Chauffants",
        "price_delta": leather_price,
        "is_default": False,
        "image_reference": "seat_leather_premium.png",
    })

    # ─── 3. Options spécifiques par Catégorie ────────────────────────────────
    if body_type == "suv" or vehicle.get("is_4x4"):
        raw_options.extend([
            {
                "category": "accessoire",
                "name": "Barres latérales en aluminium brossé",
                "price_delta": 4500.0,
                "is_default": False,
                "image_reference": "acc_side_steps_alu.png",
            },
            {
                "category": "accessoire",
                "name": "Barres de toit transversales QuickFix",
                "price_delta": 2500.0,
                "is_default": False,
                "image_reference": "acc_roof_bars.png",
            },
            {
                "category": "accessoire",
                "name": "Attelage escamotable avec faisceau 13 broches",
                "price_delta": 6000.0,
                "is_default": False,
                "image_reference": "acc_tow_bar.png",
            },
            {
                "category": "accessoire",
                "name": "Sabots de protection bas de caisse & passages de roue",
                "price_delta": 3000.0,
                "is_default": False,
                "image_reference": "acc_skid_plates.png",
            },
            {
                "category": "jante",
                "name": "Jantes alliage 19'' diamantées bi-ton",
                "price_delta": 7500.0,
                "is_default": False,
                "image_reference": "rims_19_diamond.png",
            },
        ])

    elif body_type == "citadine":
        raw_options.extend([
            {
                "category": "jante",
                "name": "Jantes alliage 16'' diamantées Sport",
                "price_delta": 3500.0,
                "is_default": False,
                "image_reference": "rims_16_alloy.png",
            },
            {
                "category": "pack",
                "name": "Pack City : Caméra de recul + Radars AV/AR",
                "price_delta": 4000.0,
                "is_default": False,
                "image_reference": "pack_city_cam.png",
            },
            {
                "category": "accessoire",
                "name": "Vitres arrière et lunette surteintées anti-UV",
                "price_delta": 1800.0,
                "is_default": False,
                "image_reference": "acc_tinted_windows.png",
            },
        ])

    elif body_type in ["berline", "break", "coupe", "cabriolet"]:
        raw_options.extend([
            {
                "category": "pack",
                "name": "Pack Conduite Semi-Autonome (ACC + Maintien voie)",
                "price_delta": 8000.0,
                "is_default": False,
                "image_reference": "pack_drive_assist.png",
            },
            {
                "category": "pack",
                "name": "Affichage Tête Haute HUD couleur",
                "price_delta": 5500.0,
                "is_default": False,
                "image_reference": "pack_hud_display.png",
            },
            {
                "category": "pack",
                "name": "Système Audio Surround Hi-Fi Premium",
                "price_delta": 6500.0,
                "is_default": False,
                "image_reference": "pack_audio_hifi.png",
            },
            {
                "category": "jante",
                "name": "Jantes alliage 18'' Aero Design",
                "price_delta": 6000.0,
                "is_default": False,
                "image_reference": "rims_18_aero.png",
            },
        ])

    # ─── 4. Options Électriques / Hybrides Rechargeables ──────────────────────
    if fuel_type in ["electrique", "hybride_rechargeable"] or "electrique" in engine_type:
        raw_options.extend([
            {
                "category": "pack",
                "name": "Pack Recharge Rapide & Câble renforcé 22kW",
                "price_delta": 5500.0,
                "is_default": False,
                "image_reference": "pack_ev_charge_22kw.png",
            },
            {
                "category": "pack",
                "name": "Pompe à chaleur haute efficacité énergétique",
                "price_delta": 6000.0,
                "is_default": False,
                "image_reference": "pack_heat_pump.png",
            },
            {
                "category": "accessoire",
                "name": "Câble de recharge domestique Green'up sécurisé",
                "price_delta": 2000.0,
                "is_default": False,
                "image_reference": "acc_ev_cable_mode2.png",
            },
        ])

    # ─── 5. Application de la Règle de Plausibilité (<= 15% prix de base) ────
    options_data = []
    for opt in raw_options:
        price_delta = opt["price_delta"]
        if not opt["is_default"] and price_delta > max_allowed_option_price:
            # Plafonnement au seuil acceptable (ex: 12% du prix du véhicule)
            adjusted_price = round(base_price * 0.10, -2) # arrondi aux centaines
            warnings.append(
                f"Option '{opt['name']}' sur véhicule {v_id} ({base_price} MAD) "
                f"dépassait 15% ({price_delta} > {max_allowed_option_price:.0f} MAD). "
                f"Prix ajusté à {adjusted_price} MAD."
            )
            price_delta = adjusted_price

        opt_uuid = uuid.uuid5(WAKALA_OPTIONS_NAMESPACE, f"opt::{v_id}::{opt['category']}::{opt['name']}")
        options_data.append({
            "id": str(opt_uuid),
            "vehicle_id": v_id,
            "category": opt["category"],
            "name": opt["name"],
            "price_delta": price_delta,
            "is_default": opt["is_default"],
            "image_reference": opt["image_reference"],
        })

    return options_data, colors_data, warnings


def seed_options_for_all_vehicles(dry_run: bool = False) -> Dict[str, Any]:
    """Charge tous les véhicules existants et peuple leurs options et couleurs."""
    from data_pipeline.scripts.import_wakala_catalogue import get_db_url

    db_url = get_db_url()
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Récupération des véhicules
        res = session.execute(text("SELECT id, brand, model, version, price, body_type, fuel_type, engine_type, is_4x4 FROM vehicles;"))
        vehicles = [dict(row._mapping) for row in res.fetchall()]
        logger.info(f"{len(vehicles)} véhicules récupérés en base pour génération des options.")

        total_options = 0
        total_colors = 0
        all_warnings = []

        upsert_option_sql = text("""
            INSERT INTO vehicle_options (id, vehicle_id, category, name, price_delta, is_default, image_reference, created_at, updated_at)
            VALUES (:id, :vehicle_id, :category, :name, :price_delta, :is_default, :image_reference, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                price_delta = EXCLUDED.price_delta,
                is_default = EXCLUDED.is_default,
                image_reference = EXCLUDED.image_reference,
                updated_at = NOW();
        """)

        upsert_color_sql = text("""
            INSERT INTO vehicle_colors (id, vehicle_id, color_name, hex_code, price_delta, is_default, created_at, updated_at)
            VALUES (:id, :vehicle_id, :color_name, :hex_code, :price_delta, :is_default, NOW(), NOW())
            ON CONFLICT (id) DO UPDATE SET
                hex_code = EXCLUDED.hex_code,
                price_delta = EXCLUDED.price_delta,
                is_default = EXCLUDED.is_default,
                updated_at = NOW();
        """)

        for v in vehicles:
            opts, cols, warns = generate_options_for_vehicle(v)
            all_warnings.extend(warns)
            total_options += len(opts)
            total_colors += len(cols)

            if not dry_run:
                for opt in opts:
                    session.execute(upsert_option_sql, opt)
                for col in cols:
                    session.execute(upsert_color_sql, col)

        if not dry_run:
            session.commit()
            logger.info(f"✅ Seeding terminé : {total_options} options et {total_colors} couleurs enregistrées en BDD.")
        else:
            logger.info(f"[DRY-RUN] {total_options} options et {total_colors} couleurs calculées sans écriture.")

        return {
            "vehicles_count": len(vehicles),
            "total_options": total_options,
            "total_colors": total_colors,
            "warnings_count": len(all_warnings),
        }

    except Exception as e:
        session.rollback()
        logger.error(f"❌ Erreur lors du seeding des options : {e}")
        raise
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Générer les options & accessoires configurables par véhicule.")
    parser.add_argument("--dry-run", action="store_true", help="Calculer sans écrire en base de données")
    args = parser.parse_args()

    stats = seed_options_for_all_vehicles(dry_run=args.dry_run)
    print("\n" + "=" * 50)
    print("RÉSUMÉ DU SEEDING DES OPTIONS DU CONFIGURATEUR")
    print("=" * 50)
    print(f"Véhicules traités     : {stats['vehicles_count']}")
    print(f"Options générées      : {stats['total_options']}")
    print(f"Couleurs générées     : {stats['total_colors']}")
    print(f"Ajustements de prix   : {stats['warnings_count']}")
    print("=" * 50)


if __name__ == "__main__":
    main()
