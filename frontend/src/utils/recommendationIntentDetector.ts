/**
 * utils/recommendationIntentDetector.ts
 * =====================================
 * Détecteur intelligent d'intention pour la barre de recherche.
 * Distingue un filtre catalogue direct (ex: "Clio", "Golf 8", "Dacia")
 * d'une demande de recommandation / conseil IA (ex: "voiture pour famille", "SUV économique moins de 200k").
 */

// Mots-clés et verbes d'intention de recherche / conseil (normalisés sans accents)
const INTENT_VERBS = /\b(cherche|recherche|trouve|propose|recommande|recommandation|conseil|conseillez|choisir|choisis|acheter|achat|buy|recommend|suggest|choose|need|want|help|aide|quel|quelle|quels|quelles|lequel|laquelle|meilleur|meilleure|meilleurs|meilleures|top|pourquoi|comment|avis|comparer|comparaison)\b/i;

// Contextes d'usage, famille, profil
const USAGE_AND_SITUATION = /\b(famille|familial|familiale|enfants?|bebe|voyage|ville|route|autoroute|travail|jeune|debutant|femme|etudiant|quotidien|piste|montagne|longs?\s+trajets?|ideal\s+pour|adapte\s+pour|besoin\s+de|concu\s+pour|pour\s+(?:la|une|ma|les|mon|mes)?)\b/i;

// Critères et qualificatifs de recherche
const CRITERIA_PATTERNS = /\b(economique|fiable|fiabilite|spacieux|spacieuse|confortable|robuste|puissant|puissante|securise|securite|faible\s+consommation|petit\s+budget|pas\s+cher|grand\s+coffre|7\s+places|5\s+places|automatique\s+ou\s+manuelle|essence\s+ou\s+diesel)\b/i;

// Expressions de budget naturel ou contraintes
const BUDGET_PATTERNS = /\b(budget|moins\s+de|max|maximum|plafond|entre\s+\d+|autour\s+de|jusqu['’]?\s*a|\d+\s*(?:000|k)\s*(?:dh|mad|dhs?))\b/i;
const BUDGET_NUMBER_WITH_CURRENCY = /\b\d{5,7}\s*(?:dh|mad|dhs)\b/i;

// Expressions en Darija (arabe dialectal marocain) et Arabe classique
const DARIJA_AND_ARABIC_PATTERNS = /(?:بغيت|باغي|كنقلب|خاصني|نحتاج|أريد|أبحث|شكون|أحسن|افضل|انصحني|شنو|واش|عائلة|وليدات|طريق|خدمة|اقتصادية|رخيصة|صحيحة|عندي\s+\d+|قل\s+من|أقل\s+من|bghit|baghi|kan9leb|kanqleb|khassni|ahsan|a7san|3a2ila|tri9|khdma|9tisadiya|s7i7a|rkhisa|chmen|achmen|dyal\s+3a2ila|dyal\s+tri9|nchri)/iu;

// Marques connues seules pour éviter de faux positifs sur des filtres simples
const COMMON_BRANDS = new Set([
  'dacia', 'renault', 'peugeot', 'volkswagen', 'vw', 'hyundai', 'kia',
  'toyota', 'citroen', 'fiat', 'ford', 'nissan', 'seat', 'skoda',
  'opel', 'audi', 'bmw', 'mercedes', 'volvo', 'land rover', 'jeep',
  'cupra', 'porsche', 'honda', 'suzuki', 'chery', 'geely', 'mg', 'byd'
]);

/**
 * Normalise une chaîne en minuscules et sans accents pour fiabiliser le matching regex.
 */
function normalizeText(text: string): string {
  return text
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '');
}

/**
 * Analyse une chaîne de recherche et détermine si elle correspond à une demande de recommandation IA.
 * @param query Texte saisi par l'utilisateur
 * @returns true si intention de recommandation / conseil IA, false si filtre catalogue direct
 */
export function isRecommendationQuery(query: string): boolean {
  if (!query) return false;
  const rawTrimmed = query.trim();
  if (rawTrimmed.length < 3) return false;

  // 1. Présence d'un point d'interrogation (question directe)
  if (rawTrimmed.includes('?')) {
    return true;
  }

  // 2. Darija ou Arabe (sur chaîne brute non normalisée)
  if (DARIJA_AND_ARABIC_PATTERNS.test(rawTrimmed)) {
    return true;
  }

  const normalized = normalizeText(rawTrimmed);

  // Si c'est juste un mot unique correspondant à une marque classique (ex: "dacia", "clio") -> filtre direct
  if (!normalized.includes(' ') && COMMON_BRANDS.has(normalized)) {
    return false;
  }

  // 3. Mots d'intention explicite (conseil, cherche, meilleur, quel, etc.)
  if (INTENT_VERBS.test(normalized)) {
    return true;
  }

  // 4. Usage ou situation de vie (famille, voyage, autoroute, etc.)
  if (USAGE_AND_SITUATION.test(normalized)) {
    return true;
  }

  // 5. Critères qualitatifs (économique, grand coffre, 7 places, etc.)
  if (CRITERIA_PATTERNS.test(normalized)) {
    return true;
  }

  // 6. Budget avec contrainte ou unité monétaire
  if (BUDGET_PATTERNS.test(normalized) || BUDGET_NUMBER_WITH_CURRENCY.test(normalized)) {
    return true;
  }

  // 7. Requêtes longues (>= 3 mots) contenant des prépositions ou conjonctions naturelles
  const words = normalized.split(/\s+/);
  if (words.length >= 3) {
    const naturalConnectors = /\b(pour|avec|sans|de|qui|dans|moins|plus|ou|et)\b/i;
    if (naturalConnectors.test(normalized)) {
      return true;
    }
  }

  return false;
}