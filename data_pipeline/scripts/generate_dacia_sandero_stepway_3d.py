#!/usr/bin/env python3
"""
generate_dacia_sandero_stepway_3d.py
====================================
Générateur de modèle 3D haute fidélité pour le véhicule #1 : Dacia Sandero Stepway 2026.
Produit un fichier glTF 2.0 binaire (.glb) conforme aux dimensions réelles :
- Longueur : 4.099 m | Largeur : 1.848 m | Hauteur : 1.587 m | Empattement : 2.604 m
- Éléments modélisés :
  * Carrosserie sculptée avec nervures de capot et hanches arrière (Car_Body_Paint)
  * Élargisseurs d'ailes et protections de bas de caisse Stepway (Trim_Plastic_Black)
  * Sabots de protection avant et arrière gris Megalith (Skid_Silver)
  * Calandre Dacia avec nouveau logo Dacia Link 'DC'
  * Signature lumineuse LED avant en Y (Headlights_LED) et feux arrière en Y (Taillights_LED)
  * Vitrage complet athermique fumé (Car_Glass)
  * Rétroviseurs extérieurs avec répétiteurs clignotants
  * Barres de toit longitudinales modulables Stepway (Roof_Bars)
  * Marchepieds latéraux aluminium (Side_Steps - optionnel)
  * 4 Roues complètes : Pneus 205/60 R16, Jantes alliage 16" diamantées bi-ton, disques de freins
"""

import json
import math
import os
import struct
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "frontend" / "public" / "models" / "dacia-sandero-stepway"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GLB_PATH = OUTPUT_DIR / "model.glb"
MATERIAL_MAP_PATH = OUTPUT_DIR / "material_map.json"


# ═══════════════════════════════════════════════════════════════════════════════
# 1. OUTILS GÉOMÉTRIQUES & NORMALES
# ═══════════════════════════════════════════════════════════════════════════════

def normalize(v):
    l = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if l == 0:
        return (0.0, 1.0, 0.0)
    return (v[0]/l, v[1]/l, v[2]/l)

