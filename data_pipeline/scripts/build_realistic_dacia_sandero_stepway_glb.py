#!/usr/bin/env python3
"""
build_realistic_dacia_sandero_stepway_glb.py
=============================================
Générateur de modèle 3D carrosserie lisse, organique et haute fidélité pour Three.js.
Utilise des surfaces paramétriques courbes avec lissage de normales (smooth normals),
passages de roues sculptés, jantes détaillées, feux LED et finitions PBR.
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


def normalize(v):
    l = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    if l == 0: return (0.0, 1.0, 0.0)
    return (v[0]/l, v[1]/l, v[2]/l)

def add_vec(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def sub_vec(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def cross_vec(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    )

def create_smooth_loft_surface(cross_sections):
    """
    Crée une surface lissée le long de sections transversales.
    cross_sections: list of list of (x, y, z) points (toutes de même longueur M).
    Retourne (positions, normals, indices).
    """
    N = len(cross_sections)
    M = len(cross_sections[0])

    grid_points = cross_sections
    grid_normals = [[(0.0, 1.0, 0.0) for _ in range(M)] for _ in range(N)]

    # Calcul des normales de sommets lissées
    for i in range(N):
        for j in range(M):
            p = grid_points[i][j]
            # Tangente u (le long de la section)
            p_prev_u = grid_points[i][(j - 1) % M]
            p_next_u = grid_points[i][(j + 1) % M]
            tu = sub_vec(p_next_u, p_prev_u)

            # Tangente v (le long du profil longitudinal)
            p_prev_v = grid_points[max(0, i - 1)][j]
            p_next_v = grid_points[min(N - 1, i + 1)][j]
            tv = sub_vec(p_next_v, p_prev_v)

            n = normalize(cross_vec(tv, tu))
            grid_normals[i][j] = n

    positions, normals, indices = [], [], []
    for i in range(N):
        for j in range(M):
            positions.extend(grid_points[i][j])
            normals.extend(grid_normals[i][j])

    for i in range(N - 1):
        for j in range(M - 1):
            p00 = i * M + j
            p01 = i * M + (j + 1)
            p10 = (i + 1) * M + j
            p11 = (i + 1) * M + (j + 1)
            indices.extend([p00, p10, p01, p01, p10, p11])

    return positions, normals, indices


def generate_curved_body_mesh():
    """
    Génère la carrosserie aérodynamique galbée de la Dacia Sandero Stepway 2026.
    Échelle réelle : 4.09m long, 1.84m large, 1.58m haut.
    """
    # 24 profils longitudinaux le long de l'axe Z (de l'avant +2.05m à l'arrière -2.05m)
    # Chaque profil a 16 points courbes de gauche à droite
    z_stations = [
        2.05, 1.95, 1.80, 1.60, 1.35, 1.10, 0.85, 0.55, 0.25, 0.0,
        -0.25, -0.55, -0.85, -1.10, -1.35, -1.60, -1.80, -1.95, -2.05
    ]

    cross_sections = []
    for z in z_stations:
        # Interpolation des proportions selon la station Z
        # Caisse avant / capot / habitacle / hayon
        if z > 1.4: # Avant (calandre + phare + début capot)
            prog = (z - 1.4) / 0.65
            w = 0.82 - 0.08 * prog
            y_base = 0.32 + 0.04 * prog
            y_top = 0.74 - 0.12 * prog
            y_mid = 0.54
        elif z > 0.6: # Capot et base de pare-brise
            prog = (z - 0.6) / 0.8
            w = 0.88 - 0.06 * prog
            y_base = 0.28
            y_top = 0.88 - 0.14 * prog
            y_mid = 0.58
        elif z > -0.9: # Habitacle / Pavillon toit
            prog = (z - (-0.9)) / 1.5
            w = 0.90
            y_base = 0.26
            y_top = 1.42 - 0.04 * (1 - prog)
            y_mid = 0.68
        elif z > -1.7: # Descente de lunette arrière
            prog = (z - (-1.7)) / 0.8
            w = 0.88
            y_base = 0.28
            y_top = 0.95 + 0.45 * prog
            y_mid = 0.62
        else: # Hayon et pare-chocs arrière
            prog = (z - (-2.05)) / 0.35
            w = 0.84 - 0.06 * (1 - prog)
            y_base = 0.34
            y_top = 0.82 + 0.12 * prog
            y_mid = 0.56

        # 17 points de contour courbe transversal (de gauche -X à droite +X)
        pts = []
        M = 17
        for k in range(M):
            t = k / (M - 1) # de 0.0 à 1.0
            x = (t - 0.5) * 2.0 * w
            # Profil courbe en arche douce avec nervures
            arch = math.cos((t - 0.5) * math.pi)
            if y_top > 1.0: # Zone toit / habitacle
                y = y_base + (y_top - y_base) * math.pow(arch, 0.35)
            else: # Zone capot / coffre
                y = y_base + (y_top - y_base) * math.pow(arch, 0.55)
            
            # Nervure de capot Stepway
            if z > 0.7 and (0.35 < t < 0.42 or 0.58 < t < 0.65):
                y += 0.025

            pts.append((x, y, z))
        cross_sections.append(pts)

    return create_smooth_loft_surface(cross_sections)


def create_smooth_cylinder(radius, length, segments=32, cx=0.0, cy=0.0, cz=0.0, axis="x"):
    """Cylindre à normales lissées pour roues et pneus."""
    positions, normals, indices = [], [], []
    half_l = length / 2.0

    # Vertices latéraux avec normales radiales lissées
    for i in range(segments):
        a = 2 * math.pi * i / segments
        sin_a, cos_a = math.sin(a), math.cos(a)
        
        if axis == "x":
            p0 = (cx - half_l, cy + radius * sin_a, cz + radius * cos_a)
            p1 = (cx + half_l, cy + radius * sin_a, cz + radius * cos_a)
            n = (0.0, sin_a, cos_a)
        elif axis == "y":
            p0 = (cx + radius * cos_a, cy - half_l, cz + radius * sin_a)
            p1 = (cx + radius * cos_a, cy + half_l, cz + radius * sin_a)
            n = (cos_a, 0.0, sin_a)
        else:
            p0 = (cx + radius * cos_a, cy + radius * sin_a, cz - half_l)
            p1 = (cx + radius * cos_a, cy + radius * sin_a, cz + half_l)
            n = (cos_a, sin_a, 0.0)

        positions.extend([*p0, *p1])
        normals.extend([*n, *n])

    for i in range(segments):
        next_i = (i + 1) % segments
        p0 = i * 2
        p1 = i * 2 + 1
        p2 = next_i * 2 + 1
        p3 = next_i * 2
        indices.extend([p0, p1, p2, p0, p2, p3])

    # Disques d'extrémités
    for sign in [-1, 1]:
        cap_n = (sign, 0.0, 0.0) if axis == "x" else ((0.0, sign, 0.0) if axis == "y" else (0.0, 0.0, sign))
        center = (cx + sign * half_l, cy, cz) if axis == "x" else ((cx, cy + sign * half_l, cz) if axis == "y" else (cx, cy, cz + sign * half_l))
        base_idx = len(positions) // 3
        positions.extend(center)
        normals.extend(cap_n)

        for i in range(segments):
            a = 2 * math.pi * i / segments
            if axis == "x":
                pt = (cx + sign * half_l, cy + radius * math.sin(a), cz + radius * math.cos(a))
            elif axis == "y":
                pt = (cx + radius * math.cos(a), cy + sign * half_l, cz + radius * math.sin(a))
            else:
                pt = (cx + radius * math.cos(a), cy + radius * math.sin(a), cz + sign * half_l)
            positions.extend(pt)
            normals.extend(cap_n)

        for i in range(segments):
            next_i = (i + 1) % segments
            if sign > 0:
                indices.extend([base_idx, base_idx + 1 + i, base_idx + 1 + next_i])
            else:
                indices.extend([base_idx, base_idx + 1 + next_i, base_idx + 1 + i])

    return positions, normals, indices


def create_box_mesh(width, height, depth, cx=0.0, cy=0.0, cz=0.0):
    """Boîte simple."""
    w, h, d = width / 2.0, height / 2.0, depth / 2.0
    p = [
        (cx - w, cy - h, cz + d), (cx + w, cy - h, cz + d), (cx + w, cy + h, cz + d), (cx - w, cy + h, cz + d),
        (cx + w, cy - h, cz - d), (cx - w, cy - h, cz - d), (cx - w, cy + h, cz - d), (cx + w, cy + h, cz - d),
        (cx - w, cy + h, cz + d), (cx + w, cy + h, cz + d), (cx + w, cy + h, cz - d), (cx - w, cy + h, cz - d),
        (cx - w, cy - h, cz - d), (cx + w, cy - h, cz - d), (cx + w, cy - h, cz + d), (cx - w, cy - h, cz + d),
        (cx + w, cy - h, cz + d), (cx + w, cy - h, cz - d), (cx + w, cy + h, cz - d), (cx + w, cy + h, cz + d),
        (cx - w, cy - h, cz - d), (cx - w, cy - h, cz + d), (cx - w, cy + h, cz + d), (cx - w, cy + h, cz - d)
    ]
    n = [
        (0,0,1),(0,0,1),(0,0,1),(0,0,1),
        (0,0,-1),(0,0,-1),(0,0,-1),(0,0,-1),
        (0,1,0),(0,1,0),(0,1,0),(0,1,0),
        (0,-1,0),(0,-1,0),(0,-1,0),(0,-1,0),
        (1,0,0),(1,0,0),(1,0,0),(1,0,0),
        (-1,0,0),(-1,0,0),(-1,0,0),(-1,0,0)
    ]
    positions, normals, indices = [], [], []
    for i in range(6):
        b = i * 4
        for j in range(4):
            positions.extend(p[b+j])
            normals.extend(n[b+j])
        indices.extend([b, b+1, b+2, b, b+2, b+3])
    return positions, normals, indices


def merge_mesh_parts(part_list):
    pos, norm, ind = [], [], []
    offset = 0
    for p, n, i in part_list:
        pos.extend(p)
        norm.extend(n)
        ind.extend([idx + offset for idx in i])
        offset += len(p) // 3
    return pos, norm, ind


def build_full_3d_car_model():
    parts = {}

    # 1. Carrosserie galbée principale (Car_Body_Paint)
    body_p, body_n, body_i = generate_curved_body_mesh()
    parts["Car_Body"] = {
        "material_name": "Car_Body_Paint",
        "positions": body_p,
        "normals": body_n,
        "indices": body_i,
        "pbr": {
            "baseColorFactor": [0.31, 0.33, 0.26, 1.0], # Kaki Lichen officiel Dacia
            "metallicFactor": 0.85,
            "roughnessFactor": 0.22
        }
    }

    # 2. Vitrage teinté athermique (Car_Glass)
    w1 = create_box_mesh(1.48, 0.44, 0.82, cx=0.0, cy=1.12, cz=0.35)
    w2 = create_box_mesh(1.44, 0.42, 0.65, cx=0.0, cy=1.10, cz=-1.15)
    glass_p, glass_n, glass_i = merge_mesh_parts([w1, w2])
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

    # 3. Protections Plastiques Noires Stepway (Trim_Plastic_Black)
    # Élargisseurs d'ailes et bas de portes
    trim_fl = create_smooth_cylinder(0.42, 0.12, segments=24, cx=-0.88, cy=0.36, cz=1.30, axis="x")
    trim_fr = create_smooth_cylinder(0.42, 0.12, segments=24, cx=0.88, cy=0.36, cz=1.30, axis="x")
    trim_rl = create_smooth_cylinder(0.42, 0.12, segments=24, cx=-0.88, cy=0.36, cz=-1.30, axis="x")
    trim_rr = create_smooth_cylinder(0.42, 0.12, segments=24, cx=0.88, cy=0.36, cz=-1.30, axis="x")
    grille_mesh = create_box_mesh(1.20, 0.16, 0.10, cx=0.0, cy=0.64, cz=2.00)
    skirt_l = create_box_mesh(0.08, 0.14, 2.40, cx=-0.90, cy=0.28, cz=0.0)
    skirt_r = create_box_mesh(0.08, 0.14, 2.40, cx=0.90, cy=0.28, cz=0.0)

    trim_p, trim_n, trim_i = merge_mesh_parts([
        trim_fl, trim_fr, trim_rl, trim_rr, grille_mesh, skirt_l, skirt_r
    ])
    parts["Car_Trim_Plastic"] = {
        "material_name": "Trim_Plastic_Black",
        "positions": trim_p,
        "normals": trim_n,
        "indices": trim_i,
        "pbr": {
            "baseColorFactor": [0.12, 0.14, 0.16, 1.0],
            "metallicFactor": 0.10,
            "roughnessFactor": 0.78
        }
    }

    # 4. Sabots de protection gris Megalith & Calandre DC (Skid_Silver)
    skid_f = create_box_mesh(1.10, 0.16, 0.14, cx=0.0, cy=0.24, cz=2.02)
    skid_r = create_box_mesh(1.10, 0.16, 0.14, cx=0.0, cy=0.26, cz=-2.02)
    dc_l = create_box_mesh(0.08, 0.08, 0.04, cx=-0.06, cy=0.64, cz=2.06)
    dc_r = create_box_mesh(0.08, 0.08, 0.04, cx=0.06, cy=0.64, cz=2.06)
    mirror_l = create_box_mesh(0.24, 0.14, 0.16, cx=-0.98, cy=0.96, cz=0.65)
    mirror_r = create_box_mesh(0.24, 0.14, 0.16, cx=0.98, cy=0.96, cz=0.65)

    skid_p, skid_n, skid_i = merge_mesh_parts([skid_f, skid_r, dc_l, dc_r, mirror_l, mirror_r])
    parts["Car_Skid_Plates"] = {
        "material_name": "Skid_Silver",
        "positions": skid_p,
        "normals": skid_n,
        "indices": skid_i,
        "pbr": {
            "baseColorFactor": [0.82, 0.84, 0.88, 1.0],
            "metallicFactor": 0.90,
            "roughnessFactor": 0.25
        }
    }

    # 5. Phares LED avant en Y & Feux arrière (Headlights_LED & Taillights_LED)
    hl_l = create_box_mesh(0.38, 0.10, 0.06, cx=-0.65, cy=0.65, cz=1.98)
    hl_r = create_box_mesh(0.38, 0.10, 0.06, cx=0.65, cy=0.65, cz=1.98)
    front_l_p, front_l_n, front_l_i = merge_mesh_parts([hl_l, hl_r])
    parts["Car_Headlights"] = {
        "material_name": "Headlights_LED",
        "positions": front_l_p,
        "normals": front_l_n,
        "indices": front_l_i,
        "pbr": {
            "baseColorFactor": [0.98, 0.98, 1.0, 1.0],
            "metallicFactor": 0.20,
            "roughnessFactor": 0.10
        }
    }

    tl_l = create_box_mesh(0.32, 0.16, 0.06, cx=-0.68, cy=0.72, cz=-1.98)
    tl_r = create_box_mesh(0.32, 0.16, 0.06, cx=0.68, cy=0.72, cz=-1.98)
    rear_l_p, rear_l_n, rear_l_i = merge_mesh_parts([tl_l, tl_r])
    parts["Car_Taillights"] = {
        "material_name": "Taillights_LED",
        "positions": rear_l_p,
        "normals": rear_l_n,
        "indices": rear_l_i,
        "pbr": {
            "baseColorFactor": [0.90, 0.08, 0.12, 1.0],
            "metallicFactor": 0.30,
            "roughnessFactor": 0.15
        }
    }

    # 6. 4 Roues Complètes (Pneus lisses & Jantes diamantées)
    wheel_coords = [(-0.86, 0.34, 1.30), (0.86, 0.34, 1.30), (-0.86, 0.34, -1.30), (0.86, 0.34, -1.30)]
    tires_list, rims_list = [], []

    for cx, cy, cz in wheel_coords:
        sign = 1 if cx > 0 else -1
        # Pneu Michelin 205/60 R16
        t = create_smooth_cylinder(0.34, 0.24, segments=28, cx=cx, cy=cy, cz=cz, axis="x")
        tires_list.append(t)

        # Jante alliage Mahalia 16" diamantée
        r = create_smooth_cylinder(0.24, 0.08, segments=24, cx=cx + sign * 0.09, cy=cy, cz=cz, axis="x")
        rims_list.append(r)

        # 5 branches profilées
        for b in range(5):
            angle = 2 * math.pi * b / 5.0
            sp = create_box_mesh(0.04, 0.05, 0.18, cx=cx + sign * 0.11, cy=cy + 0.12 * math.sin(angle), cz=cz + 0.12 * math.cos(angle))
            rims_list.append(sp)

        # Moyeu central
        hub = create_smooth_cylinder(0.06, 0.04, segments=16, cx=cx + sign * 0.12, cy=cy, cz=cz, axis="x")
        rims_list.append(hub)

    tires_p, tires_n, tires_i = merge_mesh_parts(tires_list)
    parts["Car_Wheels"] = {
        "material_name": "Car_Tires_Mat",
        "positions": tires_p,
        "normals": tires_n,
        "indices": tires_i,
        "pbr": {
            "baseColorFactor": [0.10, 0.10, 0.12, 1.0],
            "metallicFactor": 0.05,
            "roughnessFactor": 0.85
        }
    }

    rims_p, rims_n, rims_i = merge_mesh_parts(rims_list)
    parts["Car_Rims"] = {
        "material_name": "Rims_Alloy",
        "positions": rims_p,
        "normals": rims_n,
        "indices": rims_i,
        "pbr": {
            "baseColorFactor": [0.90, 0.92, 0.95, 1.0],
            "metallicFactor": 0.92,
            "roughnessFactor": 0.15
        }
    }

    # 7. Barres de toit longitudinales modulables Stepway (Roof_Bars)
    r1 = create_box_mesh(0.06, 0.06, 2.20, cx=-0.64, cy=1.46, cz=-0.15)
    r2 = create_box_mesh(0.06, 0.06, 2.20, cx=0.64, cy=1.46, cz=-0.15)
    r_cross1 = create_box_mesh(1.30, 0.03, 0.08, cx=0.0, cy=1.50, cz=0.35)
    r_cross2 = create_box_mesh(1.30, 0.03, 0.08, cx=0.0, cy=1.50, cz=-0.75)
    roof_p, roof_n, roof_i = merge_mesh_parts([r1, r2, r_cross1, r_cross2])
    parts["Roof_Bars"] = {
        "material_name": "Roof_Bars_Mat",
        "positions": roof_p,
        "normals": roof_n,
        "indices": roof_i,
        "pbr": {
            "baseColorFactor": [0.80, 0.82, 0.86, 1.0],
            "metallicFactor": 0.88,
            "roughnessFactor": 0.25
        }
    }

    # 8. Marchepieds latéraux inox (Side_Steps)
    s1 = create_box_mesh(0.12, 0.04, 2.30, cx=-0.96, cy=0.22, cz=0.0)
    s2 = create_box_mesh(0.12, 0.04, 2.30, cx=0.96, cy=0.22, cz=0.0)
    side_p, side_n, side_i = merge_mesh_parts([s1, s2])
    parts["Side_Steps"] = {
        "material_name": "Side_Steps_Mat",
        "positions": side_p,
        "normals": side_n,
        "indices": side_i,
        "pbr": {
            "baseColorFactor": [0.85, 0.87, 0.90, 1.0],
            "metallicFactor": 0.92,
            "roughnessFactor": 0.20
        }
    }

    return parts


def encode_glb(parts):
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
                "mode": 4
            }]
        })

        nodes.append({
            "name": part_name,
            "mesh": mesh_idx
        })

    gltf_json = {
        "asset": {
            "version": "2.0",
            "generator": "Wakala 3D Curved Automotive Mesh Builder"
        },
        "scene": 0,
        "scenes": [{
            "name": "Dacia_Sandero_Stepway_2026",
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

    json_bytes = json.dumps(gltf_json, separators=(",", ":")).encode("utf-8")
    json_padding = (4 - (len(json_bytes) % 4)) % 4
    json_bytes += b" " * json_padding

    bin_padding = (4 - (len(binary_data) % 4)) % 4
    binary_data += b"\x00" * bin_padding

    header = struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(json_bytes) + 8 + len(binary_data))
    json_chunk_header = struct.pack("<II", len(json_bytes), 0x4E4F534A)
    bin_chunk_header = struct.pack("<II", len(binary_data), 0x004E4942)

    with open(GLB_PATH, "wb") as f:
        f.write(header)
        f.write(json_chunk_header)
        f.write(json_bytes)
        f.write(bin_chunk_header)
        f.write(binary_data)

    print(f"✅ Modèle GLB 3D généré avec succès : {GLB_PATH} ({len(binary_data)/1024:.1f} KB)")


if __name__ == "__main__":
    parts = build_full_3d_car_model()
    encode_glb(parts)
