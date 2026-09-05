import { describe, expect, it, vi } from 'vitest';
import { FastApiRecommendationClient, MockRecommendationClient, type Car, type ChatTurn, detectConstraintConflict, computeFallback8dScores, detectClientProfile, getUniqueModelCars, deduplicateCars, extractMaximumBudget, extractBrandPreference, informativeRequestPattern, isCriterionPreference } from './recommendationClient';
import { alignQuestionOptions } from './recommendationClient';

vi.mock('../../services/chatbotService', () => ({
  chatbotService: { streamMessage: vi.fn() },
}));

const mockGetVehicles = vi.fn();
const mockRecommendationSearch = vi.fn();
vi.mock('../../services/vehicleService', () => ({
  vehicleService: {
    getVehicles: (...args: unknown[]) => mockGetVehicles(...args),
    getVehicleById: vi.fn(),
  },
}));

vi.mock('../../services/recommendationService', () => ({
  recommendationService: { search: (...args: unknown[]) => mockRecommendationSearch(...args) },
}));

const car = (overrides: Partial<Car> = {}): Car => ({
  id: overrides.id || crypto.randomUUID(),
  seller_id: 'seller-1',
  brand: 'Toyota',
  model: 'Rav-4',
  version: 'Active',
  year: 2025,
  mileage: 0,
  fuel_type: 'essence',
  body_type: 'suv',
  transmission: 'automatique',
  engine_power_hp: 150,
  doors: 5,
  seats: 5,
  city: 'Casablanca',
  price: 400000,
  trunk_volume_l: 500,
  ncap_rating: '4★ (Euro NCAP 2021)',
  created_at: '',
  updated_at: '',
  ...overrides,
});

const history = (...contents: string[]): ChatTurn[] => contents.map((content, index) => ({
  role: index % 2 === 0 ? 'user' : 'assistant',
  content,
}));