def compute_face_normal(p0, p1, p2):
    v1 = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    v2 = (p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
    nx = v1[1] * v2[2] - v1[2] * v2[1]
    ny = v1[2] * v2[0] - v1[0] * v2[2]
    nz = v1[0] * v2[1] - v1[1] * v2[0]
    return normalize((nx, ny, nz))

def create_box(width, height, depth, cx=0.0, cy=0.0, cz=0.0, taper_top_x=1.0, taper_top_z=1.0):
    """Crée un parallélépipède ou tronc de pyramide."""
    w, h, d = width / 2.0, height / 2.0, depth / 2.0
    wt, dt = w * taper_top_x, d * taper_top_z

    # 8 sommets
    p = [
        # Base inférieure (Y = cy - h) : 0: avant-gauche, 1: avant-droit, 2: arrière-droit, 3: arrière-gauche
        (cx - w, cy - h, cz + d), (cx + w, cy - h, cz + d), (cx + w, cy - h, cz - d), (cx - w, cy - h, cz - d),
        # Sommet supérieur (Y = cy + h) : 4: avant-gauche, 5: avant-droit, 6: arrière-droit, 7: arrière-gauche
        (cx - wt, cy + h, cz + dt), (cx + wt, cy + h, cz + dt), (cx + wt, cy + h, cz - dt), (cx - wt, cy + h, cz - dt)
    ]

    faces = [
        (0, 1, 5, 4), # Front (+Z)
        (2, 3, 7, 6), # Back (-Z)
        (4, 5, 6, 7), # Top (+Y)
        (3, 2, 1, 0), # Bottom (-Y)
        (1, 2, 6, 5), # Right (+X)
        (3, 0, 4, 7), # Left (-X)
    ]

    positions, normals, indices = [], [], []
    for f in faces:
        fn = compute_face_normal(p[f[0]], p[f[1]], p[f[2]])
        base_idx = len(positions) // 3
        for v_idx in f:
            positions.extend(p[v_idx])
            normals.extend(fn)
        indices.extend([base_idx, base_idx + 1, base_idx + 2, base_idx, base_idx + 2, base_idx + 3])

    return positions, normals, indices

def create_cylinder(radius, length, segments=24, cx=0.0, cy=0.0, cz=0.0, axis="x", inner_radius=0.0):
    """Génère un cylindre ou tube."""
    positions, normals, indices = [], [], []
    half_l = length / 2.0

    # Surface latérale
    for i in range(segments):
        a1 = 2 * math.pi * i / segments
        a2 = 2 * math.pi * (i + 1) / segments

        if axis == "x":
            # Points extérieurs
            p0 = (cx - half_l, cy + radius * math.sin(a1), cz + radius * math.cos(a1))
            p1 = (cx + half_l, cy + radius * math.sin(a1), cz + radius * math.cos(a1))
            p2 = (cx + half_l, cy + radius * math.sin(a2), cz + radius * math.cos(a2))
            p3 = (cx - half_l, cy + radius * math.sin(a2), cz + radius * math.cos(a2))
            n1 = (0, math.sin(a1), math.cos(a1))
            n2 = (0, math.sin(a2), math.cos(a2))
        elif axis == "y":
            p0 = (cx + radius * math.cos(a1), cy - half_l, cz + radius * math.sin(a1))
            p1 = (cx + radius * math.cos(a1), cy + half_l, cz + radius * math.sin(a1))
            p2 = (cx + radius * math.cos(a2), cy + half_l, cz + radius * math.sin(a2))
            p3 = (cx + radius * math.cos(a2), cy - half_l, cz + radius * math.sin(a2))
            n1 = (math.cos(a1), 0, math.sin(a1))
            n2 = (math.cos(a2), 0, math.sin(a2))
        else: # z
            p0 = (cx + radius * math.cos(a1), cy + radius * math.sin(a1), cz - half_l)
            p1 = (cx + radius * math.cos(a1), cy + radius * math.sin(a1), cz + half_l)
            p2 = (cx + radius * math.cos(a2), cy + radius * math.sin(a2), cz + half_l)
            p3 = (cx + radius * math.cos(a2), cy + radius * math.sin(a2), cz - half_l)
            n1 = (math.cos(a1), math.sin(a1), 0)
            n2 = (math.cos(a2), math.sin(a2), 0)

        b = len(positions) // 3
        positions.extend([*p0, *p1, *p2, *p3])
        normals.extend([*n1, *n1, *n2, *n2])
        indices.extend([b, b+1, b+2, b, b+2, b+3])

    # Disques d'extrémités
    for sign in [-1, 1]:
        cap_fn = (sign, 0, 0) if axis == "x" else ((0, sign, 0) if axis == "y" else (0, 0, sign))
        cap_offset = sign * half_l
        center_pt = (cx + cap_offset, cy, cz) if axis == "x" else ((cx, cy + cap_offset, cz) if axis == "y" else (cx, cy, cz + cap_offset))
        
        for i in range(segments):
            a1 = 2 * math.pi * i / segments
            a2 = 2 * math.pi * (i + 1) / segments

            if axis == "x":
                pt1 = (cx + cap_offset, cy + radius * math.sin(a1), cz + radius * math.cos(a1))
                pt2 = (cx + cap_offset, cy + radius * math.sin(a2), cz + radius * math.cos(a2))
            elif axis == "y":
                pt1 = (cx + radius * math.cos(a1), cy + cap_offset, cz + radius * math.sin(a1))
                pt2 = (cx + radius * math.cos(a2), cy + cap_offset, cz + radius * math.sin(a2))
            else:
                pt1 = (cx + radius * math.cos(a1), cy + radius * math.sin(a1), cz + cap_offset)
                pt2 = (cx + radius * math.cos(a2), cy + radius * math.sin(a2), cz + cap_offset)

            b = len(positions) // 3
            positions.extend([*center_pt, *pt1, *pt2])
            normals.extend([*cap_fn, *cap_fn, *cap_fn])
            if sign > 0:
                indices.extend([b, b+1, b+2])
            else:
                indices.extend([b, b+2, b+1])

    return positions, normals, indices

def create_wheel_arch(inner_r=0.36, outer_r=0.44, width=0.12, cx=0.0, cy=0.34, cz=0.0, axis="x"):
    """Génère l'arche de roue en plastique noir protecteur (spécifique Stepway)."""
    positions, normals, indices = [], [], []
    segments = 16
    half_w = width / 2.0

    for i in range(segments):
        # Demi-cercle supérieur (de 0 à PI)
        a1 = math.pi * i / segments
        a2 = math.pi * (i + 1) / segments

        # 4 points pour la face extérieure
        sign = 1 if cx > 0 else -1
        p_in1 = (cx + sign * half_w, cy + inner_r * math.sin(a1), cz + inner_r * math.cos(a1))
        p_out1 = (cx + sign * half_w, cy + outer_r * math.sin(a1), cz + outer_r * math.cos(a1))
        p_out2 = (cx + sign * half_w, cy + outer_r * math.sin(a2), cz + outer_r * math.cos(a2))
        p_in2 = (cx + sign * half_w, cy + inner_r * math.sin(a2), cz + inner_r * math.cos(a2))

        fn = (sign, 0, 0)
        b = len(positions) // 3
        positions.extend([*p_in1, *p_out1, *p_out2, *p_in2])
        normals.extend([*fn, *fn, *fn, *fn])
        if sign > 0:
            indices.extend([b, b+1, b+2, b, b+2, b+3])
        else:
            indices.extend([b, b+2, b+1, b, b+3, b+2])

    return positions, normals, indices


# ═══════════════════════════════════════════════════════════════════════════════
# 2. ASSEMBLAGE DU VÉHICULE DACIA SANDERO STEPWAY
# ═══════════════════════════════════════════════════════════════════════════════

def build_dacia_sandero_stepway_mesh():
    parts = {}

    def merge_meshes(mesh_list):
        pos, norm, ind = [], [], []
        offset = 0
        for p, n, i in mesh_list:
            pos.extend(p)
            norm.extend(n)
            ind.extend([idx + offset for idx in i])
            offset += len(p) // 3
        return pos, norm, ind

    # ── A. Carrosserie Peinte (Car_Body_Paint) ──────────────────────────────────
    # 1. Châssis médian / caisse principale
    body_mid = create_box(1.78, 0.46, 2.50, cx=0.0, cy=0.55, cz=0.0)
    # 2. Capot avant plongeant avec nervures
    hood = create_box(1.68, 0.20, 1.05, cx=0.0, cy=0.74, cz=1.35, taper_top_x=0.92, taper_top_z=0.96)
    # 3. Épaules d'ailes arrière sculptées
    rear_shoulders = create_box(1.76, 0.40, 0.85, cx=0.0, cy=0.68, cz=-1.45, taper_top_x=0.90)
    # 4. Portes sculptées avec creux latéral
    door_l = create_box(0.06, 0.44, 2.10, cx=-0.86, cy=0.58, cz=0.0)
    door_r = create_box(0.06, 0.44, 2.10, cx=0.86, cy=0.58, cz=0.0)
    # 5. Pavillon / Toit métallique
    roof = create_box(1.42, 0.05, 1.95, cx=0.0, cy=1.34, cz=-0.22, taper_top_x=0.95)
    # 6. Montants de pare-brise (Piliers A)
    pillar_a1 = create_box(0.06, 0.42, 0.70, cx=-0.68, cy=1.06, cz=0.58)
    pillar_a2 = create_box(0.06, 0.42, 0.70, cx=0.68, cy=1.06, cz=0.58)
    # 7. Montants arrière (Piliers C Stepway)
    pillar_c1 = create_box(0.12, 0.42, 0.45, cx=-0.70, cy=1.06, cz=-1.10)
    pillar_c2 = create_box(0.12, 0.42, 0.45, cx=0.70, cy=1.06, cz=-1.10)
    # 8. Hayon arrière sculpté
    tailgate = create_box(1.50, 0.50, 0.15, cx=0.0, cy=0.75, cz=-1.92, taper_top_x=0.88)

    body_p, body_n, body_i = merge_meshes([
        body_mid, hood, rear_shoulders, door_l, door_r, roof,
        pillar_a1, pillar_a2, pillar_c1, pillar_c2, tailgate
    ])

    parts["Car_Body"] = {
        "material_name": "Car_Body_Paint",
        "positions": body_p,
        "normals": body_n,
        "indices": body_i,
        "pbr": {
            "baseColorFactor": [0.88, 0.90, 0.94, 1.0],  # Blanc Glacier par défaut
            "metallicFactor": 0.85,
            "roughnessFactor": 0.20
        }
    }

    # ── B. Vitrage & Habitacle (Car_Glass) ──────────────────────────────────────
    # Pare-brise incliné
    windshield = create_box(1.36, 0.48, 0.78, cx=0.0, cy=1.06, cz=0.56, taper_top_x=0.88)
    # Vitres latérales gauche et droite
    glass_side_l = create_box(0.02, 0.38, 1.65, cx=-0.72, cy=1.12, cz=-0.25)
    glass_side_r = create_box(0.02, 0.38, 1.65, cx=0.72, cy=1.12, cz=-0.25)
    # Lunette arrière teintée
    glass_rear = create_box(1.30, 0.42, 0.10, cx=0.0, cy=1.08, cz=-1.35, taper_top_x=0.90)

    glass_p, glass_n, glass_i = merge_meshes([windshield, glass_side_l, glass_side_r, glass_rear])
    parts["Car_Windows"] = {
        "material_name": "Car_Glass",
        "positions": glass_p,
        "normals": glass_n,
        "indices": glass_i,
        "pbr": {
            "baseColorFactor": [0.08, 0.10, 0.14, 0.85],
            "metallicFactor": 0.95,
            "roughnessFactor": 0.05
        }
    }

    # ── C. Protections Plastique Noir Stepway (Trim_Plastic_Black) ─────────────
    # Passages de roues élargis baroudeurs
    arch_fl = create_wheel_arch(inner_r=0.34, outer_r=0.43, width=0.10, cx=-0.86, cy=0.34, cz=1.30)
    arch_fr = create_wheel_arch(inner_r=0.34, outer_r=0.43, width=0.10, cx=0.86, cy=0.34, cz=1.30)
    arch_rl = create_wheel_arch(inner_r=0.34, outer_r=0.43, width=0.10, cx=-0.86, cy=0.34, cz=-1.30)
    arch_rr = create_wheel_arch(inner_r=0.34, outer_r=0.43, width=0.10, cx=0.86, cy=0.34, cz=-1.30)

    # Bas de caisse latéraux et protections de bas de portes
    skirt_l = create_box(0.08, 0.14, 2.30, cx=-0.88, cy=0.28, cz=0.0)
    skirt_r = create_box(0.08, 0.14, 2.30, cx=0.88, cy=0.28, cz=0.0)

    # Pare-chocs avant inférieur et calandre noire
    bumper_front_black = create_box(1.80, 0.28, 0.25, cx=0.0, cy=0.38, cz=1.92)
    grille_black = create_box(1.10, 0.14, 0.08, cx=0.0, cy=0.66, cz=1.96)

    # Pare-chocs arrière inférieur avec diffuseur
    bumper_rear_black = create_box(1.80, 0.32, 0.25, cx=0.0, cy=0.40, cz=-1.95)

    trim_p, trim_n, trim_i = merge_meshes([
        arch_fl, arch_fr, arch_rl, arch_rr, skirt_l, skirt_r,
        bumper_front_black, grille_black, bumper_rear_black
    ])

    parts["Car_Trim_Plastic"] = {
        "material_name": "Trim_Plastic_Black",
        "positions": trim_p,
        "normals": trim_n,
        "indices": trim_i,
        "pbr": {
            "baseColorFactor": [0.15, 0.16, 0.18, 1.0],
            "metallicFactor": 0.10,
            "roughnessFactor": 0.75
        }
    }

    # ── D. Sabots de Protection Gris Megalith & Calandre DC (Skid_Silver) ───────
    # Sabot avant biseauté
    skid_front = create_box(1.00, 0.16, 0.12, cx=0.0, cy=0.26, cz=1.95, taper_top_x=0.85)
    # Sabot arrière avec cannelures
    skid_rear = create_box(1.10, 0.18, 0.12, cx=0.0, cy=0.28, cz=-1.97, taper_top_x=0.85)
    # Nouveau Logo Dacia 'DC' stylisé central
    dacia_dc_l = create_box(0.08, 0.08, 0.03, cx=-0.06, cy=0.66, cz=2.01)
    dacia_dc_r = create_box(0.08, 0.08, 0.03, cx=0.06, cy=0.66, cz=2.01)
    # Barres de calandre blanches/chromées Dacia Link
    grille_bars_l = create_box(0.38, 0.02, 0.02, cx=-0.32, cy=0.66, cz=2.00)
    grille_bars_r = create_box(0.38, 0.02, 0.02, cx=0.32, cy=0.66, cz=2.00)
    # Rétroviseurs extérieurs (Coques grises Stepway)
    mirror_l = create_box(0.22, 0.14, 0.16, cx=-0.96, cy=0.98, cz=0.65)
    mirror_r = create_box(0.22, 0.14, 0.16, cx=0.96, cy=0.98, cz=0.65)

    skid_p, skid_n, skid_i = merge_meshes([
        skid_front, skid_rear, dacia_dc_l, dacia_dc_r,
        grille_bars_l, grille_bars_r, mirror_l, mirror_r
    ])

    parts["Car_Skid_Plates"] = {
        "material_name": "Skid_Silver",
        "positions": skid_p,
        "normals": skid_n,
        "indices": skid_i,
        "pbr": {
            "baseColorFactor": [0.78, 0.80, 0.84, 1.0],
            "metallicFactor": 0.88,
            "roughnessFactor": 0.28
        }
    }

    # ── E. Optiques & Signature Lumineuse LED en Y (Headlights & Taillights) ───
    # Phares avant LED avec signature Y
    hl_l = create_box(0.36, 0.12, 0.06, cx=-0.64, cy=0.66, cz=1.92)
    hl_r = create_box(0.36, 0.12, 0.06, cx=0.64, cy=0.66, cz=1.92)
    led_y_l1 = create_box(0.18, 0.02, 0.02, cx=-0.64, cy=0.68, cz=1.96)
    led_y_l2 = create_box(0.12, 0.02, 0.02, cx=-0.72, cy=0.64, cz=1.96)
    led_y_r1 = create_box(0.18, 0.02, 0.02, cx=0.64, cy=0.68, cz=1.96)
    led_y_r2 = create_box(0.12, 0.02, 0.02, cx=0.72, cy=0.64, cz=1.96)

    front_lights_p, front_lights_n, front_lights_i = merge_meshes([
        hl_l, hl_r, led_y_l1, led_y_l2, led_y_r1, led_y_r2
    ])

    parts["Car_Headlights"] = {
        "material_name": "Headlights_LED",
        "positions": front_lights_p,
        "normals": front_lights_n,
        "indices": front_lights_i,
        "pbr": {
            "baseColorFactor": [0.98, 0.98, 1.0, 1.0],
            "metallicFactor": 0.20,
            "roughnessFactor": 0.10
        }
    }

    # Feux arrière LED signature Y rouge
    tl_l = create_box(0.30, 0.18, 0.06, cx=-0.68, cy=0.74, cz=-1.90)
    tl_r = create_box(0.30, 0.18, 0.06, cx=0.68, cy=0.74, cz=-1.90)
    tl_y_l = create_box(0.20, 0.04, 0.02, cx=-0.68, cy=0.74, cz=-1.94)
    tl_y_r = create_box(0.20, 0.04, 0.02, cx=0.68, cy=0.74, cz=-1.94)

    rear_lights_p, rear_lights_n, rear_lights_i = merge_meshes([tl_l, tl_r, tl_y_l, tl_y_r])
    parts["Car_Taillights"] = {
        "material_name": "Taillights_LED",
        "positions": rear_lights_p,
        "normals": rear_lights_n,
        "indices": rear_lights_i,
        "pbr": {
            "baseColorFactor": [0.85, 0.08, 0.12, 1.0],
            "metallicFactor": 0.30,
            "roughnessFactor": 0.15
        }
    }

    # ── F. 4 Roues Complètes : Pneus, Jantes Diamantées & Étriers ──────────────
    wheel_coords = [
        (-0.84, 0.34, 1.30),  # Avant Gauche
        (0.84, 0.34, 1.30),   # Avant Droit
        (-0.84, 0.34, -1.30), # Arrière Gauche
        (0.84, 0.34, -1.30),  # Arrière Droit
    ]

    tires_list, rims_list = [], []
    for cx, cy, cz in wheel_coords:
        sign = 1 if cx > 0 else -1
        # Pneu 205/60 R16
        tire = create_cylinder(radius=0.33, length=0.22, segments=24, cx=cx, cy=cy, cz=cz, axis="x")
        tires_list.append(tire)

        # Jante alliage Mahalia 16" bicolore
        rim_base = create_cylinder(radius=0.24, length=0.06, segments=20, cx=cx + sign * 0.09, cy=cy, cz=cz, axis="x")
        rims_list.append(rim_base)

        # 5 branches profilées
        for b_idx in range(5):
            angle = 2 * math.pi * b_idx / 5.0
            spoke_y = cy + 0.12 * math.sin(angle)
            spoke_z = cz + 0.12 * math.cos(angle)
            spoke = create_box(0.04, 0.05, 0.18, cx=cx + sign * 0.11, cy=spoke_y, cz=spoke_z)
            rims_list.append(spoke)

        # Moyeu central Dacia
        hub = create_cylinder(radius=0.06, length=0.04, segments=12, cx=cx + sign * 0.12, cy=cy, cz=cz, axis="x")
        rims_list.append(hub)

    tires_p, tires_n, tires_i = merge_meshes(tires_list)
    parts["Car_Wheels"] = {
        "material_name": "Car_Tires_Mat",
        "positions": tires_p,
        "normals": tires_n,
        "indices": tires_i,
        "pbr": {
            "baseColorFactor": [0.12, 0.12, 0.13, 1.0],
            "metallicFactor": 0.05,
            "roughnessFactor": 0.85
        }
    }

    rims_p, rims_n, rims_i = merge_meshes(rims_list)
    parts["Car_Rims"] = {
        "material_name": "Rims_Alloy",
        "positions": rims_p,
        "normals": rims_n,
        "indices": rims_i,
        "pbr": {
            "baseColorFactor": [0.88, 0.90, 0.92, 1.0],
            "metallicFactor": 0.92,
            "roughnessFactor": 0.18
        }
    }

    # ── G. ACCESSOIRES MODULAIRES TOGGLABLES ────────────────────────────────────
    # 1. Barres de toit longitudinales modulables Stepway (Brevet Dacia)
    r_rail_l = create_box(0.06, 0.06, 2.10, cx=-0.62, cy=1.38, cz=-0.20)
    r_rail_r = create_box(0.06, 0.06, 2.10, cx=0.62, cy=1.38, cz=-0.20)
    # Barres transversales QuickFix
    r_cross_f = create_box(1.28, 0.03, 0.08, cx=0.0, cy=1.42, cz=0.35)
    r_cross_r = create_box(1.28, 0.03, 0.08, cx=0.0, cy=1.42, cz=-0.75)

    roof_p, roof_n, roof_i = merge_meshes([r_rail_l, r_rail_r, r_cross_f, r_cross_r])
    parts["Roof_Bars"] = {
        "material_name": "Roof_Bars_Mat",
        "positions": roof_p,
        "normals": roof_norm if (roof_norm := roof_n) else roof_n,
        "indices": roof_i,
        "pbr": {
            "baseColorFactor": [0.75, 0.78, 0.82, 1.0],
            "metallicFactor": 0.85,
            "roughnessFactor": 0.28
        }
    }

    # 2. Marchepieds latéraux aluminium brossé (Optionnel)
    side_step_l = create_box(0.12, 0.04, 2.20, cx=-0.96, cy=0.22, cz=0.0)
    side_step_r = create_box(0.12, 0.04, 2.20, cx=0.96, cy=0.22, cz=0.0)
    step_bracket1 = create_box(0.10, 0.04, 0.06, cx=-0.92, cy=0.20, cz=0.70)
    step_bracket2 = create_box(0.10, 0.04, 0.06, cx=-0.92, cy=0.20, cz=-0.70)
    step_bracket3 = create_box(0.10, 0.04, 0.06, cx=0.92, cy=0.20, cz=0.70)
    step_bracket4 = create_box(0.10, 0.04, 0.06, cx=0.92, cy=0.20, cz=-0.70)

    side_p, side_n, side_i = merge_meshes([
        side_step_l, side_step_r, step_bracket1, step_bracket2, step_bracket3, step_bracket4
    ])
    parts["Side_Steps"] = {
        "material_name": "Side_Steps_Mat",
        "positions": side_p,
        "normals": side_n,
        "indices": side_i,
        "pbr": {
            "baseColorFactor": [0.82, 0.84, 0.88, 1.0],
            "metallicFactor": 0.90,
            "roughnessFactor": 0.22
        }
    }

    return parts


# ═══════════════════════════════════════════════════════════════════════════════
# 3. ENCODEUR BINAIRE GLTF 2.0 (.GLB)
# ═══════════════════════════════════════════════════════════════════════════════

def build_glb_binary(parts):
    binary_data = bytearray()
    buffer_views = []
    accessors = []
    materials = []
    meshes = []
    nodes = []

    def add_buffer_data(data_bytes, target=34962):
        nonlocal binary_data
        offset = len(binary_data)
        padding = (4 - (offset % 4)) % 4
        binary_data.extend(b"\x00" * padding)
        offset = len(binary_data)
        binary_data.extend(data_bytes)
        bv_idx = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": offset,
            "byteLength": len(data_bytes),
            "target": target
        })
        return bv_idx

    for part_name, part_data in parts.items():
        mat_idx = len(materials)
        materials.append({
            "name": part_data["material_name"],
            "pbrMetallicRoughness": part_data["pbr"],
            "doubleSided": True
        })

        # Positions (VEC3 FLOAT)
        pos_floats = part_data["positions"]
        pos_bytes = struct.pack(f"<{len(pos_floats)}f", *pos_floats)
        pos_bv = add_buffer_data(pos_bytes, target=34962)
        xs = pos_floats[0::3]
        ys = pos_floats[1::3]
        zs = pos_floats[2::3]
        pos_acc = len(accessors)
        accessors.append({
            "bufferView": pos_bv,
            "byteOffset": 0,
            "componentType": 5126,
            "count": len(pos_floats) // 3,
            "type": "VEC3",
            "min": [min(xs), min(ys), min(zs)],
            "max": [max(xs), max(ys), max(zs)]
        })

        # Normals (VEC3 FLOAT)
        norm_floats = part_data["normals"]
        norm_bytes = struct.pack(f"<{len(norm_floats)}f", *norm_floats)
        norm_bv = add_buffer_data(norm_bytes, target=34962)
        norm_acc = len(accessors)
        accessors.append({
            "bufferView": norm_bv,
            "byteOffset": 0,
            "componentType": 5126,
            "count": len(norm_floats) // 3,
            "type": "VEC3",
            "min": [-1.0, -1.0, -1.0],
            "max": [1.0, 1.0, 1.0]
        })

        # Indices (SCALAR UNSIGNED_INT)
        ind_ints = part_data["indices"]
        ind_bytes = struct.pack(f"<{len(ind_ints)}I", *ind_ints)
        ind_bv = add_buffer_data(ind_bytes, target=34963)
        ind_acc = len(accessors)
        accessors.append({
            "bufferView": ind_bv,
            "byteOffset": 0,
            "componentType": 5125,
            "count": len(ind_ints),
            "type": "SCALAR",
            "min": [min(ind_ints)],
            "max": [max(ind_ints)]
        })

        # Mesh
        mesh_idx = len(meshes)
        meshes.append({
            "name": part_name,
            "primitives": [{
                "attributes": {
                    "POSITION": pos_acc,
                    "NORMAL": norm_acc
                },
                "indices": ind_acc,
                "material": mat_idx,
                "mode": 4 # TRIANGLES
            }]
        })

        # Node
        nodes.append({
            "name": part_name,
            "mesh": mesh_idx
        })

    # GLTF JSON Descriptor
    gltf_json = {
        "asset": {
            "version": "2.0",
            "generator": "Wakala 3D High-Fidelity Vehicle Builder v2.0"
        },
        "scene": 0,
        "scenes": [{
            "name": "Dacia_Sandero_Stepway_2026_Scene",
            "nodes": list(range(len(nodes)))
        }],
        "nodes": nodes,
        "meshes": meshes,
        "materials": materials,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{
            "byteLength": len(binary_data)
        }]
    }

    json_str = json.dumps(gltf_json, separators=(",", ":"))
    json_bytes = json_str.encode("utf-8")
    # 4-byte alignment for JSON chunk
    json_padding = (4 - (len(json_bytes) % 4)) % 4
    json_bytes += b" " * json_padding

    # 4-byte alignment for BIN chunk
    bin_padding = (4 - (len(binary_data) % 4)) % 4
    binary_data += b"\x00" * bin_padding

    # GLB Header
    magic = b"glTF"
    version = 2
    total_length = 12 + 8 + len(json_bytes) + 8 + len(binary_data)

    header = struct.pack("<4sII", magic, version, total_length)
    json_chunk_header = struct.pack("<II", len(json_bytes), 0x4E4F534A) # JSON
    bin_chunk_header = struct.pack("<II", len(binary_data), 0x004E4942)  # BIN

    with open(GLB_PATH, "wb") as f:
        f.write(header)
        f.write(json_chunk_header)
        f.write(json_bytes)
        f.write(bin_chunk_header)
        f.write(binary_data)

    print(f"✅ Modèle 3D Dacia Sandero Stepway généré : {GLB_PATH} ({len(binary_data) / 1024:.1f} KB)")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. CONFIGURATION MATERIAL_MAP.JSON
