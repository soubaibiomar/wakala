import { describe, expect, it, vi } from 'vitest';
import { FastApiRecommendationClient, type Car, type ChatTurn } from './recommendationClient';

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
  ])('detects recommendation intent for scenario: %s', async (message) => {
    const client = new FastApiRecommendationClient();
    await expect(client.detectRecommendationIntent(message)).resolves.toBe(true);
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

  it('uses the full catalogue when a direct body filter misses the current shortlist', async () => {
    const client = new FastApiRecommendationClient();
    const suv = car({ id: 'suv', body_type: 'suv' });
    mockGetVehicles.mockResolvedValue({ items: [suv], pages: 1 });
    const result = await client.applyAnswer('I want an SUV', history('I want an SUV'), [car({ body_type: 'berline' })]);
    expect(result.map((vehicle) => vehicle.id)).toEqual(['suv']);
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
});
