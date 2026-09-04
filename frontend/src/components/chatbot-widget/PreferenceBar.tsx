import React, { useState, useMemo, useEffect } from 'react';
import styles from './chatbot.module.css';

export interface PreferenceOption {
  label: string;
  value: string;
}

export type SupportedLanguage = 'fr' | 'darija' | 'ar' | 'en';

export interface PreferenceCategoryDef {
  id: string;
  type: 'slider' | 'pills';
  name: string;
  questionPatterns: RegExp[];
  sliderMin?: number;
  sliderMax?: number;
  sliderStep?: number;
  sliderDefault?: number;
  sliderLabels?: Record<SupportedLanguage, string>;
  formatValue?: (val: number, lang: SupportedLanguage) => string;
  formatSubmitText?: (val: number, lang: SupportedLanguage) => string;
  localizedOptions?: Record<SupportedLanguage, PreferenceOption[]>;
}

export function getSuitcasesText(liters: number, lang: SupportedLanguage = 'fr'): string {
  if (lang === 'ar') {
    if (liters < 280) return '1-2 حقائب يد صغيرة';
    if (liters <= 380) return '2-3 حقائب سفر';
    if (liters <= 500) return '3-4 حقائب سفر';
    if (liters <= 650) return '4-5 حقائب سفر كبيرة';
    return '5-6+ حقائب سفر كبيرة';
  }
  if (lang === 'darija') {
    if (liters < 280) return '1-2 فاليزات صغار';
    if (liters <= 380) return '2-3 فاليزات';
    if (liters <= 500) return '3-4 فاليزات';
    if (liters <= 650) return '4-5 فاليزات كبار';
    return '5-6+ فاليزات كبار';
  }
  if (lang === 'en') {
    if (liters < 280) return '1-2 cabin bags';
    if (liters <= 380) return '2-3 suitcases';
    if (liters <= 500) return '3-4 suitcases';
    if (liters <= 650) return '4-5 large suitcases';
    return '5-6+ large suitcases';
  }
  // French default
  if (liters < 280) return '1-2 valises cabine';
  if (liters <= 380) return '2-3 valises cabine';
  if (liters <= 500) return '3-4 valises';
  if (liters <= 650) return '4-5 grandes valises';
  return '5-6+ grandes valises';
}

function resolveLang(explicitLang?: string, text?: string): SupportedLanguage {
  if (text) {
    const hasArabicScript = /[\u0600-\u06FF]/.test(text);
    if (hasArabicScript) {
      const isDarija = /(?:ديال|ديالي|طوموبيل|شحال|فاليز|مزيان|بغيت|كاين|مخلط)/i.test(text);
      return isDarija ? 'darija' : 'ar';
    }
    const isEnglish = /(?:budget|what|which|fuel|transmission|driving|trunk|suitcases|prefer|vehicle|looking for|car|cars)/i.test(text);
    const isFrench = /(?:quel|votre|boîte|voiture|carburant|véhicule|recherchez|souhaitez)/i.test(text);
    if (isEnglish && !isFrench) {
      return 'en';
    }
    if (isFrench && !isEnglish) {
      return 'fr';
    }
  }

  if (explicitLang) {
    const l = explicitLang.toLowerCase();
    if (l === 'darija' || l === 'darija_ar' || l === 'darija_lat') return 'darija';
    if (l === 'ar' || l === 'arabic') return 'ar';
    if (l === 'en' || l === 'english') return 'en';
    if (l === 'fr' || l === 'french') return 'fr';
  }

  return 'fr';
}

