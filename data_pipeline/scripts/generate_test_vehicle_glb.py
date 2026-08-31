"""
generate_test_vehicle_glb.py — Générateur de modèle 3D .glb pour le premier véhicule test (Dacia Sandero Stepway).
Produit un fichier binaire glTF 2.0 (.glb) valide avec nœuds nommés et matériaux PBR distincts.
"""

import json
import math
import os
import struct
from pathlib import Path

# Création des répertoires cibles
TARGET_DIR = Path("d:/Projet automobile/vente-auto-platform/frontend/public/models/dacia-sandero-stepway")
TARGET_DIR.mkdir(parents=True, exist_ok=True)
GLB_PATH = TARGET_DIR / "model.glb"
MATERIAL_MAP_PATH = TARGET_DIR / "material_map.json"


def create_box_mesh(width, height, depth, center_x=0, center_y=0, center_z=0):
    """Génère les positions, normales et indices d'une boîte 3D."""
    w, h, d = width / 2.0, height / 2.0, depth / 2.0
    cx, cy, cz = center_x, center_y, center_z

    # 24 vertices (4 per face for flat shading)
    positions = [
        # Front (+Z)
        cx - w, cy - h, cz + d,  cx + w, cy - h, cz + d,  cx + w, cy + h, cz + d,  cx - w, cy + h, cz + d,
        # Back (-Z)
        cx + w, cy - h, cz - d,  cx - w, cy - h, cz - d,  cx - w, cy + h, cz - d,  cx + w, cy + h, cz - d,
        # Top (+Y)
        cx - w, cy + h, cz + d,  cx + w, cy + h, cz + d,  cx + w, cy + h, cz - d,  cx - w, cy + h, cz - d,
        # Bottom (-Y)
        cx - w, cy - h, cz - d,  cx + w, cy - h, cz - d,  cx + w, cy - h, cz + d,  cx - w, cy - h, cz + d,
        # Right (+X)
        cx + w, cy - h, cz + d,  cx + w, cy - h, cz - d,  cx + w, cy + h, cz - d,  cx + w, cy + h, cz + d,
        # Left (-X)
        cx - w, cy - h, cz - d,  cx - w, cy - h, cz + d,  cx - w, cy + h, cz + d,  cx - w, cy + h, cz - d,
    ]

    normals = [
        0, 0, 1,   0, 0, 1,   0, 0, 1,   0, 0, 1,
        0, 0, -1,  0, 0, -1,  0, 0, -1,  0, 0, -1,
        0, 1, 0,   0, 1, 0,   0, 1, 0,   0, 1, 0,
        0, -1, 0,  0, -1, 0,  0, -1, 0,  0, -1, 0,
        1, 0, 0,   1, 0, 0,   1, 0, 0,   1, 0, 0,
        -1, 0, 0, -1, 0, 0,  -1, 0, 0,  -1, 0, 0,
    ]

    indices = []
    for f in range(6):
        base = f * 4
        indices.extend([base, base + 1, base + 2, base, base + 2, base + 3])

    return positions, normals, indices


def create_cylinder_mesh(radius, length, segments=16, center_x=0, center_y=0, center_z=0, axis="x"):
    """Génère un cylindre (pour les roues / barres)."""
    positions = []
    normals = []
    indices = []
    
    half_l = length / 2.0
    
    # Vertices for circular ends
    for side, sign in [(0, -1), (1, 1)]:
        offset = sign * half_l
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            if axis == "x":
                px = center_x + offset
                py = center_y + radius * math.sin(angle)
                pz = center_z + radius * math.cos(angle)
                nx, ny, nz = 0, math.sin(angle), math.cos(angle)
            elif axis == "z":
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                pz = center_z + offset
                nx, ny, nz = math.cos(angle), math.sin(angle), 0
            else:
                px = center_x + radius * math.cos(angle)
                py = center_y + offset
                pz = center_z + radius * math.sin(angle)
                nx, ny, nz = math.cos(angle), 0, math.sin(angle)
                
            positions.extend([px, py, pz])
            normals.extend([nx, ny, nz])
            
    # Side quads
    for i in range(segments):
        next_i = (i + 1) % segments
        p0 = i
        p1 = next_i
        p2 = segments + next_i
        p3 = segments + i
        indices.extend([p0, p1, p2, p0, p2, p3])
        
    return positions, normals, indices