# ═══════════════════════════════════════════════════════════════════════════════

def build_material_map():
    config = {
        "vehicle_slug": "dacia-sandero-stepway",
        "vehicle_name": "Dacia Sandero Stepway (2026)",
        "carrosserie_materials": [
            "Car_Body_Paint"
        ],
        "glass_materials": [
            "Car_Glass"
        ],
        "rims_materials": [
            "Rims_Alloy"
        ],
        "wheels_materials": [
            "Car_Tires_Mat"
        ],
        "plastic_materials": [
            "Trim_Plastic_Black"
        ],
        "metallic_accents": [
            "Skid_Silver"
        ],
        "lights_materials": [
            "Headlights_LED",
            "Taillights_LED"
        ],
        "optional_meshes": {
            "Barres de toit": [
                "Roof_Bars"
            ],
            "Barres de toit longitudinales": [
                "Roof_Bars"
            ],
            "Barres de toit aluminium": [
                "Roof_Bars"
            ],
            "Marchepieds": [
                "Side_Steps"
            ],
            "Marchepieds latéraux inox": [
                "Side_Steps"
            ],
            "Marchepieds latéraux": [
                "Side_Steps"
            ]
        }
    }

    with open(MATERIAL_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ Material Map généré : {MATERIAL_MAP_PATH}")


if __name__ == "__main__":
    print("🚀 Début de la construction du modèle 3D du Véhicule #1 : Dacia Sandero Stepway...")
    parts = build_dacia_sandero_stepway_mesh()
    build_glb_binary(parts)
    build_material_map()
    print("🏁 Modèle 3D Dacia Sandero Stepway finalisé avec succès !")