const PREFERENCE_CATEGORIES: PreferenceCategoryDef[] = [
  {
    id: 'budget',
    type: 'slider',
    name: 'Budget',
    sliderMin: 50000,
    sliderMax: 700000,
    sliderStep: 5000,
    sliderDefault: 180000,
    sliderLabels: {
      fr: 'Ajustez votre budget :',
      darija: 'حدد الميزانية ديالك بالدرهم :',
      ar: 'حدد ميزانيتك المستهدفة بالدرهم :',
      en: 'Adjust your target budget in MAD:',
    },
    formatValue: (val: number, lang: SupportedLanguage) => {
      if (lang === 'ar' || lang === 'darija') {
        return `${val.toLocaleString('fr-FR')} درهم`;
      }
      if (lang === 'en') {
        return `${val.toLocaleString('en-US')} MAD`;
      }
      return `${val.toLocaleString('fr-FR')} DH`;
    },
    formatSubmitText: (val: number, lang: SupportedLanguage) => {
      if (lang === 'ar') {
        return `ميزانيتي المستهدفة هي ${val.toLocaleString('fr-FR')} درهم`;
      }
      if (lang === 'darija') {
        return `البودجي ديالي هو ${val.toLocaleString('fr-FR')} درهم`;
      }
      if (lang === 'en') {
        return `My budget is ${val.toLocaleString('en-US')} MAD`;
      }
      return `Mon budget est de ${val.toLocaleString('fr-FR')} DH`;
    },
    questionPatterns: [
      /quel(?: est)? (?:donc )?(?:votre )?budget/i,
      /quel budget/i,
      /budget (?:maximal|maximum|approximatif|envisag|pr[ée]vu|estim[ée]|souhait[ée]|cible)/i,
      /fourchette budg[ée]taire/i,
      /budget.*(?:envisagez|souhaitez|prévoyez).*\?/i,
      /chhal (?:l-)?budget/i,
      /chhal (?:3ndek|baghi t7et|tqder tdfa3|flous)/i,
      /شحال (?:هي )?(?:الميزانية|البودجي)/i,
      /الميزانية (?:المرصودة|التقريبية|المحددة|القصوى|ديالك|المستهدفة)/i,
      /كم (?:هي )?ميزانيتك/i,
      /ما (?:هي )?ميزانيتك/i,
      /ميزانيتك/i,
      /البودجي/i,
      /what(?:'s| is) your (?:approximate |target )?budget/i,
      /approximate budget/i,
      /target budget/i,
      /budget in mad/i,
      /how much (?:would you like|do you plan) to spend/i,
    ],
  },
  {
    id: 'usage',
    type: 'pills',
    name: 'Usage',
    questionPatterns: [
      /quel(?: est)? (?:votre )?usage/i,
      /quel type de (?:trajet|route|conduite)/i,
      /ville (?:ou|wla) (?:autoroute|triq)/i,
      /trajets? (?:quotidiens?|mixtes?)/i,
      /utilisation (?:principale|quotidienne)/i,
      /wach (?:baghiha )?l-mdina wla/i,
      /isti3mal.*(?:mdina|safar|triq)/i,
      /طبيعة (?:الاستعمال|القيادة|التنقل)/i,
      /نوع (?:الاستعمال|التنقل)/i,
      /داخل المدينة|طرق سريعة|سفر/i,
      /وسط المدينة|طريق وسفر/i,
      /daily driving habits/i,
      /city.*highway/i,
      /driving commute/i,
      /usage/i,
    ],
    localizedOptions: {
      fr: [
        { label: 'Usage mixte (ville & autoroute)', value: 'Usage mixte (ville et autoroute)' },
        { label: '100% Ville au quotidien', value: 'Principalement de la ville au quotidien' },
        { label: 'Grands trajets & Autoroute', value: 'Longs trajets et autoroute fréquents' },
      ],
      darija: [
        { label: 'مخلط (مدينة وطريق)', value: 'تنقل مخلط بين المدينة والطريق' },
        { label: 'المدينة بزاف', value: 'كنستعملها بزاف وسط المدينة' },
        { label: 'طريق طويلة وسفر', value: 'طريق طويلة وسفر مستمر' },
      ],
      ar: [
        { label: 'تنقل مختلط (مدينة وسفر)', value: 'استعمال مختلط بين المدينة والطرق السريعة' },
        { label: 'داخل المدينة يومياً', value: 'تنقل يومي داخل المدينة' },
        { label: 'مسافات طويلة وسفر', value: 'سفر متكرر ومسافات طويلة' },
      ],
      en: [
        { label: 'Mixed (City & Highway)', value: 'Mixed city and highway driving' },
        { label: 'Mainly City Commute', value: 'Mainly daily city driving' },
        { label: 'Long Distance & Highway', value: 'Frequent long distance and highway travel' },
      ],
    },
  },
  {
    id: 'fuel',
    type: 'pills',
    name: 'Carburant',
    questionPatterns: [
      /quel(?: type de)? carburant/i,
      /quelle motorisation/i,
      /(?:diesel|essence|hybride).*ou.*(?:diesel|essence|hybride|électrique)/i,
      /moteur.*(?:diesel|essence|hybride)/i,
      /mazot (?:wla|ou) lisans/i,
      /نوع (?:الوقود|المحرك)/i,
      /المحرك المفضل/i,
      /ديزل (?:أم|أو) بنزين/i,
      /مازوط (?:ولا|أو) ليسانص/i,
      /what (?:type of )?fuel/i,
      /petrol, diesel or hybrid/i,
      /fuel type/i,
      /preferred fuel/i,
    ],
    localizedOptions: {
      fr: [
        { label: 'Diesel', value: 'Je préfère un moteur diesel économique' },
        { label: 'Essence', value: 'Je préfère un moteur essence' },
        { label: 'Hybride', value: 'Je cherche un véhicule hybride' },
        { label: '100% Électrique', value: 'Je cherche un véhicule 100% électrique' },
      ],
      darija: [
        { label: 'مازوط (Diesel)', value: 'كنفضل محرك مازوط اقتصادي' },
        { label: 'ليصانص (Essence)', value: 'كنفضل محرك ليسانص' },
        { label: 'هجين (Hybride)', value: 'كنقلب على طوموبيل إيبريد' },
        { label: 'كهربائي (Électrique)', value: 'كنقلب على طوموبيل كهربائية 100%' },
      ],
      ar: [
        { label: 'ديزل (Diesel)', value: 'أفضل محرك ديزل اقتصادي' },
        { label: 'بنزين (Essence)', value: 'أفضل محرك بنزين' },
        { label: 'هجين (Hybride)', value: 'أبحث عن سيارة هجينة (هايبرد)' },
        { label: 'كهربائي بالكامل', value: 'أبحث عن سيارة كهربائية بالكامل' },
      ],
      en: [
        { label: 'Diesel', value: 'I prefer an economical diesel engine' },
        { label: 'Petrol / Gasoline', value: 'I prefer a petrol engine' },
        { label: 'Hybrid', value: 'I am looking for a hybrid vehicle' },
        { label: '100% Electric', value: 'I am looking for a 100% electric vehicle' },
      ],
    },
  },
  {
    id: 'transmission',
    type: 'pills',
    name: 'Boîte',
    questionPatterns: [
      /quelle boîte/i,
      /type de boîte/i,
      /boîte (?:manuelle|automatique)/i,
      /automatique ou manuelle/i,
      /bva ou bvm/i,
      /automatique wla manuelle/i,
      /ناقل (?:الحركة|السرعة)/i,
      /علبة السرعات/i,
      /أوتوماتيك (?:أم|أو) عادي/i,
      /أوتوماتيك (?:أم|أو) مانييل/i,
      /manual or automatic/i,
      /transmission preference/i,
      /automatic or manual/i,
      /gearbox/i,
    ],
    localizedOptions: {
      fr: [
        { label: 'Boîte Automatique', value: 'Je préfère une boîte automatique' },
        { label: 'Boîte Manuelle', value: 'Je préfère une boîte manuelle' },
      ],
      darija: [
        { label: 'أوتوماتيك (Automatique)', value: 'كنفضل بواط أوتوماتيك' },
        { label: 'مانييل (Manuelle)', value: 'كنفضل بواط مانييل عادية' },
      ],
      ar: [
        { label: 'ناقل حركة أوتوماتيكي', value: 'أفضل ناقل حركة أوتوماتيكي' },
        { label: 'ناقل حركة يدوي', value: 'أفضل ناقل حركة يدوي' },
      ],
      en: [
        { label: 'Automatic', value: 'I prefer an automatic gearbox' },
        { label: 'Manual', value: 'I prefer a manual gearbox' },
      ],
    },
  },
  {
    id: 'body',
    type: 'pills',
    name: 'Format',
    questionPatterns: [
      /carrosserie/i,
      /format/i,
      /body\s*(?:type|style)/i,
      /quel type de véhicule/i,
      /citadine, suv ou berline/i,
      /suv ou berline/i,
      /suv.*(?:berline|sedan|citadine|hatchback)/i,
      /taille du véhicule/i,
      /نوع الهيكل/i,
      /فئة السيارة/i,
      /شكل السيارة/i,
      /سيتادين.*suv/i,
      /دفع رباعي.*سيدان/i,
      /suv, sedan or hatchback/i,
      /preferred body/i,
      /vehicle style/i,
    ],
    localizedOptions: {
      fr: [
        { label: 'Citadine compacte', value: 'Je recherche une citadine compacte' },
        { label: 'SUV / Crossover', value: 'Je recherche un SUV / Crossover' },
        { label: 'Berline', value: 'Je recherche une berline élégante' },
        { label: 'Grand coffre (~4+ valises)', value: 'Je recherche un véhicule spacieux avec grand coffre' },
      ],
      darija: [
        { label: 'سيتادين صغيرة', value: 'كنقلب على سيتادين مصلوحة للمدينة' },
        { label: 'SUV / Crossover', value: 'كنقلب على SUV عالية ومريحة' },
        { label: 'بيرلين (Berline)', value: 'كنقلب على بيرلين عائلية أنيقة' },
        { label: 'صندوق كبير (~4 فاليزات)', value: 'كنقلب على طوموبيل بكوفر كبير كيهز الفاليزات' },
      ],
      ar: [
        { label: 'سيارة مدمجة للمدينة', value: 'أبحث عن سيارة مدينة مدمجة وعملية' },
        { label: 'سيارة دفع رباعي / SUV', value: 'أبحث عن سيارة SUV / كروس أوفر مرتفعة' },
        { label: 'سيدان (Berline)', value: 'أبحث عن سيارة سيدان أنيقة ومريحة' },
        { label: 'صندوق واسع (~4+ حقائب)', value: 'أبحث عن سيارة بصندوق أمتعة واسع يتسع لحقائب السفر' },
      ],
      en: [
        { label: 'Compact City Car', value: 'I am looking for a compact city car' },
        { label: 'SUV / Crossover', value: 'I am looking for an SUV or Crossover' },
        { label: 'Sedan / Saloon', value: 'I am looking for an elegant sedan' },
        { label: 'Large Trunk (~4+ suitcases)', value: 'I am looking for a spacious vehicle with a large trunk' },
      ],
    },
  },
  {
    id: 'coffre',
    type: 'slider',
    name: 'Capacité bagages',
    sliderMin: 1,
    sliderMax: 12,
    sliderStep: 1,
    sliderDefault: 5,
    sliderLabels: {
      fr: 'Nombre de valises :',
      darija: 'عدد الفاليزات :',
      ar: 'عدد الحقائب :',
      en: 'Number of suitcases:',
    },
    formatValue: (val: number, lang: SupportedLanguage) => `${val} ${lang === 'fr' ? 'valise(s)' : lang === 'darija' ? 'فاليزات' : lang === 'ar' ? 'حقيبة/حقائب' : 'suitcase(s)'}`,
    formatSubmitText: (val: number, lang: SupportedLanguage) => {
      if (lang === 'ar') {
        return `أرغب في سيارة تتسع لحوالي ${val} حقائب`;
      }
      if (lang === 'darija') {
        return `باغي طوموبيل كتسع تقريباً لـ ${val} فاليزات`;
      }
      if (lang === 'en') {
        return `I need space for around ${val} suitcases`;
      }
      return `Je souhaite un coffre pouvant contenir environ ${val} valises`;
    },
    questionPatterns: [
      /coffre/i,
      /volume (?:du |de |en )?coffre/i,
      /taille (?:du )?coffre/i,
      /capacit[ée] (?:du )?coffre/i,
      /valises?/i,
      /bagages?/i,
      /chhal (?:l-)?coffre/i,
      /صندوق/i,
      /حقائب/i,
      /فاليز/i,
      /trunk/i,
      /boot (?:space|capacity|size)/i,
      /luggage/i,
      /suitcases?/i,
    ],
  },
];

const VALIDATE_BTN_LABELS: Record<SupportedLanguage, string> = {
  fr: 'Valider',
  darija: 'تأكيد',
  ar: 'تأكيد',
  en: 'Confirm',
};

interface PreferenceBarProps {
  lastAssistantMessage?: string;
  currentLanguage?: string;
  onSelectOption: (optionText: string) => void;
  disabled?: boolean;
}

export default function PreferenceBar({
  lastAssistantMessage,
  currentLanguage,
  onSelectOption,
  disabled = false,
}: PreferenceBarProps) {
  const activeLang = useMemo<SupportedLanguage>(() => {
    return resolveLang(currentLanguage, lastAssistantMessage);
  }, [currentLanguage, lastAssistantMessage]);

  const activeCategory = useMemo<PreferenceCategoryDef | null>(() => {
    if (!lastAssistantMessage) return null;
    const cleanMsg = lastAssistantMessage.trim();
    const lower = cleanMsg.toLowerCase();

    // 1. Masquer si c'est une recommandation / fiche finale de véhicule
    if (
      lower.includes('car_recommendation') ||
      lower.includes('voici une sélection') ||
      lower.includes('voici les véhicules') ||
      lower.includes('here are some recommended vehicles') ||
      cleanMsg.includes('إليك أبرز السيارات') ||
      cleanMsg.includes('هاهما أحسن الموديلات')
    ) {
      return null;
    }

    // 2. Masquer si c'est une salutation générale ou un message d'accueil ouvert
    const isGeneralGreeting =
      lower.includes('welcome to wakala') ||
      lower.includes('bienvenue sur wakala') ||
      lower.includes('comment puis-je vous accompagner') ||
      lower.includes('comment puis-je vous guider') ||
      lower.includes('comment puis-je vous aider') ||
      lower.includes('how can i help you') ||
      lower.includes('how can i best assist you') ||
      lower.includes('expert technical advice') ||
      lower.includes('que recherchez-vous') ||
      cleanMsg.includes('مرحباً بك في منصة وكالة') ||
      cleanMsg.includes('مرحباً بك في وكالة') ||
      cleanMsg.includes('أهلاً وسهلاً بك') ||
      cleanMsg.includes('كيفاش نقدر نعاونك') ||
      cleanMsg.includes('كيف يمكنني مساعدتك');

    if (isGeneralGreeting) {
      return null;
    }

    // 3. Vérifier si le message pose explicitement une question ciblée
    for (const category of PREFERENCE_CATEGORIES) {
      const isMatchingQuestion = category.questionPatterns.some((pattern) => pattern.test(cleanMsg));
      if (isMatchingQuestion) {
        return category;
      }
    }

    // 4. Fallback générique: Extraire les options listées entre parenthèses, ex: "(Diesel, Petrol, or Hybrid)"
    const parenMatch = cleanMsg.match(/\(([^)]+)\)\s*[?؟]?$/);
    if (parenMatch) {
      const rawItems = parenMatch[1].split(/,\s*(?:or|ou|and|et|أم|أو|ولا)?\s*|\s+(?:or|ou|أم|أو|ولا)\s+/i);
      const extracted = rawItems
        .map((item) => item.trim())
        .filter((item) => item.length > 0 && item.length < 35 && !/^(?:etc|ex|e\.g\.)/i.test(item));
      if (extracted.length >= 2) {
        const options: PreferenceOption[] = extracted.map((item) => ({
          label: item.charAt(0).toUpperCase() + item.slice(1),
          value: item,
        }));
        return {
          id: 'dynamic_paren_choices',
          type: 'pills',
          name: 'Choix',
          questionPatterns: [],
          localizedOptions: {
            fr: options,
            en: options,
            ar: options,
            darija: options,
          },
        };
      }
    }

    return null;
  }, [lastAssistantMessage]);

  const [sliderValue, setSliderValue] = useState<number>(() => activeCategory?.sliderDefault ?? 180000);

  useEffect(() => {
    if (activeCategory?.sliderDefault !== undefined) {
      setSliderValue(activeCategory.sliderDefault);
    }
  }, [activeCategory?.id, activeCategory?.sliderDefault]);

  if (!activeCategory) {
    return null;
  }

  // Isolation des événements de glissement pour éviter tout mouvement parasite
  const stopPropagationHandler = (e: React.SyntheticEvent) => {
    e.stopPropagation();
  };

  // 1. Mode Slider Numérique Pur (Budget, Coffre)
  if (activeCategory.type === 'slider') {
    const minVal = activeCategory.sliderMin ?? 50000;
    const maxVal = activeCategory.sliderMax ?? 700000;
    const step = activeCategory.sliderStep ?? 5000;
    const percentage = Math.min(100, Math.max(0, ((sliderValue - minVal) / (maxVal - minVal)) * 100));

    const handleValidateSlider = () => {
      if (activeCategory.formatSubmitText) {
        onSelectOption(activeCategory.formatSubmitText(sliderValue, activeLang));
      } else {
        onSelectOption(`${activeCategory.name} : ${sliderValue}`);
      }
    };

    const label = activeCategory.sliderLabels?.[activeLang] ?? `Ajustez votre ${activeCategory.name.toLowerCase()} :`;
    const displayValue = activeCategory.formatValue
      ? activeCategory.formatValue(sliderValue, activeLang)
      : `${sliderValue}`;
    const validateBtnText = VALIDATE_BTN_LABELS[activeLang] || 'Valider';

    return (
      <div 
        className={styles.preferenceBarContainer}
        onMouseDown={stopPropagationHandler}
        onTouchStart={stopPropagationHandler}
        onPointerDown={stopPropagationHandler}
      >
        <div className={styles.prefSliderContainer}>
          <div className={styles.prefSliderHeader}>
            <span className={styles.prefSliderLabel}>{label}</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className={styles.prefSliderValue}>{displayValue}</span>
              <button
                type="button"
                className={styles.prefSliderValidateBtn}
                onClick={handleValidateSlider}
                disabled={disabled}
              >
                {validateBtnText}
              </button>
            </div>
          </div>

          <div 
            className={styles.prefSliderTrackWrapper}
            onMouseDown={stopPropagationHandler}
            onTouchStart={stopPropagationHandler}
            onPointerDown={stopPropagationHandler}
          >
            <input
              type="range"
              min={minVal}
              max={maxVal}
              step={step}
              value={sliderValue}
              onChange={(e) => setSliderValue(Number(e.target.value))}
              onMouseDown={stopPropagationHandler}
              onTouchStart={stopPropagationHandler}
              onPointerDown={stopPropagationHandler}
              disabled={disabled}
              className={styles.prefSliderInput}
              style={{
                background: `linear-gradient(to right, #10B981 0%, #10B981 ${percentage}%, #E2E8F0 ${percentage}%, #E2E8F0 100%)`,
              }}
            />
          </div>
        </div>
      </div>
    );
  }

  // 2. Mode Pastilles de Choix Discrètes (Usage, Carburant, Boîte, Format)
  const currentOptions = activeCategory.localizedOptions?.[activeLang] || activeCategory.localizedOptions?.['fr'] || [];

  return (
    <div 
      className={styles.preferenceBarContainer}
      onMouseDown={stopPropagationHandler}
      onTouchStart={stopPropagationHandler}
      onPointerDown={stopPropagationHandler}
    >
      <div className={styles.prefChipsScroll}>
        <div className={styles.prefChipsWrapper}>
          {currentOptions.map((opt) => (
            <button
              key={opt.label}
              type="button"
              className={styles.prefChipBtn}
              onClick={() => onSelectOption(opt.value)}
              disabled={disabled}
              title={opt.value}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
