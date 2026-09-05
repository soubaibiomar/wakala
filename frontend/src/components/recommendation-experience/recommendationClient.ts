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

export type BrandPreference = { name: string; apiValue: string; model?: string };

export const POPULAR_MODELS_TO_BRAND: Record<string, { brand: string; model: string }> = {
  // Dacia
  duster: { brand: 'Dacia', model: 'Duster' },
  sandero: { brand: 'Dacia', model: 'Sandero' },
  stepway: { brand: 'Dacia', model: 'Sandero Stepway' },
  logan: { brand: 'Dacia', model: 'Logan' },
  jogger: { brand: 'Dacia', model: 'Jogger' },
  bigster: { brand: 'Dacia', model: 'Bigster' },
  spring: { brand: 'Dacia', model: 'Spring' },
  lodgy: { brand: 'Dacia', model: 'Lodgy' },
  dokker: { brand: 'Dacia', model: 'Dokker' },
  // Renault
  clio: { brand: 'Renault', model: 'Clio' },
  megane: { brand: 'Renault', model: 'Megane' },
  captur: { brand: 'Renault', model: 'Captur' },
  austral: { brand: 'Renault', model: 'Austral' },
  arkana: { brand: 'Renault', model: 'Arkana' },
  twingo: { brand: 'Renault', model: 'Twingo' },
  kadjar: { brand: 'Renault', model: 'Kadjar' },
  symbioz: { brand: 'Renault', model: 'Symbioz' },
  scenic: { brand: 'Renault', model: 'Scenic' },
  rafale: { brand: 'Renault', model: 'Rafale' },
  espace: { brand: 'Renault', model: 'Espace' },
  kangoo: { brand: 'Renault', model: 'Kangoo' },
  express: { brand: 'Renault', model: 'Express' },
  // Peugeot
  '208': { brand: 'Peugeot', model: '208' },
  '308': { brand: 'Peugeot', model: '308' },
  '2008': { brand: 'Peugeot', model: '2008' },
  '3008': { brand: 'Peugeot', model: '3008' },
  '5008': { brand: 'Peugeot', model: '5008' },
  '508': { brand: 'Peugeot', model: '508' },
  '408': { brand: 'Peugeot', model: '408' },
  rifter: { brand: 'Peugeot', model: 'Rifter' },
  partner: { brand: 'Peugeot', model: 'Partner' },
  // Volkswagen
  golf: { brand: 'Volkswagen', model: 'Golf' },
  polo: { brand: 'Volkswagen', model: 'Polo' },
  tiguan: { brand: 'Volkswagen', model: 'Tiguan' },
  't-roc': { brand: 'Volkswagen', model: 'T-Roc' },
  troc: { brand: 'Volkswagen', model: 'T-Roc' },
  't-cross': { brand: 'Volkswagen', model: 'T-Cross' },
  tcross: { brand: 'Volkswagen', model: 'T-Cross' },
  touareg: { brand: 'Volkswagen', model: 'Touareg' },
  passat: { brand: 'Volkswagen', model: 'Passat' },
  taigo: { brand: 'Volkswagen', model: 'Taigo' },
  caddy: { brand: 'Volkswagen', model: 'Caddy' },
  // Hyundai
  tucson: { brand: 'Hyundai', model: 'Tucson' },
  i10: { brand: 'Hyundai', model: 'i10' },
  i20: { brand: 'Hyundai', model: 'i20' },
  i30: { brand: 'Hyundai', model: 'i30' },
  creta: { brand: 'Hyundai', model: 'Creta' },
  accent: { brand: 'Hyundai', model: 'Accent' },
  elantra: { brand: 'Hyundai', model: 'Elantra' },
  'santa fe': { brand: 'Hyundai', model: 'Santa Fe' },
  santafe: { brand: 'Hyundai', model: 'Santa Fe' },
  kona: { brand: 'Hyundai', model: 'Kona' },
  bayon: { brand: 'Hyundai', model: 'Bayon' },
  // Kia
  picanto: { brand: 'Kia', model: 'Picanto' },
  sportage: { brand: 'Kia', model: 'Sportage' },
  seltos: { brand: 'Kia', model: 'Seltos' },
  sorento: { brand: 'Kia', model: 'Sorento' },
  stonic: { brand: 'Kia', model: 'Stonic' },
  sonet: { brand: 'Kia', model: 'Sonet' },
  ceed: { brand: 'Kia', model: 'Ceed' },
  niro: { brand: 'Kia', model: 'Niro' },
  ev6: { brand: 'Kia', model: 'EV6' },
  ev9: { brand: 'Kia', model: 'EV9' },
  // Toyota
  yaris: { brand: 'Toyota', model: 'Yaris' },
  corolla: { brand: 'Toyota', model: 'Corolla' },
  rav4: { brand: 'Toyota', model: 'Rav-4' },
  'rav-4': { brand: 'Toyota', model: 'Rav-4' },
  'c-hr': { brand: 'Toyota', model: 'C-HR' },
  chr: { brand: 'Toyota', model: 'C-HR' },
  hilux: { brand: 'Toyota', model: 'Hilux' },
  prado: { brand: 'Toyota', model: 'Prado' },
  'land cruiser': { brand: 'Toyota', model: 'Land Cruiser' },
  // Citroën
  c3: { brand: 'Citroën', model: 'C3' },
  c4: { brand: 'Citroën', model: 'C4' },
  c5: { brand: 'Citroën', model: 'C5' },
  'c-elysee': { brand: 'Citroën', model: 'C-Elysée' },
  berlingo: { brand: 'Citroën', model: 'Berlingo' },
  ami: { brand: 'Citroën', model: 'Ami' },
  // Fiat
  '500': { brand: 'Fiat', model: '500' },
  tipo: { brand: 'Fiat', model: 'Tipo' },
  panda: { brand: 'Fiat', model: 'Panda' },
  doblo: { brand: 'Fiat', model: 'Doblo' },
  '600': { brand: 'Fiat', model: '600' },
  // Seat
  ibiza: { brand: 'Seat', model: 'Ibiza' },
  leon: { brand: 'Seat', model: 'Leon' },
  arona: { brand: 'Seat', model: 'Arona' },
  ateca: { brand: 'Seat', model: 'Ateca' },
  tarraco: { brand: 'Seat', model: 'Tarraco' },
  // Skoda
  octavia: { brand: 'Skoda', model: 'Octavia' },
  fabia: { brand: 'Skoda', model: 'Fabia' },
  kodiaq: { brand: 'Skoda', model: 'Kodiaq' },
  karoq: { brand: 'Skoda', model: 'Karoq' },
  kamiq: { brand: 'Skoda', model: 'Kamiq' },
  scala: { brand: 'Skoda', model: 'Scala' },
  superb: { brand: 'Skoda', model: 'Superb' },
  // Ford
  fiesta: { brand: 'Ford', model: 'Fiesta' },
  focus: { brand: 'Ford', model: 'Focus' },
  kuga: { brand: 'Ford', model: 'Kuga' },
  puma: { brand: 'Ford', model: 'Puma' },
  ranger: { brand: 'Ford', model: 'Ranger' },
  // Nissan
  qashqai: { brand: 'Nissan', model: 'Qashqai' },
  juke: { brand: 'Nissan', model: 'Juke' },
  'x-trail': { brand: 'Nissan', model: 'X-Trail' },
  xtrail: { brand: 'Nissan', model: 'X-Trail' },
  micra: { brand: 'Nissan', model: 'Micra' },
  // Suzuki
  swift: { brand: 'Suzuki', model: 'Swift' },
  vitara: { brand: 'Suzuki', model: 'Vitara' },
  jimny: { brand: 'Suzuki', model: 'Jimny' },
  's-presso': { brand: 'Suzuki', model: 'S-Presso' },
  // Cupra
  formentor: { brand: 'Cupra', model: 'Formentor' },
  terramar: { brand: 'Cupra', model: 'Terramar' },
};

export function getBrandFallbackBudgetRange(brandName: string): { min: number; max: number; step: number; label: string } {
  const norm = normalizeBrandText(brandName);
  if (norm === 'dacia') {
    return { min: 80000, max: 300000, step: 5000, label: 'Budget recommandé' };
  }
  if (['ferrari', 'lamborghini', 'mclaren', 'aston martin', 'bugatti', 'bentley', 'rolls royce'].includes(norm)) {
    return { min: 2500000, max: 8000000, step: 100000, label: 'Budget recommandé' };
  }
  if (norm === 'porsche') {
    return { min: 400000, max: 2500000, step: 25000, label: 'Budget recommandé' };
  }
  if (['mercedes benz', 'mercedes', 'bmw', 'audi', 'land rover', 'jaguar', 'lexus', 'maserati'].includes(norm)) {
    return { min: 300000, max: 1500000, step: 25000, label: 'Budget recommandé' };
  }
  if (['fiat', 'suzuki', 'mahindra', 'dfsk'].includes(norm)) {
    return { min: 70000, max: 350000, step: 5000, label: 'Budget recommandé' };
  }
  return { min: 80000, max: 600000, step: 5000, label: 'Budget recommandé' };
}

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

export function extractBrandPreference(text: string): BrandPreference | null {
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

const knownBrand = candidates.find((candidate) => {
  if (!new RegExp(`(?:^| )${escapeRegExp(candidate.alias)}(?:$| )`, 'i').test(normalizedText)) {
    return false;
  }
  if (candidate.alias === 'seat') {
    const isCarSeat = /(?:ergonomic|comfort|comfortable|cuir|leather|chauffant|heated|ventilated|isofix|bebe|bébé|baby|enfant|child|booster|rehausseur|places?|sieges?|sièges?|arriere|arrière|avant|conducteur|passager)\s+seats?|seats?\s+(?:comfort|confort|belt|ceinture|ergonomic|heating|massage|cover|housse|adjustment|reglage|réglage|memory|memoire|mémoire|capacity|count|number)|\b\d+\s*seats?\b/i.test(text);
    if (isCarSeat) return false;
  }
  return true;
});
if (knownBrand) return knownBrand;

  // Match popular car models (e.g. "duster", "clio", "golf", "tucson")
  const modelEntries = Object.entries(POPULAR_MODELS_TO_BRAND).sort((a, b) => b[0].length - a[0].length);
  const matchedModel = modelEntries.find(([modelKey]) => (
    new RegExp(`(?:^| )${escapeRegExp(modelKey)}(?:$| )`, 'i').test(normalizedText)
  ));
  if (matchedModel) {
    return {
      name: matchedModel[1].brand,
      apiValue: matchedModel[1].brand,
      model: matchedModel[1].model,
    };
  }

  // Keep an explicitly requested, unknown make strict as well. This prevents
  // a request such as "I want a Lamborghini" from silently becoming a full
  // catalogue recommendation when that make is not available locally.
  const genericVehicleTerms = new Set([
    'car', 'cars', 'vehicle', 'vehicles', 'suv', 'model', 'models', 'auto', 'automobile', 'automobiles',
    'voiture', 'voitures', 'vehicule', 'vehicules', 'véhicule', 'véhicules',
    'family', 'familly', 'familiale', 'familial', 'electric', 'electrique', 'hybrid',
    'hybride', 'diesel', 'essence', 'safe', 'safest', 'secure',
    'city', 'citadine', 'berline', 'sedan', 'saloon', 'coupe', 'cabriolet',
    'convertible', 'break', 'estate', 'wagon', 'pickup', 'van', 'monospace',
    'utilitaire', 'compact', 'compacte', 'hatchback',
    'ma', 'mon', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses', 'notre', 'nos', 'votre', 'vos', 'leur', 'leurs',
    'my', 'our', 'your', 'his', 'her', 'their', 'the', 'a', 'an', 'this', 'that',
    'un', 'une', 'des', 'le', 'la', 'les', 'du', 'de', 'd', 'l', 'ce', 'cet', 'cette', 'ces',
    'premier', 'premiere', 'première', 'first', 'deuxieme', 'deuxième', 'second', 'troisieme', 'troisième', 'third',
    'nouveau', 'nouvelle', 'new', 'neuf', 'neuve', 'occasion', 'used',
    'bonne', 'bon', 'meilleur', 'meilleure', 'best', 'good', 'cheap', 'economique', 'économique',
    'petite', 'petit', 'small', 'grande', 'grand', 'large', 'big',
    'pas', 'cher', 'chere', 'fiable', 'sobre', 'rapide', 'propre',
    'pour', 'avec', 'sans', 'qui', 'que', 'dans', 'sur', 'en', 'par', 'et', 'ou',
    'for', 'with', 'without', 'in', 'on', 'at', 'to', 'from',
    'tomobil', 'tomobile', 'tomobila', 'tonobile', 'sayara', 'sayarat',
    'dyal', 'dial', 'ta3', 'bghit', 'baghi', 'kanqleb', 'khesni', 'khassni',
  ]);
  const unknownMatch = normalizedText.match(/(?:^| )(?:(?:i|je) )?(?:want|need|buy|looking for|show me|find me|cherche|recherche|acheter|veux|cherche) (?:a|an|the|une|un|une voiture|un vehicule|voiture|véhicule)? ?([a-z][a-z-]+)(?:$| )/i);
  const unknownBrand = unknownMatch?.[1];
  if (unknownBrand && unknownBrand.length >= 3 && !genericVehicleTerms.has(unknownBrand)) {
    return { name: unknownBrand, apiValue: unknownBrand };
  }
  return null;
}

const safetyPreferencePattern = /\b(safe|safest|safety|security|secure|sécurité|securite|sûr|sûre|sûreté|crash|ncap|airbag)\b|(?:^|[^\p{L}\p{N}])(?:ال)?(سلامة|السلامة|آمن|أمان)(?:$|[^\p{L}\p{N}])/iu;
const maxNcapPreferencePattern = /(?:highest ncap|note ncap maximale|ncap maximale|note maximale|highest ncap rating|5\s*(?:stars?|étoiles?|نجوم?|★)|أعلى تقييم|أعلى نقطة)/iu;
const goodNcapPreferencePattern = /(?:good safety|bonne s[eé]curit[eé]|4\s*(?:stars?|étoiles?|نجوم?|★)|سلامة جيدة|سلامة مزيانة)/iu;

// Age, gender, and profession describe the client profile, not vehicle catalogue fields.
// Recognise them so natural requests such as "a car for 22 years old", "I am a doctor",
// or "أنا طالب" start the discovery flow instead of being sent to semantic search
// or general informational QA as over-constrained queries.
const agePreferencePattern = /\b(?:\d{1,3}\s*(?:years?[- ]?old|ans?|an|3am))\b|\b(?:age|âge)\s*[:：-]?\s*\d{1,3}\b|\b3omr\w*\s*\d{1,3}\b|\b(?:i['’]?m|i\s+am|j['’]?ai|j\s+ai)\s*\d{1,3}\b|(?:^|[^\p{L}\p{N}])\d{1,3}\s*(?:عام|سنة)(?:$|[^\p{L}\p{N}])|(?:^|[^\p{L}\p{N}])(?:عام|سنة)\s*\d{1,3}\b|(?:^|[^\p{L}\p{N}])(?:عمري|عندي)\s*\d{1,3}\b/iu;
const genderPreferencePattern = /\b(?:woman|women|female|man|men|male|girl|boy|femme|homme|fille|garçon|garcon|lmra|l\s*mra|mra|raj[e]?l|l\s*raj[e]?l)\b|(?:^|[^\p{L}\p{N}])(?:ال|لل|ل)?(?:مرأة|مرا|نساء|رجل|راجل|رجال|بنت|شاب|سيدة)(?:$|[^\p{L}\p{N}])/iu;

const latinOccupationPattern = new RegExp(
  '(?<![\\p{L}\\p{N}])(?:' + [
    // Executive & Corporate
    'directeur|directrice|director|managing\\s+director|general\\s+manager|executive|manager|ceo|coo|cfo|cto|vp|president|président(?:e)?|cadre(?:\\s+supérieur|\\s+dirigeant)?|dirigeant(?:e)?|chef\\s+d[\'’]entreprise|patron(?:ne)?|entrepreneur(?:e)?|fondateur|fondatrice|business(?:man|woman)?|responsable|gérant(?:e)?|statutaire|standing|prestige|représentation|rendez[- ]vous\\s+(?:d[\'’]affaires|clients?)|business\\s+meetings?',
    // Corporate & Executive vehicle phrasing
    'executive\\s+car|business\\s+car|company\\s+car|prestige\\s+car|status\\s+car|voiture\\s+statutaire|véhicule\\s+statutaire|voiture\\s+de\\s+fonction|voiture\\s+de\\s+direction|voiture\\s+de\\s+prestige|voiture\\s+de\\s+standing',
    // Healthcare & Medical
    'doctor|physician|surgeon|dentist|pharmacist|nurse|médecin|medecin|docteur|doctoresse|chirurgien(?:ne)?|dentiste|pharmacien(?:ne)?|infirmier|infirmière|infirmiere|praticien(?:ne)?|kinésithérapeute|kinesitherapeute|kine|vétérinaire|veterinaire',
    // Legal & Finance
    'lawyer|attorney|notary|judge|accountant|banker|avocat(?:e)?|notaire|juriste|magistrat(?:e)?|juge|comptable|expert[- ]comptable|banquier|banquière|banquiere|financier|financière|financiere',
    // Tech, Engineering, Architecture
    'engineer|developer|architect|software\\s+engineer|consultant|ingénieur(?:e)?|ingenieur(?:e)?|développeur|developpeur|développeuse|developpeuse|architecte|informaticien(?:ne)?|technicien(?:ne)?|data\\s+scientist',
    // Education & Public Service
    'teacher|professor|lecturer|educator|enseignant(?:e)?|professeur(?:e)?|prof|instituteur|institutrice|fonctionnaire|chercheur|chercheuse',
    // Transport, Drivers, Commercial & Field
    'sales\\s+rep|salesman|saleswoman|commercial(?:e)?|vrp|représentant(?:e)?|representant(?:e)?|délégué(?:e)?\\s+médical(?:e)?|delegue(?:e)?\\s+medical(?:e)?|taxi|taxi\\s+driver|chauffeur(?:\\s+de\\s+taxi|\\s+vtc)?|vtc|driver|livreur|delivery\\s+driver|coursier|grand\\s+rouleur|commuter|frequent\\s+traveler|voyageur',
    // Trades, Freelance & Agriculture
    'freelancer|freelance|indépendant(?:e)?|independant(?:e)?|artisan(?:e)?|commerçant(?:e)?|commercant(?:e)?|agriculteur|agricultrice|fermier|farmer',
    // Students, Young Drivers, Beginners
    'student|college\\s+student|university\\s+student|étudiant(?:e)?|etudiant(?:e)?|stagiaire|jeune\\s+diplômé(?:e)?|jeune\\s+diplome(?:e)?|jeune\\s+actif|jeune\\s+active|premier\\s+emploi|débutant(?:e)?|debutant(?:e)?|beginner|young\\s+driver|nouveau\\s+conducteur|nouvelle\\s+conductrice|jeune\\s+conducteur|jeune\\s+conductrice|jeune\\s+permis|nouveau\\s+permis|permis\\s+probatoire|premier\\s+achat|première\\s+voiture|premiere\\s+voiture|first\\s+car',
    // Seniors & Retirees
    'retiree|retired|senior|retraité(?:e)?|retraite|retraitee|pensionné(?:e)?|pensionne(?:e)?',
    // Family & Household
    'parent|father|mother|dad|mom|père|mère|pere|mere|papa|maman|père\\s+de\\s+famille|pere\\s+de\\s+famille|mère\\s+de\\s+famille|mere\\s+de\\s+famille|chef\\s+de\\s+famille|large\\s+family|famille\\s+nombreuse|famille\\s+de\\s+\\d+|femme\\s+au\\s+foyer',
    // Arabizi
    'taleb|talba|chab|chaba|mta9ed|mta9eda|walid|walida|moul\\s+taxi|sa2e9|sa2e9\\s+taxi|sa2e9\\s+livraison|fellah|msafer|kheddam|khedama|mowadaf|mowadafa|ostad|ostada|tbib|tbiba|mouhandis|mouhandisa|mou7ami|mou7amiya|moudir|moudira|modir|modira|mdir|mdira|patron|patrona',
  ].join('|') + ')(?![\\p{L}\\p{N}])',
  'iu',
);