describe('FastApiRecommendationClient recommendation logic', () => {
  it.each([
    'I want a car', 'I need an SUV', 'show me an electric car', 'find me a diesel vehicle',
    'I want the safest car', 'I am looking for a Mercedes', 'I want a family car',
    'I want a Porsche', 'je veux acheter une voiture', 'je veux une voiture familiale', 'je cherche un SUV',
    'أبحث عن سيارة', 'بغيت طوموبيل', 'budget 300000 MAD', 'car under 250000 dhs',
    'best car for city', 'which vehicle fits me', 'recommend a hybrid car',
    'I need a manual vehicle', 'show me a sedan', 'most secure vehicle',
    'tonobile dyal 3a2ila', 'tomobile dyal l3a2ila',
    'a car for 22 years old', 'voiture pour une femme de 30 ans',
    'سيارة لرجل عمره 35 سنة', 'tomobil l wa7ed 3omro 22 3am',
    'I am a director', 'I am a student', 'I am a taxi driver', 'je suis entrepreneur',
    'je suis directeur', 'مدير', 'رجل أعمال', 'ana mdir',
    'I am a doctor', 'I am an engineer', 'I am a lawyer', 'I am a teacher', 'I am retired',
    'car for a young driver', 'car for a family of 5',
    'je suis médecin', 'je suis ingénieur', 'je suis avocat', 'je suis enseignant',
    'je suis commercial', 'je suis jeune conducteur', 'je suis retraité',
    'je suis père de famille', 'voiture pour médecin', 'véhicule pour commercial',
    'أنا محامي', 'أنا أستاذ', 'أنا مهندس', 'أنا طبيب', 'أنا طالب', 'أنا مدير',
    'أنا متقاعد', 'أنا رجل أعمال', 'أنا سائق طاكسي', 'سيارة لطالب', 'سيارة لطبيب',
    'ana mta9ed', 'ana tbib', 'ana mouhandis', 'ana taleb', 'ana moul taxi', 'ana ostad',
  ])('detects recommendation intent for scenario: %s', async (message) => {
    const client = new FastApiRecommendationClient();
    await expect(client.detectRecommendationIntent(message)).resolves.toBe(true);
  });

  it('understands age and gender context without producing zero recommendations', async () => {
    const client = new FastApiRecommendationClient();
    const available = [car({ id: 'context-car' })];
    mockGetVehicles.mockResolvedValue({ items: available, pages: 1 });

    const result = await client.applyAnswer(
      'a car for 22 years old',
      [{ role: 'user', content: 'a car for 22 years old' }],
      [],
    );

    expect(result).toEqual(available);
    await expect(client.getNextQuestion(
      [{ role: 'user', content: 'voiture pour une femme de 30 ans' }],
      available,
    )).resolves.toMatchObject({ question: expect.stringContaining('budget') });
  });

  it('keeps a French family-car request inside the one-question flow', async () => {
    const client = new FastApiRecommendationClient();
    client.setLanguage('fr');
    mockGetVehicles.mockResolvedValue({
      items: [car({ price: 200000 })],
      pages: 1,
    });
    await expect(client.detectRecommendationIntent('je veux une voiture familiale')).resolves.toBe(true);
    const question = await client.getNextQuestion(
      history('je veux une voiture familiale', 'question'),
      [car({ body_type: 'suv' }), car({ body_type: 'monospace', trunk_volume_l: 700 })],
    );
    expect(question?.question).toContain('budget');
    expect(question?.question).not.toContain('deux');
  });

  it('recognizes Latin Darija family-car requests', async () => {
    const client = new FastApiRecommendationClient();
    client.setLanguage('darija');
    await expect(client.detectRecommendationIntent('tonobile dyal 3a2ila')).resolves.toBe(true);
    const question = await client.getNextQuestion(
      [{ role: 'user', content: 'tonobile dyal 3a2ila' }],
      [car(), car({ body_type: 'monospace', trunk_volume_l: 700 })],
    );
    expect(question?.question).toContain('الميزانية');
  });

  it('advances after an Arabic budget range instead of repeating the budget control', async () => {
    const client = new FastApiRecommendationClient();
    client.setLanguage('darija');
    const question = await client.getNextQuestion([
      { role: 'user', content: 'tonobile dyal 3a2ila' },
      { role: 'assistant', content: 'شحال هي الميزانية القصوى ديالك بالدرهم؟' },
      { role: 'user', content: 'الميزانية بين 263900 و39578300 درهم' },
      { role: 'assistant', content: 'فين غادي تستعمل الطوموبيل أكثر؟' },
      { role: 'user', content: 'Ville' },
    ], [car({ body_type: 'monospace', trunk_volume_l: 700 }), car({ body_type: 'suv', trunk_volume_l: 500 })]);
    expect(question?.question).toContain('الفاليزات');
    expect(question?.question).not.toContain('الميزانية');
  });

  it('localizes usage choices in Darija', async () => {
    const client = new FastApiRecommendationClient();
    client.setLanguage('darija');
    const question = await client.getNextQuestion([
      { role: 'user', content: 'tonobile dyal 3a2ila' },
      { role: 'assistant', content: 'شحال هي الميزانية القصوى ديالك بالدرهم؟' },
      { role: 'user', content: 'الميزانية بين 263900 و39578300 درهم' },
    ], [car(), car({ body_type: 'monospace', trunk_volume_l: 700 })]);
    expect(question?.options?.map((option) => option.label)).toEqual(['فالمدينة', 'فالطريق السيار', 'بجوج']);
  });

  it('keeps the requested brand when a later answer is applied', async () => {
    const client = new FastApiRecommendationClient();
    const mercedes = car({ brand: 'Mercedes-Benz', model: 'GLC' });
    const porsche = car({ brand: 'Porsche', model: 'Cayenne' });
    mockGetVehicles.mockResolvedValue({ items: [mercedes], pages: 1 });
    mockRecommendationSearch.mockResolvedValue({ items: [{ vehicle_id: mercedes.id, match_score: 1, key_facts: [] }] });
    const candidates = await client.applyAnswer('I want a Mercedes', history('I want a Mercedes'), [mercedes, porsche]);
    const afterUsage = await client.applyAnswer('Mostly city', history('I want a Mercedes', 'What is your budget?', 'budget between 399000 and 1870000 MAD', 'How will you use it?', 'Mostly city'), candidates);
    expect(candidates.every((vehicle) => vehicle.brand === 'Mercedes-Benz')).toBe(true);
    expect(afterUsage.every((vehicle) => vehicle.brand === 'Mercedes-Benz')).toBe(true);
  });

  it('orders safest vehicles by their NCAP rating across the catalogue', async () => {
    const client = new FastApiRecommendationClient();
    const vehicles = [
      car({ id: 'low', ncap_rating: '2★', model: 'Low' }),
      car({ id: 'high', ncap_rating: '5★', model: 'High' }),
      car({ id: 'unknown', ncap_rating: undefined, model: 'Unknown' }),
    ];
    mockGetVehicles.mockResolvedValue({ items: vehicles, pages: 1 });
    const result = await client.applyAnswer('I want the safest car', history('I want the safest car'), []);
    expect(result.map((vehicle) => vehicle.id)).toEqual(['high', 'low', 'unknown']);
  });

  it('filters strictly for 5-star NCAP vehicles when Note NCAP maximale is selected', async () => {
    const client = new FastApiRecommendationClient();
    const candidateCars = [
      car({ id: 'two-stars', ncap_rating: '2★', model: 'Low' }),
      car({ id: 'three-stars', ncap_rating: '3★', model: 'Mid' }),
      car({ id: 'five-stars', ncap_rating: '5★ (Euro NCAP 2022)', model: 'High' }),
    ];
    mockGetVehicles.mockResolvedValue({ items: candidateCars, pages: 1 });
    const result = await client.applyAnswer('Note NCAP maximale', history('Note NCAP maximale'), candidateCars);
    expect(result.map((vehicle) => vehicle.id)).toEqual(['five-stars']);
  });

  it('filters strictly for >= 4-star NCAP vehicles when Bonne sécurité is selected', async () => {
    const client = new FastApiRecommendationClient();
    const candidateCars = [
      car({ id: 'two-stars', ncap_rating: '2★', model: 'Low' }),
      car({ id: 'four-stars', ncap_rating: '4★ (Euro NCAP 2024)', model: 'Good' }),
      car({ id: 'five-stars', ncap_rating: '5★ (Euro NCAP 2022)', model: 'Top' }),
    ];
    mockGetVehicles.mockResolvedValue({ items: candidateCars, pages: 1 });
    const result = await client.applyAnswer('Bonne sécurité', history('Bonne sécurité'), candidateCars);
    expect(result.map((vehicle) => vehicle.id)).toEqual(['five-stars', 'four-stars']);
  });

  it('consults and prioritizes the currently recommended candidate cars when filtering by safety', async () => {
    const client = new FastApiRecommendationClient();
    const instantCars = [
      car({ id: 'suv-instant-safe', ncap_rating: '5★ (Euro NCAP 2023)', model: 'Instant SUV' }),
      car({ id: 'suv-instant-untested', ncap_rating: 'NT (Non testé)', model: 'Untested SUV' }),
    ];
    const otherCatalogueCars = [
      car({ id: 'other-car-5stars', ncap_rating: '5★ (Euro NCAP 2022)', model: 'Other Car' }),
    ];
    mockGetVehicles.mockResolvedValue({ items: otherCatalogueCars, pages: 1 });
    const result = await client.applyAnswer('Note NCAP maximale', history('Note NCAP maximale'), instantCars);
    expect(result.map((vehicle) => vehicle.id)).toEqual(['suv-instant-safe']);
  });


  it('uses the full catalogue when a direct body filter misses the current shortlist', async () => {
    const client = new FastApiRecommendationClient();
    const suv = car({ id: 'suv', body_type: 'suv' });
    mockGetVehicles.mockResolvedValue({ items: [suv], pages: 1 });
    const result = await client.applyAnswer('I want an SUV', history('I want an SUV'), [car({ body_type: 'berline' })]);
    expect(result.map((vehicle) => vehicle.id)).toEqual(['suv']);
  });

  it('applies body and fuel constraints together from one request', async () => {
    const client = new FastApiRecommendationClient();
    const electricSuv = car({ id: 'electric-suv', body_type: 'suv', fuel_type: 'electrique' });
    const petrolSuv = car({ id: 'petrol-suv', body_type: 'suv', fuel_type: 'essence' });
    const electricSedan = car({ id: 'electric-sedan', body_type: 'berline', fuel_type: 'electrique' });
    const result = await client.applyAnswer(
      'I need an electric SUV',
      history('I need an electric SUV'),
      [electricSuv, petrolSuv, electricSedan],
    );
    expect(result.map((vehicle) => vehicle.id)).toEqual(['electric-suv']);
  });

  it('keeps an unavailable explicitly requested brand from falling back to the catalogue', async () => {
    mockGetVehicles.mockResolvedValue({ items: [], pages: 0 });
    const client = new FastApiRecommendationClient();
    const result = await client.applyAnswer('I want a Lamborghini', history('I want a Lamborghini'), [car()]);
    expect(result).toEqual([]);
    expect(mockGetVehicles).toHaveBeenCalledWith(expect.objectContaining({ brand: 'lamborghini' }));
  });

  it('reapplies all prior constraints when a later fuel answer misses the shortlist', async () => {
    const client = new FastApiRecommendationClient();
    const validDiesel = car({ id: 'valid-diesel', fuel_type: 'diesel', body_type: 'suv', price: 450000, trunk_volume_l: 700 });
    const wrongFuel = car({ id: 'wrong-fuel', fuel_type: 'essence', body_type: 'suv', price: 450000, trunk_volume_l: 700 });
    const wrongBody = car({ id: 'wrong-body', fuel_type: 'diesel', body_type: 'coupe', price: 450000, trunk_volume_l: 700 });
    mockGetVehicles.mockResolvedValue({ items: [validDiesel, wrongFuel, wrongBody], pages: 1 });
    const result = await client.applyAnswer(
      'Diesel',
      history(
        'I want a family car',
        'What is your budget?',
        'budget between 199900 and 1334500 MAD',
        'How will you use it?',
        'Mostly city',
        'How much luggage space?',
        'Suitcase capacity between 3 and 13',
        'Which fuel type?',
        'Diesel',
      ),
      [wrongFuel],
    );
    expect(result.map((vehicle) => vehicle.id)).toEqual(['valid-diesel']);
  });

  it('returns no manual vehicles when the catalogue has none', async () => {
    const client = new FastApiRecommendationClient();
    mockGetVehicles.mockResolvedValue({ items: [], pages: 1 });
    await expect(client.applyAnswer('Manual', history('I need a manual car'), [])).resolves.toEqual([]);
  });

  it('keeps the next question sequence data-driven after three visible cars', async () => {
    const client = new FastApiRecommendationClient();
    const candidates = [
      car({ id: '1', body_type: 'monospace', seats: 7, trunk_volume_l: 700, price: 200000 }),
      car({ id: '2', body_type: 'suv', seats: 5, trunk_volume_l: 500, price: 400000 }),
      car({ id: '3', body_type: 'break', seats: 5, trunk_volume_l: 600, price: 600000 }),
    ];
    const question = await client.getNextQuestion(history('I want a family car', 'question'), candidates);
    expect(question?.question).toContain('budget');
    expect(question?.rangeBounds).toBeDefined();
  });

  it('does not repeat a preference question after an explicit no-preference answer', async () => {
    const client = new FastApiRecommendationClient();
    const candidates = [
      car({ id: '1', body_type: 'suv', fuel_type: 'essence', engine_power_hp: 150, trunk_volume_l: 500 }),
      car({ id: '2', body_type: 'suv', fuel_type: 'hybride', engine_power_hp: 180, trunk_volume_l: 600 }),
    ];
    const question = await client.getNextQuestion([
      { role: 'user', content: 'I want a family car' },
      { role: 'assistant', content: 'What is your maximum budget in MAD?' },
      { role: 'user', content: 'My budget is 500000 MAD' },
      { role: 'assistant', content: 'How will you mainly use the car?' },
      { role: 'user', content: 'Mostly city' },
      { role: 'assistant', content: 'How much luggage space do you need, in suitcases?' },
      { role: 'user', content: 'Suitcase capacity between 5 and 37' },
      { role: 'assistant', content: 'For city driving, do you prefer a compact car that is easy to park?' },
      { role: 'user', content: 'More space' },
      { role: 'assistant', content: 'Do you prioritize power and acceleration over lower running costs?' },
      { role: 'user', content: 'No preference' },
    ], candidates);
    expect(question?.question).not.toContain('power and acceleration');
  });

  it('provides quick choices for performance preferences', async () => {
    const client = new FastApiRecommendationClient();
    client.setLanguage('en');
    const candidates = [
      car({ id: '1', engine_power_hp: 150 }),
      car({ id: '2', engine_power_hp: 220 }),
    ];
    const question = await client.getNextQuestion([
      { role: 'user', content: 'I want a 500000 MAD SUV for city driving with hybrid fuel and an automatic gearbox, with space for 5 suitcases' },
      { role: 'assistant', content: 'Do you prioritize power and acceleration over lower running costs?' },
    ], candidates);
    expect(question?.question).toContain('power and acceleration');
    expect(question?.options).toHaveLength(2);
  });

  it('provides 3 distinct options for drivetrain preference (4x4 vs 2WD vs No preference)', async () => {
    const client = new FastApiRecommendationClient();
    client.setLanguage('en');
    const candidates = [
      car({ id: '1', is_4x4: true, body_type: 'suv', engine_power_hp: 200, trunk_volume_l: 500, fuel_type: 'diesel' }),
      car({ id: '2', is_4x4: false, body_type: 'suv', engine_power_hp: 200, trunk_volume_l: 500, fuel_type: 'diesel' }),
    ];
    const question = await client.getNextQuestion([
      { role: 'user', content: 'I want a 500000 MAD SUV for highway driving with diesel fuel and an automatic gearbox, with space for 5 suitcases and high safety' },
      { role: 'assistant', content: 'Do you prioritize power and acceleration over lower running costs?' },
      { role: 'user', content: 'No preference' },
    ], candidates);
    expect(question?.question).toContain('all-wheel drive (4x4 / AWD)');
    expect(question?.options).toHaveLength(3);
    expect(question?.options.map((o) => o.label)).toEqual(['Yes, 4x4 / AWD', 'Standard (2WD)', 'No preference']);
  });

  it('filters strictly for 4x4 or 2WD vehicles when drivetrain preference is answered', async () => {
    const client = new FastApiRecommendationClient();
    const car4x4 = car({ id: 'awd-car', is_4x4: true });
    const car2wd = car({ id: '2wd-car', is_4x4: false });
    const candidates = [car4x4, car2wd];

    const resultAwd = await client.applyAnswer('Yes, 4x4 / AWD', history('Yes, 4x4 / AWD'), candidates);
    expect(resultAwd.map((c) => c.id)).toEqual(['awd-car']);

    const result2wd = await client.applyAnswer('Standard (2WD)', history('Standard (2WD)'), candidates);
    expect(result2wd.map((c) => c.id)).toEqual(['2wd-car']);
  });

  it('strictly excludes supercar brands like Ferrari from city car / citadine recommendations', async () => {
    const client = new FastApiRecommendationClient();
    const clio = car({ id: 'renault-clio', brand: 'Renault', model: 'Clio', body_type: 'citadine' });
    const ferrari = car({ id: 'ferrari-296', brand: 'Ferrari', model: '296 GTB', body_type: 'citadine' });
    mockGetVehicles.mockResolvedValue({ items: [clio, ferrari], pages: 1 });

    const result = await client.applyAnswer('I want a city car', history('I want a city car'), [clio, ferrari]);
    expect(result.map((c) => c.id)).toEqual(['renault-clio']);
  });

  it('detects citadine with 7 seats conflict and provides didactic explanations and options', () => {
    const conflict = detectConstraintConflict([
      { role: 'user', content: 'Je veux une citadine avec 7 places' },
    ]);
    expect(conflict).not.toBeNull();
    expect(conflict?.type).toBe('citadine_large_capacity');
    expect(conflict?.explanation.fr).toContain('Une citadine est conçue pour être compacte');
    expect(conflict?.options.fr.length).toBeGreaterThanOrEqual(2);
    expect(conflict?.options.fr[0].label).toContain('7 places');
  });

  it('detects supercar with diesel conflict and suggests petrol or executive diesel alternatives', () => {
    const conflict = detectConstraintConflict([
      { role: 'user', content: 'Je veux une Ferrari diesel' },
    ]);
    expect(conflict).not.toBeNull();
    expect(conflict?.type).toBe('supercar_diesel');
    expect(conflict?.explanation.fr).toContain('Ferrari');
    expect(conflict?.options.fr[0].label).toContain('essence');
  });

  it('detects electric vehicle with impossible low budget and suggests hybrids or budget adjustment', () => {
    const conflict = detectConstraintConflict([
      { role: 'user', content: 'Je cherche une voiture electrique avec un budget max de 90000 MAD' },
    ]);
    expect(conflict).not.toBeNull();
    expect(conflict?.type).toBe('ev_low_budget');
    expect(conflict?.explanation.fr).toContain('170 000 MAD');
  });

  it('computes realistic fallback 8D scores when backend scoring is unavailable', () => {
    const testCars = [
      car({ id: 'car-1', trunk_volume_l: 520, engine_power_hp: 150, ncap_rating: '5★ (Euro NCAP)', fuel_consumption: 4.8 }),
      car({ id: 'car-2', trunk_volume_l: 300, engine_power_hp: 90, ncap_rating: '4★ (Euro NCAP)', fuel_consumption: 5.5 }),
    ];
    const scored = computeFallback8dScores(testCars);
    expect(scored).toHaveLength(2);
    expect(scored[0].eight_dimension_scores).toBeDefined();
    expect(scored[0].eight_dimension_scores?.securite).toBe(100);
    expect(scored[0].eight_dimension_scores?.espace_coffre).toBeGreaterThanOrEqual(80);
    expect(scored[0].total_8d_score).toBeGreaterThan(0);
  });

  describe('Taxi profile qualification & recommendations', () => {
    it.each([
      'Ana moul taxi khesni tomobil s7i7a',
      'chauffeur de taxi',
      'je veux une voiture pour petit taxi',
      'bghit nakhdem grand taxi',
      'أنا سائق طاكسي ونبحث عن سيارة اقتصادية',
      'مول طاكسي باغي طوموبيل ديال الخدمة',
      'I am a taxi driver looking for a reliable car',
    ])('identifies taxi client profile for: %s', (query) => {
      expect(detectClientProfile(query)).toBe('taxi');
    });

    it('asks Petit Taxi vs Grand Taxi qualification first when taxi type is unspecified', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('darija');
      const testCars = [car({ id: 'dacia-logan', brand: 'Dacia', model: 'Logan', price: 140000 })];

      const nextQuestion = await client.getNextQuestion(
        [{ role: 'user', content: 'Ana moul taxi khesni tomobil s7i7a' }],
        testCars,
      );

      expect(nextQuestion).not.toBeNull();
      expect(nextQuestion?.question).toContain('بيتي طاكسي');
      expect(nextQuestion?.question).toContain('ݣران طاكسي');
      expect(nextQuestion?.options).toHaveLength(2);
      expect(nextQuestion?.options[0].label).toContain('بيتي طاكسي');
      expect(nextQuestion?.options[1].label).toContain('ݣران طاكسي');
    });

    it('asks realistic taxi investment budget with appropriate slider bounds', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');
      const testCars = [
        car({ id: 'dacia-logan', brand: 'Dacia', model: 'Logan', price: 139000 }),
        car({ id: 'fiat-tipo', brand: 'Fiat', model: 'Tipo', price: 175000 }),
      ];

      const nextQuestion = await client.getNextQuestion(
        [
          { role: 'user', content: 'Je suis chauffeur de taxi' },
          { role: 'assistant', content: 'Exercez-vous en Petit Taxi (urbain, 5 places) ou en Grand Taxi (interurbain, 6-7 places) ?' },
          { role: 'user', content: 'Petit Taxi' },
        ],
        testCars,
      );

      expect(nextQuestion).not.toBeNull();
      expect(nextQuestion?.question).toContain('budget d’investissement');
      expect(nextQuestion?.rangeBounds).toBeDefined();
      expect(nextQuestion?.rangeBounds?.min).toBe(135000);
      expect(nextQuestion?.rangeBounds?.max).toBe(175000);
      expect(nextQuestion?.rangeBounds?.label).toBe('Budget taxi');
      expect(nextQuestion?.options.length).toBeGreaterThanOrEqual(2);

      // Verify envelope fallback when no cars loaded yet
      const fallbackQ = await client.getNextQuestion(
        [
          { role: 'user', content: 'Je suis chauffeur de taxi' },
          { role: 'assistant', content: 'Exercez-vous en Petit Taxi (urbain, 5 places) ou en Grand Taxi (interurbain, 6-7 places) ?' },
          { role: 'user', content: 'Petit Taxi' },
        ],
        [],
      );
      expect(fallbackQ?.rangeBounds?.min).toBe(90000);
      expect(fallbackQ?.rangeBounds?.max).toBe(250000);
    });

    it('asks taxi operational priority after budget is provided', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');
      const testCars = [car({ id: 'dacia-logan', brand: 'Dacia', model: 'Logan', price: 140000 })];

      const nextQuestion = await client.getNextQuestion(
        [
          { role: 'user', content: 'Je suis chauffeur de taxi' },
          { role: 'assistant', content: 'Exercez-vous en Petit Taxi ou en Grand Taxi ?' },
          { role: 'user', content: 'Petit Taxi' },
          { role: 'assistant', content: 'Quel est votre budget d’investissement maximum en MAD ?' },
          { role: 'user', content: 'Budget taxi 160 000 MAD' },
        ],
        testCars,
      );

      expect(nextQuestion).not.toBeNull();
      expect(nextQuestion?.question).toContain('priorité d’exploitation');
      expect(nextQuestion?.options.length).toBe(3);
      expect(nextQuestion?.options[0].label).toContain('Consommation minimale');
      expect(nextQuestion?.options[1].label).toContain('Pièces abordables');
    });

    it('strictly excludes luxury brands and ranks Moroccan taxi workhorses first', async () => {
      const client = new FastApiRecommendationClient();
      const daciaLogan = car({ id: 'dacia-logan', brand: 'Dacia', model: 'Logan', price: 139000, fuel_type: 'diesel', body_type: 'berline' });
      const fiatTipo = car({ id: 'fiat-tipo', brand: 'Fiat', model: 'Tipo', price: 180000, fuel_type: 'diesel', body_type: 'berline' });
      const audiQ8 = car({ id: 'audi-q8', brand: 'Audi', model: 'Q8', price: 950000, fuel_type: 'diesel', body_type: 'suv' });
      const porscheCayenne = car({ id: 'porsche-cayenne', brand: 'Porsche', model: 'Cayenne', price: 1200000, fuel_type: 'diesel', body_type: 'suv' });

      mockGetVehicles.mockResolvedValue({ items: [daciaLogan, fiatTipo, audiQ8, porscheCayenne], pages: 1 });

      const results = await client.applyAnswer(
        'Ana moul taxi khesni tomobil s7i7a',
        history('Ana moul taxi khesni tomobil s7i7a'),
        [daciaLogan, fiatTipo, audiQ8, porscheCayenne],
      );

      const resultIds = results.map((c) => c.id);
      expect(resultIds).toContain('dacia-logan');
      expect(resultIds).toContain('fiat-tipo');
      expect(resultIds).not.toContain('audi-q8');
      expect(resultIds).not.toContain('porsche-cayenne');
      expect(results[0].brand).toBe('Dacia');
    });
  });

  describe('Profile-adapted qualification and recommendation flows', () => {
    it('adapts budget range and format options for young_student', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');
      const clio = car({ id: 'clio-5', brand: 'Renault', model: 'Clio', price: 160000, body_type: 'citadine', engine_power_hp: 90 });
      const sandero = car({ id: 'sandero', brand: 'Dacia', model: 'Sandero Stepway', price: 145000, body_type: 'suv', engine_power_hp: 95 });

      // Step 1: Budget question adapts dynamically to recommended cars
      const qBudget = await client.getNextQuestion(
        [{ role: 'user', content: 'Je suis un jeune étudiant et je cherche ma première voiture' }],
        [clio, sandero],
      );
      expect(qBudget).not.toBeNull();
      expect(qBudget?.question).toContain('budget');
      expect(qBudget?.rangeBounds).toBeDefined();
      expect(qBudget?.rangeBounds?.min).toBe(145000);
      expect(qBudget?.rangeBounds?.max).toBe(160000);
      expect(qBudget?.options.length).toBeGreaterThanOrEqual(2);

      // Step 2: Format question offers strictly candidate bodies (Citadine & SUV, strictly NO Coupé)
      const qFormat = await client.getNextQuestion(
        [
          { role: 'user', content: 'Je suis un jeune étudiant et je cherche ma première voiture' },
          { role: 'assistant', content: 'Quel est votre budget ?' },
          { role: 'user', content: 'Budget 150 000 MAD' },
          { role: 'assistant', content: 'Quelle utilisation ?' },
          { role: 'user', content: 'Ville' },
        ],
        [clio, sandero],
      );
      expect(qFormat).not.toBeNull();
      expect(qFormat?.options.some((o) => o.label.includes('Citadine'))).toBe(true);
      expect(qFormat?.options.some((o) => o.label.includes('SUV'))).toBe(true);
      expect(qFormat?.options.some((o) => o.label.toLowerCase().includes('coupé'))).toBe(false);

      // Step 3: Priority question is an objective 8D question, not a hallucinated persona question
      const qPriority = await client.getNextQuestion(
        [
          { role: 'user', content: 'Je suis un jeune étudiant et je cherche ma première voiture' },
          { role: 'assistant', content: 'Quel est votre budget ?' },
          { role: 'user', content: 'Budget 150 000 MAD' },
          { role: 'assistant', content: 'Quelle utilisation ?' },
          { role: 'user', content: 'Ville' },
          { role: 'assistant', content: 'Quel format ?' },
          { role: 'user', content: 'Citadine' },
        ],
        [clio, sandero],
      );
      expect(qPriority).not.toBeNull();
      expect(qPriority?.question).not.toContain('étudiant');
    });

    it('adapts budget range and premium criteria for executive profile', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');
      const mbClassE = car({ id: 'mb-e', brand: 'Mercedes-Benz', model: 'Classe E', price: 680000, body_type: 'berline', transmission: 'automatique', engine_power_hp: 197 });
      const bmwX5 = car({ id: 'bmw-x5', brand: 'BMW', model: 'X5', price: 920000, body_type: 'suv', transmission: 'automatique', engine_power_hp: 286 });
      const daciaLogan = car({ id: 'dacia-logan', brand: 'Dacia', model: 'Logan', price: 140000, body_type: 'berline', engine_power_hp: 90 });

      // Step 1: Budget question adapts dynamically to recommended cars
      const qBudget = await client.getNextQuestion(
        [{ role: 'user', content: 'Je suis directeur général, je cherche un véhicule de standing' }],
        [mbClassE, bmwX5],
      );
      expect(qBudget).not.toBeNull();
      expect(qBudget?.question).toContain('budget');
      expect(qBudget?.rangeBounds).toBeDefined();
      expect(qBudget?.rangeBounds?.min).toBe(680000);
      expect(qBudget?.rangeBounds?.max).toBe(920000);
      expect(qBudget?.options.length).toBeGreaterThanOrEqual(2);

      // Step 2: Format question offers strictly candidate bodies (Berline & SUV, strictly NO Coupé)
      const qFormat = await client.getNextQuestion(
        [
          { role: 'user', content: 'Je suis directeur général' },
          { role: 'assistant', content: 'Quel est votre budget ?' },
          { role: 'user', content: 'Budget 800 000 MAD' },
          { role: 'assistant', content: 'Quelle utilisation ?' },
          { role: 'user', content: 'Mixte' },
        ],
        [mbClassE, bmwX5],
      );
      expect(qFormat).not.toBeNull();
      expect(qFormat?.options.some((o) => o.label.includes('Berline'))).toBe(true);
      expect(qFormat?.options.some((o) => o.label.includes('SUV'))).toBe(true);
      expect(qFormat?.options.some((o) => o.label.toLowerCase().includes('coupé'))).toBe(false);

      // Ranking: Premium executive brands are ranked on top, budget low-end brands are penalized
      const sorted = await client.applyAnswer(
        'Je suis directeur général',
        history('Je suis directeur général'),
        [daciaLogan, mbClassE, bmwX5],
      );
      expect(['Mercedes-Benz', 'BMW']).toContain(sorted[0].brand);
      expect(sorted[sorted.length - 1].brand).toBe('Dacia');
    });

    it('adapts safety and hybrid criteria for medical profile', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');
      const volvoXC60 = car({ id: 'volvo-xc60', brand: 'Volvo', model: 'XC60', price: 540000, body_type: 'suv', fuel_type: 'hybride', ncap_rating: '5★ (Euro NCAP 2023)' });
      const toyotaRav4 = car({ id: 'rav4', brand: 'Toyota', model: 'RAV4 Hybride', price: 420000, body_type: 'suv', fuel_type: 'hybride', ncap_rating: '5★ (Euro NCAP 2022)' });

      // Step 1: Budget question adapts dynamically to recommended cars
      const qBudget = await client.getNextQuestion(
        [{ role: 'user', content: 'Je suis médecin urgentiste' }],
        [volvoXC60, toyotaRav4],
      );
      expect(qBudget).not.toBeNull();
      expect(qBudget?.rangeBounds).toBeDefined();
      expect(qBudget?.rangeBounds?.min).toBe(420000);
      expect(qBudget?.rangeBounds?.max).toBe(540000);
      expect(qBudget?.options.length).toBeGreaterThanOrEqual(2);

      // As both cars are SUV and Hybrid, format/fuel questions are not asked when no diversity exists
      const qPriority = await client.getNextQuestion(
        [
          { role: 'user', content: 'Je suis médecin urgentiste' },
          { role: 'assistant', content: 'Quel est votre budget ?' },
          { role: 'user', content: 'Budget 500 000 MAD' },
          { role: 'assistant', content: 'Quelle utilisation ?' },
          { role: 'user', content: 'Mixte' },
        ],
        [volvoXC60, toyotaRav4],
      );
      if (qPriority) {
        expect(qPriority.question).not.toContain('soignant');
      }
    });

    it('adapts long-distance autonomy and diesel for commercial_commuter', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');
      const passat = car({ id: 'vw-passat', brand: 'Volkswagen', model: 'Passat', price: 340000, body_type: 'berline', fuel_type: 'diesel' });
      const octavia = car({ id: 'skoda-octavia', brand: 'Skoda', model: 'Octavia', price: 290000, body_type: 'berline', fuel_type: 'diesel' });

      // Step 1: Budget question adapts dynamically to recommended cars
      const qBudget = await client.getNextQuestion(
        [{ role: 'user', content: 'Je suis délégué commercial et je fais beaucoup de route' }],
        [passat, octavia],
      );
      expect(qBudget).not.toBeNull();
      expect(qBudget?.rangeBounds?.min).toBe(290000);
      expect(qBudget?.rangeBounds?.max).toBe(340000);
      expect(qBudget?.options.length).toBeGreaterThanOrEqual(2);
    });

    it('adapts family questions and priority options for family profile', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');
      const jogger = car({ id: 'jogger', brand: 'Dacia', model: 'Jogger', price: 210000, seats: 7, trunk_volume_l: 565, body_type: 'break' });
      const p5008 = car({ id: 'peugeot-5008', brand: 'Peugeot', model: '5008', price: 390000, seats: 7, trunk_volume_l: 780, body_type: 'suv' });

      // Step 1: Budget question for family adapts dynamically to recommended cars
      const qBudget = await client.getNextQuestion(
        [{ role: 'user', content: 'Je cherche une voiture pour ma grande famille' }],
        [jogger, p5008],
      );
      expect(qBudget).not.toBeNull();
      expect(qBudget?.rangeBounds?.min).toBe(210000);
      expect(qBudget?.rangeBounds?.max).toBe(390000);
      expect(qBudget?.rangeBounds?.label).toBe('Budget familial');
      expect(qBudget?.options.length).toBeGreaterThanOrEqual(2);

      // Step 2: Family space/luggage question
      const qSpace = await client.getNextQuestion(
        [
          { role: 'user', content: 'Je cherche une voiture familiale avec grand coffre' },
          { role: 'assistant', content: 'Quel est votre budget ?' },
          { role: 'user', content: 'Budget 300 000 MAD' },
          { role: 'assistant', content: 'Quelle utilisation ?' },
          { role: 'user', content: 'Mixte' },
        ],
        [jogger, p5008],
      );
      expect(qSpace).not.toBeNull();
      expect(qSpace?.options.map((o) => o.label)).toEqual(['Break', 'SUV', 'Pas de préférence']);
    });

    it('never displays suggestions that do not exist in candidate cars', () => {
      const thermalOnlyCars = [
        car({ id: '1', fuel_type: 'diesel', body_type: 'berline', is_4x4: false, seats: 5 }),
        car({ id: '2', fuel_type: 'essence', body_type: 'berline', is_4x4: false, seats: 5 }),
      ];

      // Fuel question: Diesel & Essence exist, Hybrid & Electric DO NOT
      const fuelOptions = alignQuestionOptions(
        'Which fuel type do you prefer (Diesel, Petrol, Hybrid, or Electric)?',
        [],
        'en',
        thermalOnlyCars
      );
      expect(fuelOptions.some((o) => o.value === 'diesel')).toBe(true);
      expect(fuelOptions.some((o) => o.value === 'essence')).toBe(true);
      expect(fuelOptions.some((o) => o.value === 'hybride')).toBe(false);
      expect(fuelOptions.some((o) => o.value === 'electrique')).toBe(false);

      // Drivetrain question: Only 2WD exists, 4x4 DOES NOT -> only 1 specific choice left -> returns []
      const awdOptions = alignQuestionOptions(
        'Do you need all-wheel drive (4x4 / AWD)?',
        [],
        'en',
        thermalOnlyCars
      );
      expect(awdOptions).toHaveLength(0);

      // Space question: Only 5 seats exist, 7 seats DOES NOT
      const spaceOptions = alignQuestionOptions(
        'De combien de place pour les bagages avez-vous besoin, en valises ?',
        [],
        'fr',
        thermalOnlyCars
      );
      expect(spaceOptions.some((o) => o.label.includes('7 places'))).toBe(false);
    });
  });

  describe('Identical car early completion & fix validation', () => {
    it('stops asking questions when remaining candidates are trims of the same car model', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('en');
      const stepway1 = car({
        id: 'stepway-1',
        brand: 'Dacia',
        model: 'Sandero Stepway',
        version: 'Expression',
        price: 195000,
        body_type: 'suv',
        fuel_type: 'essence',
        transmission: 'automatique',
        engine_power_hp: 90,
        trunk_volume_l: 328,
        ncap_rating: '3★',
      });
      const stepway2 = car({
        id: 'stepway-2',
        brand: 'Dacia',
        model: 'Sandero Stepway',
        version: 'Essential',
        price: 179000,
        body_type: 'suv',
        fuel_type: 'essence',
        transmission: 'automatique',
        engine_power_hp: 90,
        trunk_volume_l: 328,
        ncap_rating: '3★',
      });

      const question = await client.getNextQuestion([
        { role: 'user', content: 'I want an economical car' },
        { role: 'assistant', content: 'What is your maximum budget in MAD?' },
        { role: 'user', content: 'budget between 130000 and 210000 MAD' },
        { role: 'assistant', content: 'How will you mainly use the car: city driving, highways, or a mix of both?' },
        { role: 'user', content: 'Mostly city' },
      ], [stepway1, stepway2]);

      // Because both remaining cars are the exact same car model (Sandero Stepway)
      // with identical specs, qualification must complete immediately without asking about luggage or priorities!
      expect(question).toBeNull();
    });

    it('recognizes "baghi tonobila sghira" as citadine intent with compact budget bounds', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('darija');

      await expect(client.detectRecommendationIntent('baghi tonobila sghira')).resolves.toBe(true);

      const qBudget = await client.getNextQuestion([
        { role: 'user', content: 'baghi tonobila sghira' },
      ], []);

      expect(qBudget).not.toBeNull();
      expect(qBudget?.rangeBounds).toBeDefined();
      expect(qBudget?.rangeBounds?.min).toBe(80000);
      expect(qBudget?.rangeBounds?.max).toBe(260000);
      expect(qBudget?.rangeBounds?.label).toContain('سيارة صغيرة');
    });

    it('does not repeat suitcase question after user selects suitcase range', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');

      const car1 = car({ id: 'c1', trunk_volume_l: 300, body_type: 'berline', fuel_type: 'diesel' });
      const car2 = car({ id: 'c2', trunk_volume_l: 600, body_type: 'suv', fuel_type: 'essence' });

      const question = await client.getNextQuestion([
        { role: 'user', content: 'Je cherche une voiture' },
        { role: 'assistant', content: 'Quel est votre budget maximum en MAD ?' },
        { role: 'user', content: 'Budget entre 100 000 et 300 000 MAD' },
        { role: 'assistant', content: 'Vous roulerez surtout en ville, sur autoroute ou dans les deux ?' },
        { role: 'user', content: 'Ville' },
        { role: 'assistant', content: 'De combien de place pour les bagages avez-vous besoin, en valises ?' },
        { role: 'user', content: 'Capacité en valises entre 1 et 4' },
      ], [car1, car2]);

      expect(question?.question ?? '').not.toContain('valises');
      expect(question?.question ?? '').not.toContain('bagages');
    });

    it('does not repeat Arabic family priority question after option selection', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('ar');

      const car1 = car({ id: 'c1', body_type: 'suv', seats: 7 });
      const car2 = car({ id: 'c2', body_type: 'monospace', seats: 7 });

      const question = await client.getNextQuestion([
        { role: 'user', content: 'أبحث عن سيارة عائلية' },
        { role: 'assistant', content: 'ما هي ميزانيتك القصوى بالدرهم؟' },
        { role: 'user', content: 'الميزانية بين 150000 و 400000 درهم' },
        { role: 'assistant', content: 'كيف ستستعمل السيارة غالباً: داخل المدينة، في الطريق السيار، أم الاثنين؟' },
        { role: 'user', content: 'داخل المدينة' },
        { role: 'assistant', content: 'ما هي أولويتكم في السفر والتنقلات مع العائلة؟' },
        { role: 'user', content: 'صندوق أمتعة ضخم ومقاعد قابلة للطي' },
      ], [car1, car2]);

      expect(question?.question ?? '').not.toContain('أولويتكم');
    });

    it('deduplicates vehicle cards so identical models do not duplicate in recommendations', () => {
      const q8_1 = car({ id: 'q8-1', brand: 'Audi', model: 'Q8 50 TDI EXCLUSIVE' });
      const gla = car({ id: 'gla', brand: 'Mercedes-Benz', model: 'GLA 220 d' });
      const q8_2 = car({ id: 'q8-2', brand: 'Audi', model: 'Q8 50 TDI EXCLUSIVE' });
      const x5 = car({ id: 'x5', brand: 'BMW', model: 'X5' });

      const uniqueTop3 = getUniqueModelCars([q8_1, gla, q8_2, x5], 3);
      expect(uniqueTop3).toHaveLength(3);
      expect(uniqueTop3.map((c) => c.model)).toEqual(['Q8 50 TDI EXCLUSIVE', 'GLA 220 d', 'X5']);

      const deduplicated = deduplicateCars([q8_1, gla, q8_2, x5]);
      expect(deduplicated[0].model).toBe('Q8 50 TDI EXCLUSIVE');
      expect(deduplicated[1].model).toBe('GLA 220 d');
      expect(deduplicated[2].model).toBe('X5');
    });

    it('caps executive budget envelope below hypercar figures and filters out supercars', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');

      const valhalla = car({ id: 'valhalla', brand: 'Aston Martin', model: 'Valhalla', price: 14949300 });
      const ferrari = car({ id: 'f12', brand: 'Ferrari', model: '12Cilindri', price: 5580500 });
      const eClass = car({ id: 'e-class', brand: 'Mercedes-Benz', model: 'Classe E', price: 750000 });
      const bmw5 = car({ id: 'bmw-5', brand: 'BMW', model: 'Série 5', price: 820000 });

      const qBudget = await client.getNextQuestion([
        { role: 'user', content: 'En tant que dirigeant, je cherche un véhicule statutaire' },
      ], [valhalla, ferrari, eClass, bmw5]);

      expect(qBudget?.rangeBounds).toBeDefined();
      // Should cap realistically (<= 2.1M MAD) instead of reaching 15M or 29M MAD
      expect(qBudget?.rangeBounds?.max).toBeLessThanOrEqual(2100000);
      expect(qBudget?.rangeBounds?.max).toBeGreaterThanOrEqual(820000);
    });

    it('detects lawyer, attorney, notary and related professions under executive profile', () => {
      expect(detectClientProfile('I am a lawyer looking for a car')).toBe('executive');
      expect(detectClientProfile('Je suis avocat')).toBe('executive');
      expect(detectClientProfile('أنا محامٍ')).toBe('executive');
      expect(detectClientProfile('notaire')).toBe('executive');
    });

    it('medical profile does not repeat format question when option 3 (hybride) is selected', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');

      const car1 = car({ id: 'c1', body_type: 'suv', fuel_type: 'hybride' });
      const car2 = car({ id: 'c2', body_type: 'berline', fuel_type: 'diesel' });

      const question = await client.getNextQuestion([
        { role: 'user', content: 'Je suis médecin' },
        { role: 'assistant', content: 'Pour vos déplacements et visites : quel est votre budget maximum en MAD ?' },
        { role: 'user', content: 'Budget entre 200 000 et 400 000 MAD' },
        { role: 'assistant', content: 'Pour vos déplacements et visites : vous roulerez surtout en ville, sur autoroute ou dans les deux ?' },
        { role: 'user', content: 'Ville' },
        { role: 'assistant', content: 'En tant que soignant, quel format répond le mieux à vos trajets entre cabinet, clinique et gardes ?' },
        { role: 'user', content: 'Hybride silencieuse & économique (Ville & clinique)' },
      ], [car1, car2]);

      expect(question?.question ?? '').not.toContain('quel format répond le mieux');
    });

    it('executive profile does not repeat format question when coupe or Darija كوبي is selected', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');

      const car1 = car({ id: 'c1', body_type: 'coupe', price: 600000 });
      const car2 = car({ id: 'c2', body_type: 'berline', price: 700000 });

      const questionFr = await client.getNextQuestion([
        { role: 'user', content: 'Je suis directeur' },
        { role: 'assistant', content: 'Quel est votre budget maximum en MAD ?' },
        { role: 'user', content: 'Budget entre 400 000 et 800 000 MAD' },
        { role: 'assistant', content: 'Vous roulerez surtout en ville, sur autoroute ou dans les deux ?' },
        { role: 'user', content: 'Mixte' },
        { role: 'assistant', content: 'En tant que dirigeant, quel style de véhicule correspond le mieux à votre standing ?' },
        { role: 'user', content: 'Coupé 4 portes ou Sportback racé' },
      ], [car1, car2]);

      expect(questionFr?.question ?? '').not.toContain('quel style de véhicule');

      client.setLanguage('darija');
      const questionDarija = await client.getNextQuestion([
        { role: 'user', content: 'Ana mdir' },
        { role: 'assistant', content: 'شحال هي الميزانية القصوى ديالك بالدرهم؟' },
        { role: 'user', content: 'بين 400000 و 800000 درهم' },
        { role: 'assistant', content: 'واش غادي تسوق فالمدينة، فالطريق السيار، ولا بجوج؟' },
        { role: 'user', content: 'بجوج' },
        { role: 'assistant', content: 'كمدير، شنو هو شكل الطوموبيل اللي كيعبر أحسن على المكانة المهنية ديالك؟' },
        { role: 'user', content: 'كوبي 4 بيبان رياضي وأنيق' },
      ], [car1, car2]);

      expect(questionDarija?.question ?? '').not.toContain('شكل الطوموبيل');
    });

    it('commercial commuter does not repeat requirement question when SAV/fiabilité option is selected', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');

      const car1 = car({ id: 'c1', body_type: 'berline', fuel_type: 'diesel' });
      const car2 = car({ id: 'c2', body_type: 'break', fuel_type: 'diesel' });

      const question = await client.getNextQuestion([
        { role: 'user', content: 'Je suis commercial, je roule 40000 km par an' },
        { role: 'assistant', content: 'Pour vos tournées professionnelles et déplacements fréquents : quel est votre budget maximum en MAD ?' },
        { role: 'user', content: 'Budget entre 150 000 et 300 000 MAD' },
        { role: 'assistant', content: 'Pour vos tournées professionnelles : vous roulerez surtout en ville, sur autoroute ou dans les deux ?' },
        { role: 'user', content: 'Autoroute' },
        { role: 'assistant', content: 'Pour vos tournées professionnelles, sur quel terrain roulez-vous le plus ?' },
        { role: 'user', content: 'Grands trajets autoroutiers inter-villes (> 30 000 km/an)' },
        { role: 'assistant', content: 'Pour vos tournées professionnelles, quel critère est primordial ?' },
        { role: 'user', content: 'Fiabilité kilométrique & Réseau SAV partout au Maroc' },
      ], [car1, car2]);

      expect(question?.question ?? '').not.toContain('quel critère est primordial');
    });

    it('student profile does not repeat priority question when modern connectivity option is selected', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');

      const car1 = car({ id: 'c1', body_type: 'citadine', price: 120000 });
      const car2 = car({ id: 'c2', body_type: 'citadine', price: 140000 });

      const question = await client.getNextQuestion([
        { role: 'user', content: 'Je suis étudiant, jeune conducteur' },
        { role: 'assistant', content: 'Pour votre première voiture ou vos trajets du quotidien : quel est votre budget maximum en MAD ?' },
        { role: 'user', content: 'Budget entre 80 000 et 160 000 MAD' },
        { role: 'assistant', content: 'Vous roulerez surtout en ville, sur autoroute ou dans les deux ?' },
        { role: 'user', content: 'Ville' },
        { role: 'assistant', content: 'Pour votre première voiture ou vos études, quel style recherchez-vous en priorité ?' },
        { role: 'user', content: 'Citadine compacte & facile à garer' },
        { role: 'assistant', content: 'Pour vos trajets quotidiens, quel critère est le plus important pour vous ?' },
        { role: 'user', content: 'Connectivité moderne (Écran tactile & CarPlay)' },
      ], [car1, car2]);

      expect(question?.question ?? '').not.toContain('quel critère est le plus important');
    });

    it('fallback fuel and transmission questions do not loop when answered with non-keywords', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');

      const car1 = car({ id: 'c1', fuel_type: 'diesel', transmission: 'automatique' });
      const car2 = car({ id: 'c2', fuel_type: 'essence', transmission: 'manuelle' });

      const questionFuel = await client.getNextQuestion([
        { role: 'user', content: 'Je cherche une voiture' },
        { role: 'assistant', content: 'Quel est votre budget maximum en MAD ?' },
        { role: 'user', content: 'Budget entre 100 000 et 200 000 MAD' },
        { role: 'assistant', content: 'Vous roulerez surtout en ville, sur autoroute ou dans les deux ?' },
        { role: 'user', content: 'Mixte' },
        { role: 'assistant', content: 'Quel carburant vous convient le mieux ?' },
        { role: 'user', content: 'Pas de préférence spéciale pour le moteur' },
      ], [car1, car2]);

      expect(questionFuel?.question ?? '').not.toContain('Quel carburant');

      const questionTransmission = await client.getNextQuestion([
        { role: 'user', content: 'Je cherche une voiture' },
        { role: 'assistant', content: 'Quel est votre budget maximum en MAD ?' },
        { role: 'user', content: 'Budget entre 100 000 et 200 000 MAD' },
        { role: 'assistant', content: 'Vous roulerez surtout en ville, sur autoroute ou dans les deux ?' },
        { role: 'user', content: 'Mixte' },
        { role: 'assistant', content: 'Préférez-vous une boîte automatique ou manuelle ?' },
        { role: 'user', content: 'Peu importe la boîte' },
      ], [car1, car2]);

      expect(questionTransmission?.question ?? '').not.toContain('boîte automatique ou manuelle');
    });

    it('does not loop on running costs question when user selects Arabic options (reproducing user scenario)', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('ar');

      const carHybrid = car({ id: 'c1', fuel_type: 'hybride', engine_power_hp: 110, price: 220000 });
      const carDiesel = car({ id: 'c2', fuel_type: 'diesel', engine_power_hp: 100, price: 210000 });
      const carPetrol = car({ id: 'c3', fuel_type: 'essence', engine_power_hp: 150, price: 230000 });

      // Reproducing the exact flow from the user screenshot:
      // 1. User answered "تكاليف تشغيل أقل" to performance question
      // 2. Assistant asked "هل تفضل استهلاكاً وتكاليف تشغيل أقل؟"
      // 3. User clicked "توفير وتكاليف أقل"
      // 4. Assistant asked "هل المحرك الهجين أو الكهربائي أولوية بالنسبة لك؟"
      // 5. User clicked "هجين أو كهربائي"
      const question = await client.getNextQuestion([
        { role: 'user', content: 'أبحث عن سيارة' },
        { role: 'assistant', content: 'ما هي ميزانيتك القصوى بالدرهم؟' },
        { role: 'user', content: 'بين 180000 و 250000 درهم' },
        { role: 'assistant', content: 'كيف ستستعمل السيارة غالباً: داخل المدينة، في الطريق السيار، أم الاثنين؟' },
        { role: 'user', content: 'داخل المدينة' },
        { role: 'assistant', content: 'هل تفضل القوة والتسارع على انخفاض تكاليف التشغيل؟' },
        { role: 'user', content: 'تكاليف تشغيل أقل' },
        { role: 'assistant', content: 'هل تفضل استهلاكاً وتكاليف تشغيل أقل؟' },
        { role: 'user', content: 'توفير وتكاليف أقل' },
        { role: 'assistant', content: 'هل المحرك الهجين أو الكهربائي أولوية بالنسبة لك؟' },
        { role: 'user', content: 'هجين أو كهربائي' },
      ], [carHybrid, carDiesel, carPetrol]);

      // The bot must NEVER re-ask the cout_reel question ("هل تفضل استهلاكاً وتكاليف تشغيل أقل؟")!
      expect(question?.question ?? '').not.toContain('استهلاكاً وتكاليف تشغيل');
      expect(question?.question ?? '').not.toContain('تكاليف تشغيل أقل');
    });

    it('marks dimension covered when user answers with No preference in Arabic (لا أفضلية)', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('ar');

      const carHybrid = car({ id: 'c1', fuel_type: 'hybride', ncap_rating: '5★', price: 220000 });
      const carDiesel = car({ id: 'c2', fuel_type: 'diesel', ncap_rating: '4★', price: 210000 });

      const question = await client.getNextQuestion([
        { role: 'user', content: 'أبحث عن سيارة' },
        { role: 'assistant', content: 'ما هي ميزانيتك القصوى بالدرهم؟' },
        { role: 'user', content: '200000 درهم' },
        { role: 'assistant', content: 'كيف ستستعمل السيارة غالباً: داخل المدينة، في الطريق السيار، أم الاثنين؟' },
        { role: 'user', content: 'داخل المدينة' },
        { role: 'assistant', content: 'هل تفضل استهلاكاً وتكاليف تشغيل أقل؟' },
        { role: 'user', content: 'لا أفضلية' },
      ], [carHybrid, carDiesel]);

      expect(question?.question ?? '').not.toContain('استهلاكاً وتكاليف تشغيل');
    });

    it('applies Arabic running costs, eco-combo, and No preference answers properly in applyAnswer', async () => {
      const client = new FastApiRecommendationClient();

      const carHybrid = car({ id: 'c1', fuel_type: 'hybride', engine_power_hp: 110, price: 220000 });
      const carGas = car({ id: 'c2', fuel_type: 'essence', engine_power_hp: 200, price: 240000 });

      const filteredEco = await client.applyAnswer('توفير وتكاليف أقل', [], [carHybrid, carGas]);
      expect(filteredEco.some((c) => c.id === 'c1')).toBe(true);

      const filteredHybrid = await client.applyAnswer('هجين أو كهربائي', [], [carHybrid, carGas]);
      expect(filteredHybrid).toHaveLength(1);
      expect(filteredHybrid[0].fuel_type).toBe('hybride');

      const keptNoPref = await client.applyAnswer('لا أفضلية', [], [carHybrid, carGas]);
      expect(keptNoPref).toHaveLength(2);
    });

    it('correctly extracts Arabic budgets like "200000 درهم" and "200 ألف"', () => {
      expect(extractMaximumBudget('200000 درهم')).toBe(200000);
      expect(extractMaximumBudget('ميزانيتي 200 ألف')).toBe(200000);
      expect(extractMaximumBudget('150000 درهم')).toBe(150000);
    });

    it('detects recommendation intent for all Arabic & Darija keywords and budgets', async () => {
      const client = new FastApiRecommendationClient();
      await expect(client.detectRecommendationIntent('بغيت نشري طوموبيل')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('أريد سيارة عائلية')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('أبحث عن سيارة')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('سيارة 200000 درهم')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('عندي 200000')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('طوموبيل 180000 dh')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('بغيت dacia')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('باغي toyota')).resolves.toBe(true);
    });

    it('correctly filters Arabic and non-ASCII body preferences in applyAnswer', async () => {
      const client = new FastApiRecommendationClient();
      const carSuv = car({ id: 'suv-1', body_type: 'suv' });
      const carSedan = car({ id: 'sedan-1', body_type: 'berline' });
      const carCity = car({ id: 'city-1', body_type: 'citadine' });
      const carPickup = car({ id: 'pickup-1', body_type: 'pick_up' });
      const carCoupe = car({ id: 'coupe-1', body_type: 'coupe' });

      const pool = [carSuv, carSedan, carCity, carPickup, carCoupe];

      const resSuv = await client.applyAnswer('دفع رباعي', [], pool);
      expect(resSuv).toHaveLength(1);
      expect(resSuv[0].id).toBe('suv-1');

      const resSedan = await client.applyAnswer('سيدان', [], pool);
      expect(resSedan).toHaveLength(1);
      expect(resSedan[0].id).toBe('sedan-1');

      const resCity = await client.applyAnswer('سيتادين', [], pool);
      expect(resCity).toHaveLength(1);
      expect(resCity[0].id).toBe('city-1');

      const resPickup = await client.applyAnswer('بيك أب', [], pool);
      expect(resPickup).toHaveLength(1);
      expect(resPickup[0].id).toBe('pickup-1');

      const resCoupe = await client.applyAnswer('coupé', [], pool);
      expect(resCoupe).toHaveLength(1);
      expect(resCoupe[0].id).toBe('coupe-1');

      const resCoupeAr = await client.applyAnswer('كوبيه', [], pool);
      expect(resCoupeAr).toHaveLength(1);
      expect(resCoupeAr[0].id).toBe('coupe-1');
    });

    it('correctly filters Arabic and accented fuel & transmission in applyAnswer', async () => {
      const client = new FastApiRecommendationClient();
      const carDiesel = car({ id: 'diesel-1', fuel_type: 'diesel' });
      const carEssence = car({ id: 'essence-1', fuel_type: 'essence' });
      const carEv = car({ id: 'ev-1', fuel_type: 'electrique' });
      const carHybrid = car({ id: 'hyb-1', fuel_type: 'hybride' });

      const fuelPool = [carDiesel, carEssence, carEv, carHybrid];

      const resMazout = await client.applyAnswer('مازوط', [], fuelPool);
      expect(resMazout).toHaveLength(1);
      expect(resMazout[0].fuel_type).toBe('diesel');

      const resEssence = await client.applyAnswer('بنزين', [], fuelPool);
      expect(resEssence).toHaveLength(1);
      expect(resEssence[0].fuel_type).toBe('essence');

      const resEv = await client.applyAnswer('كهربائي', [], fuelPool);
      expect(resEv).toHaveLength(1);
      expect(resEv[0].fuel_type).toBe('electrique');

      const resElecFr = await client.applyAnswer('électrique', [], fuelPool);
      expect(resElecFr).toHaveLength(1);
      expect(resElecFr[0].fuel_type).toBe('electrique');

      const carAuto = car({ id: 'auto-1', transmission: 'automatique' });
      const carManual = car({ id: 'man-1', transmission: 'manuelle' });
      const transPool = [carAuto, carManual];

      const resAuto = await client.applyAnswer('أوتوماتيك', [], transPool);
      expect(resAuto).toHaveLength(1);
      expect(resAuto[0].transmission).toBe('automatique');

      const resManual = await client.applyAnswer('يدوي', [], transPool);
      expect(resManual).toHaveLength(1);
      expect(resManual[0].transmission).toBe('manuelle');
    });

    it('does not repeat usage or body question when answered in Arabic or accented French', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('ar');

      const car1 = car({ id: 'c1', fuel_type: 'hybride', body_type: 'suv', transmission: 'automatique', is_4x4: false });
      const car2 = car({ id: 'c2', fuel_type: 'diesel', body_type: 'berline', transmission: 'manuelle', is_4x4: true });

      const q1 = await client.getNextQuestion([
        { role: 'user', content: 'أبحث عن سيارة' },
        { role: 'assistant', content: 'ما هي ميزانيتك القصوى بالدرهم؟' },
        { role: 'user', content: '300000 درهم' },
        { role: 'assistant', content: 'أين تقطع معظم مسافاتك؟' },
        { role: 'user', content: 'مدينة' },
      ], [car1, car2]);

      expect(q1?.question ?? '').not.toContain('أين تقطع');
    });

    it('recognizes standalone brand and model queries as recommendation intent', async () => {
      const client = new FastApiRecommendationClient();
      await expect(client.detectRecommendationIntent('dacia ?')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('dacia')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('Dacia')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('duster ?')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('clio ?')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('golf ?')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('tucson ?')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('peugeot 208')).resolves.toBe(true);
    });

    it('filters out informative inquiries from recommendation intent', async () => {
      const client = new FastApiRecommendationClient();
      await expect(client.detectRecommendationIntent('avis sur dacia')).resolves.toBe(false);
      await expect(client.detectRecommendationIntent('prix de dacia sandero')).resolves.toBe(false);
      await expect(client.detectRecommendationIntent('informations sur la marque dacia')).resolves.toBe(false);
      await expect(client.detectRecommendationIntent('que pensez-vous de dacia')).resolves.toBe(false);
    });

    it('produces brand-tailored budget bounds for Dacia instead of global 600k', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');

      const daciaCars = [
        car({ id: 'd-1', brand: 'Dacia', model: 'Sandero', price: 132000 }),
        car({ id: 'd-2', brand: 'Dacia', model: 'Logan', price: 139000 }),
        car({ id: 'd-3', brand: 'Dacia', model: 'Sandero Stepway', price: 158000 }),
        car({ id: 'd-4', brand: 'Dacia', model: 'Jogger', price: 195000 }),
        car({ id: 'd-5', brand: 'Dacia', model: 'Duster', price: 232000 }),
        car({ id: 'd-6', brand: 'Dacia', model: 'Bigster', price: 299000 }),
      ];

      const question = await client.getNextQuestion(
        [{ role: 'user', content: 'dacia ?' }],
        daciaCars,
      );

      expect(question).not.toBeNull();
      expect(question?.question).toContain('budget');
      expect(question?.rangeBounds).toBeDefined();
      expect(question?.rangeBounds?.min).toBe(130000);
      expect(question?.rangeBounds?.max).toBe(300000);
      expect(question?.rangeBounds?.max).toBeLessThanOrEqual(310000);
      expect(question?.options?.length).toBeGreaterThanOrEqual(2);
      // Ensure dynamic budget options reflect Dacia range
      expect(question?.options?.[0].label).toContain('MAD');
    });

    it('applies brand and model filters on direct model query like "duster ?"', async () => {
      const client = new FastApiRecommendationClient();
      mockGetVehicles.mockResolvedValue({
        items: [
          car({ id: 'd-sandero', brand: 'Dacia', model: 'Sandero', price: 132000 }),
          car({ id: 'd-duster', brand: 'Dacia', model: 'Duster', price: 232000 }),
        ],
        pages: 1,
      });

      const result = await client.applyAnswer('duster ?', [{ role: 'user', content: 'duster ?' }], []);
      expect(mockGetVehicles).toHaveBeenCalledWith(expect.objectContaining({ brand: 'Dacia' }));
      expect(result).toHaveLength(1);
      expect(result[0].model).toBe('Duster');
    });

    it('skips asking budget when user supplies bare number budget like "une voiture 200000"', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');
      const sampleCars = [
        car({ id: 'c1', brand: 'Renault', model: 'Clio', price: 195000, body_type: 'citadine', fuel_type: 'essence' }),
        car({ id: 'c2', brand: 'Dacia', model: 'Duster', price: 200000, body_type: 'suv', fuel_type: 'diesel' }),
      ];

      const nextQ = await client.getNextQuestion(
        [{ role: 'user', content: 'une voiture 200000' }],
        sampleCars,
      );
      expect(nextQ).not.toBeNull();
      // Should NOT ask for budget since 200000 was already specified
      expect(nextQ?.question).not.toMatch(/budget|prix|price|ميزاني/i);
    });

    it('does not falsely extract Spanish brand "Seat" from car seat phrases', () => {
      expect(extractBrandPreference('Ergonomic seat comfort (after long shifts)')).toBeNull();
      expect(extractBrandPreference('seat comfort & motorway soundproofing')).toBeNull();
      expect(extractBrandPreference('leather seats with heating')).toBeNull();
      expect(extractBrandPreference('car with 7 seats')).toBeNull();
      // But actual car brand queries should still match
      const brandSeat = extractBrandPreference('I want a Seat Leon');
      expect(brandSeat).not.toBeNull();
      expect(brandSeat?.name).toBe('Seat');
    });

    it('preserves candidate cars when answering comfort priorities in healthcare profile', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('en');
      const hybridCars = [
        car({ id: 'h1', brand: 'Toyota', model: 'Corolla Cross', fuel_type: 'hybride', trunk_volume_l: 430 }),
        car({ id: 'h2', brand: 'Renault', model: 'Austral', fuel_type: 'hybride', trunk_volume_l: 500 }),
      ];

      const history: ChatTurn[] = [
        { role: 'user', content: 'I am a doctor looking for a car' },
        { role: 'assistant', content: 'Where do you drive most?' },
        { role: 'user', content: 'Mostly highway' },
        { role: 'assistant', content: 'How much luggage space?' },
        { role: 'user', content: 'Suitcase capacity between 4 and 9' },
        { role: 'assistant', content: 'What vehicle style?' },
        { role: 'user', content: 'hybride' },
        { role: 'assistant', content: 'What is your core requirement?' },
        { role: 'user', content: 'Ergonomic seat comfort (after long shifts)' },
      ];

      const result = await client.applyAnswer(
        'Ergonomic seat comfort (after long shifts)',
        history,
        hybridCars,
      );

      expect(result.length).toBeGreaterThan(0);
      expect(result.every((c) => c.fuel_type === 'hybride')).toBe(true);
    });

    it('correctly identifies informative queries and does not treat them as recommendation intent', async () => {
      const client = new FastApiRecommendationClient();
      expect(informativeRequestPattern.test('je veux des informations sur dacia')).toBe(true);
      expect(informativeRequestPattern.test('donne-moi des infos sur la clio')).toBe(true);
      expect(informativeRequestPattern.test('informations sur le duster')).toBe(true);
      expect(informativeRequestPattern.test('prix de dacia sandero')).toBe(true);
      expect(informativeRequestPattern.test('que pensez-vous de dacia')).toBe(true);
      expect(informativeRequestPattern.test('معلومات عن داسيا')).toBe(true);
      expect(informativeRequestPattern.test('بغيت معلومات على كليو')).toBe(true);

      // And detectRecommendationIntent returns false
      await expect(client.detectRecommendationIntent('je veux des informations sur dacia')).resolves.toBe(false);
      await expect(client.detectRecommendationIntent('donne-moi des infos sur la clio')).resolves.toBe(false);
      await expect(client.detectRecommendationIntent('que pensez-vous de dacia')).resolves.toBe(false);
    });

    it('extracts budget from phrases like "une voiture 200000dhs" and advances past budget question', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');
      expect(extractMaximumBudget('une voiture 200000dhs')).toBe(200000);
      expect(extractMaximumBudget('a car 200000dhs')).toBe(200000);

      // detectRecommendationIntent must return true for attached currencies and simple car buying requests
      await expect(client.detectRecommendationIntent('a car 200000dhs')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('une voiture 200000dhs')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('a car')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('une voiture')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('suv 250000')).resolves.toBe(true);

      const sampleCars = [
        car({ id: 'c1', brand: 'Renault', model: 'Clio', price: 195000, body_type: 'citadine' }),
        car({ id: 'c2', brand: 'Dacia', model: 'Duster', price: 200000, body_type: 'suv' }),
      ];

      const question = await client.getNextQuestion(
        [{ role: 'user', content: 'une voiture 200000dhs' }],
        sampleCars,
      );
      expect(question).not.toBeNull();
      // Should ask for usage, fuel, body or transmission, NOT budget
      expect(question?.question).not.toMatch(/budget|prix|price|ميزاني/i);
    });

    it('detects single-criterion responses as recommendation intent and extracts suggestions for fuel questions', async () => {
      const client = new FastApiRecommendationClient();
      const mockClient = new MockRecommendationClient([]);

      // Test isCriterionPreference
      expect(isCriterionPreference('diesel')).toBe(true);
      expect(isCriterionPreference('Diesel')).toBe(true);
      expect(isCriterionPreference('essence')).toBe(true);
      expect(isCriterionPreference('Petrol')).toBe(true);
      expect(isCriterionPreference('hybride')).toBe(true);
      expect(isCriterionPreference('Hybrid')).toBe(true);
      expect(isCriterionPreference('automatique')).toBe(true);
      expect(isCriterionPreference('automatic')).toBe(true);
      expect(isCriterionPreference('SUV')).toBe(true);
      expect(isCriterionPreference('berline')).toBe(true);
      expect(isCriterionPreference('citadine')).toBe(true);
      expect(isCriterionPreference('bonjour')).toBe(false);

      // Both FastApiRecommendationClient and MockRecommendationClient detect intent
      await expect(client.detectRecommendationIntent('diesel')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('Diesel')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('Petrol')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('Automatic')).resolves.toBe(true);
      await expect(client.detectRecommendationIntent('SUV')).resolves.toBe(true);
      await expect(mockClient.detectRecommendationIntent('Diesel')).resolves.toBe(true);

      // Verify alignQuestionOptions extracts suggestions for "Which fuel type do you prefer for this vehicle (Diesel, Petrol, or Hybrid)?"
      const enOptions = alignQuestionOptions(
        'Which fuel type do you prefer for this vehicle (Diesel, Petrol, or Hybrid)?',
        [],
        'en'
      );
      expect(enOptions).toHaveLength(4);
      expect(enOptions.map((o) => o.label)).toEqual(['Diesel', 'Petrol', 'Hybrid', '100% Electric']);
      expect(enOptions.map((o) => o.value)).toEqual(['diesel', 'essence', 'hybride', 'electrique']);

      // French equivalent
      const frOptions = alignQuestionOptions(
        'Quelle motorisation préférez-vous pour ce véhicule (Diesel, Essence ou Hybride) ?',
        [],
        'fr'
      );
      expect(frOptions.map((o) => o.label)).toEqual(['Diesel', 'Essence', 'Hybride', '100% Électrique']);

      // Darija equivalent
      const darijaOptions = alignQuestionOptions(
        'شنو نوع الكاربورون اللي كتفضل (مازوط، ليصانص، إيبريد)؟',
        [],
        'darija'
      );
      expect(darijaOptions.map((o) => o.label)).toEqual(['مازوط', 'ليصانص', 'إيبريد', 'كهربائي 100%']);

      // Body style questions
      const bodyOptions = alignQuestionOptions(
        'With a budget of 200 000 DH, what body type are you looking for (SUV, hatchback/city car, sedan)?',
        [],
        'en'
      );
      expect(bodyOptions.length).toBeGreaterThanOrEqual(3);
      expect(bodyOptions.some((o) => o.label === 'SUV')).toBe(true);

      // Generic parenthesized choices fallback
      const customParen = alignQuestionOptions(
        'Which color tone do you like (Black, White, or Metallic Grey)?',
        [],
        'en'
      );
      expect(customParen.map((o) => o.label)).toEqual(['Black', 'White', 'Metallic Grey']);
      // 8D Dimensions suggestion chips verification
      // 1. Dimension Espace (Suitcases / trunk)
      const spaceOptions = alignQuestionOptions(
        'De combien de place pour les bagages avez-vous besoin, en valises ?',
        [],
        'fr'
      );
      expect(spaceOptions.map((o) => o.label)).toEqual(['Grand coffre (3-4 valises)', 'Coffre géant (5+ valises / 7 places)', 'Coffre standard']);

      // 2. Dimension Praticité urbaine (Format compact)
      const urbanOptions = alignQuestionOptions(
        'Pour la ville, préférez-vous un format compact facile à garer ?',
        [],
        'fr'
      );
      expect(urbanOptions.map((o) => o.label)).toEqual(['Format compact (facile à garer)', 'Plus d’espace intérieur', 'Pas de préférence']);

      // 3. Dimension Écologie (Hybride ou Électrique)
      const ecoOptions = alignQuestionOptions(
        'La motorisation hybride ou électrique propre est-elle une priorité pour vous ?',
        [],
        'fr'
      );
      expect(ecoOptions.map((o) => o.label)).toEqual(['Hybride ou Électrique propre', 'Thermique très économe', 'Pas de préférence']);

      // 4. Dimension Sécurité (NCAP)
      const safetyOptions = alignQuestionOptions(
        'Quelle importance accordez-vous à la sécurité certifiée et à une note Euro NCAP maximale (5★) ?',
        [],
        'fr'
      );
      expect(safetyOptions.map((o) => o.label)).toEqual(['Note NCAP maximale (5★)', 'Bonne sécurité (4★+)', 'Pas de préférence']);

      // 5. Dimension Motricité (4x4 / AWD)
      const awdOptions = alignQuestionOptions(
        'Avez-vous besoin d’une transmission 4x4 / intégrale (AWD) ?',
        [],
        'fr'
      );
      expect(awdOptions.map((o) => o.label)).toEqual(['4x4 / Intégrale (AWD)', '2 roues motrices (Standard)', 'Pas de préférence']);

      // 6. Dimension Performance (Puissance & reprises)
      const perfOptions = alignQuestionOptions(
        'Privilégiez-vous la puissance moteur et les reprises dynamiques sur autoroute ?',
        [],
        'fr'
      );
      expect(perfOptions.map((o) => o.label)).toEqual(['Priorité puissance & reprises', 'Priorité économie de carburant', 'Compromis équilibré', 'Pas de préférence']);

      const perfOptionsEn = alignQuestionOptions(
        'Do you prioritize engine power and highway responsiveness?',
        [],
        'en'
      );
      expect(perfOptionsEn.map((o) => o.label)).toEqual(['Power & performance first', 'Fuel economy first', 'Balanced compromise', 'No preference']);

      // Verify isCriterionPreference on 8D chips
      expect(isCriterionPreference('5★')).toBe(true);
      expect(isCriterionPreference('Note NCAP maximale')).toBe(true);
      expect(isCriterionPreference('4x4 / AWD')).toBe(true);
      expect(isCriterionPreference('Yes, 4x4 / AWD')).toBe(true);
      expect(isCriterionPreference('Standard (2WD)')).toBe(true);
      expect(isCriterionPreference('Compact (easy to park)')).toBe(true);
      expect(isCriterionPreference('Format compact (facile à garer)')).toBe(true);
      expect(isCriterionPreference('Puissance & reprises')).toBe(true);
      expect(isCriterionPreference('Économie & coûts réduits')).toBe(true);
      expect(isCriterionPreference('Grand coffre (3-4 valises)')).toBe(true);
      expect(isCriterionPreference('Pas de préférence')).toBe(true);
      expect(isCriterionPreference('No preference')).toBe(true);
      expect(isCriterionPreference('لا أفضلية')).toBe(true);
      expect(isCriterionPreference('ما عنديش تفضيل')).toBe(true);
    });

    it('strictly adheres to 8 Dimensions in dynamicQuestion flow and never asks isolated transmission questions', async () => {
      const client = new FastApiRecommendationClient();
      client.setLanguage('fr');

      // Candidate cars with diverse 8D attributes
      const cars = [
        car({ id: 'c1', price: 180000, trunk_volume_l: 350, ncap_rating: '5★', fuel_type: 'essence', is_4x4: false, engine_power_hp: 90, transmission: 'manuelle' }),
        car({ id: 'c2', price: 210000, trunk_volume_l: 520, ncap_rating: '4★', fuel_type: 'hybride', is_4x4: true, engine_power_hp: 140, transmission: 'automatique' }),
      ];

      // Step 1: Budget (prix_acces)
      const q1 = await client.getNextQuestion(
        [{ role: 'user', content: 'Je cherche une bonne voiture' }],
        cars
      );
      expect(q1?.question.toLowerCase()).toContain('budget');

      // Step 2: Usage (praticite_urbaine)
      const q2 = await client.getNextQuestion(
        [
          { role: 'user', content: 'Je cherche une bonne voiture' },
          { role: 'assistant', content: 'Quel est votre budget ?' },
          { role: 'user', content: 'Budget 200 000 MAD' },
        ],
        cars
      );
      expect(q2?.question.toLowerCase()).toMatch(/ville|autoroute|mixte/i);

      // Step 3: Espace or other 8D dimension
      const q3 = await client.getNextQuestion(
        [
          { role: 'user', content: 'Je cherche une bonne voiture' },
          { role: 'assistant', content: 'Quel est votre budget ?' },
          { role: 'user', content: 'Budget 200 000 MAD' },
          { role: 'assistant', content: 'Vous roulerez surtout en ville ?' },
          { role: 'user', content: 'Ville' },
        ],
        cars
      );
      expect(q3).not.toBeNull();
      // Ensure question is strictly one of 8D and never generic transmission
      expect(q3?.question).not.toContain('boîte automatique ou manuelle');
      expect(q3?.question).not.toContain('automatic or manual gearbox');
    });
  });
});

