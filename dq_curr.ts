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
    cout_reel: /economy|consumption|consommation|coût|cost|استهلاك|تكاليف|مصاريف|الصرف|صرف/i,
    praticite_urbaine: /city|ville|parking|compact|urbain|ركن|الركنة|باركينغ|silhouette|carrosserie|format/i,
    performance: /performance|power|puissance|تسارع|القوة/i,
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
  const lastAssistantQuestion = [...history].reverse().find((turn) => turn.role === 'assistant')?.content || '';
  const pendingDimension = dimensionCandidates.find((candidate) => Boolean(dimensionTokens[candidate.key]?.test(lastAssistantQuestion)));
  const selectableDimensions = dimensionCandidates
    .filter((candidate) => !candidate.covered && candidate !== pendingDimension)
    .map((candidate) => ({ ...candidate, diversity: new Set(candidate.values).size }))
    .filter((candidate) => candidate.diversity > 1 || (!remainingCars.length));
  const selectedDimension = [...selectableDimensions].sort((a, b) => b.diversity - a.diversity || a.priority - b.priority)[0]?.key;

  if (remainingCars && remainingCars.length > 0 && hasBudget && hasUsage) {
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
      const hasPowerful = remainingCars.length === 0 || remainingCars.some((c) => (Number(c.engine_power_hp) || 0) >= 115);
      const hasModerate = remainingCars.length === 0 || remainingCars.some((c) => (Number(c.engine_power_hp) || 0) < 115);
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

  for (const key of candidateKeys) {
    const q = buildCandidateDimensionQuestion(key);
    if (q && hasAtLeastTwoValidSuggestions(q, remainingCars)) {
      return q;
    }
  }

  return null;
}