const arabicOccupationPattern = new RegExp(
  '(?<![\\p{L}\\p{N}])(?:ال|لل|ل|ف|فال|بال|ك)?(?:' + [
    // Executive & Corporate
    'مدير(?:ة)?(?:\\s+عام(?:ة)?)?|رئيس(?:ة)?(?:\\s+تنفيذي(?:ة)?|\\s+مجلس\\s+إدارة)?|مسؤول(?:ة)?|مسير(?:ة)?|رجل\\s+أعمال|سيدة\\s+أعمال|مقاول(?:ة)?|إطار(?:\\s+عالي|\\s+بنكي)?|صاحب(?:ة)?\\s+شركة|كادر',
    // Corporate & Executive vehicle phrasing in Arabic
    'سيارة\\s+(?:إدارية|فخمة|برستيج|لرجال\\s+الأعمال|رسمية|ذات\\s+هيبة|للمدير)|طوموبيل\\s+(?:برستيج|ديال\\s+مدير)',
    // Healthcare & Medical
    'طبيب(?:ة)?(?:\\s+أسنان)?|دكتور(?:ة)?|جراح(?:ة)?|صيدل(?:ي|ية)|ممرض(?:ة)?|أخصائي(?:ة)?',
    // Legal & Finance
    'محام(?:ي|ية)?|موثق(?:ة)?|قاض(?:ي|ية)?|محاسب(?:ة)?|خبير\\s+محاسب|بنك(?:ي|ية)',
    // Tech, Engineering, Architecture
    'مهندس(?:ة)?(?:\\s+معماري(?:ة)?)?|معمار(?:ي|ية)|مطور(?:ة)?|مبرمج(?:ة)?|تقن(?:ي|ية)',
    // Education & Public Service
    'أستاذ(?:ة)?|معلم(?:ة)?|مدرس(?:ة)?|دكتور\\s+جامعي|باحث(?:ة)?',
    // Transport, Drivers, Commercial & Field
    'سائق(?:ة)?(?:\\s+(?:طاكسي|تاكسي|أجرة|توصيل))?|مول\\s+طاكسي|سائق\\s+جديد|سائقة\\s+جديدة|سائق\\s+مبتدئ|سائقة\\s+مبتدئة|مندوب(?:ة)?\\s+تجار(?:ي|ية)|ممثل(?:ة)?\\s+تجار(?:ي|ية)|مسافر(?:ة)?|كثير\\s+الأسفار',
    // Trades, Freelance & Agriculture
    'تاجر(?:ة)?|حرف(?:ي|ية)|فلاح(?:ة)?',
    // Students, Young Drivers, Beginners
    'طالب(?:ة)?|تلميذ(?:ة)?|شاب(?:ة)?|رخصة\\s+جديدة|أول\\s+(?:سيارة|طوموبيل)',
    // Seniors & Retirees
    'متقاعد(?:ة)?|مسن(?:ة)?',
    // Family & Household
    'أب|أم|والد(?:ة)?|رب\\s+أسرة|ربة\\s+(?:منزل|بيت)|عائلة\\s+كبيرة',
  ].join('|') + ')(?![\\p{L}\\p{N}])',
  'iu',
);

const occupationPreferencePattern = {
  test: (text: string): boolean => latinOccupationPattern.test(text) || arabicOccupationPattern.test(text),
};

export type ClientProfileCategory =
  | 'taxi'
  | 'executive'
  | 'medical'
  | 'commercial_commuter'
  | 'young_student'
  | 'family'
  | 'general';

export const taxiProfilePattern = new RegExp(
  '(?<![\\p{L}\\p{N}])(?:' + [
    'taxi|taxi\\s+driver|chauffeur(?:\\s+de)?\\s+taxi|artisan\\s+taxi|permis\\s+de\\s+confiance|agrement\\s+taxi|agrément\\s+taxi|petit\\s+taxi|grand\\s+taxi',
    'moul\\s+taxi|moul\\s+ltaxi|sa2e9\\s+taxi|sayeq\\s+taxi|khdam\\s+taxi|khedam\\s+taxi|bghit\\s+nakhdem\\s+taxi|tomobil\\s+dyal\\s+taxi|taxi\\s+sghir|taxi\\s+kbir|gran\\s+taxi|piti\\s+taxi',
    'طاكسي|تاكسي|مول\\s+طاكسي|مول\\s+الطاكسي|سائق\\s+طاكسي|سائق\\s+تاكسي|سيارة\\s+أجرة|طاكسي\\s+صغير|طاكسي\\s+كبير|بيتي\\s+طاكسي|ݣران\\s+طاكسي|كران\\s+طاكسي|خدمة\\s+طاكسي',
  ].join('|') + ')(?![\\p{L}\\p{N}])',
  'iu',
);

const executivePattern = new RegExp(
  '(?<![\\p{L}\\p{N}])(?:' + [
    'directeur|directrice|director|managing\\s+director|general\\s+manager|executive|manager|ceo|coo|cfo|cto|vp|president|président(?:e)?|cadre|dirigeant(?:e)?|chef\\s+d[\'’]entreprise|patron(?:ne)?|entrepreneur(?:e)?|fondateur|fondatrice|business(?:man|woman)?|responsable|gérant(?:e)?',
    'lawyer|attorney|notary|avocat(?:e)?|notaire|juriste|magistrat(?:e)?|mou7ami|mou7amiya',
    'statutaire|standing|prestige|représentation|rendez[- ]vous\\s+(?:d[\'’]affaires|clients?)|business\\s+meetings?',
    'executive\\s+car|business\\s+car|company\\s+car|prestige\\s+car|status\\s+car|voiture\\s+statutaire|véhicule\\s+statutaire|voiture\\s+de\\s+fonction|voiture\\s+de\\s+direction|voiture\\s+de\\s+prestige|voiture\\s+de\\s+standing',
    'moudir|moudira|modir|modira|mdir|mdira',
    'مدير(?:ة)?|رئيس(?:ة)?|مسؤول(?:ة)?|مسير(?:ة)?|رجل\\s+أعمال|سيدة\\s+أعمال|مقاول(?:ة)?|إطار|صاحب(?:ة)?\\s+شركة|كادر|محام(?:ي|ية)?|موثق(?:ة)?|قاض(?:ي|ية)?',
    'برستيج|فخمة|هيبة|إدارية|رسمية',
  ].join('|') + ')(?![\\p{L}\\p{N}])',
  'iu',
);

const medicalPattern = new RegExp(
  '(?<![\\p{L}\\p{N}])(?:' + [
    'doctor|physician|surgeon|dentist|pharmacist|nurse|médecin|medecin|docteur|doctoresse|chirurgien(?:ne)?|dentiste|pharmacien(?:ne)?|infirmier|infirmière|infirmiere|praticien(?:ne)?|kinésithérapeute|kinesitherapeute|kine|vétérinaire|veterinaire',
    'tbib|tbiba',
    'طبيب(?:ة)?|دكتور(?:ة)?|جراح(?:ة)?|صيدل(?:ي|ية)|ممرض(?:ة)?|أخصائي(?:ة)?',
  ].join('|') + ')(?![\\p{L}\\p{N}])',
  'iu',
);

const commercialCommuterPattern = new RegExp(
  '(?<![\\p{L}\\p{N}])(?:' + [
    'sales\\s+rep|salesman|saleswoman|commercial(?:e)?|vrp|représentant(?:e)?|representant(?:e)?|délégué(?:e)?\\s+médical(?:e)?|delegue(?:e)?\\s+medical(?:e)?|chauffeur(?:\\s+vtc)?|vtc|driver|livreur|delivery\\s+driver|coursier|grand\\s+rouleur|commuter|frequent\\s+traveler|voyageur',
    'sa2e9|msafer|kheddam|khedama',
    'سائق(?:ة)?|مندوب(?:ة)?\\s+تجار(?:ي|ية)|ممثل(?:ة)?\\s+تجار(?:ي|ية)|مسافر(?:ة)?|كثير\\s+الأسفار',
  ].join('|') + ')(?![\\p{L}\\p{N}])',
  'iu',
);

const youngStudentPattern = new RegExp(
  '(?<![\\p{L}\\p{N}])(?:' + [
    'student|college\\s+student|university\\s+student|étudiant(?:e)?|etudiant(?:e)?|stagiaire|jeune\\s+diplômé(?:e)?|jeune\\s+diplome(?:e)?|jeune\\s+actif|jeune\\s+active|premier\\s+emploi|débutant(?:e)?|debutant(?:e)?|beginner|young\\s+driver|nouveau\\s+conducteur|nouvelle\\s+conductrice|jeune\\s+conducteur|jeune\\s+conductrice|jeune\\s+permis|nouveau\\s+permis|permis\\s+probatoire|premier\\s+achat|première\\s+voiture|premiere\\s+voiture|first\\s+car',
    'taleb|talba|chab|chaba',
    'طالب(?:ة)?|تلميذ(?:ة)?|شاب(?:ة)?|رخصة\\s+جديدة|أول\\s+(?:سيارة|طوموبيل)',
  ].join('|') + ')(?![\\p{L}\\p{N}])',
  'iu',
);

const familyProfilePattern = new RegExp(
  '(?<![\\p{L}\\p{N}])(?:' + [
    'parent|father|mother|dad|mom|père|mère|pere|mere|papa|maman|famille|familiale?|familial|family|children|kids|baby|poussette|large\\s+family|famille\\s+nombreuse',
    'walid|walida|3a2ila|l3a2ila|3ayla|l3ayla|wlad|drari|famila',
    'أب|أم|والد(?:ة)?|رب\\s+أسرة|ربة\\s+(?:منزل|بيت)|عائلة|عائلية|عائلي|أسرة|أطفال',
  ].join('|') + ')(?![\\p{L}\\p{N}])',
  'iu',
);

export function detectClientProfile(text: string): ClientProfileCategory {
  if (taxiProfilePattern.test(text)) return 'taxi';
  if (executivePattern.test(text)) return 'executive';
  if (medicalPattern.test(text)) return 'medical';
  if (commercialCommuterPattern.test(text)) return 'commercial_commuter';
  if (youngStudentPattern.test(text)) return 'young_student';
  if (familyProfilePattern.test(text)) return 'family';
  return 'general';
}

export const EXECUTIVE_BRANDS = new Set([
  'mercedes-benz', 'mercedes', 'bmw', 'audi', 'porsche', 'lexus', 'land rover', 'range rover',
  'volvo', 'jaguar', 'alfa romeo', 'maserati', 'ds automobiles', 'ds', 'volkswagen',
]);

export const EXECUTIVE_LOW_END_BRANDS = new Set([
  'dacia', 'fiat', 'suzuki', 'chery', 'geely', 'mg',
]);

export const MEDICAL_RECOMMENDED_BRANDS = new Set([
  'volvo', 'toyota', 'lexus', 'mercedes-benz', 'mercedes', 'audi', 'bmw', 'volkswagen', 'peugeot', 'hyundai', 'kia',
]);

export const COMMERCIAL_RECOMMENDED_BRANDS = new Set([
  'volkswagen', 'peugeot', 'renault', 'dacia', 'toyota', 'hyundai', 'skoda', 'citroen', 'citroën', 'fiat', 'ford', 'opel',
]);

export const YOUNG_STUDENT_AFFINITY_MODELS = [
  'clio', '208', 'sandero', 'stepway', 'c3', 'i10', 'i20', 'picanto', 'yaris', 'polo', '500', 'fiesta', 'ibiza', 'fabia', 'corsa', 'swift', 'stonic', 'captur', '2008',
];

export const TAXI_UNACCEPTABLE_BRANDS = new Set([
  'audi', 'bmw', 'mercedes-benz', 'mercedes', 'porsche', 'ferrari', 'lamborghini',
  'mclaren', 'bugatti', 'bentley', 'rolls-royce', 'maserati', 'aston martin',
  'land rover', 'range rover', 'jaguar', 'alfa romeo', 'lexus', 'cupra',
  'ds automobiles', 'ds', 'jeep', 'tesla',
]);

export const TAXI_WORKHORSE_BRANDS = new Map<string, number>([
  ['dacia', 60],
  ['fiat', 45],
  ['citroen', 45],
  ['citroën', 45],
  ['peugeot', 40],
  ['renault', 40],
  ['toyota', 35],
  ['hyundai', 35],
  ['kia', 25],
  ['volkswagen', 20],
]);

function sortForProfile(cars: Car[], profile: ClientProfileCategory): Car[] {
  if (profile === 'general') return cars;

  return [...cars]
    .map((car, index) => {
      let score = 0;
      const brand = normalizeBrandText(car.brand);
      const body = normalizeBodyType(car.body_type);
      const power = Number(car.engine_power_hp) || 0;
      const price = Number(car.price) || 0;
      const model = (car.model || '').toLowerCase();
      const ncap = getNcapScore(car);

      if (profile === 'taxi') {
        if (TAXI_UNACCEPTABLE_BRANDS.has(brand)) score -= 500;
        if (body === 'coupe' || body === 'cabriolet') score -= 500;

        const brandBonus = TAXI_WORKHORSE_BRANDS.get(brand) || 0;
        score += brandBonus;

        if (car.fuel_type === 'diesel') score += 25;
        else if (car.fuel_type === 'hybride' || car.fuel_type === 'hybride_rechargeable') score += 25;
        else if (car.fuel_type === 'electrique') score += 10;
        else if (car.fuel_type === 'essence') {
          if (power > 120 || price > 200000) score -= 30;
        }

        if (model.includes('logan')) score += 25;
        else if (model.includes('sandero')) score += 20;
        else if (model.includes('stepway')) score += 18;
        else if (model.includes('jogger') || model.includes('lodgy')) score += 30;
        else if (model.includes('tipo')) score += 20;
        else if (model.includes('doblo') || model.includes('fiorino')) score += 25;
        else if (model.includes('c-elysee') || model.includes('c elysee')) score += 22;
        else if (model.includes('c3')) score += 15;
        else if (model.includes('berlingo')) score += 25;
        else if (model.includes('208') || model.includes('301')) score += 20;
        else if (model.includes('rifter') || model.includes('partner')) score += 25;
        else if (model.includes('clio') || model.includes('express') || model.includes('kangoo')) score += 20;
        else if (model.includes('yaris') || model.includes('corolla')) score += 20;
        else if (model.includes('i10') || model.includes('accent')) score += 18;

        if ((car.seats || 5) >= 6) score += 20;
        if (price > 0 && price <= 200000) score += 20;
        else if (price > 200000 && price <= 280000) score += 10;
        else if (price > 350000) score -= 40;
      } else if (profile === 'executive') {
        if (EXECUTIVE_BRANDS.has(brand)) score += 55;
        if (EXECUTIVE_LOW_END_BRANDS.has(brand)) score -= 350;
        if (body === 'berline') score += 35;
        else if (body === 'suv') score += 30;
        else if (body === 'coupe') score += 20;
        else if (body === 'citadine' || body === 'monospace' || body === 'utilitaire') score -= 200;

        if (car.transmission === 'automatique') score += 25;
        if (power >= 180) score += 25;
        else if (power >= 150) score += 15;
        if (price >= 350000) score += 25;
      } else if (profile === 'medical') {
        if (MEDICAL_RECOMMENDED_BRANDS.has(brand)) score += 35;
        if (brand === 'volvo') score += 25;
        if (brand === 'toyota' || brand === 'lexus') score += 20;

        if (ncap >= 5) score += 40;
        else if (ncap >= 4) score += 20;

        if (car.transmission === 'automatique') score += 25;
        if (body === 'suv') score += 25;
        else if (body === 'berline') score += 20;
        else if (body === 'coupe' || body === 'cabriolet') score -= 250;

        if (car.fuel_type === 'hybride' || car.fuel_type === 'hybride_rechargeable') score += 30;
        else if (car.fuel_type === 'diesel') score += 15;
      } else if (profile === 'commercial_commuter') {
        if (COMMERCIAL_RECOMMENDED_BRANDS.has(brand)) score += 35;
        if (car.fuel_type === 'diesel') score += 40;
        else if (car.fuel_type === 'hybride' || car.fuel_type === 'hybride_rechargeable') score += 30;
        else if (car.fuel_type === 'essence' && power > 130) score -= 25;

        if (body === 'berline' || body === 'break') score += 30;
        else if (body === 'citadine') score += 20;
        else if (body === 'coupe' || body === 'cabriolet') score -= 350;

        if (price > 0 && price <= 380000) score += 20;
      } else if (profile === 'young_student') {
        const isStudentAffinityModel = YOUNG_STUDENT_AFFINITY_MODELS.some((m) => model.includes(m));
        if (isStudentAffinityModel) score += 55;

        if (body === 'citadine') score += 40;
        else if (body === 'suv' && (model.includes('stepway') || model.includes('captur') || model.includes('2008') || model.includes('stonic'))) score += 30;
        else if (body === 'coupe' || body === 'cabriolet' || body === 'monospace' || (car.seats || 5) >= 7) score -= 500;

        if (car.fuel_type === 'essence' || car.fuel_type === 'hybride') score += 20;

        if (power > 0 && power <= 110) score += 25;
        else if (power > 160) score -= 200;

        if (price > 0 && price <= 180000) score += 35;
        else if (price > 180000 && price <= 230000) score += 20;
        else if (price > 320000) score -= 300;

        if (SUPERCAR_BRANDS.has(brand) || ['porsche', 'maserati', 'jaguar', 'land rover', 'bentley', 'rolls-royce', 'aston martin', 'ferrari', 'lamborghini'].includes(brand)) score -= 1000;
      } else if (profile === 'family') {
        if (FAMILY_BODY_TYPES.has(body) && !SUPERCAR_BRANDS.has(brand)) score += 40;
        if ((car.seats || 5) >= 7) score += 30;
        if ((Number(car.trunk_volume_l) || 0) >= 480) score += 25;

        if (model.includes('jogger') || model.includes('5008') || model.includes('kodiaq') || model.includes('sorento') || model.includes('lodgy') || model.includes('carens') || model.includes('tucson') || model.includes('sportage') || model.includes('duster') || model.includes('tiguan')) {
          score += 25;
        }

        if (ncap >= 5) score += 30;
        else if (ncap >= 4) score += 15;

        if (body === 'coupe' || body === 'cabriolet') score -= 400;
      }

      return { car, index, score };
    })
    .sort((a, b) => b.score - a.score || a.index - b.index)
    .map(({ car }) => car);
}

export function getNcapScore(car: Pick<Car, 'ncap_rating'>): number {
  const rating = String(car.ncap_rating || '').replace(',', '.');
  const match = rating.match(/(?:^|\s)([0-5](?:\.\d+)?)\s*(?:\/\s*5|(?:stars?|étoiles?))?/i);
  if (!match) return -1;
  const score = Number(match[1]);
  return Number.isFinite(score) ? Math.min(5, Math.max(0, score)) : -1;
}

function sortForSafetyGlobal(cars: Car[], safetyRequested: boolean, profile: ClientProfileCategory = 'general'): Car[] {
  const profiled = profile !== 'general' ? sortForProfile(cars, profile) : cars;
  if (!safetyRequested) return profiled;
  return profiled
    .map((car, index) => ({ car, index, ncapScore: getNcapScore(car) }))
    .sort((a, b) => b.ncapScore - a.ncapScore || a.index - b.index)
    .map(({ car }) => car);
}

export const sortForSafety = sortForSafetyGlobal;

