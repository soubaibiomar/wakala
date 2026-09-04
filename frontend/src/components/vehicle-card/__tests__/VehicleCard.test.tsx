import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import VehicleCard from '../VehicleCard';
import { CompareProvider } from '../../../context/CompareContext';
import type { Vehicle } from '../../../types/vehicle';

const mockVehicleFinition: Vehicle = {
  id: '013c7636-52f4-47e3-b401-711651dfc714',
  seller_id: 'seller-1',
  brand: 'Hyundai',
  model: 'Staria',
  version: 'Hyundai STARIA 2.2 CRDi Diesel 177 ch 8-AT PREMIUM 9 places',
  year: 2026,
  price: 475000,
  mileage: 0,
  fuel_type: 'diesel',
  transmission: 'automatique',
  body_type: 'monospace',
  doors: 5,
  seats: 9,
  city: 'Casablanca',
  images: [],
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('VehicleCard', () => {
  it('renders card per finition with exact price and version subtitle without "À partir de"', () => {
    render(
      <CompareProvider>
        <MemoryRouter>
          <VehicleCard vehicle={mockVehicleFinition} isGrouped={false} />
        </MemoryRouter>
      </CompareProvider>
    );

    // Title
    expect(screen.getByText('Hyundai Staria')).toBeTruthy();

    // Cleaned version subtitle
    expect(screen.getByText('2.2 CRDi Diesel 177 ch 8-AT PREMIUM 9 places')).toBeTruthy();

    // Exact price without "À partir de"
    const priceEl = screen.getByText(/475\.000/);
    expect(priceEl.textContent).not.toContain('À partir de');

    // CTA button for single version
    expect(screen.getByText(/Voir la version/i)).toBeTruthy();

    // Direct link to vehicle
    const link = screen.getByRole('link');
    expect(link.getAttribute('href')).toContain('/vehicule/');
  });

  it('renders grouped model card with "À partir de" and model link when isGrouped is true', () => {
    render(
      <CompareProvider>
        <MemoryRouter>
          <VehicleCard vehicle={mockVehicleFinition} isGrouped={true} />
        </MemoryRouter>
      </CompareProvider>
    );

    // Grouped price should contain "À partir de"
    const priceEl = screen.getByText(/À partir de/);
    expect(priceEl).toBeTruthy();

    // CTA button for grouped versions
    expect(screen.getByText(/Voir les versions/i)).toBeTruthy();

    // Link to brand/model page
    const link = screen.getByRole('link');
    expect(link.getAttribute('href')).toContain('/marque/hyundai/staria');
  });
});