def build_car_glb():
    # ─── 1. Définition des parties du modèle 3D ────────────────────────────────
    # Unités en mètres (Dimensions Sandero Stepway réalistes : 4.09m long, 1.84m large, 1.58m haut)
    parts = {}

    # Carrosserie principale (Châssis bas + carrosserie principale)
    b1_p, b1_n, b1_i = create_box_mesh(1.80, 0.55, 3.90, center_x=0, center_y=0.45, center_z=0)
    # Capot incliné
    b2_p, b2_n, b2_i = create_box_mesh(1.72, 0.25, 1.10, center_x=0, center_y=0.72, center_z=1.25)
    # Pare-chocs avant & arrière baroudeur Stepway
    b3_p, b3_n, b3_i = create_box_mesh(1.82, 0.30, 0.20, center_x=0, center_y=0.35, center_z=2.00)
    b4_p, b4_n, b4_i = create_box_mesh(1.82, 0.30, 0.20, center_x=0, center_y=0.35, center_z=-2.00)

    # Combiner carrosserie
    body_pos = b1_p + b2_p + b3_p + b4_p
    body_norm = b1_n + b2_n + b3_n + b4_n
    body_ind = []
    offset = 0
    for p, idx in [(b1_p, b1_i), (b2_p, b2_i), (b3_p, b3_i), (b4_p, b4_i)]:
        body_ind.extend([i + offset for i in idx])
        offset += len(p) // 3

    parts["Car_Body"] = {
        "material_name": "Car_Body_Paint",
        "positions": body_pos,
        "normals": body_norm,
        "indices": body_ind,
        "pbr": {"baseColorFactor": [0.88, 0.90, 0.92, 1.0], "metallicFactor": 0.85, "roughnessFactor": 0.25}
    }

    # Vitrage & Habitacle supérieur
    g1_p, g1_n, g1_i = create_box_mesh(1.60, 0.55, 1.85, center_x=0, center_y=0.98, center_z=-0.20)
    parts["Car_Windows"] = {
        "material_name": "Car_Glass",
        "positions": g1_p,
        "normals": g1_n,
        "indices": g1_i,
        "pbr": {"baseColorFactor": [0.10, 0.12, 0.15, 0.85], "metallicFactor": 0.95, "roughnessFactor": 0.10}
    }

    # Phares et feux LED
    l1_p, l1_n, l1_i = create_box_mesh(0.40, 0.12, 0.05, center_x=-0.65, center_y=0.68, center_z=1.98)
    l2_p, l2_n, l2_i = create_box_mesh(0.40, 0.12, 0.05, center_x=0.65, center_y=0.68, center_z=1.98)
    l3_p, l3_n, l3_i = create_box_mesh(0.35, 0.15, 0.05, center_x=-0.65, center_y=0.72, center_z=-1.98)
    l4_p, l4_n, l4_i = create_box_mesh(0.35, 0.15, 0.05, center_x=0.65, center_y=0.72, center_z=-1.98)
    lights_pos = l1_p + l2_p + l3_p + l4_p
    lights_norm = l1_n + l2_n + l3_n + l4_n
    lights_ind = []
    offset = 0
    for p, idx in [(l1_p, l1_i), (l2_p, l2_i), (l3_p, l3_i), (l4_p, l4_i)]:
        lights_ind.extend([i + offset for i in idx])
        offset += len(p) // 3

    parts["Car_Lights"] = {
        "material_name": "Car_Lights_Mat",
        "positions": lights_pos,
        "normals": lights_norm,
        "indices": lights_ind,
        "pbr": {"baseColorFactor": [0.95, 0.95, 1.0, 1.0], "metallicFactor": 0.5, "roughnessFactor": 0.1}
    }

    # 4 Roues (Pneus caoutchouc noir)
    wheels_pos = []
    wheels_norm = []
    wheels_ind = []
    offset = 0
    wheel_coords = [(-0.85, 0.32, 1.25), (0.85, 0.32, 1.25), (-0.85, 0.32, -1.25), (0.85, 0.32, -1.25)]
    for cx, cy, cz in wheel_coords:
        wp, wn, wi = create_cylinder_mesh(0.33, 0.22, segments=20, center_x=cx, center_y=cy, center_z=cz, axis="x")
        wheels_pos.extend(wp)
        wheels_norm.extend(wn)
        wheels_ind.extend([i + offset for i in wi])
        offset += len(wp) // 3

    parts["Car_Wheels"] = {
        "material_name": "Car_Tires_Mat",
        "positions": wheels_pos,
        "normals": wheels_norm,
        "indices": wheels_ind,
        "pbr": {"baseColorFactor": [0.12, 0.12, 0.13, 1.0], "metallicFactor": 0.05, "roughnessFactor": 0.85}
    }

    # 4 Jantes alliage diamantées
    rims_pos = []
    rims_norm = []
    rims_ind = []
    offset = 0
    for cx, cy, cz in wheel_coords:
        sign = 1 if cx > 0 else -1
        rp, rn, ri = create_cylinder_mesh(0.24, 0.04, segments=16, center_x=cx + sign * 0.10, center_y=cy, center_z=cz, axis="x")
        rims_pos.extend(rp)
        rims_norm.extend(rn)
        rims_ind.extend([i + offset for i in ri])
        offset += len(rp) // 3

    parts["Car_Rims"] = {
        "material_name": "Rims_Alloy",
        "positions": rims_pos,
        "normals": rims_norm,
        "indices": rims_ind,
        "pbr": {"baseColorFactor": [0.85, 0.87, 0.90, 1.0], "metallicFactor": 0.90, "roughnessFactor": 0.20}
    }

    # ─── ACCESSOIRES TOGGLABLES ───────────────────────────────────────────────
    # 1. Barres de toit (Accessoire optionnel)
    r1_p, r1_n, r1_i = create_box_mesh(0.06, 0.06, 2.10, center_x=-0.65, center_y=1.30, center_z=-0.15)
    r2_p, r2_n, r2_i = create_box_mesh(0.06, 0.06, 2.10, center_x=0.65, center_y=1.30, center_z=-0.15)
    r3_p, r3_n, r3_i = create_box_mesh(1.36, 0.04, 0.08, center_x=0, center_y=1.34, center_z=0.40)
    r4_p, r4_n, r4_i = create_box_mesh(1.36, 0.04, 0.08, center_x=0, center_y=1.34, center_z=-0.70)
    roof_pos = r1_p + r2_p + r3_p + r4_p
    roof_norm = r1_n + r2_n + r3_n + r4_n
    roof_ind = []
    offset = 0
    for p, idx in [(r1_p, r1_i), (r2_p, r2_i), (r3_p, r3_i), (r4_p, r4_i)]:
        roof_ind.extend([i + offset for i in idx])
        offset += len(p) // 3

    parts["Roof_Bars"] = {
        "material_name": "Roof_Bars_Mat",
        "positions": roof_pos,
        "normals": roof_norm,
        "indices": roof_ind,
        "pbr": {"baseColorFactor": [0.75, 0.77, 0.80, 1.0], "metallicFactor": 0.85, "roughnessFactor": 0.30}
    }

    # 2. Barres latérales aluminium (Accessoire optionnel)
    s1_p, s1_n, s1_i = create_box_mesh(0.10, 0.05, 2.30, center_x=-0.96, center_y=0.22, center_z=0)
    s2_p, s2_n, s2_i = create_box_mesh(0.10, 0.05, 2.30, center_x=0.96, center_y=0.22, center_z=0)
    side_pos = s1_p + s2_p
    side_norm = s1_n + s2_n
    side_ind = []
    offset = 0
    for p, idx in [(s1_p, s1_i), (s2_p, s2_i)]:
        side_ind.extend([i + offset for i in idx])
        offset += len(p) // 3

    parts["Side_Steps"] = {
        "material_name": "Side_Steps_Mat",
        "positions": side_pos,
        "normals": side_norm,
        "indices": side_ind,
        "pbr": {"baseColorFactor": [0.80, 0.82, 0.85, 1.0], "metallicFactor": 0.90, "roughnessFactor": 0.25}
    }

    # ─── 2. Encodage du binaire GLTF ──────────────────────────────────────────
    binary_data = bytearray()
    buffer_views = []
    accessors = []
    materials = []
    meshes = []
    nodes = []

    def add_buffer_data(data_bytes, target=34962):
        nonlocal binary_data
        offset = len(binary_data)
        # 4-byte alignment
        padding = (4 - (offset % 4)) % 4
        binary_data.extend(b"\x00" * padding)
        offset = len(binary_data)
        binary_data.extend(data_bytes)
        length = len(data_bytes)
        bv_idx = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": offset,
            "byteLength": length,
            "target": target
        })
        return bv_idx

    for part_name, part_data in parts.items():
        mat_idx = len(materials)
        materials.append({
            "name": part_data["material_name"],
            "pbrMetallicRoughness": part_data["pbr"]
        })

        # 1. Positions (VEC3 FLOAT)
        pos_floats = part_data["positions"]
        pos_bytes = struct.pack(f"<{len(pos_floats)}f", *pos_floats)
        pos_bv = add_buffer_data(pos_bytes, target=34962)
        
        # Min / Max bounds for positions
        xs = pos_floats[0::3]
        ys = pos_floats[1::3]
        zs = pos_floats[2::3]
        pos_acc = len(accessors)
        accessors.append({
            "bufferView": pos_bv,
            "byteOffset": 0,
            "componentType": 5126,  # FLOAT
            "count": len(pos_floats) // 3,
            "type": "VEC3",
            "min": [min(xs), min(ys), min(zs)],
            "max": [max(xs), max(ys), max(zs)]
        })

        # 2. Normals (VEC3 FLOAT)
        norm_floats = part_data["normals"]
        norm_bytes = struct.pack(f"<{len(norm_floats)}f", *norm_floats)
        norm_bv = add_buffer_data(norm_bytes, target=34962)
        norm_acc = len(accessors)
        accessors.append({
            "bufferView": norm_bv,
            "byteOffset": 0,
            "componentType": 5126,
            "count": len(norm_floats) // 3,
            "type": "VEC3"
        })

        # 3. Indices (SCALAR UNSIGNED_SHORT)
        ind_ints = part_data["indices"]
        ind_bytes = struct.pack(f"<{len(ind_ints)}H", *ind_ints)
        ind_bv = add_buffer_data(ind_bytes, target=34963)
        ind_acc = len(accessors)
        accessors.append({
            "bufferView": ind_bv,
            "byteOffset": 0,
            "componentType": 5123,  # UNSIGNED_SHORT
            "count": len(ind_ints),
            "type": "SCALAR"
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
                "material": mat_idx
            }]
        })

        node_idx = len(nodes)
        nodes.append({
            "name": part_name,
            "mesh": mesh_idx
        })

    # Root node / Scene
    gltf_dict = {
        "asset": {"version": "2.0", "generator": "Wakala 3D Generator"},
        "scene": 0,
        "scenes": [{"name": "CarScene", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": meshes,
        "materials": materials,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{"byteLength": len(binary_data)}]
    }

    json_str = json.dumps(gltf_dict, separators=(",", ":"))
    json_bytes = json_str.encode("utf-8")
    # 4-byte alignment for JSON
    json_padding = (4 - (len(json_bytes) % 4)) % 4
    json_bytes += b" " * json_padding

    # 4-byte alignment for binary
    bin_padding = (4 - (len(binary_data) % 4)) % 4
    binary_data.extend(b"\x00" * bin_padding)

    # GLB Header
    total_length = 12 + 8 + len(json_bytes) + 8 + len(binary_data)
    header = struct.pack("<4sII", b"glTF", 2, total_length)
    chunk0_header = struct.pack("<II", len(json_bytes), 0x4E4F534A)  # "JSON"
    chunk1_header = struct.pack("<II", len(binary_data), 0x004E4942)  # "BIN\0"

    with open(GLB_PATH, "wb") as f:
        f.write(header)
        f.write(chunk0_header)
        f.write(json_bytes)
        f.write(chunk1_header)
        f.write(binary_data)

    print(f"[OK] 3D Model GLB successfully created: {GLB_PATH} ({os.path.getsize(GLB_PATH)} bytes)")

    # ─── 3. Création du material_map.json ─────────────────────────────────────
    material_map = {
        "vehicle_slug": "dacia-sandero-stepway",
        "carrosserie_materials": ["Car_Body_Paint"],
        "glass_materials": ["Car_Glass"],
        "rims_materials": ["Rims_Alloy"],
        "wheels_materials": ["Car_Tires_Mat"],
        "optional_meshes": {
            "Barres de toit": ["Roof_Bars"],
            "Barres de toit transversales QuickFix": ["Roof_Bars"],
            "Barres latérales": ["Side_Steps"],
            "Barres latérales en aluminium brossé": ["Side_Steps"]
        }
    }

    with open(MATERIAL_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(material_map, f, indent=2, ensure_ascii=False)

    print(f"[OK] Material Map successfully created: {MATERIAL_MAP_PATH}")


if __name__ == "__main__":
    build_car_glb()
