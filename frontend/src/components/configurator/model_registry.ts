/**
 * components/configurator/model_registry.ts
 * =========================================
 * Table de correspondance vehicle_id / slug -> Fichiers 3D (.glb et material_map.json).
 * 
 * Un véhicule sans entrée ici bascule automatiquement sur les photos statiques 2D
 * (sans erreur, aucun bouton 3D rendu).
 */

export interface VehicleModel3DEntry {
  modelPath: string;
  materialMapPath: string;
  name?: string;
  scale?: number;
  cameraPosition?: [number, number, number];
}

export const MODEL_REGISTRY: Record<string, VehicleModel3DEntry> = {
  // Premier véhicule test officiel
  "dacia-sandero-stepway": {
    modelPath: "/models/dacia-sandero-stepway/model.glb",
    materialMapPath: "/models/dacia-sandero-stepway/material_map.json",
    name: "Dacia Sandero Stepway",
    scale: 1.0,
    cameraPosition: [3.8, 1.8, 4.8],
  },
  // Alias pour correspondre aux formats de slug ou noms de modèles
  "sandero-stepway": {
    modelPath: "/models/dacia-sandero-stepway/model.glb",
    materialMapPath: "/models/dacia-sandero-stepway/material_map.json",
    name: "Dacia Sandero Stepway",
    scale: 1.0,
    cameraPosition: [3.8, 1.8, 4.8],
  },
  "dacia-sandero": {
    modelPath: "/models/dacia-sandero-stepway/model.glb",
    materialMapPath: "/models/dacia-sandero-stepway/material_map.json",
    name: "Dacia Sandero",
    scale: 1.0,
    cameraPosition: [3.8, 1.8, 4.8],
  }
};

/**
 * Normalise un identifiant (slug, ID ou nom combiné) pour la recherche dans le registre.
 */
export function normalizeModelKey(key: string): string {
  if (!key) return "";
  return key
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/**
 * Vérifie si un véhicule dispose d'un modèle 3D répertorié.
 */
export function has3DModel(identifier?: string | null): boolean {
  if (!identifier) return false;
  const directKey = identifier.toLowerCase().trim();
  if (MODEL_REGISTRY[directKey]) return true;

  const normalized = normalizeModelKey(identifier);
  if (MODEL_REGISTRY[normalized]) return true;

  // Recherche par inclusion partielle
  for (const regKey of Object.keys(MODEL_REGISTRY)) {
    if (normalized.includes(regKey) || regKey.includes(normalized)) {
      return true;
    }
  }

  return false;
}

/**
 * Récupère l'entrée 3D associée à un véhicule, ou null si inexistante.
 */
export function getModel3DEntry(identifier?: string | null): VehicleModel3DEntry | null {
  if (!identifier) return null;
  const directKey = identifier.toLowerCase().trim();
  if (MODEL_REGISTRY[directKey]) return MODEL_REGISTRY[directKey];

  const normalized = normalizeModelKey(identifier);
  if (MODEL_REGISTRY[normalized]) return MODEL_REGISTRY[normalized];

  // Recherche par inclusion partielle
  for (const [regKey, entry] of Object.entries(MODEL_REGISTRY)) {
    if (normalized.includes(regKey) || regKey.includes(normalized)) {
      return entry;
    }
  }

  return null;
}
