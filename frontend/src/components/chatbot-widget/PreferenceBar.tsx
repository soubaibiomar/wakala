import React, { useState, useMemo, useEffect } from 'react';
import styles from './chatbot.module.css';

interface PreferenceOption {
  label: string;
  value: string;
}

interface PreferenceCategory {
  id: string;
  type: 'slider' | 'pills';
  name: string;
  questionPatterns: RegExp[];
  options?: PreferenceOption[];
  // Slider properties
  sliderMin?: number;
  sliderMax?: number;
  sliderStep?: number;
  sliderDefault?: number;
  sliderLabel?: string;
  formatValue?: (val: number) => string;
  formatSubmitText?: (val: number) => string;
}

export function getSuitcasesText(liters: number): string {
  if (liters < 280) return '1-2 valises cabine';
  if (liters <= 380) return '2-3 valises cabine';
  if (liters <= 500) return '3-4 valises';
  if (liters <= 650) return '4-5 grandes valises';
  return '5-6+ grandes valises';
}

const PREFERENCE_CATEGORIES: PreferenceCategory[] = [
  {
    id: 'budget',
    type: 'slider',
    name: 'Budget',
    sliderMin: 50000,
    sliderMax: 700000,
    sliderStep: 5000,
    sliderDefault: 180000,
    sliderLabel: 'Ajustez votre budget :',
    formatValue: (val: number) => `${val.toLocaleString('fr-FR')} DH`,
    formatSubmitText: (val: number) => `Mon budget est de ${val.toLocaleString('fr-FR')} DH`,
    questionPatterns: [
      /quel(?: est)? (?:donc )?(?:votre )?budget/i,
      /quel budget/i,
      /budget (?:maximal|maximum|approximatif|envisag|pr[ée]vu|estim[ée]|souhait[ée]|cible)/i,
      /fourchette budg[ée]taire/i,
      /chhal (?:l-)?budget/i,
      /chhal (?:3ndek|baghi t7et|tqder tdfa3|flous)/i,
      /شحال (?:هي )?الميزانية/i,
      /الميزانية (?:المرصودة|التقريبية|المحددة|القصوى|ديالك)/i,
      /كم (?:هي )?ميزانيتك/i,
      /what(?:'s| is) your (?:approximate |target )?budget/i,
      /approximate budget/i,
      /target budget/i,
      /budget.*(?:envisagez|souhaitez|prévoyez).*\?/i,
    ],
  },
  {
    id: 'coffre',
    type: 'slider',
    name: 'Volume Coffre & Valises',
    sliderMin: 150,
    sliderMax: 800,
    sliderStep: 25,
    sliderDefault: 425,
    sliderLabel: 'Volume du coffre & valises :',
    formatValue: (val: number) => `${val} L (${getSuitcasesText(val)})`,
    formatSubmitText: (val: number) => `Je souhaite un volume de coffre d'environ ${val} L (~ ${getSuitcasesText(val)})`,
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
      /trunk/i,
      /boot (?:space|capacity|size)/i,
      /luggage/i,
      /suitcases?/i,
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
      /داخل المدينة (?:أم|أو) السفر/i,
      /what type of (?:driving|commute)/i,
      /city or highway/i,
    ],
    options: [
      { label: 'Ville & Quotidien', value: 'Usage principal en ville pour les trajets quotidiens' },
      { label: 'Trajets mixtes (Ville & Route)', value: 'Usage mixte ville et autoroute' },
      { label: 'Autoroute & Longues distances', value: 'Principalement autoroute et longs trajets' },
      { label: 'Usage familial & Espace', value: 'Usage familial spacieux et confortable' },
    ],
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
      /ديزل (?:أم|أو) بنزين/i,
      /what (?:type of )?fuel/i,
      /petrol, diesel or hybrid/i,
    ],
    options: [
      { label: 'Diesel', value: 'Je préfère un moteur diesel économique' },
      { label: 'Essence', value: 'Je préfère un moteur essence' },
      { label: 'Hybride', value: 'Je cherche un véhicule hybride' },
      { label: '100% Électrique', value: 'Je cherche un véhicule 100% électrique' },
    ],
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
      /أوتوماتيك (?:أم|أو) عادي/i,
      /manual or automatic/i,
    ],
    options: [
      { label: 'Boîte Manuelle', value: 'Je préfère une boîte manuelle' },
      { label: 'Boîte Automatique', value: 'Je préfère une boîte automatique' },
    ],
  },
  {
    id: 'body',
    type: 'pills',
    name: 'Format',
    questionPatterns: [
      /quelle carrosserie/i,
      /quel format/i,
      /quel type de véhicule/i,
      /citadine, suv ou berline/i,
      /suv ou berline/i,
      /taille du véhicule/i,
      /نوع الهيكل/i,
      /فئة السيارة/i,
      /body style/i,
    ],
    options: [
      { label: 'Citadine compacte', value: 'Je recherche une citadine compacte' },
      { label: 'SUV / Crossover', value: 'Je recherche un SUV / Crossover' },
      { label: 'Berline', value: 'Je recherche une berline élégante' },
      { label: 'Grand coffre (~4+ valises)', value: 'Je recherche un véhicule spacieux avec grand coffre' },
    ],
  },
];

