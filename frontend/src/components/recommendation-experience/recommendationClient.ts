import type { Vehicle } from '../../types/vehicle';
import { chatbotService } from '../../services/chatbotService';
import { recommendationService } from '../../services/recommendationService';
import type { EightDimensionScores } from '../../services/recommendationService';
import { vehicleService } from '../../services/vehicleService';
import { POPULAR_BRANDS } from '../../constants/brands';

export type Car = Vehicle & {
  match_score?: number;
  key_facts?: string[];
  eight_dimension_scores?: EightDimensionScores;
  total_8d_score?: number;
  total_8d_percent?: number;
};

export interface ChatTurn {
  role: 'user' | 'assistant';
  content: string;
}

export interface QuestionOption {
  label: string;
  value?: string;
}

export interface NextQuestion {
  question: string;
  options: QuestionOption[];
  rangeBounds?: { min: number; max: number; step?: number; label: string };
}

export type ChatLanguage = 'fr' | 'darija' | 'ar' | 'en';

const LITERS_PER_SUITCASE = 70;
const SUPERCAR_BRANDS = new Set([
  'ferrari', 'lamborghini', 'mclaren', 'bugatti', 'aston martin', 'bentley', 'rolls-royce', 'maserati',
]);

const FAMILY_BODY_TYPES = new Set(['monospace', 'suv', 'break', 'berline', 'citadine']);

type BrandPreference = { name: string; apiValue: string };

