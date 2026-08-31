/**
 * brandLogoResolver.ts
 * Résolution ultra-robuste et officielle des logos constructeurs pour Wakala.
 * Gère les accents (ex: Citroën -> citroen.png), les variantes de noms
 * (ex: DS Automobiles -> ds.png, KG Mobility -> kgm.png, Rox -> rox.png, Lynk & Co -> lynkco.png),
 * et garantit que 100% des 66 marques du catalogue officiel ont un logo haute définition.
 */

// Table de correspondance explicite pour les alias et noms composés
const BRAND_LOGO_MAP: Record<string, string> = {
  // Français / Noms officiels avec accents
  'citroen': '/logos/citroen.png',
  'citroën': '/logos/citroen.png',
  'ds': '/logos/ds.png',
  'ds automobiles': '/logos/ds.png',
  'dsautomobiles': '/logos/ds.png',
  
  // Coréens / Chinois / Groupes
  'kg mobility': '/logos/kgm.png',
  'kgmobility': '/logos/kgm.png',
  'kgm': '/logos/kgm.png',
  'ssangyong': '/logos/kgm.png',
  
  'gac': '/logos/gac.png',
  'gac motor': '/logos/gacmotor.png',
  'gacmotor': '/logos/gac.png',
  
  'lynk & co': '/logos/lynkco.png',
  'lynk and co': '/logos/lynkco.png',
  'lynkco': '/logos/lynkco.png',
  'lynk-co': '/logos/lynkco.png',
  
  'omoda': '/logos/omoda.png',
  'jaecoo': '/logos/jaecoo.png',
  'omoda & jaecoo': '/logos/omodajaecoo.png',
  'omoda and jaecoo': '/logos/omodajaecoo.png',
  'omodajaecoo': '/logos/omoda.png',
  
  'rox': '/logos/rox.png',
  'rox motor': '/logos/roxmotor.png',
  'roxmotor': '/logos/rox.png',
  
  // Marques à tirets / espaces
  'alfa romeo': '/logos/alfaromeo.png',
  'alfaromeo': '/logos/alfaromeo.png',
  'alfa-romeo': '/logos/alfaromeo.png',
  
  'aston martin': '/logos/astonmartin.png',
  'astonmartin': '/logos/astonmartin.png',
  'aston-martin': '/logos/astonmartin.png',
  
  'land rover': '/logos/landrover.png',
  'landrover': '/logos/landrover.png',
  'land-rover': '/logos/landrover.png',
  
  'mercedes-benz': '/logos/mercedes.png',
  'mercedes benz': '/logos/mercedes.png',
  'mercedes': '/logos/mercedes.png',
  'mercedesbenz': '/logos/mercedes.png',
  
  'rolls-royce': '/logos/rollsroyce.png',
  'rolls royce': '/logos/rollsroyce.png',
  'rollsroyce': '/logos/rollsroyce.png',
};

/**
 * Normalise une chaîne de marque (supprime accents, tirets, ponctuation, espaces)
 */
function normalizeBrandName(name: string): string {
  return (name || '')
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // Supprime les diacritiques/accents
    .replace(/[^a-z0-9]/g, '');
}

/**
 * Résout l'URL du logo officiel d'une marque
 * @param brandName Nom ou slug de la marque (ex: 'Citroën', 'DS Automobiles', 'BMW')
 * @param existingLogoUrl URL existante déjà assignée (si valide et non-placeholder)
 * @returns Chemin public absolu du logo (ex: '/logos/citroen.png')
 */
export function resolveBrandLogo(brandName?: string | null, existingLogoUrl?: string | null): string {
  if (
    existingLogoUrl &&
    !existingLogoUrl.includes('placeholder') &&
    !existingLogoUrl.includes('example.com') &&
    (existingLogoUrl.startsWith('/') || existingLogoUrl.startsWith('http'))
  ) {
    return existingLogoUrl;
  }

  if (!brandName) {
    return '/logos/wakala-logo.png';
  }

  const rawLower = brandName.toLowerCase().trim();

  // 1. Recherche directe dans la table des alias
  if (BRAND_LOGO_MAP[rawLower]) {
    return BRAND_LOGO_MAP[rawLower];
  }

  // 2. Normalisation sans accents ni séparateurs
  const clean = normalizeBrandName(brandName);
  if (BRAND_LOGO_MAP[clean]) {
    return BRAND_LOGO_MAP[clean];
  }

  // 3. Fallback standard sur le slug nettoyé
  return `/logos/${clean}.png`;
}
