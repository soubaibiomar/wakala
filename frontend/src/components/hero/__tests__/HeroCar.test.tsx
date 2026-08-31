import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import HeroCar from '../HeroCar';

vi.mock('../../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
}));

vi.mock('../hero.module.css', () => ({ default: {} }));

describe('HeroCar', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('renders without crashing', () => {
    const { container } = render(
      <MemoryRouter>
        <HeroCar />
      </MemoryRouter>
    );
    expect(container).toBeTruthy();
  });

  it('renders the title elements', () => {
    render(
      <MemoryRouter>
        <HeroCar />
      </MemoryRouter>
    );
    expect(screen.getByText(/WAKALA/i)).toBeInTheDocument();
  });

  it('renders CTA button', () => {
    render(
      <MemoryRouter>
        <HeroCar />
      </MemoryRouter>
    );
    expect(screen.getByText(/Explorer les véhicules/i)).toBeInTheDocument();
  });

  it('renders the search bar input and submit button', () => {
    render(
      <MemoryRouter>
        <HeroCar />
      </MemoryRouter>
    );
    expect(screen.getByPlaceholderText(/Décrivez vos besoins/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Rechercher/i })).toBeInTheDocument();
  });

  it('renders the scroll hint initially', () => {
    render(
      <MemoryRouter>
        <HeroCar />
      </MemoryRouter>
    );
    const scrollBtn = screen.queryByLabelText(/Défiler vers le bas/i);
    expect(scrollBtn).toBeInTheDocument();
  });
});
