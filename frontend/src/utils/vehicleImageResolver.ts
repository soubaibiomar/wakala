/**
 * vehicleImageResolver.ts
 * Résolveur d'images réelles et officielles pour tous les modèles et marques.
 * Priorité :
 * 1. Image spécifique du véhicule (si présente et valide)
 * 2. Image profil studio détourée officielle du modèle (Moteur.ma / Constructeur)
 * 3. Visuel officiel de la marque par catégorie de carrosserie (SUV, Berline, Citadine)
 */

import { VEHICLE_STUDIO_IMAGES, BODY_FALLBACKS } from './vehicleImageCatalogData';

export function resolveVehicleImage(brand?: string, model?: string, currentImages?: Array<{ file_path: string }>): string {
  // 1. Check if vehicle already has a valid scraped/uploaded image (excluding broken unsplash or generic placeholders)
  if (currentImages && currentImages.length > 0 && currentImages[0]?.file_path) {
    const p = currentImages[0].file_path;
    const isGeneric = p.includes('placeholder') || p.includes('example.com') || p.includes('phares-intro');
    if (!isGeneric && (p.startsWith('http') || p.startsWith('/'))) {
      return p;
    }
  }

  const b = (brand || '').toLowerCase().trim();
  const m = (model || '').toLowerCase().trim();

  // Normalize model string
  const cleanM = m
    .replace(/^dacia\s*/i, '')
    .replace(/^renault\s*/i, '')
    .replace(/^peugeot\s*/i, '')
    .replace(/^hyundai\s*/i, '')
    .replace(/^volkswagen\s*/i, '')
    .replace(/^toyota\s*/i, '')
    .replace(/^audi\s*/i, '')
    .replace(/^bmw\s*/i, '')
    .replace(/^mercedes[- ]benz\s*/i, '')
    .replace(/^mercedes\s*/i, '')
    .replace(/^kia\s*/i, '')
    .replace(/^citro[eë]n\s*/i, '')
    .replace(/^fiat\s*/i, '')
    .replace(/^ford\s*/i, '')
    .replace(/^nissan\s*/i, '')
    .replace(/^byd\s*/i, '')
    .replace(/^mg\s*/i, '')
    .replace(/^chery\s*/i, '')
    .replace(/^geely\s*/i, '')
    .replace(/^changan\s*/i, '')
    .trim();

  // Check direct brand map in studio catalogue
  const brandDict = VEHICLE_STUDIO_IMAGES[b];
  if (brandDict) {
    // 1. Direct exact model match
    if (brandDict[cleanM]) return brandDict[cleanM];
    if (brandDict[m]) return brandDict[m];

    // 2. Substring match
    for (const [modKey, imgUrl] of Object.entries(brandDict)) {
      if (cleanM.includes(modKey) || modKey.includes(cleanM)) {
        return imgUrl;
      }
    }
  }

  // Cross-brand search
  for (const [bKey, modelsMap] of Object.entries(VEHICLE_STUDIO_IMAGES)) {
    if (b.includes(bKey) || bKey.includes(b)) {
      for (const [modKey, imgUrl] of Object.entries(modelsMap)) {
        if (cleanM.includes(modKey) || modKey.includes(cleanM)) {
          return imgUrl;
        }
      }
    }
  }

  // Body type fallback
  if (m.includes('duster') || m.includes('suv') || m.includes('cross') || m.includes('tucson') || m.includes('sportage') || m.includes('tiguan')) {
    return BODY_FALLBACKS.suv;
  }
  if (m.includes('sandero') || m.includes('clio') || m.includes('208') || m.includes('picanto') || m.includes('i10') || m.includes('i20')) {
    return BODY_FALLBACKS.citadine;
  }
  if (m.includes('logan') || m.includes('berline') || m.includes('tipo') || m.includes('corolla') || m.includes('octavia')) {
    return BODY_FALLBACKS.berline;
  }

  return BODY_FALLBACKS.default;
}
