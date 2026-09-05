import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import RecommendationExperience from './RecommendationExperience';
import type { RecommendationClient, Car } from './recommendationClient';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

Element.prototype.scrollIntoView = vi.fn() as unknown as () => void;

const sampleCars: Car[] = [
  {
    id: 'car-1',
    brand: 'Dacia',
    model: 'Duster',
    price: 195000,
    body_type: 'suv',
    fuel_type: 'diesel',
    transmission: 'manuelle',
    year: 2024,
    images: [{ file_path: '/assets/duster.jpg' }],
  },
  {
    id: 'car-2',
    brand: 'Renault',
    model: 'Captur',
    price: 220000,
    body_type: 'suv',
    fuel_type: 'essence',
    transmission: 'automatique',
    year: 2024,
    images: [{ file_path: '/assets/captur.jpg' }],
  },
] as unknown as Car[];

describe('RecommendationExperience - Navigation and Process Continuation', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  it('detects a recommendation request outside of catalogue, navigates to /catalogue?q=..., and continues normal qualification', async () => {
    const mockClient: RecommendationClient = {
      detectRecommendationIntent: vi.fn().mockResolvedValue(true),
      applyAnswer: vi.fn().mockResolvedValue(sampleCars),
      getNextQuestion: vi.fn().mockResolvedValue({
        question: 'Quel est votre budget maximum ?',
        options: [{ label: 'Moins de 200 000 MAD' }, { label: 'Moins de 300 000 MAD' }],
        rangeBounds: { min: 100000, max: 300000, step: 10000, label: 'Budget recommandé' },
      }),
    };

    let dispatchedEventDetail: any = null;
    const eventListener = (e: Event) => {
      dispatchedEventDetail = (e as CustomEvent).detail;
    };
    window.addEventListener('wakala:recommendation-results', eventListener);

    render(
      <MemoryRouter initialEntries={['/']}>
        <RecommendationExperience client={mockClient} initialCars={sampleCars} />
      </MemoryRouter>
    );

    // 1. Open chat widget
    const bubble = screen.getByRole('button');
    fireEvent.click(bubble);

    // 2. Select language 'Français'
    await waitFor(() => {
      expect(screen.getByText('Français')).toBeTruthy();
    });
    fireEvent.click(screen.getByText('Français'));

    // 3. Verify chat composer is enabled
    await waitFor(() => {
      const input = screen.getByRole('textbox');
      expect(input).not.toBeDisabled();
    });

    // 4. Send recommendation query
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'je cherche un SUV familial' } });
    
    const form = input.closest('form');
    expect(form).toBeTruthy();
    fireEvent.submit(form!);

    // 5. Verify it navigates to /catalogue?q=...
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        expect.stringContaining('/catalogue?q=je%20cherche%20un%20SUV%20familial')
      );
    });

    // 6. Verify wakala:recommendation-results custom event was dispatched to populate the catalogue
    await waitFor(() => {
      expect(dispatchedEventDetail).toBeTruthy();
      expect(dispatchedEventDetail.cars).toHaveLength(2);
    });

    // 7. Verify normal qualification process continues: next question & budget slider rendered
    await waitFor(() => {
      expect(screen.getByText(/Quel est votre budget maximum \?/i)).toBeTruthy();
      expect(screen.getByText(/Budget recommandé/i)).toBeTruthy();
      expect(screen.getByText(/Utiliser cette fourchette/i)).toBeTruthy();
    });

    // 8. Test Turn 2: Click "Utiliser cette fourchette"
    fireEvent.click(screen.getByText(/Utiliser cette fourchette/i));

    // Verify mockClient.applyAnswer was called for the range
    await waitFor(() => {
      expect(mockClient.applyAnswer).toHaveBeenCalledTimes(2);
    });

    window.removeEventListener('wakala:recommendation-results', eventListener);
  });

  it('does NOT navigate to /catalogue for purely informative queries', async () => {
    const mockClient: RecommendationClient = {
      detectRecommendationIntent: vi.fn().mockResolvedValue(false),
      applyAnswer: vi.fn().mockResolvedValue([]),
      getNextQuestion: vi.fn().mockResolvedValue(null),
    };

    render(
      <MemoryRouter initialEntries={['/']}>
        <RecommendationExperience client={mockClient} initialCars={sampleCars} />
      </MemoryRouter>
    );

    // Open chat widget
    const bubble = screen.getByRole('button');
    fireEvent.click(bubble);

    await waitFor(() => {
      expect(screen.getByText('Français')).toBeTruthy();
    });
    fireEvent.click(screen.getByText('Français'));

    await waitFor(() => {
      const input = screen.getByRole('textbox');
      expect(input).not.toBeDisabled();
    });

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'je veux des informations sur dacia' } });
    
    const form = input.closest('form');
    expect(form).toBeTruthy();
    fireEvent.submit(form!);

    // Should NOT navigate to catalogue
    await waitFor(() => {
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  it('when already on /catalogue, does NOT navigate again and directly continues qualification', async () => {
    const mockClient: RecommendationClient = {
      detectRecommendationIntent: vi.fn().mockResolvedValue(true),
      applyAnswer: vi.fn().mockResolvedValue(sampleCars),
      getNextQuestion: vi.fn().mockResolvedValue({
        question: 'Quel est votre budget maximum ?',
        options: [],
        rangeBounds: { min: 100000, max: 300000, step: 10000, label: 'Budget recommandé' },
      }),
    };

    render(
      <MemoryRouter initialEntries={['/catalogue']}>
        <RecommendationExperience client={mockClient} initialCars={sampleCars} />
      </MemoryRouter>
    );

    // Open chat widget via event on /catalogue
    window.dispatchEvent(new CustomEvent('wakala:open-chat'));

    await waitFor(() => {
      expect(screen.getByText('Français')).toBeTruthy();
    });
    fireEvent.click(screen.getByText('Français'));

    await waitFor(() => {
      const input = screen.getByRole('textbox');
      expect(input).not.toBeDisabled();
    });

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'je veux un SUV' } });
    
    const form = input.closest('form');
    expect(form).toBeTruthy();
    fireEvent.submit(form!);

    // Should NOT call navigate('/catalogue...') because it is ALREADY on /catalogue
    await waitFor(() => {
      expect(screen.getByText(/Quel est votre budget maximum \?/i)).toBeTruthy();
    });
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('navigates to /catalogue?q=... when sending "a car 200000dhs"', async () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <RecommendationExperience initialCars={sampleCars} />
      </MemoryRouter>
    );

    // Open chat widget
    const bubble = screen.getByRole('button');
    fireEvent.click(bubble);

    await waitFor(() => {
      expect(screen.getByText('English')).toBeTruthy();
    });
    fireEvent.click(screen.getByText('English'));

    await waitFor(() => {
      const input = screen.getByRole('textbox');
      expect(input).not.toBeDisabled();
    });

    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'a car 200000dhs' } });
    
    const form = input.closest('form');
    expect(form).toBeTruthy();
    fireEvent.submit(form!);

    // Must navigate to catalogue with encoded query
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        expect.stringContaining('/catalogue?q=a%20car%20200000dhs')
      );
    });
  });

  it('renders suggestion chips when the assistant asks "Which fuel type do you prefer for this vehicle (Diesel, Petrol, or Hybrid)?" and handles chip click', async () => {
    const allFuelCars: Car[] = [
      ...sampleCars,
      {
        id: 'car-3',
        brand: 'Toyota',
        model: 'Corolla Cross',
        price: 260000,
        body_type: 'suv',
        fuel_type: 'hybride',
        transmission: 'automatique',
        year: 2024,
        images: [{ file_path: '/assets/corolla.jpg' }],
      } as unknown as Car,
      {
        id: 'car-4',
        brand: 'MG',
        model: 'ZS EV',
        price: 320000,
        body_type: 'suv',
        fuel_type: 'electrique',
        transmission: 'automatique',
        year: 2024,
        images: [{ file_path: '/assets/mgev.jpg' }],
      } as unknown as Car,
    ];

    const mockClient: RecommendationClient = {
      detectRecommendationIntent: vi.fn().mockResolvedValue(true),
      applyAnswer: vi.fn().mockResolvedValue(allFuelCars),
      getNextQuestion: vi.fn().mockResolvedValue({
        question: 'Which fuel type do you prefer for this vehicle (Diesel, Petrol, or Hybrid)?',
        options: [],
      }),
    };

    render(
      <MemoryRouter initialEntries={['/catalogue']}>
        <RecommendationExperience client={mockClient} initialCars={allFuelCars} />
      </MemoryRouter>
    );

    // 1. Open chat widget via event on /catalogue
    window.dispatchEvent(new CustomEvent('wakala:open-chat'));

    // 2. Select English
    await waitFor(() => {
      expect(screen.getByText('English')).toBeTruthy();
    });
    fireEvent.click(screen.getByText('English'));

    // 3. Send initial message
    await waitFor(() => {
      const input = screen.getByRole('textbox');
      expect(input).not.toBeDisabled();
    });
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'I want an SUV' } });
    const form = input.closest('form');
    fireEvent.submit(form!);

    // 4. Verify question is displayed
    await waitFor(() => {
      expect(screen.getByText(/Which fuel type do you prefer for this vehicle/i)).toBeTruthy();
    });

    // 5. Verify suggestion chips are present: Diesel, Petrol, Hybrid, 100% Electric
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Diesel' })).toBeTruthy();
      expect(screen.getByRole('button', { name: 'Petrol' })).toBeTruthy();
      expect(screen.getByRole('button', { name: 'Hybrid' })).toBeTruthy();
      expect(screen.getByRole('button', { name: '100% Electric' })).toBeTruthy();
    });

    // 6. Click 'Diesel' chip
    const dieselChip = screen.getByRole('button', { name: 'Diesel' });
    fireEvent.click(dieselChip);

    // 7. Verify applyAnswer was called with diesel
      await waitFor(() => {
        expect(mockClient.applyAnswer).toHaveBeenCalledWith(
          'diesel',
          expect.any(Array),
          expect.any(Array)
        );
      });
    });

  it('renders a close button in the chat header and closes the widget when clicked', async () => {
    const mockClient: RecommendationClient = {
      detectRecommendationIntent: vi.fn().mockResolvedValue(false),
      applyAnswer: vi.fn().mockResolvedValue([]),
      getNextQuestion: vi.fn().mockResolvedValue(null),
    };

    render(
      <MemoryRouter initialEntries={['/']}>
        <RecommendationExperience client={mockClient} />
      </MemoryRouter>
    );

    // Open the widget by clicking the launcher bubble
    const bubble = screen.getByRole('button', { name: /ouvrir le conseiller/i });
    fireEvent.click(bubble);

    // Verify header close button is rendered
    const closeBtn = screen.getByRole('button', { name: /^fermer$/i });
    expect(closeBtn).toBeTruthy();

    // Click the header close button
    fireEvent.click(closeBtn);

    // Widget should be closed and launcher bubble restored
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /ouvrir le conseiller/i })).toBeTruthy();
    });
  });
});