interface PreferenceBarProps {
  lastAssistantMessage?: string;
  onSelectOption: (optionText: string) => void;
  disabled?: boolean;
}

export default function PreferenceBar({
  lastAssistantMessage,
  onSelectOption,
  disabled = false,
}: PreferenceBarProps) {
  const activeCategory = useMemo<PreferenceCategory | null>(() => {
    if (!lastAssistantMessage) return null;
    const cleanMsg = lastAssistantMessage.trim();
    const lower = cleanMsg.toLowerCase();

    // 1. Masquer si c'est une recommandation / fiche finale de véhicule
    if (
      lower.includes('car_recommendation') ||
      lower.includes('voici une sélection') ||
      lower.includes('voici les véhicules')
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

  // Isolation des événements de glissement pour éviter tout mouvement de la fenêtre du chatbot
  const stopPropagationHandler = (e: React.SyntheticEvent) => {
    e.stopPropagation();
  };

  // 1. Mode Slider Numérique Pur (Budget, Coffre) - AUCUN bouton de suggestion sous le slider
  if (activeCategory.type === 'slider') {
    const minVal = activeCategory.sliderMin ?? 50000;
    const maxVal = activeCategory.sliderMax ?? 700000;
    const step = activeCategory.sliderStep ?? 5000;
    const percentage = Math.min(100, Math.max(0, ((sliderValue - minVal) / (maxVal - minVal)) * 100));

    const handleValidateSlider = () => {
      if (activeCategory.formatSubmitText) {
        onSelectOption(activeCategory.formatSubmitText(sliderValue));
      } else {
        onSelectOption(`${activeCategory.name} : ${sliderValue}`);
      }
    };

    const displayValue = activeCategory.formatValue
      ? activeCategory.formatValue(sliderValue)
      : `${sliderValue}`;

    return (
      <div 
        className={styles.preferenceBarContainer}
        onMouseDown={stopPropagationHandler}
        onTouchStart={stopPropagationHandler}
        onPointerDown={stopPropagationHandler}
      >
        <div className={styles.prefSliderContainer}>
          <div className={styles.prefSliderHeader}>
            <span className={styles.prefSliderLabel}>
              {activeCategory.sliderLabel ?? `Ajustez votre ${activeCategory.name.toLowerCase()} :`}
            </span>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className={styles.prefSliderValue}>{displayValue}</span>
              <button
                type="button"
                className={styles.prefSliderValidateBtn}
                onClick={handleValidateSlider}
                disabled={disabled}
              >
                Valider
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
  return (
    <div 
      className={styles.preferenceBarContainer}
      onMouseDown={stopPropagationHandler}
      onTouchStart={stopPropagationHandler}
      onPointerDown={stopPropagationHandler}
    >
      <div className={styles.prefChipsScroll}>
        <div className={styles.prefChipsWrapper}>
          {activeCategory.options?.map((opt) => (
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