function normalizeBrandText(value: string): string {
  return value
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
    .replace(/\s+/g, ' ');
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function extractBrandPreference(text: string): BrandPreference | null {
  const normalizedText = normalizeBrandText(text);
  if (!normalizedText) return null;

  // Match the longest names first so "DS Automobiles" wins over "DS" and
  // add the common short form for hyphenated names such as Mercedes-Benz.
  const candidates = POPULAR_BRANDS.flatMap((brand) => {
    const aliases = new Set([
      brand.name,
      brand.slug.replace(/-/g, ' '),
      ...(brand.name.includes('-') ? [brand.name.split('-')[0]] : []),
    ]);
    return [...aliases].map((alias) => ({
      alias: normalizeBrandText(alias),
      name: brand.name,
      apiValue: brand.name,
    }));
  })
    .filter((candidate) => candidate.alias.length > 1)
    .sort((a, b) => b.alias.length - a.alias.length);

  const knownBrand = candidates.find((candidate) => (
    new RegExp(`(?:^| )${escapeRegExp(candidate.alias)}(?:$| )`, 'i').test(normalizedText)
  ));
  if (knownBrand) return knownBrand;

  // Keep an explicitly requested, unknown make strict as well. This prevents
  // a request such as "I want a Lamborghini" from silently becoming a full
  // catalogue recommendation when that make is not available locally.
    const genericVehicleTerms = new Set([
    'car', 'cars', 'vehicle', 'vehicles', 'suv', 'model', 'models',
    'voiture', 'voitures', 'vehicule', 'vehicules', 'véhicule', 'véhicules',
    'family', 'familiale', 'familial', 'electric', 'electrique', 'hybrid',
    'hybride', 'diesel', 'essence', 'safe', 'safest', 'secure',
    'city', 'citadine', 'berline', 'sedan', 'saloon', 'coupe', 'cabriolet',
    'convertible', 'break', 'estate', 'wagon', 'pickup', 'van', 'monospace',
    'utilitaire', 'compact', 'compacte', 'hatchback',
  ]);
  const unknownMatch = normalizedText.match(/(?:^| )(?:(?:i|je) )?(?:want|need|buy|looking for|show me|find me|cherche|recherche|acheter|veux|cherche) (?:a|an|the|une|un|une voiture|un vehicule|voiture|véhicule)? ?([a-z][a-z-]+)(?:$| )/i);
  const unknownBrand = unknownMatch?.[1];
  if (unknownBrand && !genericVehicleTerms.has(unknownBrand)) {
    return { name: unknownBrand, apiValue: unknownBrand };
  }
  return null;
}

const safetyPreferencePattern = /\b(safe|safest|safety|security|secure|sécurité|securite|sûr|sûre|sûreté|crash|ncap|airbag|السلامة|آمن|أمان)\b/i;
const maxNcapPreferencePattern = /(?:highest ncap|note ncap maximale|ncap maximale|note maximale|highest ncap rating|5\s*(?:stars?|étoiles?|★)|أعلى تقييم|أعلى نقطة)/i;
const goodNcapPreferencePattern = /(?:good safety|bonne s[eé]curit[eé]|4\s*(?:stars?|étoiles?|★)|سلامة جيدة|سلامة مزيانة)/i;

// Age and gender describe the client profile, not vehicle catalogue fields.
// Recognise them so a natural request such as "a car for 22 years old" starts
// the discovery flow instead of being sent to the semantic search as an
// over-constrained query.
const agePreferencePattern = /\b(?:\d{1,3}\s*(?:years?[- ]?old|ans?|an|3am))\b|\b(?:age|âge)\s*[:：-]?\s*\d{1,3}\b|\b\d{1,3}\s*(?:عام|سنة)\b|\b(?:عام|سنة)\s*\d{1,3}\b|\b3omr\w*\s*\d{1,3}\b|\b(?:i['’]?m|i am|j['’]?ai|j ai|عمري|عندي)\s*\d{1,3}\b/i;
const genderPreferencePattern = /\b(?:woman|women|female|man|men|male|girl|boy|femme|homme|fille|garçon|lmra|l\s*mra|mra|raj[e]?l|l\s*raj[e]?l)\b|(?:للمرأة|للمرا|للنساء|لرجل|للراجل|للرجال)/i;

function getNcapScore(car: Pick<Car, 'ncap_rating'>): number {
  const rating = String(car.ncap_rating || '').replace(',', '.');
  const match = rating.match(/(?:^|\s)([0-5](?:\.\d+)?)\s*(?:\/\s*5|(?:stars?|étoiles?))?/i);
  if (!match) return -1;
  const score = Number(match[1]);
  return Number.isFinite(score) ? Math.min(5, Math.max(0, score)) : -1;
}

function sortForSafety(cars: Car[], safetyRequested: boolean): Car[] {
  if (!safetyRequested) return cars;
  return cars
    .map((car, index) => ({ car, index, ncapScore: getNcapScore(car) }))
    .sort((a, b) => b.ncapScore - a.ncapScore || a.index - b.index)
    .map(({ car }) => car);
}

async function loadAllCatalogueVehicles(): Promise<Car[]> {
  const firstPage = await vehicleService.getVehicles({ page: 1, page_size: 100 });
  if (firstPage.pages <= 1) return firstPage.items;

  const remainingPages = await Promise.all(
    Array.from({ length: firstPage.pages - 1 }, (_, index) => (
      vehicleService.getVehicles({ page: index + 2, page_size: 100 })
    )),
  );
  return [firstPage.items, ...remainingPages.map((page) => page.items)].flat();
}

export const LANGUAGE_OPTIONS: Array<{ value: ChatLanguage; label: string; nativeLabel: string }> = [
  { value: 'fr', label: 'Français', nativeLabel: 'Français' },
  { value: 'darija', label: 'Darija', nativeLabel: 'الدارجة' },
  { value: 'ar', label: 'العربية', nativeLabel: 'العربية' },
  { value: 'en', label: 'English', nativeLabel: 'English' },
];

/** The UI depends on this contract, never on FastAPI response shapes. */
export interface RecommendationClient {
  detectRecommendationIntent(message: string): Promise<boolean>;
  getNextQuestion(history: ChatTurn[], remainingCars: Car[]): Promise<NextQuestion | null>;
  applyAnswer(answer: string, history: ChatTurn[], remainingCars: Car[]): Promise<Car[]>;
}

export interface LanguageAwareRecommendationClient extends RecommendationClient {
  setLanguage(language: ChatLanguage): void;
}

// Route only car-finding requests to the recommendation tool. Automotive
// knowledge questions (engines, maintenance, gearboxes, safety, etc.) belong
// to the chatbot expert and must not start a discovery questionnaire.
const intentPattern = /\b(cherche|recherche|trouve|propose|recommande|choisir|choisis|conseil|acheter|achat|buy|recommend|suggest|choose|choosing|advice|looking\s+for|want\s+to\s+buy|want\s+(?:a\s+|an\s+|the\s+)?(?:[a-z-]+\s+){0,3}(?:car|suv|vehicle)|need\s+(?:a\s+)?(?:[a-z-]+\s+){0,3}(?:car|suv|vehicle)|find\s+me|show\s+me|help\s+me\s+choose|which\s+(?:car|suv|vehicle|model)|what\s+(?:car|suv|vehicle)\s+(?:should|can|fits)|best\s+(?:car|suv|vehicle)|safest\s+(?:car|suv|vehicle)|most\s+secure\s+(?:car|suv|vehicle)|(?:car|suv|vehicle)\s+for|family\s+car|family\s+vehicle|city\s+car|je\s+veux\s+acheter|je\s+veux\s+une\s+voiture|voiture\s+familiale?|véhicule\s+familial|voiture\s+pour|quel(?:le)?\s+voiture|quelle\s+voiture|meilleur(?:e)?\s+voiture|budget\s+(?:de|maximum|max)|mon\s+budget|bghit\s+(?:nchri|tomobil)|baghi\s+(?:nchri|tomobil)|kanqleb\s+3la|tomobil(?:e|a)?\s+dyal|tonobile\s+dyal|3a2ila|بغيت\s+(?:نشري|طوموبيل)|شراء|أبحث|أريد\s+(?:سيارة|طوموبيل)|ساعدني\s+(?:في\s+)?اختيار)\b/i;
const nonLatinIntentPattern = /(?:بغيت\s+(?:نشري|طوموبيل)|باغي\s+(?:نشري|طوموبيل)|كنقلب\s+على|kanqleb\s+3la|tomobil(?:e|a)?\s+dyal|tonobile\s+dyal|3a2ila|شراء|أبحث|أريد\s+(?:سيارة|طوموبيل)|ساعدني\s+(?:في\s+)?اختيار)/i;

// A direct request such as "car 300000dhs" is already a buying/search
// request even when it does not contain an explicit verb like "recommend".
// Keep technical questions out of this path: they should remain chatbot-only.
const budgetSearchPattern = /(?:\b(?:car|cars|vehicle|voiture|voitures|véhicule|tomobil|tomobila|سيارة|سيارات)\b[^\d]{0,24}|\b(?:budget|prix|price|have|j'ai|عندي)\b[^\d]{0,24})\d[\d\s.,]*(?:k|mad|dhs?|dh|dirhams?|درهم|دراهم|ألف)?\b/i;
const brandRequestPattern = /\b(?:want|need|looking\s+for|search(?:ing)?\s+for|show\s+me|find\s+me|buy|acheter|cherche|recherche|je\s+veux|je\s+cherche|بغيت|باغي|كنقلب)\b/i;

function hasProfilePreference(text: string): boolean {
  return agePreferencePattern.test(text) || genderPreferencePattern.test(text);
}

function hasAny(text: string, patterns: RegExp[]): boolean {
  return patterns.some((pattern) => pattern.test(text));
}

function profileText(history: ChatTurn[]): string {
  return history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' ').toLowerCase();
}

function dynamicQuestion(language: ChatLanguage, history: ChatTurn[], remainingCars: Car[]): NextQuestion | null {
  const text = profileText(history);
  const lastUserAnswer = [...history].reverse().find((turn) => turn.role === 'user')?.content || '';
  const budgetQuestionAsked = history.some((turn) => turn.role === 'assistant' && /budget|prix|price|ميزاني/i.test(turn.content));
  // Do not treat unrelated numeric answers (for example, "22 years old") as
  // a budget. Once the budget question has been asked, a bare number is a
  // valid answer because the user may enter just the MAD amount.
  const hasExplicitBudget = /\b(?:budget|prix|price|mad|dhs?|dh|dirhams?|درهم|دراهم)\b|ميزاني/i.test(text)
    || /\d[\d\s.,]*\s*(?:k|mad|dhs?|dirhams?|درهم|دراهم|ألف)\b/i.test(text)
    || /(?:under|below|less than|moins de|jusqu['’à]|between|entre|بين)\s*\d/i.test(text);
  const hasBudget = hasExplicitBudget
    || (budgetQuestionAsked && /\d/.test(lastUserAnswer));
  const hasUsage = hasAny(text, [/\b(city|ville|urban|highway|autoroute|motorway|mixed|mixte|daily|quotidien|commut|family trip|long trip|both|mostly city|mostly highway|city commute|highway driving)\b/i, /\b(مدينة|طريق|سفر|مخلط|يومي|العائلة|بجوج)\b/]);
  const hasFuel = hasAny(text, [/\b(diesel|petrol|essence|gasoline|hybrid|hybride|electric|électrique|ev|mazout|mazot|بنزين|مازوط|هجين|كهربائ)\b/i]);
  const hasTransmission = hasAny(text, [/\b(automatic|automatique|manual|manuelle|gearbox|boîte|boite|bva|bvm)\b/i, /\b(أوتوماتيك|اوتوماتيك|يدوي|بواط)\b/]);
  // “Family car” describes the use case, not a specific body style. Keep the
  // body-style question visible until the client chooses SUV, sedan, etc.
  const hasBody = hasAny(text, [/\b(suv|sedan|berline|hatchback|citadine|crossover|wagon|break|pickup|4x4|monospace)\b/i, /\b(سيدان|suv|سيتادين|كروس)\b/]);
  // A family request signals a need for space, but it does not answer the
  // suitcase-capacity question by itself.
  const hasSpace = hasAny(text, [/\b(children|kids|baby|trunk|boot|luggage|space|spacious|coffre|bagages|poussette|places|7 seats|suitcases?)\b/i, /\b(أطفال|شنطة|أمتعة|واسعة|بلايص|حقائب|فاليزات)\b/]);
  const questionWasAnswered = (pattern: RegExp) => history.some((turn, index) => (
    turn.role === 'assistant'
      && pattern.test(turn.content)
      && history.slice(index + 1).some((nextTurn) => nextTurn.role === 'user')
  ));
  // An explicit “No preference” still answers the dimension. Without this
  // check, the same performance/economy question is shown forever because
  // the answer contains none of the dimension keywords.
  const hasPriority = hasAny(text, [/\b(safe|safety|security|sécurité|economical|economy|consumption|consommation|performance|power|comfort|confort|reliable|fiable)\b/i, /\b(السلامة|اقتصادية|استهلاك|قوية|مريحة|موثوقة)\b/])
    || questionWasAnswered(/priority|importance|performance|power|acceleration|running costs|consumption|coûts|أولوية|الأداء|القوة|التسارع|استهلاك/i);

  const fuels = new Set(remainingCars.map((car) => car.fuel_type).filter(Boolean));
  const transmissions = new Set(remainingCars.map((car) => car.transmission).filter(Boolean));
  const bodies = new Set(remainingCars.map((car) => car.body_type).filter(Boolean));

  if (!hasBudget) return {
    question: language === 'en' ? 'What is your maximum budget in MAD?' : language === 'ar' ? 'ما هي ميزانيتك القصوى بالدرهم؟' : language === 'darija' ? 'شحال هي الميزانية القصوى ديالك بالدرهم؟' : 'Quel est votre budget maximum en MAD ?',
    // Budget is always selected with the adaptive range bar. Suggestions are
    // reserved for the non-numeric preferences that follow.
    options: [],
  };
  if (!hasUsage) return {
    question: language === 'en' ? 'How will you mainly use the car: city driving, highways, or a mix of both?' : language === 'ar' ? 'كيف ستستعمل السيارة غالباً: داخل المدينة، في الطريق السيار، أم الاثنين؟' : language === 'darija' ? 'فين غادي تستعمل الطوموبيل أكثر: فالمدينة، فالطريق السيار، ولا بجوج؟' : 'Vous roulerez surtout en ville, sur autoroute ou dans les deux ?',
    options: language === 'en'
      ? [{ label: 'Mostly city' }, { label: 'Mostly highway' }, { label: 'Both' }]
      : language === 'ar'
        ? [{ label: 'داخل المدينة' }, { label: 'في الطريق السيار' }, { label: 'الاثنين' }]
        : language === 'darija'
          ? [{ label: 'فالمدينة' }, { label: 'فالطريق السيار' }, { label: 'بجوج' }]
          : [{ label: 'Ville' }, { label: 'Autoroute' }, { label: 'Mixte' }],
  };
  const trunkValues = remainingCars.map((car) => car.trunk_volume_l).filter((value): value is number => Number.isFinite(value));
  const trunkMin = trunkValues.length ? Math.min(...trunkValues) : 0;
  const trunkMax = trunkValues.length ? Math.max(...trunkValues) : 0;
  const hasWideTrunkRange = trunkMax - trunkMin > 150;
  const suitcaseMin = Math.max(1, Math.round(trunkMin / LITERS_PER_SUITCASE));
  const suitcaseMax = Math.max(suitcaseMin + 1, Math.round(trunkMax / LITERS_PER_SUITCASE));
  const hasWideSuitcaseRange = suitcaseMax - suitcaseMin > 2;

  // Select the next missing dimension from the information that most varies
  // in the remaining pool. Budget and usage are hard-filter context; they do
  // not automatically mark an 8D preference as answered. This keeps the UI
  // aligned with the same Analyze → Select → Formulate loop as the backend.
  const ncapValues = remainingCars.map((car) => getNcapScore(car)).filter((value) => value >= 0);
  const powerValues = remainingCars.map((car) => car.engine_power_hp).filter((value): value is number => Number.isFinite(value));
  const dimensionCandidates = [
    { key: 'espace', covered: hasSpace, values: trunkValues.map(String), priority: 0 },
    { key: 'securite', covered: safetyPreferencePattern.test(text), values: ncapValues.map(String), priority: 1 },
    { key: 'cout_reel', covered: /economy|economical|consumption|consommation|conso|économique|استهلاك/i.test(text) || questionWasAnswered(/lower fuel consumption|running costs|coûts d’usage|مصاريف الاستعمال/i), values: [...fuels], priority: 2 },
    { key: 'praticite_urbaine', covered: questionWasAnswered(/compact|easy to park|facile à garer|parking|ركن/i), values: [...bodies], priority: 3 },
    { key: 'performance', covered: /performance|power|puissance|sportif|قوية/i.test(text) || questionWasAnswered(/power and acceleration|performance|puissance|التسارع|الأداء/i), values: powerValues.map(String), priority: 4 },
    { key: 'ecologie', covered: /hybrid|hybride|electric|électrique|ecolog|écolog|co2|بيئي/i.test(text) || questionWasAnswered(/hybrid or electric|hybride ou électrique|هجين|الهجين/i), values: [...fuels], priority: 5 },
    { key: 'motricite', covered: /4x4|awd|offroad|tout.?terrain|mountain|montagne|دفع رباعي/i.test(text) || questionWasAnswered(/four-wheel drive|all-wheel drive|4x4|awd|off-road|transmission intégrale|الدفع الرباعي/i), values: remainingCars.map((car) => String(Boolean(car.is_4x4))), priority: 6 },
  ];
  const lastAssistantQuestion = [...history].reverse().find((turn) => turn.role === 'assistant')?.content || '';
  const pendingDimension = dimensionCandidates.find((candidate) => {
    const tokens: Record<string, RegExp> = {
      espace: /luggage|suitcase|valise|coffre|bagages|passengers|حقائب/i,
      securite: /safety|security|sécurité|ncap|السلامة/i,
      cout_reel: /economy|consumption|consommation|coût|cost|استهلاك/i,
      praticite_urbaine: /city|ville|parking|compact|urbain/i,
      performance: /performance|power|puissance/i,
      ecologie: /hybrid|electric|électrique|ecolog|co2/i,
      motricite: /4x4|awd|offroad|terrain|motricité/i,
    };
    return Boolean(tokens[candidate.key]?.test(lastAssistantQuestion));
  });
  const selectableDimensions = dimensionCandidates
    .filter((candidate) => !candidate.covered && candidate !== pendingDimension)
    .map((candidate) => ({ ...candidate, diversity: new Set(candidate.values).size }))
    .filter((candidate) => candidate.diversity > 1 || (!remainingCars.length && candidate.key === 'securite'));
  const selectedDimension = [...selectableDimensions].sort((a, b) => b.diversity - a.diversity || a.priority - b.priority)[0]?.key;

  if (!hasSpace && (hasAny(text, [/\b(family|famille|children|kids|baby|poussette|trunk|boot|coffre|luggage|bagages|3a2ila)\b/i]) || remainingCars.some((car) => (car.seats || 5) >= 7) || hasWideTrunkRange)) return {
    question: language === 'en' ? 'How much luggage space do you need, in suitcases?' : language === 'ar' ? 'كم من مساحة الأمتعة تحتاج، بعدد الحقائب؟' : language === 'darija' ? 'شحال من بلاصة ديال الباݣاج كتحتاج، بعدد الفاليزات؟' : 'De combien de place pour les bagages avez-vous besoin, en valises ?',
    options: hasWideSuitcaseRange ? [] : suitcaseChoices(language, suitcaseMin, suitcaseMax),
    ...(hasWideSuitcaseRange ? { rangeBounds: { min: suitcaseMin, max: suitcaseMax, step: 1, label: language === 'en' ? 'Suitcase capacity' : language === 'ar' ? 'سعة الحقائب' : language === 'darija' ? 'سعة الفاليزات' : 'Capacité en valises' } } : {}),
  };

  if (selectedDimension === 'securite') return {
    question: language === 'en' ? 'How important is certified safety and a high NCAP rating to you?' : language === 'ar' ? 'ما مدى أهمية السلامة المعتمدة ونتيجة NCAP المرتفعة؟' : language === 'darija' ? 'شحال مهمة عندك السلامة ونتيجة NCAP؟' : 'Quelle importance accordez-vous à la sécurité certifiée et à une bonne note NCAP ?',
    options: language === 'en'
      ? [{ label: 'Highest NCAP rating (5★)' }, { label: 'Good safety (4★+)' }, { label: 'No preference' }]
      : language === 'ar'
        ? [{ label: 'أعلى تقييم NCAP (5★)' }, { label: 'سلامة جيدة (4★+)' }, { label: 'لا أفضلية' }]
        : language === 'darija'
          ? [{ label: 'أعلى نقطة NCAP (5★)' }, { label: 'سلامة مزيانة (4★+)' }, { label: 'ما عنديش تفضيل' }]
          : [{ label: 'Note NCAP maximale (5★)' }, { label: 'Bonne sécurité (4★+)' }, { label: 'Pas de préférence' }],
  };
  if (selectedDimension === 'cout_reel') return {
    question: language === 'en' ? 'Would you prioritize lower fuel consumption and running costs?' : language === 'ar' ? 'هل تفضل استهلاكاً وتكاليف تشغيل أقل؟' : language === 'darija' ? 'كتفضل الصرف ومصاريف الاستعمال يكونو قليلين؟' : 'Souhaitez-vous privilégier une consommation et des coûts d’usage réduits ?',
    options: language === 'en'
      ? [{ label: 'Economy & lower costs' }, { label: 'No preference' }]
      : language === 'ar'
        ? [{ label: 'توفير وتكاليف أقل' }, { label: 'لا أفضلية' }]
        : language === 'darija'
          ? [{ label: 'اقتصاد ومصاريف قليلة' }, { label: 'ما عنديش تفضيل' }]
          : [{ label: 'Économie & coûts réduits' }, { label: 'Pas de préférence' }],
  };
  if (selectedDimension === 'praticite_urbaine') return {
    question: language === 'en' ? 'For city driving, do you prefer a compact car that is easy to park?' : language === 'ar' ? 'للاستعمال داخل المدينة، هل تفضل سيارة صغيرة وسهلة الركن؟' : language === 'darija' ? 'فالمدينة، كتفضل طوموبيل صغيرة وساهلة فالباركينغ؟' : 'Pour la ville, préférez-vous une voiture compacte et facile à garer ?',
    options: language === 'en'
      ? [{ label: 'Compact (easy to park)' }, { label: 'More interior space' }]
      : language === 'ar'
        ? [{ label: 'حجم مدمج (سهل الركن)' }, { label: 'مساحة داخلية أكبر' }]
        : language === 'darija'
          ? [{ label: 'صغيرة وساهلة فالركنة' }, { label: 'بلاصة أكثر' }]
          : [{ label: 'Format compact (facile à garer)' }, { label: 'Plus d’espace intérieur' }],
  };
  if (selectedDimension === 'performance') return {
    question: language === 'en' ? 'Do you prioritize power and acceleration over lower running costs?' : language === 'ar' ? 'هل تفضل القوة والتسارع على انخفاض تكاليف التشغيل؟' : language === 'darija' ? 'كتفضل القوة والتسارع ولا مصاريف قليلة؟' : 'Privilégiez-vous la puissance et les reprises plutôt que les coûts d’usage réduits ?',
    options: language === 'en'
      ? [{ label: 'Power and acceleration' }, { label: 'Lower running costs' }]
      : language === 'ar'
        ? [{ label: 'القوة والتسارع' }, { label: 'تكاليف تشغيل أقل' }]
        : language === 'darija'
          ? [{ label: 'القوة والتسارع' }, { label: 'مصاريف قليلة' }]
          : [{ label: 'Puissance & reprises' }, { label: 'Coûts d’usage réduits' }],
  };
  if (selectedDimension === 'ecologie') return {
    question: language === 'en' ? 'Is hybrid or electric power a priority for you?' : language === 'ar' ? 'هل المحرك الهجين أو الكهربائي أولوية بالنسبة لك؟' : language === 'darija' ? 'واش الهجين ولا الكهربائي أولوية عندك؟' : 'La motorisation hybride ou électrique est-elle une priorité pour vous ?',
    options: language === 'en'
      ? [{ label: 'Hybrid or Electric' }, { label: 'Petrol / Diesel' }, { label: 'No preference' }]
      : language === 'ar'
        ? [{ label: 'هجين أو كهربائي' }, { label: 'بنزين / ديزل' }, { label: 'لا أفضلية' }]
        : language === 'darija'
          ? [{ label: 'هجين ولا كهربائي' }, { label: 'ليصانص ولا مازوط' }, { label: 'ما عنديش تفضيل' }]
          : [{ label: 'Hybride ou Électrique' }, { label: 'Essence / Diesel' }, { label: 'Pas de préférence' }],
  };
  if (selectedDimension === 'motricite') return {
    question: language === 'en'
      ? 'Do you need all-wheel drive (4x4 / AWD)?'
      : language === 'ar'
        ? 'هل تحتاج إلى دفع رباعي (4x4 / AWD)؟'
        : language === 'darija'
          ? 'واش كتحتاج الدفع الرباعي (4x4)؟'
          : 'Avez-vous besoin d’une transmission 4x4 / intégrale (AWD) ?',
    options: language === 'en'
      ? [{ label: 'Yes, 4x4 / AWD' }, { label: 'Standard (2WD)' }, { label: 'No preference' }]
      : language === 'ar'
        ? [{ label: 'دفع رباعي (4x4 / AWD)' }, { label: 'دفع ثنائي عادي (2WD)' }, { label: 'لا أفضلية' }]
        : language === 'darija'
          ? [{ label: 'دفع رباعي (4x4)' }, { label: 'دفع عادي (2WD)' }, { label: 'ما عنديش تفضيل' }]
          : [{ label: '4x4 / Intégrale (AWD)' }, { label: '2 roues motrices (Standard)' }, { label: 'Pas de préférence' }],
  };

  if (!hasFuel && fuels.size > 1) return {
    question: language === 'en' ? 'Which fuel type suits you best?' : language === 'ar' ? 'أي نوع وقود يناسبك أكثر؟' : language === 'darija' ? 'شنو نوع الكاربيرون اللي كيناسبك أكثر؟' : 'Quel carburant vous convient le mieux ?',
    options: [...fuels].slice(0, 4).map((fuel) => ({ label: fuel, value: fuel })),
  };
  if (!hasTransmission && transmissions.size > 1) return {
    question: language === 'en' ? 'Do you prefer an automatic or manual gearbox?' : language === 'ar' ? 'هل تفضل ناقل حركة أوتوماتيكي أم يدوي؟' : language === 'darija' ? 'كتفضل بواط أوتوماتيك ولا مانيويل؟' : 'Préférez-vous une boîte automatique ou manuelle ?',
    options: [{ label: language === 'en' ? 'Automatic' : 'Automatique' }, { label: language === 'en' ? 'Manual' : 'Manuelle' }],
  };
  if (!hasBody && bodies.size > 1) return {
    question: language === 'en' ? 'Which body style fits your needs best?' : language === 'ar' ? 'أي نوع هيكل يناسب احتياجاتك أكثر؟' : language === 'darija' ? 'شنو هو شكل الطوموبيل اللي كيناسبك أكثر؟' : 'Quel format de carrosserie correspond le mieux à vos besoins ?',
    options: [...bodies].slice(0, 4).map((body) => ({ label: body, value: body })),
  };
  if (!hasPriority) return {
    question: language === 'en' ? 'What matters most to you: economy, safety, comfort, or performance?' : language === 'ar' ? 'ما الأولوية الأهم لك: الاقتصاد، السلامة، الراحة أم الأداء؟' : language === 'darija' ? 'شنو هي الحاجة اللي مهمة عندك أكثر: الاقتصاد، السلامة، الراحة ولا الأداء؟' : 'Quelle est votre priorité : économie, sécurité, confort ou performance ?',
    options: language === 'en'
      ? [{ label: 'Economy' }, { label: 'Safety' }, { label: 'Comfort' }, { label: 'Performance' }]
      : language === 'ar'
        ? [{ label: 'الاقتصاد' }, { label: 'السلامة' }, { label: 'الراحة' }, { label: 'الأداء' }]
        : language === 'darija'
          ? [{ label: 'الاقتصاد' }, { label: 'السلامة' }, { label: 'الراحة' }, { label: 'الأداء' }]
          : [{ label: 'Économie' }, { label: 'Sécurité' }, { label: 'Confort' }, { label: 'Performance' }],
  };
  // All supported criteria are complete. The caller should present the final
  // shortlist instead of asking an empty, generic question.
  return null;
}

function extractMaximumBudget(query: string): number | null {
  const range = extractBudgetRange(query);
  if (range) {
    return range.max;
  }
  const match = query.match(/(?:under|below|less than|max(?:imum)?|budget|have|avec|moins de|jusqu['’à]|≤)?\s*(\d[\d\s.,]*)\s*(k|000|mad|dhs?|dh|dirhams?|دراهم?|ألف)?/i);
  if (!match) return null;
  const value = Number(match[1].replace(/[\s.,]/g, ''));
  if (!Number.isFinite(value) || value <= 0) return null;
  const suffix = (match[2] || '').toLowerCase();
  return suffix === 'k' || suffix === '000' || suffix === 'ألف' ? value * 1000 : value;
}

function extractBudgetRange(query: string): { min: number; max: number } | null {
  const match = query.match(/(?:between|entre|بين)\s*(\d[\d\s.,]*)\s*(?:and|et|و|[-–])\s*(\d[\d\s.,]*)/i);
  if (!match) return null;
  const min = Number(match[1].replace(/[\s.,]/g, ''));
  const max = Number(match[2].replace(/[\s.,]/g, ''));
  return Number.isFinite(min) && Number.isFinite(max) && min > 0 && max >= min
    ? { min, max }
    : null;
}

function extractJson<T>(text: string): T | null {
  const match = text.match(/\{[\s\S]*\}/);
  if (!match) return null;
  try {
    return JSON.parse(match[0]) as T;
  } catch {
    return null;
  }
}

async function streamText(prompt: string, history: ChatTurn[], language: ChatLanguage): Promise<string> {
  let response = '';
  await chatbotService.streamMessage(
    prompt,
    history,
    (chunk) => { response += chunk; },
    undefined,
    undefined,
    language,
  );
  return response;
}

export class FastApiRecommendationClient implements RecommendationClient {
  private language: ChatLanguage = 'fr';

  setLanguage(language: ChatLanguage) { this.language = language; }

  async detectRecommendationIntent(message: string): Promise<boolean> {
    // Keep intent detection local. A second LLM request here made every
    // ordinary chat message wait for the slowest service in the stack.
    const isBrandPurchase = brandRequestPattern.test(message) && Boolean(extractBrandPreference(message));
    return intentPattern.test(message) || nonLatinIntentPattern.test(message) || budgetSearchPattern.test(message)
      || hasProfilePreference(message) || isBrandPurchase;
  }

  async getNextQuestion(history: ChatTurn[], remainingCars: Car[]): Promise<NextQuestion | null> {
    const question = dynamicQuestion(this.language, history, remainingCars);
    if (!question) return null;
    // Budget is the first qualification step. Keep it available even when a
    // semantic search has temporarily returned a very small candidate set;
    // otherwise the UI shows a budget prompt without its preference control.
    if (/budget|prix|ميزاني/i.test(question.question)) {
      // Keep the preference bar tied to the candidates currently visible in
      // the catalogue. Zero-price records are placeholders and are ignored.
      let prices = remainingCars
        .map((car) => Number(car.price))
        .filter((price) => Number.isFinite(price) && price > 0);
      const requestedBrand = extractBrandPreference(profileText(history));

      // The first recommendation turn can receive an incomplete candidate
      // set, so fall back to the full positive-price catalogue in that case.
      // Once a brand was requested, however, the range must stay scoped to
      // that brand; using the global catalogue here makes a Mercedes request
      // display unrelated price bounds.
      if (!requestedBrand && (prices.length < 2 || Math.max(...prices) - Math.min(...prices) <= 100000)) {
        const [lowest, highest] = await Promise.all([
          vehicleService.getVehicles({ page: 1, page_size: 1, price_min: 1, sort_by: 'price', sort_order: 'asc' }),
          vehicleService.getVehicles({ page: 1, page_size: 1, price_min: 1, sort_by: 'price', sort_order: 'desc' }),
        ]);
        prices = [Number(lowest.items[0]?.price), Number(highest.items[0]?.price)]
          .filter((price) => Number.isFinite(price) && price > 0);
      }

      const min = prices.length ? Math.min(...prices) : 0;
      const max = prices.length ? Math.max(...prices) : 0;
      if (prices.length && Number.isFinite(min) && Number.isFinite(max)) {
        return { ...question, rangeBounds: { min, max, step: 5000, label: 'Budget catalogue' } };
      }
    }
    return question;
  }

  async applyAnswer(answer: string, history: ChatTurn[], remainingCars: Car[]): Promise<Car[]> {
        // `history` already contains the current answer. Duplicating it made the
    // recommender overweight the last criterion and prevented stable refinement.
    const query = history
      .map((turn) => `${turn.role}: ${turn.content}`)
      .join('\n');
    const userTurns = history.filter((turn) => turn.role === 'user').length;
    const historyText = history.map((turn) => turn.content).join(' ');
    // The candidate pool already contains the constraints from previous
    // answers. Only apply the criterion answered in this turn; re-reading an
    // old budget range from the full history would swallow later answers such
    // as suitcase capacity or body style.
    const previousAssistantQuestion = [...history]
      .reverse()
      .find((turn) => turn.role === 'assistant')?.content || '';
    const budgetAnswerContext = /\b(budget|price|prix|mad|dhs?|dh|dirhams?|درهم|دراهم)\b|ميزاني/i.test(answer)
      || /budget|prix|price|ميزاني/i.test(previousAssistantQuestion);
    // “between 3 and 13” is also used by the suitcase control. Require
    // budget context before interpreting a numeric range as a price range.
    const budgetRange = budgetAnswerContext ? extractBudgetRange(answer) : null;
    const budget = extractMaximumBudget(historyText);
    const suitcaseRange = extractSuitcaseRange(answer);
    const suitcaseMinimum = extractSuitcaseMinimum(answer);
    const bodyPreference = extractBodyPreference(answer);
    const fuelPreference = extractFuelPreference(answer);
    const answerBrand = extractBrandPreference(answer);
    const profilePreferenceOnly = hasProfilePreference(answer)
      && !budgetRange && !suitcaseRange && !bodyPreference && !fuelPreference
      && !extractTransmissionPreference(answer) && !answerBrand;
    const requestedBrand = extractBrandPreference(
      history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
    );
    const safetyRequested = safetyPreferencePattern.test(
      history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
    );
    const scopedRemainingCars = requestedBrand
      ? remainingCars.filter((car) => normalizeBrandText(car.brand) === normalizeBrandText(requestedBrand.name))
      : remainingCars;

    // There is deliberately no gender or age column in the catalogue. Keep
    // these preferences as conversational context and continue asking useful
    // objective questions; never turn them into a stereotype-based hard filter
    // or let them produce an accidental zero-result recommendation.
    if (profilePreferenceOnly) {
      const profilePool = scopedRemainingCars.length ? scopedRemainingCars : await loadAllCatalogueVehicles();
      return sortForSafety(profilePool, safetyRequested);
    }

    // A requested brand is a hard constraint, not a semantic hint. Query the
    // catalogue directly so an unavailable brand produces zero results rather
    // than silently falling back to unrelated vehicles.
    if (answerBrand) {
      const response = await vehicleService.getVehicles({
        brand: answerBrand.apiValue,
        page: 1,
        page_size: 100,
      });
      const answerBudget = extractMaximumBudget(answer);
      const brandItems = answerBudget !== null
        ? response.items.filter((car) => Number(car.price) > 0 && Number(car.price) <= answerBudget)
        : response.items;
      return sortForSafety(brandItems, safetyRequested);
    }

    // A selected preference range is an exact catalogue filter. Do this
    // before semantic ranking so both slider endpoints affect the result.
    if (budgetRange) {
      // Keep the current recommendation candidates. Querying a fresh page
      // here could expand a narrowed list (for example, 10 candidates could
      // suddenly become 20 after a budget selection).
      if (scopedRemainingCars.length) {
        return sortForSafety(scopedRemainingCars.filter((car) => {
          const price = Number(car.price);
          return Number.isFinite(price) && price > 0 && price >= budgetRange.min && price <= budgetRange.max;
        }), safetyRequested);
      }

      const response = await vehicleService.getVehicles({
        ...(requestedBrand ? { brand: requestedBrand.apiValue } : {}),
        price_min: budgetRange.min,
        price_max: budgetRange.max,
        page: 1,
        // A range selection belongs to the recommendation flow. Never turn
        // it into a full catalogue request when the local candidate state is
        // temporarily empty; the UI must remain a three-car shortlist.
        page_size: 3,
      });
      return sortForSafety(response.items.slice(0, 3), safetyRequested);
    }

    // A single answer can contain several hard filters (for example,
    // "electric SUV"). Apply them together so the second criterion cannot
    // accidentally reintroduce petrol or unrelated body styles.
    if (bodyPreference && fuelPreference) {
      const matches = scopedRemainingCars.filter((car) => (
        normalizeBodyType(car.body_type) === bodyPreference && car.fuel_type === fuelPreference
      ));
      if (matches.length) return sortForSafety(matches, safetyRequested);
      const catalogueMatches = applyConversationConstraints(
        await loadAllCatalogueVehicles(),
        history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
      ).filter((car) => normalizeBodyType(car.body_type) === bodyPreference && car.fuel_type === fuelPreference);
      return sortForSafety(catalogueMatches, safetyRequested);
    }

    if (suitcaseRange) {
      const matchesCurrentPool = scopedRemainingCars.filter((car) => {
        const trunkLiters = Number(car.trunk_volume_l);
        if (!Number.isFinite(trunkLiters)) return false;
        const suitcases = Math.round(trunkLiters / LITERS_PER_SUITCASE);
        return suitcases >= suitcaseRange.min && suitcases <= suitcaseRange.max;
      });
      if (matchesCurrentPool.length) return sortForSafety(matchesCurrentPool, safetyRequested);

      // Semantic ranking can temporarily omit a valid luggage-size match.
      // Recover from the full catalogue while retaining the budget range
      // already selected earlier in the conversation.
      const catalogueMatches = applyConversationConstraints(
        await loadAllCatalogueVehicles(),
        history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
      );
      return sortForSafety(catalogueMatches, safetyRequested);
    }

    if (suitcaseMinimum !== null) {
      return sortForSafety(scopedRemainingCars.filter((car) => {
        const trunkLiters = Number(car.trunk_volume_l);
        if (!Number.isFinite(trunkLiters)) return false;
        return Math.round(trunkLiters / LITERS_PER_SUITCASE) >= suitcaseMinimum;
      }), safetyRequested);
    }

        // Motricite / Drivetrain constraint (4x4 vs 2WD)
    const isAwdYes = /\b(4x4|awd|integrale|intégrale|دفع رباعي|رباعي)\b/i.test(answer)
      && !/\b(no|non|pas|2wd|deux|ثنائي)\b/i.test(answer);
    const isAwdNo = /\b(2wd|standard|2 roues|deux roues|دفع ثنائي|ثنائي)\b/i.test(answer)
      || (/\b(no|non|pas besoin|لا)\b/i.test(answer) && /4x4|awd|transmission intégrale|off-road|الدفع الرباعي/i.test(previousAssistantQuestion));

    if (isAwdYes) {
      const currentMatches = scopedRemainingCars.filter((car) => Boolean(car.is_4x4));
      if (currentMatches.length) return sortForSafety(currentMatches, safetyRequested);
      const catalogueMatches = applyConversationConstraints(
        await loadAllCatalogueVehicles(),
        history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
      ).filter((car) => Boolean(car.is_4x4));
      return sortForSafety(catalogueMatches, safetyRequested);
    } else if (isAwdNo) {
      const currentMatches = scopedRemainingCars.filter((car) => !car.is_4x4);
      if (currentMatches.length) return sortForSafety(currentMatches, safetyRequested);
      const catalogueMatches = applyConversationConstraints(
        await loadAllCatalogueVehicles(),
        history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
      ).filter((car) => !car.is_4x4);
      return sortForSafety(catalogueMatches, safetyRequested);
    }

    if (bodyPreference) {
      const currentMatches = scopedRemainingCars.filter((car) => {
        if (bodyPreference === 'citadine' && SUPERCAR_BRANDS.has(normalizeBrandText(car.brand))) return false;
        return normalizeBodyType(car.body_type) === bodyPreference;
      });
      if (currentMatches.length) return sortForSafety(currentMatches, safetyRequested);
      const catalogueMatches = applyConversationConstraints(
        await loadAllCatalogueVehicles(),
        history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
      );
      return sortForSafety(catalogueMatches, safetyRequested);
    }

    if (fuelPreference) {
      const currentMatches = scopedRemainingCars.filter((car) => car.fuel_type === fuelPreference);
      if (currentMatches.length) return sortForSafety(currentMatches, safetyRequested);
      const catalogueMatches = applyConversationConstraints(
        await loadAllCatalogueVehicles(),
        history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
      ).filter((car) => car.fuel_type === fuelPreference);
      return sortForSafety(catalogueMatches, safetyRequested);
    }

    const transmissionPreference = extractTransmissionPreference(answer);
    if (transmissionPreference) {
      const currentMatches = scopedRemainingCars.filter((car) => car.transmission === transmissionPreference);
      if (currentMatches.length) return sortForSafety(currentMatches, safetyRequested);
      const catalogueMatches = applyConversationConstraints(
        await loadAllCatalogueVehicles(),
        history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
      ).filter((car) => car.transmission === transmissionPreference);
      return sortForSafety(catalogueMatches, safetyRequested);
    }

    // Safety is an explicit ranking and filtering criterion.
    // When the user specifies "Note NCAP maximale" (5★) or "Bonne sécurité" (>= 4★),
    // we must strictly filter for vehicles satisfying the requested NCAP rating.
    const isMaxSafety = maxNcapPreferencePattern.test(answer) || (userTurns > 1 && maxNcapPreferencePattern.test(historyText));
    const isGoodSafety = goodNcapPreferencePattern.test(answer) || (userTurns > 1 && goodNcapPreferencePattern.test(historyText));

    if (isMaxSafety || isGoodSafety) {
      if (requestedBrand && !scopedRemainingCars.length) return [];

      // 1. Priorité absolue : consulter et filtrer les voitures recommandées à l'instant T
      if (scopedRemainingCars.length > 0) {
        const currentSafeMatches = scopedRemainingCars.filter((car) => {
          const score = getNcapScore(car);
          return isMaxSafety ? score === 5 : score >= 4;
        });

        // Si des voitures de l'instant T répondent au critère, on garde et classe celles-ci
        if (currentSafeMatches.length > 0) {
          return sortForSafety(currentSafeMatches, true);
        }

        // Si l'utilisateur voulait la sécurité max mais que la sélection actuelle n'a pas de 5★,
        // on conserve en priorité les voitures de l'instant T qui ont au moins 4★
        if (isMaxSafety) {
          const currentFourStars = scopedRemainingCars.filter((car) => getNcapScore(car) >= 4);
          if (currentFourStars.length > 0) {
            return sortForSafety(currentFourStars, true);
          }
        }

        // Si aucune des voitures de l'instant n'a 4+ étoiles, on trie celles de l'instant par score de sécurité
        const ratedCars = scopedRemainingCars.filter((car) => getNcapScore(car) > 0);
        if (ratedCars.length > 0) {
          return sortForSafety(ratedCars, true);
        }
      }

      // 2. Si le groupe de l'instant était vide, chercher dans le catalogue avec les contraintes existantes
      const allVehicles = await loadAllCatalogueVehicles();
      const constrainedCatalogue = applyConversationConstraints(allVehicles, historyText);

      const catalogueSafeMatches = constrainedCatalogue.filter((car) => {
        const score = getNcapScore(car);
        return isMaxSafety ? score === 5 : score >= 4;
      });

      if (catalogueSafeMatches.length > 0) {
        return sortForSafety(catalogueSafeMatches, true);
      }

      if (isMaxSafety) {
        const fallbackFourStars = constrainedCatalogue.filter((car) => getNcapScore(car) >= 4);
        if (fallbackFourStars.length > 0) {
          return sortForSafety(fallbackFourStars, true);
        }
      }

      const fallbackPool = scopedRemainingCars.length ? scopedRemainingCars : constrainedCatalogue;
      return sortForSafety(fallbackPool, true);
    }

    if (safetyRequested) {
      if (requestedBrand && !scopedRemainingCars.length) return [];
      const safetyPool = scopedRemainingCars.length
        ? scopedRemainingCars
        : await loadAllCatalogueVehicles();
      return sortForSafety(safetyPool, true);
    }

    // A clear first-turn budget is an exact catalogue filter, not a semantic
    // search. Load real vehicles immediately so the catalogue never shows a
    // misleading zero-match state for requests such as "car 300000dhs".
    if (userTurns === 1 && budget !== null) {
      if (safetyRequested) {
        const safetyPool = await loadAllCatalogueVehicles();
        return sortForSafety(safetyPool.filter((car) => Number(car.price) > 0 && car.price <= budget), true);
      }
      const response = await vehicleService.getVehicles({ price_max: budget, page: 1, page_size: 20 });
      return sortForSafety(response.items, safetyRequested);
    }

    // Let the recommendation engine decide when the set is small enough. The
    // number of questions is data-driven, not tied to a fixed turn count.
    // Use a broad internal pool for ranking. The UI only displays three
    // vehicles, but a 20-item request can omit valid family SUVs/sedans before
    // the later budget and preference answers are applied.
    const pageSize = 100;
    // An unavailable requested brand must stay unavailable. Never let a
    // semantic response or fallback reintroduce vehicles from other brands.
    if (requestedBrand && !scopedRemainingCars.length) return [];
    const response = await recommendationService.search({ query, page: 1, page_size: pageSize });
    // Preserve the current catalogue set if semantic ranking temporarily
    // returns no rows; a transient ranking miss must never display zero cars.
    if (!response.items.length && scopedRemainingCars.length) {
      return sortForSafety(scopedRemainingCars.slice(0, Math.max(3, Math.ceil(scopedRemainingCars.length / 2))), safetyRequested);
    }
    // Keep a broad candidate pool for the multi-step questionnaire. The UI
    // renders only three cars, but truncating the pool here would permanently
    // discard valid matches (for example other family vehicles).
    const rankedPool = requestedBrand ? scopedRemainingCars : remainingCars;
    const allowedIds = rankedPool.length ? new Set(rankedPool.map((car) => car.id)) : null;
    const compatibleRankedItems = allowedIds
      ? response.items.filter((item) => allowedIds.has(item.vehicle_id))
      : response.items;
    const candidateLimit = rankedPool.length
      ? Math.max(3, Math.ceil(rankedPool.length / 2))
      : pageSize;
    const rankedItems = compatibleRankedItems.length
      ? compatibleRankedItems.slice(0, candidateLimit)
      : (rankedPool.length ? rankedPool.slice(0, candidateLimit).map((car) => ({ vehicle_id: car.id, match_score: 0, key_facts: [] })) : []);
    const details = await Promise.all(
      rankedItems.map(async (item) => {
        const existing = rankedPool.find((car) => car.id === item.vehicle_id);
        const vehicle = existing ?? await vehicleService.getVehicleById(item.vehicle_id);
        return { ...vehicle, match_score: item.match_score, key_facts: item.key_facts };
      }),
    );
    return sortForSafety(details, safetyRequested);
  }
}

function extractSuitcaseRange(query: string): { min: number; max: number } | null {
  const keyword = query.search(/suitcase|valise|حقائب|فاليزات/i);
  if (keyword < 0) return null;
  const numbers = query.slice(keyword, keyword + 120).match(/\d+/g);
  if (!numbers || numbers.length < 2) return null;
  const min = Number(numbers[0]);
  const max = Number(numbers[1]);
  return Number.isFinite(min) && Number.isFinite(max) && max >= min ? { min, max } : null;
}

function extractSuitcaseMinimum(query: string): number | null {
  const match = query.match(/(?:around|about|environ|environ\s+de|approximately|minimum|au moins|(?:space|place|capacit[ée]).{0,24})\s*(\d{1,2})\s*(?:suitcases?|valises?|حقائب|فاليزات)/i);
  if (!match) return null;
  const value = Number(match[1]);
  return Number.isFinite(value) && value > 0 ? value : null;
}

function extractBodyPreference(query: string): string | null {
  const normalized = query.toLowerCase();
  if (/\b(suv|crossover|4x4|d[ée]part\s+quatre|دفع رباعي|كروس)\b/i.test(normalized)) return 'suv';
  if (/\b(sedan|berline|saloon|سيدان)\b/i.test(normalized)) return 'berline';
  if (/\b(hatchback|citadine|city car|compact car|سيتادين)\b/i.test(normalized)) return 'citadine';
  if (/\b(wagon|break|estate)\b/i.test(normalized)) return 'break';
  if (/\b(pickup|pick-up|pick up|بيك ?أب)\b/i.test(normalized)) return 'pick_up';
  if (/\b(van|monospace|mpv)\b/i.test(normalized)) return 'monospace';
  if (/\b(utilitaire)\b/i.test(normalized)) return 'utilitaire';
  return null;
}

function normalizeBodyType(bodyType?: string | null): string {
  const normalized = (bodyType || '').toLowerCase().replace(/[-_]/g, ' ');
  if (/suv|crossover|4x4|دفع رباعي|كروس/.test(normalized)) return 'suv';
  if (/berline|sedan|saloon|سيدان/.test(normalized)) return 'berline';
  if (/citadine|hatchback|city car|compact|سيتادين/.test(normalized)) return 'citadine';
  if (/break|wagon|estate/.test(normalized)) return 'break';
  if (/pick ?up|pickup|بيك/.test(normalized)) return 'pick_up';
  if (/monospace|mpv|van/.test(normalized)) return 'monospace';
  if (/utilitaire/.test(normalized)) return 'utilitaire';
  if (/coupe|coupé|gt|sport|supercar|berlinetta/.test(normalized)) return 'coupe';
  if (/cabriolet|convertible|spider|roadster/.test(normalized)) return 'cabriolet';
  return normalized.trim();
}

function isFamilyRequest(query: string): boolean {
  return /\b(family|famille|children|kids|baby|poussette|spacious|space|famille)\b/i.test(query)
    || /\b(العائلة|أطفال|واسعة|بلايص)\b/i.test(query);
}

function applyConversationConstraints(cars: Car[], userText: string): Car[] {
  let constrained = cars;
  const requestedBrand = extractBrandPreference(userText);
  const bodyPreference = extractBodyPreference(userText);
  const budgetRange = extractBudgetRange(userText);
  const suitcaseRange = extractSuitcaseRange(userText);

  if (requestedBrand) {
    constrained = constrained.filter((car) => normalizeBrandText(car.brand) === normalizeBrandText(requestedBrand.name));
  }
  if (bodyPreference) {
    constrained = constrained.filter((car) => {
      if (bodyPreference === 'citadine' && SUPERCAR_BRANDS.has(normalizeBrandText(car.brand))) {
        return false;
      }
      return normalizeBodyType(car.body_type) === bodyPreference;
    });
  } else if (isFamilyRequest(userText)) {
    constrained = constrained.filter((car) => FAMILY_BODY_TYPES.has(normalizeBodyType(car.body_type)));
  }
  if (budgetRange) {
    constrained = constrained.filter((car) => {
      const price = Number(car.price);
      return Number.isFinite(price) && price > 0 && price >= budgetRange.min && price <= budgetRange.max;
    });
  }
  if (suitcaseRange) {
    constrained = constrained.filter((car) => {
      const trunkLiters = Number(car.trunk_volume_l);
      if (!Number.isFinite(trunkLiters)) return false;
      const suitcases = Math.round(trunkLiters / LITERS_PER_SUITCASE);
      return suitcases >= suitcaseRange.min && suitcases <= suitcaseRange.max;
    });
  }
  if (maxNcapPreferencePattern.test(userText)) {
    const fiveStarCars = constrained.filter((car) => getNcapScore(car) === 5);
    if (fiveStarCars.length) {
      constrained = fiveStarCars;
    } else {
      const fourStarCars = constrained.filter((car) => getNcapScore(car) >= 4);
      if (fourStarCars.length) constrained = fourStarCars;
    }
  } else if (goodNcapPreferencePattern.test(userText)) {
    const safeCars = constrained.filter((car) => getNcapScore(car) >= 4);
    if (safeCars.length) constrained = safeCars;
  }
  return constrained;
}

function extractFuelPreference(query: string): Car['fuel_type'] | null {
  const normalized = query
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();
  if (/\b(diesel|gazoil|mazout|mazot|nafta|مازوط)\b/i.test(normalized)) return 'diesel';
  if (/\b(petrol|essence|gasoline|super|بنزين)\b/i.test(normalized)) return 'essence';
  if (/\b(hybride rechargeable|plug[- ]?in|phev)\b/i.test(normalized)) return 'hybride_rechargeable';
  if (/\b(hybrid|hybride|هجين)\b/i.test(normalized)) return 'hybride';
  if (/\b(electric|electrique|ev|كهربائي|كهربائ)\b/i.test(normalized)) return 'electrique';
  if (/\b(gpl)\b/i.test(normalized)) return 'gpl';
  return null;
}

function extractTransmissionPreference(query: string): Car['transmission'] | null {
  const normalized = query
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase();
  if (/\b(automatic|automatique|auto|bva|اوتوماتيك|أوتوماتيك)\b/i.test(normalized)) return 'automatique';
  if (/\b(manual|manuelle|bvm|يدوي)\b/i.test(normalized)) return 'manuelle';
  return null;
}

function suitcaseChoices(language: ChatLanguage, min: number, max: number): QuestionOption[] {
  const values = [...new Set([min, Math.round((min + max) / 2), max])];
  return values.map((value) => {
    if (language === 'fr') return { label: `${value} ${value > 1 ? 'valises' : 'valise'}`, value: `Je souhaite de la place pour environ ${value} valises` };
    if (language === 'darija') return { label: `${value} فاليزات`, value: `باغي بلاصة لحوالي ${value} فاليزات` };
    if (language === 'ar') return { label: `${value} حقائب`, value: `أحتاج مساحة لحوالي ${value} حقائب` };
    return { label: `${value} ${value > 1 ? 'suitcases' : 'suitcase'}`, value: `I need space for around ${value} suitcases` };
  });
}

export class MockRecommendationClient implements RecommendationClient {
  constructor(private readonly cars: Car[]) {}
  private language: ChatLanguage = 'fr';

  setLanguage(language: ChatLanguage) { this.language = language; }

  async detectRecommendationIntent(message: string): Promise<boolean> {
    return intentPattern.test(message) || nonLatinIntentPattern.test(message) || budgetSearchPattern.test(message)
      || (brandRequestPattern.test(message) && Boolean(extractBrandPreference(message)));
  }

  async getNextQuestion(history: ChatTurn[], remainingCars: Car[]): Promise<NextQuestion | null> {
    // A small result set is not proof that the questionnaire is complete.
    // Keep the mock aligned with the production client so local/demo flows do
    // not stop after the first three matches.
    if (history.filter((turn) => turn.role === 'user').length >= 6) return null;
    const brands = [...new Set(remainingCars.map((car) => car.brand))].slice(0, 4);
    return brands.length > 1
      ? { question: this.language === 'en' ? 'Do you prefer a specific brand?' : this.language === 'ar' ? 'هل تفضل علامة تجارية معينة؟' : this.language === 'darija' ? 'كاينة شي ماركة كتفضل؟' : 'Tu as une préférence de marque ?', options: brands.map((brand) => ({ label: brand, value: brand })) }
      : { question: this.language === 'en' ? 'What is your maximum budget?' : this.language === 'ar' ? 'ما هي ميزانيتك القصوى؟' : this.language === 'darija' ? 'شنو هو budget maximum ديالك؟' : 'Quel budget maximum souhaites-tu respecter ?', options: [{ label: 'Moins de 200 000 MAD' }, { label: '200 000–300 000 MAD' }, { label: 'Plus de 300 000 MAD' }] };
  }

  async applyAnswer(answer: string, _history: ChatTurn[], remainingCars: Car[]): Promise<Car[]> {
    const normalized = answer.toLowerCase();
    const byBrand = remainingCars.filter((car) => normalized.includes(car.brand.toLowerCase()));
    if (byBrand.length && byBrand.length < remainingCars.length) return byBrand;
    const budget = normalized.match(/(\d[\d\s.,]*)\s*(mad|dh|k)?/i);
    if (budget) {
      const value = Number(budget[1].replace(/[\s.,]/g, ''));
      if (Number.isFinite(value)) return remainingCars.filter((car) => car.price <= value);
    }
    return remainingCars.slice(0, Math.max(3, Math.ceil(remainingCars.length / 2)));
  }
}

export const recommendationClient = new FastApiRecommendationClient();