async function loadAllCatalogueVehicles(): Promise<Car[]> {
  try {
    const firstPage = await vehicleService.getVehicles({ page: 1, page_size: 100 });
    if (firstPage.pages <= 1) return firstPage.items;

    const pageCount = Math.min(firstPage.pages - 1, 3);
    const remainingPages = await Promise.all(
      Array.from({ length: pageCount }, (_, index) => (
        vehicleService.getVehicles({ page: index + 2, page_size: 100 }).catch(() => ({ items: [] }))
      )),
    );
    return [firstPage.items, ...remainingPages.map((page) => page.items || [])].flat();
  } catch {
    return [];
  }
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
const intentPattern = /\b(cherche|recherche|trouve|propose|recommande|choisir|choisis|conseil|conseillez-moi|acheter|achat|buy|recommend|suggest|choose|choosing|advice|looking\s+for|want\s+to\s+buy|want\s+(?:a\s+|an\s+|the\s+)?(?:[a-z-]+\s+){0,3}(?:car|suv|vehicle)|need\s+(?:a\s+)?(?:[a-z-]+\s+){0,3}(?:car|suv|vehicle)|find\s+me|show\s+me|help\s+me\s+choose|which\s+(?:car|cars|suv|suvs|vehicle|vehicles|model|models)|what\s+(?:kind\s+of\s+)?(?:car|cars|suv|suvs|vehicle|vehicles|auto|automobile)(?:\s+(?:[a-z-]+\s+){0,3}(?:should|dhould|shoud|shuld|shold|can|could|would|to|fits?|suits?|for|best|recommend|have|buy|get))?|(?:should|dhould|shoud|shuld|shold)\s+i\s+(?:buy|get|have|choose|take)|what\s+(?:should|dhould|shoud|shuld)\s+i\s+(?:buy|get|have|choose|take)|what\s+to\s+buy|best\s+(?:car|suv|vehicle)|safest\s+(?:car|suv|vehicle)|most\s+secure\s+(?:car|suv|vehicle)|(?:car|suv|vehicle)\s+for|family\s+car|family\s+vehicle|city\s+car|small\s+car|petite?\s+voiture|executive\s+car|business\s+car|status\s+car|je\s+veux\s+acheter|je\s+veux\s+une\s+voiture|voiture\s+familiale?|véhicule\s+familial|voiture\s+statutaire|véhicule\s+statutaire|voiture\s+de\s+fonction|voiture\s+de\s+direction|voiture\s+de\s+prestige|voiture\s+de\s+standing|voiture\s+pour|quel(?:le)?\s+(?:voiture|auto|véhicule|vehicule)|meilleur(?:e)?\s+voiture|budget\s+(?:de|maximum|max)|mon\s+budget|bghit\s+(?:nchri|tomobil|tonobil|sayara|chi\s+tonobil|chi\s+tomobil)|baghi\s+(?:nchri|tomobil|tonobil|sayara|chi\s+tonobil|chi\s+tomobil)|achmen\s+(?:tonobil|tomobil|sayara)|chmen\s+(?:tonobil|tomobil|sayara)|ashmen\s+(?:tonobil|tomobil|sayara)|chnou\s+nchri|chno\s+nchri|tonobil(?:a|e)?\s+sghir(?:a)?|tomobil(?:a)?\s+sghir(?:a)?|sayara\s+saghir(?:a)?|kanqleb\s+3la|tomobil(?:e|a)?\s+dyal|tonobile\s+dyal|3a2ila|a\s+car|a\s+suv|a\s+vehicle|une\s+voiture|un\s+véhicule|un\s+vehicule)\b/i;
const nonLatinIntentPattern = /(?:بغيت\s+(?:نشري|طوموبيل|سيارة|شي\s+طوموبيل)|باغي\s+(?:نشري|طوموبيل|سيارة|شي\s+طوموبيل)|شنو\s+نشري|اشمن\s+(?:سيارة|طوموبيل)|أشمن\s+(?:سيارة|طوموبيل)|أي\s+سيارة|اي\s+سيارة|ما\s+هي\s+(?:أفضل|أحسن)\s+سيارة|طوموبيل\s+صغيرة|سيارة\s+صغيرة|كنقلب\s+على|kanqleb\s+3la|tomobil(?:e|a)?\s+dyal|tonobile\s+dyal|tonobil(?:a|e)?\s+sghir(?:a)?|tomobil(?:a)?\s+sghir(?:a)?|sayara\s+saghir(?:a)?|3a2ila|شراء|أبحث|أريد\s+(?:سيارة|طوموبيل)|سيارة\s+(?:صغيرة|عائلية|للعائلة|إدارية|فخمة|برستيج|لرجال\s+الأعمال|رسمية)|طوموبيل\s+(?:ديال\s+)?(?:العائلة|مدير)|طوموبيل\s+برستيج|ساعدني\s+(?:في\s+)?اختيار|(?:^|[^\p{L}\p{N}])(?:شراء|أبحث|أريد|نقلب|كنقلب|باغي|بغيت)(?:$|[^\p{L}\p{N}]))/iu;

// A direct request such as "car 300000dhs" is already a buying/search
// request even when it does not contain an explicit verb like "recommend".
// Keep technical questions out of this path: they should remain chatbot-only.
const budgetSearchPattern = /(?:(?:\b(?:car|cars|vehicle|vehicles|voiture|voitures|véhicule|véhicules|vehicule|vehicules|suv|suvs|auto|automobile|automobiles|berline|citadine|compacte|utilitaire|pick-?up|tomobil|tomobile|tomobila|tonobil|tonobile|tonobila|sayara|sayarat)\b|(?:^|[^\p{L}\p{N}])(?:سيارة|سيارات|طوموبيل|طوموبيلا|طوموبيلات)(?:$|[^\p{L}\p{N}]))[^\d]{0,24}|(?:\b(?:budget|prix|price|have|j'ai)\b|(?:^|[^\p{L}\p{N}])(?:عندي|ميزانية|ثمن)(?:$|[^\p{L}\p{N}]))[^\d]{0,24})\d[\d\s.,]*(?:(?:k|mad|dhs?|dh|dirhams?)\b|(?:^|[^\p{L}\p{N}])(?:درهم|دراهم|ألف)(?:$|[^\p{L}\p{N}])|$)/iu;
const brandRequestPattern = /\b(?:want|need|looking\s+for|search(?:ing)?\s+for|show\s+me|find\s+me|buy|acheter|cherche|recherche|je\s+veux|je\s+cherche)\b|(?:^|[^\p{L}\p{N}])(?:بغيت|باغي|كنقلب|أريد|نبحث)(?:$|[^\p{L}\p{N}])/iu;

function hasProfilePreference(text: string): boolean {
return agePreferencePattern.test(text) || genderPreferencePattern.test(text) || occupationPreferencePattern.test(text);
}

export const informativeRequestPattern = /\b(?:informations?|infos?)\s+(?:about|on|sur|de)\b|\b(?:informations?|infos?)\s+(?:عن|على)(?:$|[^\p{L}\p{N}])|\b(?:bghit|baghi|3tini|khassni|khsni)?\s*(?:m3lomat|ma3lomat|ma3loumat|maloumat|infos?|informations?)\s*(?:3la|3la\s+l|sur|de|about|on|عن|على)\b|\b(?:m3lomat|ma3lomat|ma3loumat|maloumat)\b|\b(?:tell|parle|renseigne)\s+(?:me|moi)\b|\b(?:can you tell me|i want to know|do you know|your opinion|price of|is .+ available)\b|\b(?:je voudrais savoir|que pensez[- ]vous|avis sur|prix de|est .+ disponible)\b|\b(?:chnahya|chnhya|chnou\s+hiya|chnou\s+howa|chnou|chniya|chnehiya|achnahya|achnhya|achnou|ach\s+hiya|ach\s+howa|chouhouwa|c'est quoi|qu'est[- ]ce que|what is|what's)\b|(?:معلومات عن|معلومات على|معلومة على|شنو رأيك|رأيك في|شنو هي|شنو هو|ما هي|ما هو|شنو كتعني|بغيت نعرف|بغيت معلومات|عطيني معلومات|ثمن|سعر|واش كاين|3tini ma3lomat 3la|3tini m3lomat 3la|gol lia 3la|bghit n3ref 3la|ach katgol 3la)/iu;

function hasAny(text: string, patterns: RegExp[]): boolean {
return patterns.some((pattern) => pattern.test(text));
}

function profileText(history: ChatTurn[]): string {
return history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' ').toLowerCase();
}

export function computeCarPriceBounds(
  cars: Car[],
  fallback: { min: number; max: number; step?: number; label: string },
): { min: number; max: number; step: number; label: string } {
  let validPrices = (cars || [])
    .map((car) => Number(car.price))
    .filter((price) => Number.isFinite(price) && price > 0);

  if (fallback.max) {
    const maxAllowed = fallback.max >= 1000000 ? fallback.max * 1.4 : fallback.max * 1.35;
    const profileRelevantPrices = validPrices.filter((price) => price <= maxAllowed);
    if (profileRelevantPrices.length > 0) {
      validPrices = profileRelevantPrices;
    }
  }

  if (validPrices.length === 0) {
    return {
      min: fallback.min,
      max: fallback.max,
      step: fallback.step || 5000,
      label: fallback.label,
    };
  }

  const minPrice = Math.min(...validPrices);
  const maxPrice = Math.max(...validPrices);

  const spread = maxPrice - minPrice;
  const step = spread > 600000 ? 25000 : spread > 150000 ? 10000 : 5000;

  let min = Math.floor(minPrice / step) * step;
  let max = Math.ceil(maxPrice / step) * step;

  if (max <= min || max - min < step * 2) {
    min = Math.max(0, min - step * 2);
    max = max + step * 2;
  }

  return {
    min,
    max,
    step,
    label: fallback.label,
  };
}

export function generateDynamicBudgetOptions(
  min: number,
  max: number,
  language: ChatLanguage,
): QuestionOption[] {
  const spread = max - min;
  const locale = language === 'en' ? 'en-US' : language === 'ar' ? 'ar-MA' : 'fr-FR';

  if (spread <= 25000) {
    const fmtMin = min.toLocaleString(locale);
    const fmtMax = max.toLocaleString(locale);
    if (language === 'en') {
      return [
        { label: `Under ${fmtMax} MAD`, value: `under ${max} MAD` },
        { label: `${fmtMin} – ${fmtMax} MAD`, value: `between ${min} and ${max} MAD` },
      ];
    }
    if (language === 'ar') {
      return [
        { label: `أقل من ${fmtMax} درهم`, value: `أقل من ${max} درهم` },
        { label: `بين ${fmtMin} و ${fmtMax} درهم`, value: `بين ${min} و ${max} درهم` },
      ];
    }
    if (language === 'darija') {
      return [
        { label: `قل من ${fmtMax} درهم`, value: `قل من ${max} درهم` },
        { label: `بين ${fmtMin} و ${fmtMax} درهم`, value: `بين ${min} و ${max} درهم` },
      ];
    }
    return [
      { label: `Moins de ${fmtMax} MAD`, value: `moins de ${max} MAD` },
      { label: `Entre ${fmtMin} et ${fmtMax} MAD`, value: `entre ${min} et ${max} MAD` },
    ];
  }

  const step = spread > 600000 ? 25000 : spread > 150000 ? 10000 : 5000;
  const tier1 = Math.round((min + spread * 0.38) / step) * step;
  const tier2 = Math.round((min + spread * 0.72) / step) * step;

  const fmtMin = min.toLocaleString(locale);
  const fmtT1 = tier1.toLocaleString(locale);
  const fmtT2 = tier2.toLocaleString(locale);
  const fmtMax = max.toLocaleString(locale);

  if (language === 'en') {
    return [
      { label: `Under ${fmtT1} MAD (Accessible)`, value: `between ${min} and ${tier1} MAD` },
      { label: `${fmtT1} – ${fmtT2} MAD (Balanced)`, value: `between ${tier1} and ${tier2} MAD` },
      { label: `${fmtT2} – ${fmtMax} MAD (Top specs)`, value: `between ${tier2} and ${max} MAD` },
    ];
  }
  if (language === 'ar') {
    return [
      { label: `أقل من ${fmtT1} درهم (اقتصادي)`, value: `بين ${min} و ${tier1} درهم` },
      { label: `بين ${fmtT1} و ${fmtT2} درهم (متوازن)`, value: `بين ${tier1} و ${tier2} درهم` },
      { label: `بين ${fmtT2} و ${fmtMax} درهم (تجهيز كامل)`, value: `بين ${tier2} و ${max} درهم` },
    ];
  }
  if (language === 'darija') {
    return [
      { label: `قل من ${fmtT1} درهم (اقتصادي)`, value: `بين ${min} و ${tier1} درهم` },
      { label: `بين ${fmtT1} و ${fmtT2} درهم (مناسب)`, value: `بين ${tier1} و ${tier2} درهم` },
      { label: `بين ${fmtT2} و ${fmtMax} درهم (عامرة مزيان)`, value: `بين ${tier2} و ${max} درهم` },
    ];
  }
  return [
    { label: `Moins de ${fmtT1} MAD (Accessible)`, value: `entre ${min} et ${tier1} MAD` },
    { label: `${fmtT1} – ${fmtT2} MAD (Équilibré)`, value: `entre ${tier1} et ${tier2} MAD` },
    { label: `${fmtT2} – ${fmtMax} MAD (Toutes options)`, value: `entre ${tier2} et ${max} MAD` },
  ];
}

function dynamicQuestion(language: ChatLanguage, history: ChatTurn[], remainingCars: Car[]): NextQuestion | null {
  const text = profileText(history);
  const detectedProfile = detectClientProfile(text);
  const lastUserAnswer = [...history].reverse().find((turn) => turn.role === 'user')?.content || '';
  const budgetQuestionAsked = history.some((turn) => turn.role === 'assistant' && /budget|prix|price|ميزاني/i.test(turn.content));
  // Do not treat unrelated numeric answers (for example, "22 years old") as
  // a budget. Once the budget question has been asked, a bare number is a
  // valid answer because the user may enter just the MAD amount.
  const hasExplicitBudget = /\b(?:budget|prix|price|mad|dhs?|dh|dirhams?)\b|ميزاني|درهم|دراهم/i.test(text)
    || /\d[\d\s.,]*\s*(?:k|mad|dhs?|dirhams?)\b/i.test(text)
    || /\d[\d\s.,]*\s*(?:درهم|دراهم|ألف)/i.test(text)
    || /(?:under|below|less than|moins de|jusqu['’à]|between|entre|بين)\s*\d/i.test(text);
  const hasBudget = Boolean(extractMaximumBudget(text))
    || Boolean(extractBudgetRange(text))
    || hasExplicitBudget
    || (budgetQuestionAsked && /\d/.test(lastUserAnswer));
  const questionWasAnswered = (pattern: RegExp) => history.some((turn, index) => (
    turn.role === 'assistant'
      && pattern.test(turn.content)
      && history.slice(index + 1).some((nextTurn) => nextTurn.role === 'user')
  ));

  const usageQuestionAnswered = questionWasAnswered(/ville|autoroute|city|highway|طريق|مدينة|أين تقطع|sur quel terrain/i);
  const hasUsage = hasAny(text, [
    /\b(city|ville|urban|highway|autoroute|motorway|mixed|mixte|daily|quotidien|commut|family trip|long trip|both|mostly city|mostly highway|city commute|highway driving)\b/i,
    /(?:^|[^\p{L}\p{N}])(?:ال|ف|فال|بال|طريق\s+)?(مدينة|طريق|سفر|مخلط|يومي|العائلة|عائلية|عائلي|الأسرة|اسرة|بجوج)(?:$|[^\p{L}\p{N}])/iu,
  ]) || usageQuestionAnswered;

  const fuelQuestionAnswered = questionWasAnswered(/fuel|carburant|وقود|كاربيرون/i);
  const hasFuel = hasAny(text, [
    /\b(diesel|petrol|essence|gasoline|hybrid|hybride|electric|électrique|ev|mazout|mazot)\b/i,
    /(?:^|[^\p{L}\p{N}])(?:ال)?(بنزين|مازوط|هجين|كهربائي|كهربائ)(?:$|[^\p{L}\p{N}])/iu,
  ]) || fuelQuestionAnswered;

  const transmissionQuestionAnswered = questionWasAnswered(/gearbox|transmission|boîte|boite|ناقل|بواط/i);
  const hasTransmission = hasAny(text, [
    /\b(automatic|automatique|manual|manuelle|gearbox|boîte|boite|bva|bvm)\b/i,
    /(?:^|[^\p{L}\p{N}])(?:ال)?(أوتوماتيك|اوتوماتيك|يدوي|بواط)(?:$|[^\p{L}\p{N}])/iu,
  ]) || transmissionQuestionAnswered;

  const bodyQuestionAnswered = questionWasAnswered(/style|format|carrosserie|body|هيكل|شكل|نمط/i);
  const hasBody = hasAny(text, [
    /\b(suv|sedan|berline|hatchback|citadine|crossover|wagon|break|pickup|4x4|monospace|coupe|coupé|cabriolet)\b/i,
    /(?:^|[^\p{L}\p{N}])(?:ال)?(سيدان|suv|سيتادين|كروس|كوبيه|كوبي|بيرلين|برلين|هاتشباك|مونوسباس)(?:$|[^\p{L}\p{N}])/iu,
  ]) || bodyQuestionAnswered;

  const suitcaseQuestionAnswered = questionWasAnswered(/valises?|suitcases?|bagages?|coffre|luggage|حقائب|فاليزات|أمتعة/i);
  const hasSuitcaseRangeInHistory = Boolean(extractSuitcaseRange(text) || extractSuitcaseMinimum(text));
  const hasSpace = hasAny(text, [
    /\b(children|kids|baby|trunk|boot|luggage|space|spacious|coffre|bagages?|valises?|suitcases?|poussette|places|7 seats)\b/i,
    /(?:^|[^\p{L}\p{N}])(?:ال)?(أطفال|شنطة|أمتعة|واسعة|بلايص|حقائب|فاليزات)(?:$|[^\p{L}\p{N}])/iu,
  ]) || suitcaseQuestionAnswered || hasSuitcaseRangeInHistory;

  const priorityQuestionAnswered = questionWasAnswered(
    /priorit|importance|important|matters most|exigence|primordial|critère|requirement|أولوية|أولويتكم|الأولوية|معيار|أهم|المعيار|لا غنى عليه|تجربة|experience|performance|power|acceleration|running costs|consumption|coûts|standing|prestige|الأداء|القوة|التسارع|استهلاك|الأمان|أمان/i
  );

  const hasPriority = hasAny(text, [
    /\b(safe|safety|security|sécurité|economical|economy|consumption|consommation|performance|power|comfort|confort|reliable|fiable|fiabilité|sav|connectivité|carplay|autonomie|insonorisation|hybrid|hybride|electric|électrique|prestige|standing)\b/i,
    /(?:^|[^\p{L}\p{N}])(?:ال)?(السلامة|اقتصادية|استهلاك|قوية|مريحة|موثوقة|الأمان|الامان|صندوق|مقاعد|أمتعة|امتعة|موثوقية|اعتمادية|اتصال|شاشة|تكنولوجيا|صيانة|عزل|تكاليف|مصاريف|توفير|اقتصاد|برستيج|هيبة)(?:$|[^\p{L}\p{N}])/iu,
  ]) || priorityQuestionAnswered;

  const fuels = new Set(remainingCars.map((car) => car.fuel_type).filter(Boolean));
  const transmissions = new Set(remainingCars.map((car) => car.transmission).filter(Boolean));
  const bodies = new Set(remainingCars.map((car) => car.body_type).filter(Boolean));

  if (detectedProfile === 'taxi') {
    const isGrandTaxi = hasAny(text, [
      /\b(grand\s*taxi|gran\s*taxi|interurbain|interurbaine|intervilles|inter-villes|ludospace|monospace|6\s*places|7\s*places|7\s*seats|6\s*seats)\b/i,
      /(?:^|[^\p{L}\p{N}])(?:ال)?(طاكسي\s*كبير|تاكسي\s*كبير|ݣران\s*طاكسي|كران\s*طاكسي|بين\s*المدن|6\s*بلايص|7\s*بلايص)(?:$|[^\p{L}\p{N}])/iu,
    ]);

    const isPetitTaxi = hasAny(text, [
      /\b(petit\s*taxi|piti\s*taxi|urbain|urbaine|citadine|berline|ville|5\s*places|5\s*seats)\b/i,
      /(?:^|[^\p{L}\p{N}])(?:ال)?(طاكسي\s*صغير|تاكسي\s*صغير|بيتي\s*طاكسي|حضر(?:ي|ية)|داخل\s*المدينة|5\s*بلايص)(?:$|[^\p{L}\p{N}])/iu,
    ]);

    const hasTaxiType = isGrandTaxi || isPetitTaxi || questionWasAnswered(/petit taxi|grand taxi|طاكسي صغير|طاكسي كبير|بيتي طاكسي|ݣران طاكسي/i);

    if (!hasTaxiType) {
      return {
        question: language === 'en'
          ? 'Do you operate a Petit Taxi (urban, 5 seats) or a Grand Taxi (intercity, 6-7 seats)?'
          : language === 'ar'
            ? 'هل تعمل بسيارة أجرة صغيرة (حضرية، 5 مقاعد) أم سيارة أجرة كبيرة (بين المدن، 6-7 مقاعد)؟'
            : language === 'darija'
              ? 'واش خدام بيتي طاكسي (صغير فالمرحلة الحضرية، 5 بلايص) ولا ݣران طاكسي (كبير بين المدن، 6-7 بلايص)؟'
              : 'Exercez-vous en Petit Taxi (urbain, 5 places) ou en Grand Taxi (interurbain, 6-7 places) ?',
        options: language === 'en'
          ? [{ label: 'Petit Taxi (5 seats)', value: 'petit taxi' }, { label: 'Grand Taxi (6-7 seats)', value: 'grand taxi' }]
          : language === 'ar'
            ? [{ label: 'طاكسي صغير (5 مقاعد)', value: 'طاكسي صغير' }, { label: 'طاكسي كبير (6-7 مقاعد)', value: 'طاكسي كبير' }]
            : language === 'darija'
              ? [{ label: 'بيتي طاكسي (5 بلايص)', value: 'بيتي طاكسي' }, { label: 'ݣران طاكسي (6-7 بلايص)', value: 'ݣران طاكسي' }]
              : [{ label: 'Petit Taxi (Urbain 5 places)', value: 'petit taxi' }, { label: 'Grand Taxi (Interurbain 6-7 places)', value: 'grand taxi' }],
      };
    }

    if (!hasBudget) {
      const fallbackBounds = {
        min: 90000,
        max: isGrandTaxi ? 320000 : 250000,
        step: 5000,
        label: language === 'en' ? 'Taxi budget' : language === 'ar' || language === 'darija' ? 'ميزانية الطاكسي' : 'Budget taxi',
      };
      const bounds = computeCarPriceBounds(remainingCars, fallbackBounds);
      return {
        question: language === 'en'
          ? 'For your taxi operation, what is your maximum investment budget in MAD for optimal profitability and low running costs?'
          : language === 'ar'
            ? 'لنشاطك في سيارات الأجرة ولتحقيق أفضل مردودية وتوفير في المصاريف: ما هي ميزانيتك القصوى بالدرهم؟'
            : language === 'darija'
              ? 'باش تخدم طاكسي وتكون الضربة رابحة فالمصاريف والكيلومتراج: شحال هي الميزانية القصوى ديالك بالدرهم؟'
              : 'Pour votre activité de taxi, quel est votre budget d’investissement maximum en MAD (rentabilité et coût au kilomètre optimisés) ?',
        options: generateDynamicBudgetOptions(bounds.min, bounds.max, language),
        rangeBounds: bounds,
      };
    }

    const hasTaxiPriority = hasPriority || questionWasAnswered(/priorité d’exploitation|rentabiliser|أولويتك التشغيلية|الأولوية ديالك فخدمة الطاكسي|taxi profitability/i);
    if (!hasTaxiPriority) {
      return {
        question: language === 'en'
          ? 'What is your main operational priority to maximize your daily taxi profitability?'
          : language === 'ar'
            ? 'ما هي أولويتك التشغيلية لضمان أفضل مردودية لسيارة الأجرة يومياً؟'
            : language === 'darija'
              ? 'شنو هي الأولوية ديالك فخدمة الطاكسي باش تكون رابح كل نهار؟'
              : 'Quelle est votre priorité d’exploitation pour rentabiliser votre taxi au quotidien ?',
        options: language === 'en'
          ? [
              { label: 'Lowest fuel consumption', value: 'lowest fuel consumption' },
              { label: 'Cheap spare parts & easy maintenance', value: 'cheap spare parts and easy maintenance' },
              { label: 'Large trunk & passenger comfort', value: 'large trunk and passenger comfort' },
            ]
          : language === 'ar'
            ? [
                { label: 'استهلاك وقود منخفض جداً', value: 'استهلاك وقود منخفض' },
                { label: 'قطع غيار متوفرة وصيانة سهلة', value: 'قطع غيار متوفرة وصيانة سهلة' },
                { label: 'صندوق أمتعة واسع وراحة الركاب', value: 'صندوق أمتعة واسع وراحة الركاب' },
              ]
            : language === 'darija'
              ? [
                  { label: 'استهلاك قليل بزاف (مازوط/هجين)', value: 'استهلاك قليل بزاف' },
                  { label: 'بياس موجود ورخيص وصيانة ساهلة', value: 'بياس موجود ورخيص وصيانة ساهلة' },
                  { label: 'كوفير كبير وراحة للكليان', value: 'كوفير كبير وراحة للكليان' },
                ]
              : [
                  { label: 'Consommation minimale (Diesel/Hybride)', value: 'consommation minimale' },
                  { label: 'Pièces abordables & entretien facile', value: 'pièces abordables et entretien facile' },
                  { label: 'Grand coffre & confort passagers', value: 'grand coffre et confort passagers' },
                ],
      };
    }

    return null;
  }

  if (!hasBudget) {
    const isCitadine = extractBodyPreference(text) === 'citadine';
    const isFamily = hasAny(text, [/\b(family|famille|children|kids|baby|poussette|3a2ila)\b/i]);
    const is7Places = /7\s*(?:places|seats|بلايص|مقاعد)/i.test(text);
    const fallbackBounds = is7Places
      ? {
          min: 140000,
          max: 550000,
          step: 10000,
          label: language === 'en' ? 'Family budget' : language === 'ar' || language === 'darija' ? 'ميزانية العائلة' : 'Budget familial',
        }
      : isFamily
        ? {
            min: 140000,
            max: 450000,
            step: 10000,
            label: language === 'en' ? 'Family budget' : language === 'ar' || language === 'darija' ? 'ميزانية العائلة' : 'Budget familial',
          }
        : isCitadine
          ? {
              min: 80000,
              max: 260000,
              step: 5000,
              label: language === 'en' ? 'City car budget' : language === 'ar' || language === 'darija' ? 'ميزانية سيارة صغيرة' : 'Budget citadine',
            }
          : {
              min: 89000,
              max: 1200000,
              step: 5000,
              label: language === 'en' ? 'Recommended budget' : language === 'ar' || language === 'darija' ? 'الميزانية الموصى بها' : 'Budget recommandé',
            };
    const bounds = computeCarPriceBounds(remainingCars, fallbackBounds);
    return {
      question: language === 'en' ? 'What is your maximum budget in MAD?' : language === 'ar' ? 'ما هي ميزانيتك القصوى بالدرهم؟' : language === 'darija' ? 'شحال هي الميزانية القصوى ديالك بالدرهم؟' : 'Quel est votre budget maximum en MAD ?',
      options: generateDynamicBudgetOptions(bounds.min, bounds.max, language),
      rangeBounds: bounds,
    };
  }

  if (!hasUsage) {
    const question = language === 'en'
      ? 'How will you mainly use the car: city driving, highways, or a mix of both?'
      : language === 'ar'
        ? 'كيف ستستعمل السيارة غالباً: داخل المدينة، في الطريق السيار، أم الاثنين؟'
        : language === 'darija'
          ? 'فين غادي تستعمل الطوموبيل أكثر: فالمدينة، فالطريق السيار، ولا بجوج؟'
          : 'Vous roulerez surtout en ville, sur autoroute ou dans les deux ?';

    return {
      question,
      options: language === 'en'
        ? [{ label: 'Mostly city' }, { label: 'Mostly highway' }, { label: 'Both' }]
        : language === 'ar'
          ? [{ label: 'داخل المدينة' }, { label: 'في الطريق السيار' }, { label: 'الاثنين' }]
          : language === 'darija'
            ? [{ label: 'فالمدينة' }, { label: 'فالطريق السيار' }, { label: 'بجوج' }]
            : [{ label: 'Ville' }, { label: 'Autoroute' }, { label: 'Mixte' }],
    };
  }

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
  const isEcoCar = (car: Car) => /hybrid|hybride|electric|electrique|phev|ev/i.test(car.fuel_type || '') || /hybrid|hybride|electric|electrique|phev|ev/i.test(car.engine_type || '');
  const is4x4Car = (car: Car) => Boolean(car.is_4x4) || /4x4|awd|integral/i.test(car.transmission || '') || /4x4|awd/i.test((car as any).drivetrain || '');
  const ncapTier = (car: Car) => {
    const s = getNcapScore(car);
    return s === 5 ? '5star' : s >= 4 ? '4star' : s > 0 ? 'standard' : 'unknown';
  };
  const bodyTier = (car: Car) => normalizeBodyType(car.body_type);
  const ncapValues = remainingCars.map(ncapTier);
  const powerValues = remainingCars.map((car) => car.engine_power_hp).filter((value): value is number => Number.isFinite(value));

  const dimensionCandidates = [
    { key: 'espace', covered: hasSpace, values: trunkValues.map(String), priority: 0 },
    { key: 'securite', covered: safetyPreferencePattern.test(text) || questionWasAnswered(/certified safety|note ncap|high ncap|safety|security|sécurité|securite|ncap|السلامة|أمان/i), values: ncapValues, priority: 1 },
    {
      key: 'cout_reel',
      covered:
        /economy|economical|consumption|consommation|conso|économique|économie|running\s+costs?|low\s+fuel|faible\s+conso|coûts?|frais/i.test(text)
        || /(?:استهلاك|توفير|تكاليف|مصاريف|اقتصاد|الصرف|صرف)/i.test(text)
        || questionWasAnswered(/lower fuel consumption|running costs|coûts?|consommation|consom|استهلاك|تكاليف(?:\s+تشغيل)?|مصاريف(?:\s+الاستعمال)?|الصرف/i),
      values: remainingCars.map((c) => (c.fuel_type || '').toLowerCase()),
      priority: 2,
    },
    { key: 'praticite_urbaine', covered: questionWasAnswered(/compact|easy to park|facile à garer|parking|ركن|الركنة|باركينغ|silhouette|carrosserie|format/i), values: remainingCars.map(bodyTier), priority: 3 },
    { key: 'performance', covered: /performance|power|puissance|sportif|قوية|تسارع|الأداء/i.test(text) || /(?:^|[^\p{L}\p{N}])(القوة|التسارع|الأداء)(?:$|[^\p{L}\p{N}])/iu.test(text) || questionWasAnswered(/power and acceleration|performance|puissance|التسارع|الأداء|القوة/i), values: powerValues.map(String), priority: 4 },
    { key: 'ecologie', covered: /hybrid|hybride|electric|électrique|ecolog|écolog|co2|بيئي/i.test(text) || /(?:^|[^\p{L}\p{N}])(هجين|كهربائي|بيئي)(?:$|[^\p{L}\p{N}])/iu.test(text) || questionWasAnswered(/hybrid or electric|hybride ou électrique|هجين|الهجين|كهربائي/i), values: remainingCars.map((c) => isEcoCar(c) ? 'eco' : 'thermal'), priority: 5 },
    { key: 'motricite', covered: /4x4|awd|offroad|tout.?terrain|mountain|montagne/i.test(text) || /(?:^|[^\p{L}\p{N}])(دفع\s*رباعي|رباعي)(?:$|[^\p{L}\p{N}])/iu.test(text) || questionWasAnswered(/four-wheel drive|all-wheel drive|4x4|awd|off-road|transmission intégrale|دفع\s*رباعي|الدفع الرباعي/i), values: remainingCars.map((c) => is4x4Car(c) ? '4x4' : '2wd'), priority: 6 },
  ];
  const dimensionTokens: Record<string, RegExp> = {
    espace: /luggage|suitcase|valise|coffre|bagages|passengers|حقائب|فاليزات|أمتعة/i,
    securite: /safety|security|sécurité|securite|ncap|السلامة|أمان/i,
    cout_reel: /(?:lower fuel consumption|fuel consumption|consommation|استهلاك|الصرف|مصاريف)/i,
    praticite_urbaine: /city|ville|parking|compact|urbain|ركن|الركنة|باركينغ|silhouette|carrosserie|format/i,
    performance: /(?:power and acceleration|puissance\s*(?:et\s*les\s*reprises|&|et)?|performance|power|تسارع|القوة)/i,
    ecologie: /hybrid|electric|électrique|ecolog|co2|هجين|كهربائي/i,
    motricite: /4x4|awd|offroad|terrain|motricité|دفع رباعي|رباعي/i,
  };
  // Any dimension whose question was asked by assistant and subsequently answered by user is definitively covered
  dimensionCandidates.forEach((candidate) => {
    const pattern = dimensionTokens[candidate.key];
    if (pattern && questionWasAnswered(pattern)) {
      candidate.covered = true;
    }
  });
  const lastTurn = history[history.length - 1];
  const lastAssistantQuestion = [...history].reverse().find((turn) => turn.role === 'assistant')?.content || '';
  const pendingDimension = dimensionCandidates.find((candidate) => Boolean(dimensionTokens[candidate.key]?.test(lastAssistantQuestion)));
  const selectableDimensions = dimensionCandidates
    .filter((candidate) => !candidate.covered && (lastTurn?.role === 'assistant' || candidate !== pendingDimension))
    .map((candidate) => ({ ...candidate, diversity: new Set(candidate.values).size }))
    .filter((candidate) => candidate.diversity > 1 || (!remainingCars.length));
  const selectedDimension = [...selectableDimensions].sort((a, b) => b.diversity - a.diversity || a.priority - b.priority)[0]?.key;

  if (remainingCars && remainingCars.length > 0 && hasBudget && hasUsage && lastTurn?.role !== 'assistant') {
    if (remainingCars.length === 1) {
      return null;
    }
    if (selectableDimensions.length === 0) {
      return null;
    }
  }

  const buildCandidateDimensionQuestion = (key: string): NextQuestion | null => {
    if (key === 'espace') {
      const has7SeatsCar = remainingCars.some((car) => (Number(car.seats) || 5) >= 7);
      const has5SeatsCar = remainingCars.length === 0 || remainingCars.some((car) => (Number(car.seats) || 5) < 7);
      if (has7SeatsCar && has5SeatsCar) {
        const spaceOptions: QuestionOption[] = [
          language === 'en' ? { label: 'Large trunk (3-4 suitcases)' } : language === 'ar' ? { label: 'صندوق كبير (3-4 حقائب)' } : language === 'darija' ? { label: 'كوفير كبير (3-4 فاليزات)' } : { label: 'Grand coffre (3-4 valises)' },
          language === 'en' ? { label: '7 seats / Extra space' } : language === 'ar' ? { label: '7 مقاعد / مساحة إضافية' } : language === 'darija' ? { label: '7 د البلايص / وسع أكثر' } : { label: '7 places / Grand espace' },
          language === 'en' ? { label: 'Standard trunk' } : language === 'ar' ? { label: 'صندوق قياسي' } : language === 'darija' ? { label: 'كوفير عادي' } : { label: 'Coffre standard' },
        ];
        return {
          question: language === 'en'
            ? 'Do you need a large trunk or 7 seats for extra space?'
            : language === 'ar'
              ? 'هل تحتاج إلى صندوق أمتعة كبير أو 7 مقاعد لمساحة إضافية؟'
              : language === 'darija'
                ? 'واش كتحتاج كوفير كبير ولا 7 د البلايص لمساحة أكبر؟'
                : 'Avez-vous besoin d’un grand coffre ou de 7 places pour plus d’espace ?',
          options: spaceOptions,
        };
      }
      if (suitcaseMax > suitcaseMin && (suitcaseMax - suitcaseMin >= 2 || remainingCars.length === 0)) {
        return {
          question: language === 'en' ? 'How much luggage space do you need, in suitcases?' : language === 'ar' ? 'كم من مساحة الأمتعة تحتاج، بعدد الحقائب؟' : language === 'darija' ? 'شحال من بلاصة ديال الباݣاج كتحتاج، بعدد الفاليزات؟' : 'De combien de place pour les bagages avez-vous besoin, en valises ?',
          options: hasWideSuitcaseRange ? [] : suitcaseChoices(language, suitcaseMin, suitcaseMax),
          ...(hasWideSuitcaseRange ? { rangeBounds: { min: suitcaseMin, max: suitcaseMax, step: 1, label: language === 'en' ? 'Suitcase capacity' : language === 'ar' ? 'سعة الحقائب' : language === 'darija' ? 'سعة الفاليزات' : 'Capacité en valises' } } : {}),
        };
      }
      const hasLargeTrunk = remainingCars.length === 0 || remainingCars.some((c) => (Number(c.trunk_volume_l) || 0) >= 380);
      const hasStandardTrunk = remainingCars.length === 0 || remainingCars.some((c) => (Number(c.trunk_volume_l) || 0) < 380);
      if (hasLargeTrunk && hasStandardTrunk) {
        const spaceOptions: QuestionOption[] = [
          language === 'en' ? { label: 'Large trunk (3-4 suitcases)' } : language === 'ar' ? { label: 'صندوق كبير (3-4 حقائب)' } : language === 'darija' ? { label: 'كوفير كبير (3-4 فاليزات)' } : { label: 'Grand coffre (3-4 valises)' },
          language === 'en' ? { label: 'Standard trunk' } : language === 'ar' ? { label: 'صندوق قياسي' } : language === 'darija' ? { label: 'كوفير عادي' } : { label: 'Coffre standard' },
        ];
        return {
          question: language === 'en'
            ? 'Do you need a large trunk for luggage and suitcases?'
            : language === 'ar'
              ? 'هل تحتاج إلى صندوق أمتعة كبير للحقائب والأمتعة؟'
              : language === 'darija'
                ? 'واش كتحتاج كوفير كبير للفاليزات والباݣاج؟'
                : 'Avez-vous besoin d’un grand coffre pour vos bagages et valises ?',
          options: spaceOptions,
        };
      }
      return null;
    }

    if (key === 'body_format') {
      const availableBodies = [...new Set(remainingCars.map((c) => normalizeBodyType(c.body_type)).filter(Boolean))];
      if (remainingCars.length > 0 && availableBodies.length < 2) return null;
      const bodies = availableBodies.length >= 2 ? availableBodies : ['suv', 'berline', 'citadine'];
      const bodyLabels: Record<string, Record<ChatLanguage, string>> = {
        suv: { fr: 'SUV', en: 'SUV', ar: 'دفع رباعي (SUV)', darija: 'SUV عالي' },
        berline: { fr: 'Berline', en: 'Sedan', ar: 'سيدان', darija: 'بيرلين' },
        citadine: { fr: 'Citadine compacte', en: 'Compact city car', ar: 'سيارة مدمجة', darija: 'سيتادين صغيرة' },
        break: { fr: 'Break', en: 'Estate / Wagon', ar: 'واغن عائلية', darija: 'بريك عائلي' },
        monospace: { fr: 'Monospace', en: 'MPV / Minivan', ar: 'مونوسباس', darija: 'مونوسباس' },
        coupe: { fr: 'Coupé', en: 'Coupe', ar: 'كوبيه', darija: 'كوبي' },
        pick_up: { fr: 'Pick-up', en: 'Pick-up', ar: 'بيك أب', darija: 'بيك آب' },
        cabriolet: { fr: 'Cabriolet', en: 'Convertible', ar: 'كابريوليه', darija: 'كابريولي' },
      };
      const bodyOptions: QuestionOption[] = bodies.map((b) => ({
        label: bodyLabels[b]?.[language] || b.toUpperCase(),
        value: b,
      }));
      bodyOptions.push(
        language === 'en' ? { label: 'No preference', value: 'no preference' }
        : language === 'ar' ? { label: 'لا أفضلية', value: 'لا أفضلية' }
        : language === 'darija' ? { label: 'ما عنديش تفضيل', value: 'ما عنديش تفضيل' }
        : { label: 'Pas de préférence', value: 'pas de preference' }
      );
      return {
        question: language === 'en'
          ? 'Which vehicle style do you prefer?'
          : language === 'ar'
            ? 'ما هو نمط وهيكل السيارة الذي تفضله؟'
            : language === 'darija'
              ? 'شنو هو شكل الطوموبيل اللي كتفضل؟'
              : 'Quel format ou silhouette de véhicule préférez-vous ?',
        options: bodyOptions,
      };
    }
if (key === 'securite') {
      const has5Star = remainingCars.length === 0 || remainingCars.some((c) => getNcapScore(c) === 5);
      const has4Star = remainingCars.length === 0 || remainingCars.some((c) => getNcapScore(c) >= 4);
      const hasLower = remainingCars.length === 0 || remainingCars.some((c) => getNcapScore(c) < 5);
      if (remainingCars.length > 0 && !hasLower) return null;
      if (remainingCars.length > 0 && !has5Star && !has4Star) return null;

      const secOptions: QuestionOption[] = [];
      if (has5Star) {
        secOptions.push(language === 'en' ? { label: 'Highest NCAP rating (5★)' } : language === 'ar' ? { label: 'أعلى تقييم NCAP (5★)' } : language === 'darija' ? { label: 'أعلى نقطة NCAP (5★)' } : { label: 'Note NCAP maximale (5★)' });
      }
      if (has4Star && (remainingCars.length === 0 || remainingCars.some((c) => getNcapScore(c) < 4))) {
        secOptions.push(language === 'en' ? { label: 'Good safety (4★+)' } : language === 'ar' ? { label: 'سلامة جيدة (4★+)' } : language === 'darija' ? { label: 'سلامة مزيانة (4★+)' } : { label: 'Bonne sécurité (4★+)' });
      }
      secOptions.push(language === 'en' ? { label: 'No preference' } : language === 'ar' ? { label: 'لا أفضلية' } : language === 'darija' ? { label: 'ما عنديش تفضيل' } : { label: 'Pas de préférence' });
      return {
        question: language === 'en' ? 'How important is certified safety and a high NCAP rating to you?' : language === 'ar' ? 'ما مدى أهمية السلامة المعتمدة ونتيجة NCAP المرتفعة؟' : language === 'darija' ? 'شحال مهمة عندك السلامة ونتيجة NCAP؟' : 'Quelle importance accordez-vous à la sécurité certifiée et à une bonne note NCAP ?',
        options: secOptions,
      };
    }

    if (key === 'cout_reel') {
      const hasEco = remainingCars.length === 0 || remainingCars.some((c) => isEcoCar(c) || /diesel/i.test(c.fuel_type || '') || Number(c.fuel_consumption ?? c.official_consumption ?? 6) <= 5.2);
      const hasHigherCost = remainingCars.length === 0 || remainingCars.some((c) => !isEcoCar(c) && !/diesel/i.test(c.fuel_type || '') && Number(c.fuel_consumption ?? c.official_consumption ?? 6) > 5.2);
      if (remainingCars.length > 0 && (!hasEco || !hasHigherCost)) return null;
      return {
        question: language === 'en' ? 'Would you prioritize lower fuel consumption and running costs?' : language === 'ar' ? 'هل تفضل استهلاكاً وتكاليف تشغيل أقل؟' : language === 'darija' ? 'كتفضل الصرف ومصاريف الاستعمال يكونو قليلين؟' : 'Souhaitez-vous privilégier une consommation et des coûts d’usage réduits ?',
        options: language === 'en'
          ? [{ label: 'Economy & lower costs' }, { label: 'No preference' }]
          : language === 'ar'
            ? [{ label: 'توفير وتكاليف أقل' }, { label: 'لا أفضلية' }]
            : language === 'darija'
              ? [{ label: 'اقتصاد ومصاريف قليلة' }, { label: 'ما عنديش تفضيل' }]
              : [{ label: 'Économie & coûts réduits' }, { label: 'Pas de préférence' }],
      };
    }

    if (key === 'praticite_urbaine') {
      const hasCompact = remainingCars.length === 0 || remainingCars.some((c) => ['citadine', 'hatchback'].includes(normalizeBodyType(c.body_type)));
      const hasLarge = remainingCars.length === 0 || remainingCars.some((c) => ['suv', 'berline', 'break', 'monospace'].includes(normalizeBodyType(c.body_type)));
      if (remainingCars.length > 0 && (!hasCompact || !hasLarge)) return null;
      const urbOptions: QuestionOption[] = [
        language === 'en' ? { label: 'Compact (easy to park)' } : language === 'ar' ? { label: 'حجم مدمج (سهل الركن)' } : language === 'darija' ? { label: 'صغيرة وساهلة فالركنة' } : { label: 'Format compact (facile à garer)' },
        language === 'en' ? { label: 'More interior space' } : language === 'ar' ? { label: 'مساحة داخلية أكبر' } : language === 'darija' ? { label: 'بلاصة أكثر' } : { label: 'Plus d’espace intérieur' },
        language === 'en' ? { label: 'No preference' } : language === 'ar' ? { label: 'لا أفضلية' } : language === 'darija' ? { label: 'ما عنديش تفضيل' } : { label: 'Pas de préférence' },
      ];
      return {
        question: language === 'en' ? 'For city driving, do you prefer a compact car that is easy to park?' : language === 'ar' ? 'للاستعمال داخل المدينة، هل تفضل سيارة صغيرة وسهلة الركن؟' : language === 'darija' ? 'فالمدينة، كتفضل طوموبيل صغيرة وساهلة فالباركينغ؟' : 'Pour la ville, préférez-vous une voiture compacte et facile à garer ?',
        options: urbOptions,
      };
    }

    if (key === 'performance') {
      const powers = remainingCars.map((c) => Number(c.engine_power_hp) || 0).filter((p) => p > 0);
      const hasDiff = powers.length > 1 && Math.min(...powers) < Math.max(...powers);
      const hasPowerful = remainingCars.length === 0 || hasDiff || remainingCars.some((c) => (Number(c.engine_power_hp) || 0) >= 115);
      const hasModerate = remainingCars.length === 0 || hasDiff || remainingCars.some((c) => (Number(c.engine_power_hp) || 0) < 115);
      if (remainingCars.length > 0 && (!hasPowerful || !hasModerate)) return null;
      return {
        question: language === 'en' ? 'Do you prioritize power and acceleration over lower running costs?' : language === 'ar' ? 'هل تفضل القوة والتسارع على انخفاض تكاليف التشغيل؟' : language === 'darija' ? 'كتفضل القوة والتسارع ولا مصاريف قليلة؟' : 'Privilégiez-vous la puissance et les reprises plutôt que les coûts d’usage réduits ?',
        options: language === 'en'
          ? [{ label: 'Power and acceleration' }, { label: 'Lower running costs' }]
          : language === 'ar'
            ? [{ label: 'القوة والتسارع' }, { label: 'تكاليف تشغيل أقل' }]
            : language === 'darija'
              ? [{ label: 'القوة والتسارع' }, { label: 'مصاريف قليلة' }]
              : [{ label: 'Puissance & reprises' }, { label: 'Coûts d’usage réduits' }],
      };
    }

    if (key === 'ecologie') {
      const hasEco = remainingCars.length === 0 || remainingCars.some(isEcoCar);
      const hasThermal = remainingCars.length === 0 || remainingCars.some((c) => !isEcoCar(c));
      if (remainingCars.length > 0 && (!hasEco || !hasThermal)) return null;
      const ecoOptions: QuestionOption[] = [
        language === 'en' ? { label: 'Hybrid or Electric' } : language === 'ar' ? { label: 'هجين أو كهربائي' } : language === 'darija' ? { label: 'هجين ولا كهربائي' } : { label: 'Hybride ou Électrique' },
        language === 'en' ? { label: 'Petrol / Diesel' } : language === 'ar' ? { label: 'بنزين / ديزل' } : language === 'darija' ? { label: 'ليصانص ولا مازوط' } : { label: 'Essence / Diesel' },
        language === 'en' ? { label: 'No preference' } : language === 'ar' ? { label: 'لا أفضلية' } : language === 'darija' ? { label: 'ما عنديش تفضيل' } : { label: 'Pas de préférence' },
      ];
      return {
        question: language === 'en' ? 'Is hybrid or electric power a priority for you?' : language === 'ar' ? 'هل المحرك الهجين أو الكهربائي أولوية بالنسبة لك؟' : language === 'darija' ? 'واش الهجين ولا الكهربائي أولوية عندك؟' : 'La motorisation hybride ou électrique est-elle une priorité pour vous ?',
        options: ecoOptions,
      };
    }

    if (key === 'motricite') {
      const has4x4 = remainingCars.length === 0 || remainingCars.some(is4x4Car);
      const has2wd = remainingCars.length === 0 || remainingCars.some((c) => !is4x4Car(c));
      if (remainingCars.length > 0 && (!has4x4 || !has2wd)) return null;
      const motOptions: QuestionOption[] = [
        language === 'en' ? { label: 'Yes, 4x4 / AWD' } : language === 'ar' ? { label: 'دفع رباعي (4x4 / AWD)' } : language === 'darija' ? { label: 'دفع رباعي (4x4)' } : { label: '4x4 / Intégrale (AWD)' },
        language === 'en' ? { label: 'Standard (2WD)' } : language === 'ar' ? { label: 'دفع ثنائي عادي (2WD)' } : language === 'darija' ? { label: 'دفع عادي (2WD)' } : { label: '2 roues motrices (Standard)' },
        language === 'en' ? { label: 'No preference' } : language === 'ar' ? { label: 'لا أفضلية' } : language === 'darija' ? { label: 'ما عنديش تفضيل' } : { label: 'Pas de préférence' },
      ];
      return {
        question: language === 'en'
          ? 'Do you need all-wheel drive (4x4 / AWD)?'
          : language === 'ar'
            ? 'هل تحتاج إلى دفع رباعي (4x4 / AWD)؟'
            : language === 'darija'
              ? 'واش كتحتاج الدفع الرباعي (4x4)؟'
              : 'Avez-vous besoin d’une transmission 4x4 / intégrale (AWD) ?',
        options: motOptions,
      };
    }

    if (key === 'priority') {
      if (remainingCars.length > 0 && remainingCars.length <= 3) {
        const uniqueCarKeys = new Set(
          remainingCars.map((car) => `${normalizeBrandText(car.brand)} ${car.model.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()}`),
        );
        if (uniqueCarKeys.size <= 1) {
          return null;
        }
      }
      return {
        question: language === 'en' ? 'What matters most to you: economy, safety, comfort, or performance?' : language === 'ar' ? 'ما الأولوية الأهم لك: الاقتصاد، السلامة، الراحة أم الأداء؟' : language === 'darija' ? 'شنو هي الحاجة اللي مهمة عندك أكثر: الاقتصاد، السلامة، الراحة ولا الأداء؟' : 'Quelle est votre priorité : économie, sécurité, confort ou performance ?',
        options: language === 'en'
          ? [{ label: 'Economy' }, { label: 'Safety' }, { label: 'Comfort' }, { label: 'Performance' }]
          : language === 'ar'
            ? [{ label: 'الاقتصاد' }, { label: 'السلامة' }, { label: 'الراحة' }, { label: 'الأداء' }]
            : language === 'darija'
              ? [{ label: 'الاقتصاد' }, { label: 'السلامة' }, { label: 'الراحة' }, { label: 'الأداء' }]
              : [{ label: 'Économie' }, { label: 'Sécurité' }, { label: 'Confort' }, { label: 'Performance' }],
      };
    }

    return null;
  };

  const candidateKeys: string[] = [];
  const shouldCheckEspace = (selectedDimension === 'espace' || (!hasSpace && (hasAny(text, [/\b(family|famille|children|kids|baby|poussette|trunk|boot|coffre|luggage|bagages|valises?|3a2ila)\b/i]) || remainingCars.some((car) => (car.seats || 5) >= 7) || hasWideTrunkRange))) && !suitcaseQuestionAnswered && !hasSuitcaseRangeInHistory;
  if (shouldCheckEspace) {
    candidateKeys.push('espace');
  }

  const availableBodies = [...new Set(remainingCars.map((c) => normalizeBodyType(c.body_type)).filter(Boolean))];
  if ((availableBodies.length > 1 || remainingCars.length === 0) && !hasBody && !bodyQuestionAnswered && !candidateKeys.includes('body_format')) {
    candidateKeys.push('body_format');
  }

  const sortedCandidates = [...selectableDimensions].sort((a, b) => b.diversity - a.diversity || a.priority - b.priority);
  for (const c of sortedCandidates) {
    if (!candidateKeys.includes(c.key)) {
      candidateKeys.push(c.key);
    }
  }

  if (!hasPriority && !priorityQuestionAnswered && !candidateKeys.includes('priority')) {
    candidateKeys.push('priority');
  }

  if (lastTurn?.role === 'assistant' && pendingDimension) {
    const q = buildCandidateDimensionQuestion(pendingDimension.key);
    if (q) return q;
  }

  for (const key of candidateKeys) {
    const q = buildCandidateDimensionQuestion(key);
    if (q && hasAtLeastTwoValidSuggestions(q, remainingCars)) {
      return q;
    }
  }

  return null;
}

export function extractMaximumBudget(query: string): number | null {
  const range = extractBudgetRange(query);
  if (range) {
    return range.max;
  }
  // Case 1: Preceded by explicit budget keyword
  const keywordMatch = query.match(/(?:under|below|less than|max(?:imum)?|budget|have|avec|moins de|jusqu['’à]|≤|ميزانية|أقل من|ماكس|حتى ل|قل من)\s*[:=]?\s*(\d[\d\s.,]*)\s*(k|000|mad|dhs?|dh|dirhams?|دراهم?|ألف)?/i);
  if (keywordMatch) {
    const value = Number(keywordMatch[1].replace(/[\s.,]/g, ''));
    if (Number.isFinite(value) && value > 0) {
      const suffix = (keywordMatch[2] || '').toLowerCase();
      return suffix === 'k' || suffix === '000' || suffix === 'ألف' ? value * 1000 : value;
    }
  }

  // Case 2: Number followed by explicit currency or magnitude suffix
  const suffixMatch = query.match(/(?:\b(\d[\d\s.,]*)\s*(k|000|mad|dhs?|dh|dirhams?)\b|(?:\b(\d[\d\s.,]*)\s*(دراهم?|درهم|ألف)))(?![\\p{L}\\p{N}])/iu);
  if (suffixMatch) {
    const numStr = suffixMatch[1] || suffixMatch[3];
    const value = Number(numStr.replace(/[\s.,]/g, ''));
    if (Number.isFinite(value) && value > 0) {
      const suffix = (suffixMatch[2] || suffixMatch[4] || '').toLowerCase();
      return suffix === 'k' || suffix === '000' || suffix === 'ألف' ? value * 1000 : value;
    }
  }

  // Case 3: Large standalone number >= 10,000 surrounded by word boundaries (not part of alphanumeric words or models)
  const standaloneMatch = query.match(/\b([1-9]\d{4,7})\b/);
  if (standaloneMatch) {
    const value = Number(standaloneMatch[1]);
    if (Number.isFinite(value) && value >= 10000) {
      return value;
    }
  }

  return null;
}

export function extractMinimumBudget(query: string): number | null {
  const match = query.match(/(?:above|more than|over|min(?:imum)?|plus de|au-dessus de|au dessus de|≥|أكثر من|اكثر من|فوق|كثر من)\s*[:=]?\s*(\d[\d\s.,]*)\s*(k|000|mad|dhs?|dh|dirhams?|دراهم?|ألف|درهم)?/iu);
  if (!match) return null;
  const value = Number(match[1].replace(/[\s.,]/g, ''));
  if (!Number.isFinite(value) || value <= 0) return null;
  const suffix = (match[2] || '').toLowerCase();
  return suffix === 'k' || suffix === '000' || suffix === 'ألف' ? value * 1000 : value;
}

export function extractBudgetRange(query: string): { min: number; max: number } | null {
  const match = query.match(/(?:between|entre|بين)\s*(\d[\d\s.,]*)\s*(?:and|et|و|[-–])\s*(\d[\d\s.,]*)/iu)
    || query.match(/\b(\d[\d\s.,]{3,})\s*[-–]\s*(\d[\d\s.,]{3,})\s*(?:mad|dhs?|dh|dirhams?|درهم|دراهم)?/iu);
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
    if (informativeRequestPattern.test(message)) return false;
    const isBrandOrModelPurchase = Boolean(extractBrandPreference(message));
    const extractedMax = extractMaximumBudget(message);
    const hasExtractedBudget = extractedMax !== null && extractedMax >= 10000;
    const hasVehicleTerm = /\b(?:car|cars|vehicle|vehicles|suv|suvs|auto|automobile|automobiles|voiture|voitures|véhicule|véhicules|vehicule|vehicules|tomobil|tomobile|tomobila|tonobil|tonobile|tonobila|sayara|sayarat|berline|citadine|compacte|utilitaire|pick-?up)\b|(?:^|[^\p{L}\p{N}])(?:سيارة|سيارات|طوموبيل|طوموبيلا|طوموبيلات)(?:$|[^\p{L}\p{N}])/iu.test(message);
    const hasPurchaseOrBudgetContext = hasVehicleTerm
      || /\b(?:budget|prix|price|have|j'ai|under|below|less\s+than|moins\s+de|jusqu['’à]|max|maximum|plafond|pour|for|bghit|baghi)\b|(?:^|[^\p{L}\p{N}])(?:عندي|ميزانية|ثمن|أقل|بغيت|باغي)(?:$|[^\p{L}\p{N}])/iu.test(message);
    const isBudgetSearch = hasExtractedBudget && hasPurchaseOrBudgetContext;

    return intentPattern.test(message) || nonLatinIntentPattern.test(message) || budgetSearchPattern.test(message)
      || isBudgetSearch || hasProfilePreference(message) || isDailyUsageRequest(message) || isBrandOrModelPurchase
      || isCriterionPreference(message);
  }

  async getNextQuestion(history: ChatTurn[], remainingCars: Car[]): Promise<NextQuestion | null> {
    const question = dynamicQuestion(this.language, history, remainingCars);
    if (!question) return null;
    // Budget is the first qualification step. Keep it available even when a
    // semantic search has temporarily returned a very small candidate set;
    // otherwise the UI shows a budget prompt without its preference control.
    if (/budget|prix|ميزاني/i.test(question.question)) {
      const prices = remainingCars
        .map((car) => Number(car.price))
        .filter((price) => Number.isFinite(price) && price > 0);

      if (prices.length > 0) {
        const bounds = computeCarPriceBounds(remainingCars, question.rangeBounds || {
          min: Math.min(...prices),
          max: Math.max(...prices),
          step: 5000,
          label: this.language === 'en' ? 'Recommended budget' : this.language === 'ar' || this.language === 'darija' ? 'الميزانية الموصى بها' : 'Budget recommandé',
        });
        return {
          ...question,
          rangeBounds: bounds,
          options: question.options.length ? question.options : generateDynamicBudgetOptions(bounds.min, bounds.max, this.language),
        };
      }

      if (question.rangeBounds) {
        return question;
      }

      const [lowest, highest] = await Promise.all([
        vehicleService.getVehicles({ page: 1, page_size: 1, price_min: 1, sort_by: 'price', sort_order: 'asc' }),
        vehicleService.getVehicles({ page: 1, page_size: 1, price_min: 1, sort_by: 'price', sort_order: 'desc' }),
      ]);
      const fetchedPrices = [Number(lowest.items[0]?.price), Number(highest.items[0]?.price)]
        .filter((price) => Number.isFinite(price) && price > 0);
      const min = fetchedPrices.length ? Math.min(...fetchedPrices) : 89000;
      const max = fetchedPrices.length ? Math.max(...fetchedPrices) : 1500000;
      const bounds = { min, max, step: 10000, label: 'Budget catalogue' };
      return {
        ...question,
        rangeBounds: bounds,
        options: generateDynamicBudgetOptions(min, max, this.language),
      };
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
    const detectedProfile = detectClientProfile(historyText);
    const requestedBrand = extractBrandPreference(
      history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
    );
    const safetyRequested = safetyPreferencePattern.test(
      history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
    );
    const sortForSafety = (cars: Car[], forceSafety = safetyRequested): Car[] => (
      sortForSafetyGlobal(cars, forceSafety, detectedProfile)
    );
// The candidate pool already contains the constraints from previous
// answers. Only apply the criterion answered in this turn; re-reading an
// old budget range from the full history would swallow later answers such
// as suitcase capacity or body style.
const previousAssistantQuestion = [...history]
.reverse()
.find((turn) => turn.role === 'assistant')?.content || '';
  const budgetAnswerContext = /\b(budget|price|prix|mad|dhs?|dh|dirhams?)\b/i.test(answer)
    || /(?:درهم|دراهم|ميزاني)/i.test(answer)
    || /budget|prix|price|ميزاني/i.test(previousAssistantQuestion);
// “between 3 and 13” is also used by the suitcase control. Require
// budget context before interpreting a numeric range as a price range.
const budgetRange = budgetAnswerContext ? extractBudgetRange(answer) : null;
const budget = extractMaximumBudget(historyText);
const suitcaseRange = extractSuitcaseRange(answer);
const suitcaseMinimum = extractSuitcaseMinimum(answer);
const seatRange = extractSeatRange(answer);
const conditionPreference = extractConditionPreference(answer);
const bodyPreference = extractBodyPreference(answer);
const fuelPreference = extractFuelPreference(answer);
const answerBrand = extractBrandPreference(answer);
    const answerBudget = extractMaximumBudget(answer);
    const profilePreferenceOnly = hasProfilePreference(answer)
      && !budgetRange && answerBudget === null && !suitcaseRange && !bodyPreference && !fuelPreference
      && !extractTransmissionPreference(answer) && !answerBrand;

    let scopedRemainingCars = requestedBrand
      ? remainingCars.filter((car) => normalizeBrandText(car.brand) === normalizeBrandText(requestedBrand.name))
      : remainingCars;

    if (detectedProfile === 'executive') {
      const mentionsSupercar = hasAny(historyText, [
        /\b(supercar|hypercar|ferrari|lamborghini|mclaren|bugatti|aston martin|valhalla|sf90|12cilindri|revuelto|purosangue)\b/i,
      ]);
      if (!mentionsSupercar) {
        scopedRemainingCars = scopedRemainingCars.filter((car) => (
          !SUPERCAR_BRANDS.has(normalizeBrandText(car.brand))
          && (Number(car.price) || 0) <= 2500000
        ));
      }
    }

    // There is deliberately no gender or age column in the catalogue. Keep
    // these preferences as conversational context and continue asking useful
    // objective questions; never turn them into a stereotype-based hard filter
    // or let them produce an accidental zero-result recommendation.
    if (detectedProfile === 'taxi') {
      const isGrandTaxi = hasAny(historyText, [
        /\b(grand\s*taxi|gran\s*taxi|interurbain|interurbaine|intervilles|inter-villes|ludospace|monospace|6\s*places|7\s*places|7\s*seats|6\s*seats)\b/i,
        /(?:^|[^\p{L}\p{N}])(?:ال)?(طاكسي\s*كبير|تاكسي\s*كبير|ݣران\s*طاكسي|كران\s*طاكسي|بين\s*المدن|6\s*بلايص|7\s*بلايص)(?:$|[^\p{L}\p{N}])/iu,
      ]);
      const isPetitTaxi = hasAny(historyText, [
        /\b(petit\s*taxi|piti\s*taxi|urbain|urbaine|citadine|berline|ville|5\s*places|5\s*seats)\b/i,
        /(?:^|[^\p{L}\p{N}])(?:ال)?(طاكسي\s*صغير|تاكسي\s*صغير|بيتي\s*طاكسي|حضر(?:ي|ية)|داخل\s*المدينة|5\s*بلايص)(?:$|[^\p{L}\p{N}])/iu,
      ]);

      const basePool = scopedRemainingCars.length ? scopedRemainingCars : await loadAllCatalogueVehicles();
      let taxiPool = basePool.filter((c) => (
        !TAXI_UNACCEPTABLE_BRANDS.has(normalizeBrandText(c.brand))
        && normalizeBodyType(c.body_type) !== 'coupe'
        && normalizeBodyType(c.body_type) !== 'cabriolet'
      ));

      if (isGrandTaxi) {
        const grandMatches = taxiPool.filter((c) => (
          (Number(c.seats) || 5) >= 6
          || ['monospace', 'break', 'utilitaire', 'suv'].includes(normalizeBodyType(c.body_type))
        ));
        if (grandMatches.length) taxiPool = grandMatches;
      } else if (isPetitTaxi) {
        const petitMatches = taxiPool.filter((c) => (
          (Number(c.seats) || 5) <= 5
          && ['berline', 'citadine', 'compacte', 'suv'].includes(normalizeBodyType(c.body_type))
        ));
        if (petitMatches.length) taxiPool = petitMatches;
      }

      if (budget !== null) {
        const withinBudget = taxiPool.filter((c) => Number(c.price) > 0 && c.price <= budget);
        if (withinBudget.length) taxiPool = withinBudget;
      } else if (budgetRange) {
        const withinRange = taxiPool.filter((c) => Number(c.price) >= budgetRange.min && c.price <= budgetRange.max);
        if (withinRange.length) taxiPool = withinRange;
      }

      if (profilePreferenceOnly || !answerBrand) {
        return sortForSafety(taxiPool, safetyRequested);
      }
    }

    if (profilePreferenceOnly) {
      let profilePool = scopedRemainingCars.length ? scopedRemainingCars : await loadAllCatalogueVehicles();
      if (detectedProfile === 'executive' && !hasAny(historyText, [/\b(supercar|hypercar|ferrari|lamborghini|mclaren|bugatti|aston martin)\b/i])) {
        profilePool = profilePool.filter((car) => !SUPERCAR_BRANDS.has(normalizeBrandText(car.brand)) && (Number(car.price) || 0) <= 2500000);
      }
      return sortForSafety(profilePool, safetyRequested);
    }

// Apply broad body/use-case constraints before the brand shortcut. A
// request such as "a family Mercedes" must mean family Mercedes models,
// not every Mercedes model returned by the brand endpoint.
if (isFamilyRequest(answer)) {
let familyPool = scopedRemainingCars;
if (familyPool.length <= 3) {
const allCars = await loadAllCatalogueVehicles();
familyPool = requestedBrand
? allCars.filter((car) => normalizeBrandText(car.brand) === normalizeBrandText(requestedBrand.name))
: allCars;
}
const familyMatches = familyPool.filter((car) => (
FAMILY_BODY_TYPES.has(normalizeBodyType(car.body_type))
&& !SUPERCAR_BRANDS.has(normalizeBrandText(car.brand))
));
return sortForSafety(familyMatches.length ? familyMatches : familyPool, safetyRequested);
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
// A brand is one constraint, not the whole request. Apply every other
// explicit preference from the same message/history to the brand result
// instead of returning all models of that make.
const preferenceText = `${historyText} ${answer}`;
const requestedBody = extractBodyPreference(preferenceText);
const requestedFuel = extractFuelPreference(preferenceText);
const requestedTransmission = extractTransmissionPreference(preferenceText);
const requestedSeats = extractSeatRange(preferenceText);
const requestedSuitcases = extractSuitcaseRange(preferenceText);
const requestedCondition = extractConditionPreference(preferenceText);
const requestedBudget = extractMaximumBudget(preferenceText);
const brandItems = response.items.filter((car) => {
if (isFamilyRequest(preferenceText) && (
!FAMILY_BODY_TYPES.has(normalizeBodyType(car.body_type))
|| SUPERCAR_BRANDS.has(normalizeBrandText(car.brand))
)) return false;
if (requestedBody && normalizeBodyType(car.body_type) !== requestedBody) return false;
if (requestedFuel && car.fuel_type !== requestedFuel) return false;
if (requestedTransmission && car.transmission !== requestedTransmission) return false;
if (requestedSeats) {
const seats = Number(car.seats);
if (!Number.isFinite(seats) || seats < requestedSeats.min || seats > requestedSeats.max) return false;
}
if (requestedSuitcases) {
const trunk = Number(car.trunk_volume_l);
const suitcases = Number.isFinite(trunk) ? Math.round(trunk / LITERS_PER_SUITCASE) : 0;
if (suitcases < requestedSuitcases.min || suitcases > requestedSuitcases.max) return false;
}
if (requestedCondition) {
const condition = String(car.condition || car.status || '').toLowerCase();
const matchesCondition = requestedCondition === 'new'
? /new|neuf|serie|available/.test(condition)
: /used|occasion/.test(condition);
if (!matchesCondition) return false;
}
      if (requestedBudget !== null) {
        const price = Number(car.price);
        if (!Number.isFinite(price) || price <= 0 || price > requestedBudget) return false;
      }
      return true;
    });
    if (answerBrand.model) {
      const modelMatches = brandItems.filter((car) => (
        car.model.toLowerCase().includes(answerBrand.model!.toLowerCase())
        || answerBrand.model!.toLowerCase().includes(car.model.toLowerCase())
      ));
      if (modelMatches.length > 0) {
        return sortForSafety(modelMatches, safetyRequested);
      }
    }
    return sortForSafety(brandItems, safetyRequested);
  }

// Daily-use wording is an intent/context, not a database field. Preserve
// the real catalogue pool and let the next questions provide objective
// filters instead of allowing semantic search to return an empty result.
if (isDailyUsageRequest(answer)) {
const dailyPool = scopedRemainingCars.length > 3
? scopedRemainingCars
: await loadAllCatalogueVehicles();
return sortForSafety(dailyPool, safetyRequested);
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
return sortForSafety(catalogueMatches.length ? catalogueMatches : (requestedBrand ? [] : scopedRemainingCars), safetyRequested);
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
return sortForSafety(catalogueMatches.length ? catalogueMatches : (requestedBrand ? [] : scopedRemainingCars), safetyRequested);
}

    if (suitcaseMinimum !== null) {
      const suitcaseMatches = scopedRemainingCars.filter((car) => {
        const trunkLiters = Number(car.trunk_volume_l);
        if (!Number.isFinite(trunkLiters)) return false;
        return Math.round(trunkLiters / LITERS_PER_SUITCASE) >= suitcaseMinimum;
      });
      return sortForSafety(suitcaseMatches.length ? suitcaseMatches : (requestedBrand ? [] : scopedRemainingCars), safetyRequested);
    }

    const isLargeTrunkRequested = /\b(volume de coffre|grand coffre|coffre géant|large trunk|big trunk|spacious trunk|more interior space|plus d[’']espace)\b/i.test(answer)
      || /(?:كوفير واسع|كوفير كبير|صندوق أمتعة ضخم|صندوق أمتعة واسع|مساحة داخلية أكبر|مساحة أكبر|بلاصة أكثر)/i.test(answer);
    if (isLargeTrunkRequested) {
      const trunkMatches = scopedRemainingCars.filter((car) => (Number(car.trunk_volume_l) || 0) >= 420);
      if (trunkMatches.length) return sortForSafety(trunkMatches, safetyRequested);
    }

    const isLowRunningCostRequested = /\b(frais réduits|faible conso|vignette 6-7 cv|running costs|low fuel|lower costs|economy & lower|coûts d[’']usage réduits|économie & coûts)\b/i.test(answer)
      || /(?:مصاريف قليلة|استهلاك قليل وضريبة|توفير وتكاليف أقل|تكاليف تشغيل أقل|اقتصاد ومصاريف قليلة|التوفير والاقتصاد)/i.test(answer);
    if (isLowRunningCostRequested) {
      const ecoMatches = scopedRemainingCars.filter((car) => {
        const hp = Number(car.engine_power_hp) || 0;
        const fuel = car.fuel_type;
        return (hp <= 115 || fuel === 'diesel' || fuel === 'hybride') && !SUPERCAR_BRANDS.has(normalizeBrandText(car.brand));
      });
      if (ecoMatches.length) return sortForSafety(ecoMatches, safetyRequested);
    }

    const isPowerRequested = /\b(power and acceleration|puissance & reprises|puissance et reprises|sportif|dynamisme)\b/i.test(answer)
      || /(?:القوة والتسارع|أولوية القوة|القوة والجهد)/i.test(answer);
    if (isPowerRequested) {
      const powerMatches = scopedRemainingCars.filter((car) => (Number(car.engine_power_hp) || 0) >= 130);
      if (powerMatches.length) return sortForSafety(powerMatches, safetyRequested);
    }

    const isEcoCombo = /\b(hybrid or electric|hybride ou électrique)\b/i.test(answer) || /(?:هجين أو كهربائي|هجين ولا كهربائي)/i.test(answer);
    if (isEcoCombo) {
      const ecoComboMatches = scopedRemainingCars.filter((car) => car.fuel_type === 'hybride' || car.fuel_type === 'electrique' || car.fuel_type === 'hybride_rechargeable');
      if (ecoComboMatches.length) return sortForSafety(ecoComboMatches, safetyRequested);
    }

    const isThermalCombo = /\b(petrol \/ diesel|essence \/ diesel)\b/i.test(answer) || /(?:بنزين \/ ديزل|بنزين أو ديزل|ليصانص ولا مازوط)/i.test(answer);
    if (isThermalCombo) {
      const thermalMatches = scopedRemainingCars.filter((car) => car.fuel_type === 'essence' || car.fuel_type === 'diesel');
      if (thermalMatches.length) return sortForSafety(thermalMatches, safetyRequested);
    }

    const isNoPreference = /^(?:no preference|pas de préférence|pas de preference|sans préférence|لا أفضلية|ما عنديش تفضيل|بدون تفضيل|لا يوجد تفضيل)\b/i.test(answer.trim())
      || /(?:لا أفضلية|ما عنديش تفضيل|بدون تفضيل|no safety preference|pas de préférence sécurité)/i.test(answer);
    if (isNoPreference && scopedRemainingCars.length > 0) {
      return sortForSafety(scopedRemainingCars, safetyRequested);
    }

    const isAutomaticRequested = /\b(smooth automatic|bo[îi]te automatique fluide|douceur de conduite)\b/i.test(answer)
      || /(?:بواط أوتوماتيك|ناقل حركة أوتوماتيكي سلس)/iu.test(answer);
    if (isAutomaticRequested) {
      const autoMatches = scopedRemainingCars.filter((car) => car.transmission === 'automatique');
      if (autoMatches.length) return sortForSafety(autoMatches, safetyRequested);
    }

    const isComfortRequested = /\b(seat comfort|ergonomic|confort|si[èe]ges?|lounge|insonorisation|quiet|soundproofing|climatisation|suspension)\b/i.test(answer)
      || /(?:كراسي مريحة|مقاعد مريحة|راحة|هدوء|عزل)/iu.test(answer);
    if (isComfortRequested) {
      const comfortRanked = [...scopedRemainingCars].sort((a, b) => {
        const trunkA = Number(a.trunk_volume_l) || 0;
        const trunkB = Number(b.trunk_volume_l) || 0;
        const priceA = Number(a.price) || 0;
        const priceB = Number(b.price) || 0;
        return (trunkB + priceB * 0.001) - (trunkA + priceA * 0.001);
      });
      if (comfortRanked.length) return sortForSafety(comfortRanked, safetyRequested);
    }

    const isReliabilityRequested = /\b(reliability|fiabilit[ée]|breakdown|panne|sav|dealer support|durable|robuste)\b/i.test(answer)
      || /(?:موثوقية|اعتمادية|صيانة|تحمل)/iu.test(answer);
    if (isReliabilityRequested) {
      const reliableBrands = new Set(['toyota', 'lexus', 'honda', 'volvo', 'mercedes-benz', 'volkswagen']);
      const reliableRanked = [...scopedRemainingCars].sort((a, b) => {
        const scoreA = reliableBrands.has(normalizeBrandText(a.brand)) ? 1 : 0;
        const scoreB = reliableBrands.has(normalizeBrandText(b.brand)) ? 1 : 0;
        return scoreB - scoreA;
      });
      if (reliableRanked.length) return sortForSafety(reliableRanked, safetyRequested);
    }

    const isEasyParkingRequested = /\b(easy driving & parking|stationnement|radars?|cam[ée]ra|facilit[ée] de conduite)\b/i.test(answer)
      || /(?:ركنة|كاميرا|سهولة القيادة)/iu.test(answer);
    if (isEasyParkingRequested) {
      const compactRanked = [...scopedRemainingCars].sort((a, b) => {
        const bodyA = normalizeBodyType(a.body_type);
        const bodyB = normalizeBodyType(b.body_type);
        const scoreA = bodyA === 'citadine' ? 2 : bodyA === 'suv' ? 1 : 0;
        const scoreB = bodyB === 'citadine' ? 2 : bodyB === 'suv' ? 1 : 0;
        return scoreB - scoreA;
      });
      if (compactRanked.length) return sortForSafety(compactRanked, safetyRequested);
    }

if (seatRange) {
const seatMatches = scopedRemainingCars.filter((car) => {
const seats = Number(car.seats);
return Number.isFinite(seats) && seats >= seatRange.min && seats <= seatRange.max;
});
return sortForSafety(seatMatches.length ? seatMatches : (requestedBrand ? [] : scopedRemainingCars), safetyRequested);
}

if (conditionPreference) {
const conditionMatches = scopedRemainingCars.filter((car) => {
const condition = String(car.condition || car.status || '').toLowerCase();
return conditionPreference === 'new'
? /new|neuf|serie|available/.test(condition)
: /used|occasion/.test(condition);
});
return sortForSafety(conditionMatches.length ? conditionMatches : (requestedBrand ? [] : scopedRemainingCars), safetyRequested);
}

// Motricite / Drivetrain constraint (4x4 vs 2WD)
const isAwdYes = (/\b(4x4|awd|integrale|intégrale)\b/i.test(answer) || /(?:^|[^\p{L}\p{N}])(دفع رباعي|رباعي)(?:$|[^\p{L}\p{N}])/iu.test(answer))
&& !(/\b(no|non|pas|2wd|deux)\b/i.test(answer) || /(?:ثنائي|لا)/i.test(answer));
const isAwdNo = /\b(2wd|standard|2 roues|deux roues)\b/i.test(answer)
|| /(?:دفع ثنائي|ثنائي)/i.test(answer)
|| ((/\b(no|non|pas besoin)\b/i.test(answer) || /^(?:لا|لا أريد|ما بغيتش)$/i.test(answer.trim())) && /4x4|awd|transmission intégrale|off-road|الدفع الرباعي|دفع رباعي/i.test(previousAssistantQuestion));

if (isAwdYes) {
const currentMatches = scopedRemainingCars.filter((car) => Boolean(car.is_4x4));
if (currentMatches.length) return sortForSafety(currentMatches, safetyRequested);
if (bodyPreference) {
  const bodyMatches = scopedRemainingCars.filter((car) => {
    if (bodyPreference === 'citadine' && SUPERCAR_BRANDS.has(normalizeBrandText(car.brand))) return false;
    return normalizeBodyType(car.body_type) === bodyPreference;
  });
  if (bodyMatches.length) return sortForSafety(bodyMatches, safetyRequested);
}
const catalogueMatches = applyConversationConstraints(
await loadAllCatalogueVehicles(),
history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
).filter((car) => Boolean(car.is_4x4));
return sortForSafety(catalogueMatches.length ? catalogueMatches : (requestedBrand ? [] : scopedRemainingCars), safetyRequested);
} else if (isAwdNo) {
const currentMatches = scopedRemainingCars.filter((car) => !car.is_4x4);
if (currentMatches.length) return sortForSafety(currentMatches, safetyRequested);
const catalogueMatches = applyConversationConstraints(
await loadAllCatalogueVehicles(),
history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
).filter((car) => !car.is_4x4);
return sortForSafety(catalogueMatches.length ? catalogueMatches : (requestedBrand ? [] : scopedRemainingCars), safetyRequested);
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
return sortForSafety(catalogueMatches.length ? catalogueMatches : (requestedBrand ? [] : scopedRemainingCars), safetyRequested);
}

if (fuelPreference) {
const currentMatches = scopedRemainingCars.filter((car) => car.fuel_type === fuelPreference);
if (currentMatches.length) return sortForSafety(currentMatches, safetyRequested);
const catalogueMatches = applyConversationConstraints(
await loadAllCatalogueVehicles(),
history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
).filter((car) => car.fuel_type === fuelPreference);
return sortForSafety(catalogueMatches.length ? catalogueMatches : (requestedBrand ? [] : scopedRemainingCars), safetyRequested);
}

const transmissionPreference = extractTransmissionPreference(answer);
if (transmissionPreference) {
const currentMatches = scopedRemainingCars.filter((car) => car.transmission === transmissionPreference);
if (currentMatches.length) return sortForSafety(currentMatches, safetyRequested);
const catalogueMatches = applyConversationConstraints(
await loadAllCatalogueVehicles(),
history.filter((turn) => turn.role === 'user').map((turn) => turn.content).join(' '),
).filter((car) => car.transmission === transmissionPreference);
return sortForSafety(catalogueMatches.length ? catalogueMatches : (requestedBrand ? [] : scopedRemainingCars), safetyRequested);
}

// Safety is an explicit ranking and filtering criterion.
// When the user specifies "Note NCAP maximale" (5★) or "Bonne sécurité" (>= 4★),
// we must strictly filter for vehicles satisfying the requested NCAP rating.
const isMaxSafety = maxNcapPreferencePattern.test(answer) || (userTurns > 1 && maxNcapPreferencePattern.test(historyText));
const isGoodSafety = goodNcapPreferencePattern.test(answer) || (userTurns > 1 && goodNcapPreferencePattern.test(historyText));

if (isMaxSafety || isGoodSafety) {
if (requestedBrand && !scopedRemainingCars.length) return [];

// 1. Priorité absolue : consulter et filtrer les voitures recommandées à l'instant T.
// Safety is an explicit ranking constraint, so preserve the current shortlist
// when it already contains candidates (it may have been narrowed by earlier answers).
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
      if (scopedRemainingCars.length) {
        const filtered = scopedRemainingCars.filter((car) => Number(car.price) > 0 && car.price <= budget);
        if (filtered.length) return sortForSafety(filtered, safetyRequested);
      }
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
    const validDetails = details.filter((car) => car && car.id);
    if (!validDetails.length && scopedRemainingCars.length > 0) {
      return sortForSafety(scopedRemainingCars, safetyRequested);
    }
    return sortForSafety(validDetails.length ? validDetails : (scopedRemainingCars.length ? scopedRemainingCars : remainingCars), safetyRequested);
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

function extractSeatRange(query: string): { min: number; max: number } | null {
if (!/(?:seat|places?|passenger|si[eè]ge|بلايص|مقاعد|ركاب)/i.test(query)) return null;
const numbers = query.match(/\d+/g)?.map(Number) || [];
if (!numbers.length) return null;
const min = numbers[0];
const openEnded = /(?:\+|more than|over|plus de|plus que|كثر من|أكثر من)/i.test(query);
const max = openEnded ? 9 : numbers.length > 1 ? numbers[1] : min;
return min > 0 && max >= min ? { min, max } : null;
}

function extractConditionPreference(query: string): 'new' | 'used' | null {
if (/(?:\bnew\b|neuf|neuve|جديدة|جديد)/i.test(query)) return 'new';
if (/(?:\bused\b|occasion|مستعملة|مستعمل)/i.test(query)) return 'used';
return null;
}

function extractBodyPreference(query: string): string | null {
  const normalized = query.toLowerCase();
  if (/\b(suv|crossover|4x4|d[ée]part\s+quatre)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])(دفع رباعي|كروس)(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'suv';
  if (/\b(sedan|berline|saloon)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])سيدان(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'berline';
  if (/\b(hatchback|citadine|citadines|city\s*car|compact\s*car|petite?\s*voiture|petit\s*v[ée]hicule|small\s*car|compacte?s?)\b|(?:tonobil(?:a|e)?|tomobil(?:a)?|sayara|voiture)\s+(?:sghir(?:a)?|saghir(?:a)?|petite?)|(?:طوموبيل|سيارة|سيتادين)\s*(?:صغيرة|صغيره)|(?:^|[^\p{L}\p{N}])(صغيرة|صغيره|سيتادين|مدمج|مدمجة|سهل الركن)(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'citadine';
  if (/\b(wagon|break|estate)\b/i.test(normalized)) return 'break';
  if (/\b(pickup|pick-up|pick up)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])(بيك ?أب|بيك ?اب)(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'pick_up';
  if (/\b(van|monospace|mpv)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])(مونوسباس|فان)(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'monospace';
  if (/\b(utilitaire)\b/i.test(normalized)) return 'utilitaire';
  if (/\b(coupe|grand tourisme)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])(coupé|كوبيه|كوبي)(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'coupe';
  if (/\b(cabriolet|convertible|spider|roadster|decapotable|d[ée]capotable)\b/i.test(normalized)) return 'cabriolet';
  return null;
}

export function normalizeBodyType(bodyType?: string | null): string {
const normalized = (bodyType || '').toLowerCase().replace(/[-_]/g, ' ');
if (/suv|crossover|4x4|دفع رباعي|كروس/.test(normalized)) return 'suv';
if (/berline|sedan|saloon|سيدان/.test(normalized)) return 'berline';
if (/citadine|hatchback|city car|compact|سيتادين|صغيرة/.test(normalized)) return 'citadine';
if (/break|wagon|estate/.test(normalized)) return 'break';
if (/pick ?up|pickup|بيك/.test(normalized)) return 'pick_up';
if (/monospace|mpv|van/.test(normalized)) return 'monospace';
if (/utilitaire/.test(normalized)) return 'utilitaire';
if (/coupe|coupé|gt|sport|supercar|berlinetta/.test(normalized)) return 'coupe';
if (/cabriolet|convertible|spider|roadster/.test(normalized)) return 'cabriolet';
return normalized.trim();
}

function isFamilyRequest(query: string): boolean {
  return /\b(family|familly|famille|familiale?|familial|children|kids|baby|poussette|spacious|space)\b/i.test(query)
    || /(?:^|[^\p{L}\p{N}])(?:ال)?(عائلة|عائلية|عائلي|أسرة|اسرة|أطفال|واسعة|بلايص)(?:$|[^\p{L}\p{N}])/iu.test(query)
    || /\b(?:3a2ila|l3a2ila|3ayla|l3ayla|wlad|drari|famila)\b/i.test(query)
    || /(?:tomobil|tomobile|tonobile|voiture)\s+(?:dyal|dial|d|ta3|nt|n)?\s*(?:3a2ila|l3a2ila|3ayla|l3ayla)/i.test(query);
}

function isDailyUsageRequest(query: string): boolean {
return /\b(?:daily|everyday|day[- ]to[- ]day|commut(?:e|ing)|urban|regular)\s+(?:usage|use|driv(?:e|ing)|driver|car|vehicle)\b/i.test(query)
|| /(?:(?:\b(?:car|vehicle|voiture|véhicule|tomobil)\b|(?:^|[^\p{L}\p{N}])(?:طوموبيل|سيارة)(?:$|[^\p{L}\p{N}]))\s*(?:for|pour|dyal|ديال|للاستعمال)\s*(?:(?:my|mon|ma)\s*)?(?:\b(?:daily|everyday|work|tous les jours|kol nhar|lkhedma|lkhadma)\b|(?:^|[^\p{L}\p{N}])(?:اليومي|كل نهار|العمل)(?:$|[^\p{L}\p{N}])))/iu.test(query)
|| /\b(?:work|office|commute|home[- ]to[- ]work|domicile[- ]travail|trajets?\s+quotidiens?)\b/i.test(query)
|| /\b(?:usage|use)\s+(?:quotidien|daily)\b/i.test(query)
|| /\b(?:trajets?|utilisation|usage)\s+(?:quotidien(?:ne)?|de tous les jours)\b/i.test(query)
|| /(?:استعمال|سياقة)\s*(?:يومي|كل نهار)|(?:طوموبيل|سيارة)\s*(?:ديال|للاستعمال)\s*(?:كل نهار|اليومي|الخدمة|العمل)|(?:مشاوير|ذهاب)\s*(?:العمل|يومية)/iu.test(query);
}

function applyConversationConstraints(cars: Car[], userText: string): Car[] {
let constrained = cars;
const requestedBrand = extractBrandPreference(userText);
const bodyPreference = extractBodyPreference(userText);
const budgetRange = extractBudgetRange(userText);
const suitcaseRange = extractSuitcaseRange(userText);
const seatRange = extractSeatRange(userText);
const conditionPreference = extractConditionPreference(userText);

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
constrained = constrained.filter((car) => (
FAMILY_BODY_TYPES.has(normalizeBodyType(car.body_type))
&& !SUPERCAR_BRANDS.has(normalizeBrandText(car.brand))
));
}
  if (budgetRange) {
    constrained = constrained.filter((car) => {
      const price = Number(car.price);
      return Number.isFinite(price) && price > 0 && price >= budgetRange.min && price <= budgetRange.max;
    });
  } else {
    const maximumBudget = extractMaximumBudget(userText);
    if (maximumBudget !== null) {
      constrained = constrained.filter((car) => {
        const price = Number(car.price);
        return Number.isFinite(price) && price > 0 && price <= maximumBudget;
      });
    }
    const minimumBudget = extractMinimumBudget(userText);
    if (minimumBudget !== null) {
      constrained = constrained.filter((car) => {
        const price = Number(car.price);
        return Number.isFinite(price) && price > 0 && price >= minimumBudget;
      });
    }
  }
if (suitcaseRange) {
constrained = constrained.filter((car) => {
const trunkLiters = Number(car.trunk_volume_l);
if (!Number.isFinite(trunkLiters)) return false;
const suitcases = Math.round(trunkLiters / LITERS_PER_SUITCASE);
return suitcases >= suitcaseRange.min && suitcases <= suitcaseRange.max;
});
}
if (seatRange) {
constrained = constrained.filter((car) => {
const seats = Number(car.seats);
return Number.isFinite(seats) && seats >= seatRange.min && seats <= seatRange.max;
});
}
if (conditionPreference) {
constrained = constrained.filter((car) => {
const condition = String(car.condition || car.status || '').toLowerCase();
return conditionPreference === 'new'
? /new|neuf|serie|available/.test(condition)
: /used|occasion/.test(condition);
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
    .normalize('NFC')
    .toLowerCase();
  if (/\b(diesel|gazoil|mazout|mazot|nafta)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])مازوط(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'diesel';
  if (/\b(petrol|essence|gasoline|super)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])بنزين(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'essence';
  if (/\b(hybride rechargeable|plug[- ]?in|phev)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])(هجين قابلة? للشحن|إيبريد ريشارجابل)(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'hybride_rechargeable';
  if (/\b(hybrid|hybride)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])هجين(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'hybride';
  if (/\b(electric|electrique|ev)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])(كهربائي|كهربائ)(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'electrique';
  if (/\b(gpl)\b/i.test(normalized)) return 'gpl';
  return null;
}

function extractTransmissionPreference(query: string): Car['transmission'] | null {
  const normalized = query
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .normalize('NFC')
    .toLowerCase();
  if (/\b(automatic|automatique|auto|bva)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])(اوتوماتيك|أوتوماتيك)(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'automatique';
  if (/\b(manual|manuelle|bvm)\b/i.test(normalized) || /(?:^|[^\p{L}\p{N}])يدوي(?:$|[^\p{L}\p{N}])/iu.test(normalized)) return 'manuelle';
  return null;
}

export function isCriterionPreference(query: string): boolean {
  const text = query.toLowerCase().trim();
  const normalized = query
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .normalize('NFC')
    .toLowerCase()
    .trim();

  return extractFuelPreference(query) !== null
    || extractTransmissionPreference(query) !== null
    || extractBodyPreference(query) !== null
    || safetyPreferencePattern.test(query)
    || maxNcapPreferencePattern.test(query)
    || goodNcapPreferencePattern.test(query)
    || /\b(4x4|awd|2wd|integrale|motricite|all-wheel drive)\b/i.test(normalized)
    || /(?:^|[^\p{L}\p{N}])(دفع\s*رباعي|دفع\s*ثنائي|رباعي)(?:$|[^\p{L}\p{N}])/iu.test(text)
    || /\b(puissance.*reprises|power.*acceleration|reprises|performance|sportif|dynamisme)\b/i.test(normalized)
    || /(?:^|[^\p{L}\p{N}])(القوة|التسارع|الأداء|موتور قوي)(?:$|[^\p{L}\p{N}])/iu.test(text)
    || /\b(frais reduits|faible conso|running costs|low fuel|couts? d[’']usage|economie|economy & lower|couts reduits)\b/i.test(normalized)
    || /(?:^|[^\p{L}\p{N}])(توفير|اقتصاد|مصاريف قليلة|تكاليف تشغيل)(?:$|[^\p{L}\p{N}])/iu.test(text)
    || /\b(compact|facile a garer|easy to park|more interior space|plus d[’']espace)\b/i.test(normalized)
    || /(?:^|[^\p{L}\p{N}])(مدمج|سهل الركن|ساهلة فالركنة|مساحة أكبر|بلاصة أكثر)(?:$|[^\p{L}\p{N}])/iu.test(text)
    || /\b(grand coffre|coffre geant|large trunk|huge trunk|suitcases?|valises?|7 places|7 seats)\b/i.test(normalized)
    || /(?:^|[^\p{L}\p{N}])(فاليزات|حقائب|صندوق كبير|كوفير كبير|7 مقاعد|7 بلايص)(?:$|[^\p{L}\p{N}])/iu.test(text)
    || /\b(no preference|pas de preference|sans preference)\b/i.test(normalized)
    || /(?:^|[^\p{L}\p{N}])(لا أفضلية|ما عنديش تفضيل|بدون تفضيل)(?:$|[^\p{L}\p{N}])/iu.test(text);
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

export interface ConstraintConflict {
  type: 'citadine_large_capacity' | 'supercar_diesel' | 'ev_low_budget';
  explanation: Record<ChatLanguage, string>;
  options: Record<ChatLanguage, QuestionOption[]>;
}

export function detectConstraintConflict(
  history: ChatTurn[],
  _cars?: Car[],
): ConstraintConflict | null {
  const fullText = history.map((t) => t.content).join(' ');
  const body = extractBodyPreference(fullText);
  const seats = extractSeatRange(fullText);
  const suitcases = extractSuitcaseRange(fullText);
  const suitcaseMin = extractSuitcaseMinimum(fullText);
  const fuel = extractFuelPreference(fullText);
  const budget = extractMaximumBudget(fullText);
  const brand = extractBrandPreference(fullText);

  // 1. Citadine + 7 places OU > 4 valises / coffre immense
  const isCityCar = body === 'citadine' || /\b(citadine|city car|petite voiture)\b/i.test(fullText) || /(?:^|[^\p{L}\p{N}])(صغيرة|سيتادين)(?:$|[^\p{L}\p{N}])/iu.test(fullText);
  const hasSevenSeats = Boolean(seats && seats.max >= 7);
  const hasHugeCargo = Boolean((suitcases && suitcases.max >= 5) || (suitcaseMin !== null && suitcaseMin >= 5));

  if (isCityCar && (hasSevenSeats || hasHugeCargo)) {
    return {
      type: 'citadine_large_capacity',
      explanation: {
        fr: "Une citadine est conçue pour être compacte (4 à 5 places, coffre urbain de 250 à 350L). Pour accueillir 7 personnes ou de nombreux bagages, un monospace compact ou un SUV familial est nécessaire.",
        darija: "Citadine مصممة باش تكون صغيرة فالمدينة (فيها 4 حتى 5 د البلايص). إلا كنتي باغي 7 د البلايص ولا coffre كبير، الأنسب هو monospace عائلي بحال Jogger ولا SUV.",
        ar: "سيارة المدينة مخصصة للحجم المدمج (4 إلى 5 مقاعد). للحصول على 7 مقاعد أو مساحة أمتعة كبيرة، يُفضل اختيار سيارة عائلية مدمجة (Monospace أو SUV).",
        en: "A city car is designed for compact urban driving (4–5 seats). For 7 seats or high luggage capacity, a compact MPV or family SUV is needed.",
      },
      options: {
        fr: [
          { label: 'Voir monospaces / SUV 7 places', value: 'Montre-moi des monospaces ou SUV 7 places' },
          { label: 'Garder citadine 5 places', value: 'Je préfère une citadine 5 places' },
        ],
        darija: [
          { label: 'نشوف monospace / SUV 7 بلايص', value: 'باغي monospace ولا SUV 7 بلايص' },
          { label: 'نبقى فـ citadine 5 بلايص', value: 'باغي citadine 5 د البلايص' },
        ],
        ar: [
          { label: 'عرض سيارات 7 مقاعد (Monospace/SUV)', value: 'أفضل سيارة 7 مقاعد' },
          { label: 'البقاء على سيارة مدينة 5 مقاعد', value: 'أفضل سيارة مدينة 5 مقاعد' },
        ],
        en: [
          { label: 'See 7-seater MPV / SUV', value: 'Show me 7-seater MPVs or SUVs' },
          { label: 'Keep 5-seater city car', value: 'I prefer a 5-seater city car' },
        ],
      },
    };
  }

  // 2. Supercar / Marque sportive de prestige + Diesel
  const brandNorm = brand ? normalizeBrandText(brand.name) : '';
  const isSupercarBrand = SUPERCAR_BRANDS.has(brandNorm) || /\b(ferrari|lamborghini|mclaren|bugatti|aston martin)\b/i.test(fullText);
  if (isSupercarBrand && fuel === 'diesel') {
    const brandLabel = brand ? brand.name : 'Ferrari';
    return {
      type: 'supercar_diesel',
      explanation: {
        fr: `Les constructeurs de supercars comme ${brandLabel} ne fabriquent pas de motorisations diesel, mais uniquement des moteurs essence ou hybrides de haute performance.`,
        darija: `الماركات الرياضية بحال ${brandLabel} ما كيديروش المازوط، كاين فقط Essence V8/V12 ولا Hybride sportive.`,
        ar: `العلامات الرياضية الخارقة مثل ${brandLabel} لا تنتج محركات ديزل، بل محركات بنزين وهجينة فائقة الأداء.`,
        en: `Supercar manufacturers like ${brandLabel} do not produce diesel engines, focusing exclusively on petrol and high-performance hybrid powertrains.`,
      },
      options: {
        fr: [
          { label: 'Explorer en essence / hybride', value: `Voir les ${brandLabel} en essence ou hybride` },
          { label: 'Voir berlines sportives diesel (BMW, Audi...)', value: 'Montre-moi des berlines sportives diesel' },
        ],
        darija: [
          { label: 'نشوف essence / hybride', value: `نشوف ${brandLabel} essence` },
          { label: 'نشوف berlines sportives diesel', value: 'نشوف berlines sportives diesel' },
        ],
        ar: [
          { label: 'استكشاف بنزين / هجين', value: `عرض طرازات ${brandLabel} بنزين أو هجين` },
          { label: 'عرض سيارات رياضية ديزل بديلة', value: 'عرض سيارات سيدان رياضية ديزل' },
        ],
        en: [
          { label: 'Explore petrol / hybrid', value: `Show me ${brandLabel} petrol or hybrid models` },
          { label: 'See sporty diesel alternatives (BMW, Audi...)', value: 'Show me sporty diesel executive cars' },
        ],
      },
    };
  }

  // 3. Électrique pur + Budget très bas (< 150 000 MAD)
  if (fuel === 'electrique' && budget !== null && budget < 150000) {
    return {
      type: 'ev_low_budget',
      explanation: {
        fr: "Sur le marché du neuf au Maroc, les modèles 100% électriques débutent généralement au-delà de 170 000 MAD. Pour votre budget, nous vous suggérons d'examiner des citadines hybrides ou des diesels très sobres.",
        darija: "فالسوق المغربي للسيارات الجديدة، الطوموبيلات électrique كيبداو تقريباً من 170 000 درهم لفوق. فهاد الميزانية، الأنسب citadine diesel اقتصادية ولا essence.",
        ar: "في سوق السيارات الجديدة بالمغرب، تبدأ السيارات الكهربائية بالكامل عموماً من 170 ألف درهم. ضمن هذه الميزانية، نقترح سيارات هجينة أو ديزل عالية الاقتصاد.",
        en: "In Morocco's new vehicle market, fully electric cars typically start above 170,000 MAD. Within your budget, we suggest economical hybrid or diesel city cars.",
      },
      options: {
        fr: [
          { label: 'Voir diesels / essence économiques', value: 'Montre-moi des modèles économiques dans mon budget' },
          { label: 'Ajuster mon budget pour l’électrique', value: 'Je peux monter mon budget pour de l’électrique' },
        ],
        darija: [
          { label: 'نشوف diesel / essence اقتصاديين', value: 'وريني طوموبيلات اقتصادية بهاد الميزانية' },
          { label: 'نزيد فالميزانية للألكتريك', value: 'نقدر نزيد فالميزانية باش ناخد électrique' },
        ],
        ar: [
          { label: 'عرض سيارات ديزل أو بنزين اقتصادية', value: 'عرض سيارات اقتصادية ضمن ميزانيتي' },
          { label: 'تعديل الميزانية للكهربائي', value: 'يمكنني زيادة الميزانية لسيارة كهربائية' },
        ],
        en: [
          { label: 'See economical diesel/petrol', value: 'Show me fuel-efficient cars within my budget' },
          { label: 'Adjust budget for EV', value: 'I can increase my budget for an electric vehicle' },
        ],
      },
    };
  }

  return null;
}

export function computeFallback8dScores(cars: Car[], _profile?: unknown): Car[] {
  return cars.map((car, index) => {
    const trunk = Number(car.trunk_volume_l) || 380;
    const trunkScore = Math.min(100, Math.max(30, Math.round((trunk / 550) * 100)));

    const power = Number(car.engine_power_hp) || 110;
    const perfScore = Math.min(100, Math.max(30, Math.round((power / 180) * 100)));

    const ncap = getNcapScore(car) || 4;
    const secScore = Math.min(100, Math.max(40, Math.round((ncap / 5) * 100)));

    const conso = Number(car.fuel_consumption ?? car.official_consumption ?? car.real_consumption) || 5.2;
    const ecoScore = Math.min(100, Math.max(30, Math.round(Math.max(0, 10 - conso) * 10 + 20)));

    const scores: Record<string, number> = {
      securite: secScore,
      economie_usage: ecoScore,
      performance: perfScore,
      espace_coffre: trunkScore,
      confort: Math.min(95, Math.max(60, 75 + (car.body_type === 'berline' || car.body_type === 'suv' ? 10 : 0))),
      technologie: Math.min(95, Math.max(55, 70 + (Number(car.year) >= 2023 ? 15 : 5))),
      robustesse: Math.min(95, Math.max(60, car.brand === 'Dacia' || car.brand === 'Toyota' ? 90 : 78)),
      budget: Math.min(98, Math.max(50, 88 - index * 4)),
    };

    const values = Object.values(scores);
    const total = Math.round(values.reduce((a, b) => a + b, 0) / values.length);
    return {
      ...car,
      eight_dimension_scores: scores,
      total_8d_score: total,
      total_8d_percent: total,
    };
  });
}

export class MockRecommendationClient implements RecommendationClient {
constructor(private readonly cars: Car[]) {}
private language: ChatLanguage = 'fr';

setLanguage(language: ChatLanguage) { this.language = language; }

  async detectRecommendationIntent(message: string): Promise<boolean> {
    if (informativeRequestPattern.test(message)) return false;
    const isBrandOrModelPurchase = Boolean(extractBrandPreference(message));
    const extractedMax = extractMaximumBudget(message);
    const hasExtractedBudget = extractedMax !== null && extractedMax >= 10000;
    const hasVehicleTerm = /\b(?:car|cars|vehicle|vehicles|suv|suvs|auto|automobile|automobiles|voiture|voitures|véhicule|véhicules|vehicule|vehicules|tomobil|tomobile|tomobila|tonobil|tonobile|tonobila|sayara|sayarat|berline|citadine|compacte|utilitaire|pick-?up)\b|(?:^|[^\p{L}\p{N}])(?:سيارة|سيارات|طوموبيل|طوموبيلا|طوموبيلات)(?:$|[^\p{L}\p{N}])/iu.test(message);
    const hasPurchaseOrBudgetContext = hasVehicleTerm
      || /\b(?:budget|prix|price|have|j'ai|under|below|less\s+than|moins\s+de|jusqu['’à]|max|maximum|plafond|pour|for|bghit|baghi)\b|(?:^|[^\p{L}\p{N}])(?:عندي|ميزانية|ثمن|أقل|بغيت|باغي)(?:$|[^\p{L}\p{N}])/iu.test(message);
    const isBudgetSearch = hasExtractedBudget && hasPurchaseOrBudgetContext;

    return intentPattern.test(message) || nonLatinIntentPattern.test(message) || budgetSearchPattern.test(message)
      || isBudgetSearch || hasProfilePreference(message) || isDailyUsageRequest(message) || isBrandOrModelPurchase
      || isCriterionPreference(message);
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

export function deduplicateCars(cars: Car[]): Car[] {
  const seenModelKey = new Set<string>();
  const uniqueCars: Car[] = [];
  const duplicateCars: Car[] = [];

  for (const car of cars) {
    const key = `${normalizeBrandText(car.brand)} ${car.model.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()}`;
    if (!seenModelKey.has(key)) {
      seenModelKey.add(key);
      uniqueCars.push(car);
    } else {
      duplicateCars.push(car);
    }
  }

  return [...uniqueCars, ...duplicateCars];
}

export function getUniqueModelCars(cars: Car[], limit = 3): Car[] {
  const seenModelKey = new Set<string>();
  const result: Car[] = [];

  for (const car of cars) {
    const key = `${normalizeBrandText(car.brand)} ${car.model.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()}`;
    if (!seenModelKey.has(key)) {
      seenModelKey.add(key);
      result.push(car);
      if (result.length >= limit) break;
    }
  }

  return result;
}

export const FUEL_LABEL_MAP: Record<ChatLanguage, Record<string, string>> = {
  en: { diesel: 'Diesel', essence: 'Petrol', hybride: 'Hybrid', hybride_rechargeable: 'Plug-in Hybrid', electrique: '100% Electric', gpl: 'LPG' },
  fr: { diesel: 'Diesel', essence: 'Essence', hybride: 'Hybride', hybride_rechargeable: 'Hybride rechargeable', electrique: '100% Électrique', gpl: 'GPL' },
  ar: { diesel: 'ديزل', essence: 'بنزين', hybride: 'هجين', hybride_rechargeable: 'هجين قابل للشحن', electrique: 'كهربائي بالكامل', gpl: 'غاز' },
  darija: { diesel: 'مازوط', essence: 'ليصانص', hybride: 'إيبريد', hybride_rechargeable: 'إيبريد ريشارجابل', electrique: 'كهربائي 100%', gpl: 'غاز' },
};

export const BODY_LABEL_MAP: Record<ChatLanguage, Record<string, string>> = {
  en: { suv: 'SUV', berline: 'Sedan', citadine: 'Hatchback / City car', break: 'Estate / Wagon', monospace: 'MPV / Minivan', coupe: 'Coupe', pick_up: 'Pick-up', cabriolet: 'Convertible' },
  fr: { suv: 'SUV', berline: 'Berline', citadine: 'Citadine compacte', break: 'Break', monospace: 'Monospace', coupe: 'Coupé', pick_up: 'Pick-up', cabriolet: 'Cabriolet' },
  ar: { suv: 'دفع رباعي (SUV)', berline: 'سيدان', citadine: 'سيارة مدينة (سيتادين)', break: 'واغن عائلية', monospace: 'مونوسباس', coupe: 'كوبيه', pick_up: 'بيك أب', cabriolet: 'كابريوليه' },
  darija: { suv: 'SUV عالي', berline: 'بيرلين', citadine: 'سيتادين صغيرة', break: 'بريك عائلي', monospace: 'مونوسباس', coupe: 'كوبي', pick_up: 'بيك آب', cabriolet: 'كابريولي' },
};

export function isEcoCar(car: Car): boolean {
  return /hybrid|hybride|electric|electrique|phev|ev/i.test(car.fuel_type || '') ||
         /hybrid|hybride|electric|electrique|phev|ev/i.test(car.engine_type || '');
}

export function is4x4Car(car: Car): boolean {
  return Boolean(car.is_4x4) ||
         /4x4|awd|integral/i.test(car.transmission || '') ||
         /4x4|awd/i.test((car as any).drivetrain || '');
}

export function isNoPreferenceOption(opt: QuestionOption): boolean {
  const norm = (opt.value || opt.label).toLowerCase();
  return /no\s*preference|pas\s*de\s*pr[ée]f[ée]rence|ما\s*عندي(?:\s*ش)?\s*تفضيل|لا\s*أفضلية|لا\s*افضلية/i.test(norm);
}

export function doesOptionMatchCars(opt: QuestionOption, cars: Car[]): boolean {
  if (!cars || cars.length === 0) return true;
  if (isNoPreferenceOption(opt)) return true;

  const text = `${opt.label} ${opt.value || ''}`.toLowerCase();

  // Drivetrain
  if (/4x4|awd|int[ée]grale|four-wheel|all-wheel|دفع\s*رباعي/.test(text)) {
    return cars.some(is4x4Car);
  }
  if (/\b2wd\b|2\s*roues|deux\s*roues|standard\s*\(2wd\)|دفع\s*ثنائي|دفع\s*عادي/.test(text)) {
    return cars.some((c) => !is4x4Car(c));
  }

  // Seats / 7 places
  if (/7\s*(?:places|seats|مقاعد|بلايص)/.test(text)) {
    return cars.some((c) => (Number(c.seats) || 5) >= 7);
  }

  // Safety
  if (/5★|5\s*étoiles|5\s*stars|أعلى\s*تقييم|أعلى\s*نقطة/.test(text)) {
    return cars.some((c) => getNcapScore(c) === 5);
  }
  if (/4★|4\s*étoiles|4\s*stars|bonne\s*sécurité|good\s*safety|سلامة\s*جيدة|سلامة\s*مزيانة/.test(text)) {
    return cars.some((c) => getNcapScore(c) >= 4);
  }

  // Fuel / Clean / Thermal
  const isHybridText = /hybrid|hybride|phev|هجين|إيبريد/.test(text);
  const isElectricText = /electric|electrique|électrique|\bev\b|100%|كهربائي/.test(text);
  if (isHybridText && isElectricText) {
    return cars.some(isEcoCar);
  }
  if (isElectricText) {
    return cars.some((c) => /electri|\bev\b/i.test(c.fuel_type || ''));
  }
  if (isHybridText) {
    return cars.some((c) => /hybrid|hybride|phev/i.test(c.fuel_type || '') || isEcoCar(c));
  }
  if (/thermique|moteur\s*économe|essence\s*\/\s*diesel|petrol\s*\/\s*diesel|بنزين\s*\/\s*ديزل|ليصانص\s*ولا\s*مازوط/.test(text)) {
    return cars.some((c) => !isEcoCar(c));
  }
  if (/diesel|gazoil|mazout|مازوط/.test(text)) {
    return cars.some((c) => /diesel|mazout|gazoil/i.test(c.fuel_type || ''));
  }
  if (/essence|petrol|gasoline|بنزين|ليصانص/.test(text)) {
    return cars.some((c) => /essence|petrol|gasoline/i.test(c.fuel_type || ''));
  }

  // Body / Silhouette
  if (/\bsuv\b|crossover|دفع\s*رباعي\s*\(suv\)|suv\s*عالي/.test(text)) {
    return cars.some((c) => normalizeBodyType(c.body_type) === 'suv');
  }
  if (/citadine|city\s*car|hatchback|\bcompact\b|سيتادين|صغيرة/.test(text)) {
    return cars.some((c) => normalizeBodyType(c.body_type) === 'citadine');
  }
  if (/berline|sedan|saloon|سيدان|بيرلين/.test(text)) {
    return cars.some((c) => normalizeBodyType(c.body_type) === 'berline');
  }
  if (/break|wagon|estate|بريك/.test(text)) {
    return cars.some((c) => normalizeBodyType(c.body_type) === 'break');
  }
  if (/monospace|minivan|mpv|مونوسباس/.test(text)) {
    return cars.some((c) => normalizeBodyType(c.body_type) === 'monospace');
  }
  if (/coupe|coupé|كوبي/.test(text)) {
    return cars.some((c) => normalizeBodyType(c.body_type) === 'coupe');
  }
  if (/cabriolet|convertible|spider|كابريولي/.test(text)) {
    return cars.some((c) => normalizeBodyType(c.body_type) === 'cabriolet');
  }
  if (/pick.?up|بيك/.test(text)) {
    return cars.some((c) => normalizeBodyType(c.body_type) === 'pick_up');
  }

  // Gearbox
  if (/automatique|automatic|\bauto\b|\bbva\b|أوتوماتيك|اوتوماتيك/.test(text)) {
    return cars.some((c) => /auto/i.test(c.transmission || ''));
  }
  if (/manuelle|manual|\bbvm\b|يدوي|مانييل/.test(text)) {
    return cars.some((c) => /man/i.test(c.transmission || ''));
  }

  // Trunk / Space / Luggage
  if (/grand coffre|large trunk|صندوق كبير|كوفير كبير/.test(text)) {
    return cars.some((c) => (Number(c.trunk_volume_l) || 0) >= 380);
  }
  if (/coffre standard|standard trunk|صندوق قياسي|كوفير عادي/.test(text)) {
    return cars.some((c) => (Number(c.trunk_volume_l) || 0) < 450);
  }
  const suitcaseMatch = text.match(/(\d+)\s*(?:valises?|suitcases?|حقائب|فاليزات)/);
  if (suitcaseMatch) {
    const count = Number(suitcaseMatch[1]);
    return cars.some((c) => Math.round((Number(c.trunk_volume_l) || 0) / LITERS_PER_SUITCASE) >= count);
  }

  // Urban practicality & Interior space
  if (/plus d[’']espace int[ée]rieur|more interior space|مساحة داخلية أكبر|بلاصة أكثر/.test(text)) {
    return cars.some((c) => ['suv', 'berline', 'break', 'monospace'].includes(normalizeBodyType(c.body_type)));
  }

  // Performance vs Running costs
  if (/puissance|reprises|power and acceleration|القوة والتسارع/.test(text)) {
    const powers = cars.map((c) => Number(c.engine_power_hp) || 0).filter((p) => p > 0);
    const hasDiff = powers.length > 1 && Math.min(...powers) < Math.max(...powers);
    return hasDiff || cars.some((c) => (Number(c.engine_power_hp) || 0) >= 115);
  }
  if (/coûts? d[’']usage r[ée]duits?|lower running costs?|تكاليف تشغيل أقل|مصاريف قليلة|économie & coûts réduits|توفير وتكاليف أقل|اقتصاد ومصاريف قليلة/.test(text)) {
    const powers = cars.map((c) => Number(c.engine_power_hp) || 0).filter((p) => p > 0);
    const hasDiff = powers.length > 1 && Math.min(...powers) < Math.max(...powers);
    return hasDiff || cars.some((c) => (Number(c.engine_power_hp) || 0) < 115 || isEcoCar(c) || Number(c.fuel_consumption ?? c.official_consumption ?? 6) <= 5.5);
  }

  // Priority options (Économie, Sécurité, Confort, Performance)
  if (/^économie$|^economy$|^الاقتصاد$/i.test(text.trim())) {
    return cars.some((c) => isEcoCar(c) || /diesel/i.test(c.fuel_type || '') || Number(c.fuel_consumption ?? c.official_consumption ?? 6) <= 5.5);
  }
  if (/^sécurité$|^securite$|^safety$|^السلامة$/i.test(text.trim())) {
    return cars.some((c) => getNcapScore(c) >= 4);
  }
  if (/^confort$|^comfort$|^الراحة$/i.test(text.trim())) {
    return cars.some((c) => ['berline', 'suv', 'break', 'monospace'].includes(normalizeBodyType(c.body_type)));
  }
  if (/^performance$|^الأداء$/i.test(text.trim())) {
    return cars.some((c) => (Number(c.engine_power_hp) || 0) >= 115);
  }

  // Budget bracket options
  const budgetUnderMatch = text.match(/(?:moins de|under|less than|أقل من|قل من)\s*(\d[\d\s.,]*)/i);
  if (budgetUnderMatch) {
    const maxP = Number(budgetUnderMatch[1].replace(/[\s.,]/g, ''));
    if (Number.isFinite(maxP) && maxP > 0) return cars.some((c) => Number(c.price) <= maxP);
  }
  const budgetOverMatch = text.match(/(?:plus de|over|more than|أكثر من|كثر من)\s*(\d[\d\s.,]*)/i);
  if (budgetOverMatch) {
    const minP = Number(budgetOverMatch[1].replace(/[\s.,]/g, ''));
    if (Number.isFinite(minP) && minP > 0) return cars.some((c) => Number(c.price) >= minP);
  }

  return true;
}

export function getValidSpecificOptions(options: QuestionOption[], cars?: Car[]): QuestionOption[] {
  if (!options || options.length === 0) return [];
  if (!cars || cars.length === 0) {
    return options.filter((opt) => !isNoPreferenceOption(opt));
  }
  return options.filter((opt) => !isNoPreferenceOption(opt) && doesOptionMatchCars(opt, cars));
}

export function hasAtLeastTwoValidSuggestions(question: NextQuestion | null, cars?: Car[]): boolean {
  if (!question) return false;
  if (question.rangeBounds) {
    return question.rangeBounds.max > question.rangeBounds.min;
  }
  const specificOptions = getValidSpecificOptions(question.options || [], cars);
  return specificOptions.length >= 2;
}

export function filterOptionsByCandidateCars(options: QuestionOption[], cars?: Car[]): QuestionOption[] {
  if (!cars || cars.length === 0 || !options || options.length === 0) {
    return options || [];
  }
  const filtered = options.filter((opt) => doesOptionMatchCars(opt, cars));
  const specificOptions = filtered.filter((opt) => !isNoPreferenceOption(opt));
  if (specificOptions.length < 2) {
    return [];
  }
  return filtered;
}

export function alignQuestionOptions(
  question: string,
  options: QuestionOption[],
  language: ChatLanguage,
  candidateCars?: Car[]
): QuestionOption[] {
  let resolved: QuestionOption[] = [];

  // If specific tailored options were already supplied with 2 or more choices, preserve and localize them
  if (options && options.length >= 2) {
    resolved = options.map((opt) => {
      const lowerVal = (opt.value || opt.label).toLowerCase();
      const mappedFuel = FUEL_LABEL_MAP[language]?.[lowerVal];
      const mappedBody = BODY_LABEL_MAP[language]?.[lowerVal];
      let cleanLabel = mappedFuel || mappedBody || opt.label;
      if (!/^(est-ce que|confirmez-vous|do you confirm|واش متأكد)/i.test(question)) {
        cleanLabel = cleanLabel.replace(/^(?:Oui,?\s*|Yes,?\s*|نعم،?\s*|آه،?\s*)/i, '');
        if (cleanLabel.length > 0) {
          cleanLabel = cleanLabel.charAt(0).toUpperCase() + cleanLabel.slice(1);
        }
      }
      return { ...opt, label: cleanLabel || opt.label };
    });
  } else {
    const text = question.toLowerCase();

    // 1. Priorité Puissance vs Économie / Reprises
    if (/(puissance.*(?:économie|conso|coût|reprises)|power.*(?:running costs|consumption|fuel economy|acceleration|responsiveness|highway)|(?:reprises|performance).*(?:conso|économie|running costs|acceleration)|تسارع.*(?:استهلاك|تكاليف)|أداء.*(?:اقتصاد|تكاليف)|جهد.*صرف|قوة.*(?:استهلاك|تكاليف)|تكاليف التشغيل)/i.test(text)) {
      resolved = language === 'en'
        ? [{ label: 'Power & performance first' }, { label: 'Fuel economy first' }, { label: 'Balanced compromise' }, { label: 'No preference' }]
        : language === 'ar'
          ? [{ label: 'أولوية القوة والتسارع' }, { label: 'أولوية التوفير والاقتصاد' }, { label: 'توازن معتدل' }, { label: 'لا أفضلية' }]
          : language === 'darija'
            ? [{ label: 'القوة والجهد أولاً' }, { label: 'الاقتصاد فالمصاريف أولاً' }, { label: 'حل متوازن' }, { label: 'ما عنديش تفضيل' }]
            : [{ label: 'Priorité puissance & reprises' }, { label: 'Priorité économie de carburant' }, { label: 'Compromis équilibré' }, { label: 'Pas de préférence' }];
    }
    // 2. Format urbain / Compact vs Espace / Parking (Dimension Praticité urbaine)
    else if (/(gabarit|compact.*garer|facile à garer|voiture compacte|format compact|format de véhicule|compact car.*easy to park|صغيرة.*ركن|ساهلة فالركنة|حجم مدمج)/i.test(text)) {
      resolved = language === 'en'
        ? [{ label: 'Compact (easy to park)' }, { label: 'More interior space' }, { label: 'No preference' }]
        : language === 'ar'
          ? [{ label: 'حجم مدمج (سهل الركن)' }, { label: 'مساحة داخلية أكبر' }, { label: 'لا أفضلية' }]
          : language === 'darija'
            ? [{ label: 'صغيرة وساهلة فالركنة' }, { label: 'بلاصة أكثر' }, { label: 'ما عنديش تفضيل' }]
            : [{ label: 'Format compact (facile à garer)' }, { label: 'Plus d’espace intérieur' }, { label: 'Pas de préférence' }];
    }
    // 2b. Espace / Coffre en valises / 7 places (Dimension Espace)
    else if (/(bagages|valises?|coffre|luggage|suitcases?|7\s*(?:places|seats|مقاعد|بلايص)|أمتعة|حقائب|فاليزات|كوفير)/i.test(text)) {
      resolved = language === 'en'
        ? [{ label: 'Large trunk (3-4 suitcases)' }, { label: 'Huge trunk (5+ suitcases / 7 seats)' }, { label: 'Standard trunk' }]
        : language === 'ar'
          ? [{ label: 'صندوق كبير (3-4 حقائب)' }, { label: 'صندوق ضخم (5+ حقائب / 7 مقاعد)' }, { label: 'صندوق عادي' }]
          : language === 'darija'
            ? [{ label: 'كوفير كبير (3-4 فاليزات)' }, { label: 'كوفير ضخم (5+ فاليزات / 7 بلايص)' }, { label: 'كوفير عادي' }]
            : [{ label: 'Grand coffre (3-4 valises)' }, { label: 'Coffre géant (5+ valises / 7 places)' }, { label: 'Coffre standard' }];
    }
    // 2c. Carburant / Énergie
    else if (/(carburant|fuel|type\s+de\s+carburant|essence.*diesel|diesel.*essence|وقود|مازوط|ليصانص)/i.test(text)) {
      resolved = language === 'en'
        ? [{ label: 'Diesel', value: 'diesel' }, { label: 'Petrol', value: 'essence' }, { label: 'Hybrid', value: 'hybride' }, { label: '100% Electric', value: 'electrique' }]
        : language === 'ar'
          ? [{ label: 'ديزل', value: 'diesel' }, { label: 'بنزين', value: 'essence' }, { label: 'هجين', value: 'hybride' }, { label: 'كهربائي بالكامل', value: 'electrique' }]
          : language === 'darija'
            ? [{ label: 'مازوط', value: 'diesel' }, { label: 'ليصانص', value: 'essence' }, { label: 'إيبريد', value: 'hybride' }, { label: 'كهربائي 100%', value: 'electrique' }]
            : [{ label: 'Diesel', value: 'diesel' }, { label: 'Essence', value: 'essence' }, { label: 'Hybride', value: 'hybride' }, { label: '100% Électrique', value: 'electrique' }];
    }
    // 2d. Écologie & Coût réel (Hybride/Électrique propre vs thermique économe)
    else if (/(hybride.*(?:électrique|electrique)|hybrid.*electric|motorisation propre|clean.*propulsion|faible consommation|thermique.*économe|moteur.*économe|هجين.*كهربائي|إيبريد.*كهربائي)/i.test(text)) {
      resolved = language === 'en'
        ? [{ label: 'Clean Hybrid or Electric' }, { label: 'Fuel-efficient engine' }, { label: 'No preference' }]
        : language === 'ar'
          ? [{ label: 'هجين أو كهربائي نظيف' }, { label: 'محرك اقتصادي في الوقود' }, { label: 'لا أفضلية' }]
          : language === 'darija'
            ? [{ label: 'إيبريد ولا كهربائي نظيف' }, { label: 'موتور اقتصادي فالمصاريف' }, { label: 'ما عنديش تفضيل' }]
            : [{ label: 'Hybride ou Électrique propre' }, { label: 'Thermique très économe' }, { label: 'Pas de préférence' }];
    }
    // 2e. Transmission 4x4 / AWD (Dimension Motricité)
    else if (/(4x4|awd|intégrale|integrale|motricité|all-wheel drive|drivetrain|دفع رباعي)/i.test(text)) {
      resolved = language === 'en'
        ? [{ label: '4x4 / All-Wheel Drive (AWD)', value: 'Yes, 4x4 / AWD' }, { label: 'Standard (2WD)', value: 'Standard (2WD)' }, { label: 'No preference', value: 'No preference' }]
        : language === 'ar'
          ? [{ label: 'دفع رباعي (4x4 / AWD)', value: 'دفع رباعي (4x4)' }, { label: 'دفع ثنائي عادي (2WD)', value: 'دفع ثنائي عادي' }, { label: 'لا أفضلية', value: 'لا أفضلية' }]
          : language === 'darija'
            ? [{ label: 'دفع رباعي (4x4)', value: '4x4' }, { label: 'دفع عادي (2WD)', value: 'دفع عادي (2WD)' }, { label: 'ما عنديش تفضيل', value: 'ما عنديش تفضيل' }]
            : [{ label: '4x4 / Intégrale (AWD)', value: '4x4 / Intégrale' }, { label: '2 roues motrices (Standard)', value: '2 roues motrices (Standard)' }, { label: 'Pas de préférence', value: 'Pas de préférence' }];
    }
    // 2f. Sécurité NCAP (Dimension Sécurité)
    else if (/(sécurité|ncap|crash-test|safety|السلامة)/i.test(text)) {
      resolved = language === 'en'
        ? [{ label: 'Highest NCAP rating (5★)', value: 'Highest NCAP rating' }, { label: 'Good safety (4★+)', value: 'Good safety' }, { label: 'No preference', value: 'no safety preference' }]
        : language === 'ar'
          ? [{ label: 'أعلى تقييم NCAP (5★)', value: 'أعلى تقييم NCAP' }, { label: 'سلامة جيدة (4★+)', value: 'سلامة جيدة' }, { label: 'لا أفضلية', value: 'لا أفضلية في السلامة' }]
          : language === 'darija'
            ? [{ label: 'أعلى نقطة NCAP (5★)', value: 'أعلى نقطة NCAP' }, { label: 'سلامة مزيانة (4★+)', value: 'سلامة مزيانة' }, { label: 'ما عنديش تفضيل', value: 'ما عنديش تفضيل فالسلامة' }]
            : [{ label: 'Note NCAP maximale (5★)', value: 'Note NCAP maximale' }, { label: 'Bonne sécurité (4★+)', value: 'Bonne sécurité' }, { label: 'Pas de préférence', value: 'Pas de préférence' }];
    }
    // 3. Transmission / Boîte de vitesses
    else if (!/(4x4|awd|intégrale|integrale|motricité|drivetrain|دفع)/i.test(text) && /(bo[îi]te|gearbox|transmission|automatique.*manuelle|manual.*automatic|ناقل الحركة|علبة السرعات|بواط)/i.test(text)) {
      resolved = language === 'en'
        ? [{ label: 'Automatic' }, { label: 'Manual' }, { label: 'No preference' }]
        : language === 'ar'
          ? [{ label: 'أوتوماتيك' }, { label: 'يدوي' }, { label: 'لا أفضلية' }]
          : language === 'darija'
            ? [{ label: 'أوتوماتيك' }, { label: 'مانييل' }, { label: 'ما عنديش تفضيل' }]
            : [{ label: 'Automatique' }, { label: 'Manuelle' }, { label: 'Pas de préférence' }];
    }
    // 5. Carrosserie / Format de véhicule (SUV / Berline / Citadine)
    else if (/(carrosserie|body\s*style|body\s*type|format|suv.*berline|suv.*sedan|hatchback|citadine|berline|هيكل|شكل الطوموبيل)/i.test(text)) {
      resolved = language === 'en'
        ? [{ label: 'SUV', value: 'suv' }, { label: 'Hatchback / City car', value: 'citadine' }, { label: 'Sedan', value: 'berline' }, { label: 'No preference', value: 'no preference' }]
        : language === 'ar'
          ? [{ label: 'دفع رباعي (SUV)', value: 'suv' }, { label: 'سيارة مدينة (هاتشباك)', value: 'citadine' }, { label: 'سيدان', value: 'berline' }, { label: 'لا أفضلية', value: 'لا أفضلية' }]
          : language === 'darija'
            ? [{ label: 'SUV عالي', value: 'suv' }, { label: 'سيتادين صغيرة', value: 'citadine' }, { label: 'بيرلين', value: 'berline' }, { label: 'ما عنديش تفضيل', value: 'ما عنديش تفضيل' }]
            : [{ label: 'SUV', value: 'suv' }, { label: 'Citadine compacte', value: 'citadine' }, { label: 'Berline', value: 'berline' }, { label: 'Pas de préférence', value: 'Pas de préférence' }];
    }
    // 8. Usage (Ville / Autoroute / Mixte)
    else if (/(use the car|mainly use|city driving|surtout en ville|ville,?\s*(sur autoroute|ou)|usage.*principal|trajets?.*quotidiens?|فين غادي تسوق|استعمال|ستستعمل|تستعمل)/i.test(text)) {
      resolved = language === 'en'
        ? [{ label: 'Mostly city' }, { label: 'Mostly highway' }, { label: 'Both' }]
        : language === 'ar'
          ? [{ label: 'داخل المدينة' }, { label: 'في الطريق السيار' }, { label: 'الاثنين' }]
          : language === 'darija'
            ? [{ label: 'فالمدينة' }, { label: 'فالطريق السيار' }, { label: 'بجوج' }]
            : [{ label: 'Ville' }, { label: 'Autoroute' }, { label: 'Mixte' }];
    }
    // 9. Fallback: Extract options listed in parentheses
    else {
      const parenMatch = question.match(/\(([^)]+)\)\s*[?؟]?$/);
      if (parenMatch) {
        const rawItems = parenMatch[1].split(/,\s*(?:or|ou|and|et|أم|أو|ولا)?\s*|\s+(?:or|ou|أم|أو|ولا)\s+/i);
        const extracted = rawItems
          .map((item) => item.trim())
          .filter((item) => item.length > 0 && item.length < 35 && !/^(?:etc|ex|e\.g\.)/i.test(item));
        if (extracted.length >= 2) {
          resolved = extracted.map((item) => ({
            label: item.charAt(0).toUpperCase() + item.slice(1),
            value: item.toLowerCase(),
          }));
        }
      }
    }
  }

  // Nettoyage de tout préfixe "Oui, " / "Yes, " / "نعم، " résiduel
  const cleaned = resolved.map((opt) => {
    let cleanLabel = opt.label;
    if (!/^(est-ce que|confirmez-vous|do you confirm|واش متأكد)/i.test(question)) {
      cleanLabel = cleanLabel.replace(/^(?:Oui,?\s*|Yes,?\s*|نعم،?\s*|آه،?\s*)/i, '');
      if (cleanLabel.length > 0) {
        cleanLabel = cleanLabel.charAt(0).toUpperCase() + cleanLabel.slice(1);
      }
    }
    return { ...opt, label: cleanLabel || opt.label };
  });

  return filterOptionsByCandidateCars(cleaned, candidateCars);
}