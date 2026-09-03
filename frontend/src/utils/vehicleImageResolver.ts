/**
 * vehicleImageResolver.ts
 * Résolveur d'images réelles et officielles pour tous les modèles et marques.
 * Priorité :
 * 1. Image spécifique du véhicule (si présente et valide)
 * 2. Image locale ou provenant d'une source autorisée (Carwow / constructeur)
 * 3. Fallback local neutre en profil latéral
 */

import { VEHICLE_STUDIO_IMAGES } from './vehicleImageCatalogData';

/** The catalogue must never fall back to a hero/headlight or aggregator image. */
export const CATALOGUE_IMAGE_FALLBACK = '/assets/car-side-fallback.svg';

// Curated real images for models that the generic image CDN returns as a
// covered-car placeholder. These are only used for Ferrari until the provider
// has transparent studio coverage for these model names.
const CURATED_MODEL_IMAGES: Record<string, string> = {
  'ferrari|12cilindri': 'https://www.ferraribeverlyhills.com/_next/image?q=90&url=https%3A%2F%2Fvrrb-prod-s3.s3.us-west-1.amazonaws.com%2Fstrapi%2Fda580f22_0ff7_4070_9055_8d03b975b89d_b4c0709fc4.jpg&w=1080',
  'ferrari|296 gtb': 'https://ph-classic-prod-images.s3.amazonaws.com/nimg/44336/06_296_GTB_side.jpg',
  'ferrari|296 gts': 'https://web.imgstore.it/b402371cdb774f79ad0f4bb130ff2fc4.jpg',
  'ferrari|purosangue': 'https://images.91wheels.com/assets/c_images/gallery/ferrari/purosangue/ferrari-purosangue-2-1767871315.png?q=40&w=800',
  'ferrari|roma spider': 'https://www.latribuneauto.com/media/cache/resolve/vehicule_slider/photos/FERRARI/Roma%20Spider/FERR-ROMS-CA-23-146130/04%20Ferrari%20Roma%20Spider%202023%20Exterieur%20Profil.jpg',
  'ferrari|sf90 spider': 'https://cdn.ferrari.com/cms/network/media/img/resize/5fad6036e1bd8b32c9642ff0-sf90_spider_design_intro_v00_mobile_out',
};

function isUsableImage(value: string): boolean {
  if (value.startsWith('/')) return !value.includes('hero-car') && !value.includes('phares-intro');
  if (!value.startsWith('http')) return false;

  const url = value.toLowerCase();
  // Moteur model URLs are retained when they resolve successfully; Wandaloo,
  // generic stock photos, and hero/headlight assets are never accepted.
  return !url.includes('wandaloo') && !url.includes('unsplash.com');
}

function getCarwowSideImage(brand: string, model: string): string {
  // Image providers use ASCII make slugs. In particular, `Citroën` with its
  // accent can otherwise return a generic or empty result.
  const normalizedBrand = brand
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, '-');
  const make = encodeURIComponent(normalizedBrand);
  const modelName = encodeURIComponent(model.trim().toLowerCase());
  return `https://cdn.imagin.studio/getImage?angle=208&customer=carwow&make=${make}&modelFamily=${modelName}&modelRange=${modelName}&modelYear=2024&width=800&zoomType=fullscreen`;
}

export function resolveVehicleImage(brand?: string, model?: string, currentImages?: Array<{ file_path: string }>): string {
  // 1. Check if vehicle already has a valid scraped/uploaded image (excluding broken unsplash or generic placeholders)
  if (currentImages && currentImages.length > 0 && currentImages[0]?.file_path) {
    const p = currentImages[0].file_path;
    const isGeneric = p.includes('placeholder') || p.includes('example.com');
    if (!isGeneric && isUsableImage(p)) {
      return p;
    }
  }

  const b = (brand || '').toLowerCase().trim();
  const m = (model || '').toLowerCase().trim();

  const curatedImage = CURATED_MODEL_IMAGES[`${b}|${m}`]
    || Object.entries(CURATED_MODEL_IMAGES).find(([key]) => {
      const [curatedBrand, curatedModel] = key.split('|');
      return curatedBrand === b && (m.includes(curatedModel) || curatedModel.includes(m));
    })?.[1];
  if (curatedImage) return curatedImage;

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

  // Carwow's side-angle vehicle render is the catalogue-wide source of truth
  // for models that do not have a curated image.
  // The image element's error handler still protects models not available there.
  if (b && cleanM) return getCarwowSideImage(b, cleanM);

  // Check direct brand map in studio catalogue
  const brandDict = VEHICLE_STUDIO_IMAGES[b];
  if (brandDict) {
    // 1. Direct exact model match
    if (brandDict[cleanM] && isUsableImage(brandDict[cleanM])) return brandDict[cleanM];
    if (brandDict[m] && isUsableImage(brandDict[m])) return brandDict[m];

    // 2. Substring match
    for (const [modKey, imgUrl] of Object.entries(brandDict)) {
      if ((cleanM.includes(modKey) || modKey.includes(cleanM)) && isUsableImage(imgUrl)) {
        return imgUrl;
      }
    }
  }

  // Cross-brand search
  for (const [bKey, modelsMap] of Object.entries(VEHICLE_STUDIO_IMAGES)) {
    if (b.includes(bKey) || bKey.includes(b)) {
      for (const [modKey, imgUrl] of Object.entries(modelsMap)) {
        if ((cleanM.includes(modKey) || modKey.includes(cleanM)) && isUsableImage(imgUrl)) {
          return imgUrl;
        }
      }
    }
  }

  // Body type fallback
  if (m.includes('duster') || m.includes('suv') || m.includes('cross') || m.includes('tucson') || m.includes('sportage') || m.includes('tiguan')) {
    return CATALOGUE_IMAGE_FALLBACK;
  }
  if (m.includes('sandero') || m.includes('clio') || m.includes('208') || m.includes('picanto') || m.includes('i10') || m.includes('i20')) {
    return CATALOGUE_IMAGE_FALLBACK;
  }
  if (m.includes('logan') || m.includes('berline') || m.includes('tipo') || m.includes('corolla') || m.includes('octavia')) {
    return CATALOGUE_IMAGE_FALLBACK;
  }

  return CATALOGUE_IMAGE_FALLBACK;
}
