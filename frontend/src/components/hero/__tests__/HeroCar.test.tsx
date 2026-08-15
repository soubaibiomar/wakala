import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import HeroCar from '../HeroCar';
import { AuthProvider } from '../../../context/AuthContext';

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
      <AuthProvider>
        <MemoryRouter>
          <HeroCar />
        </MemoryRouter>
      </AuthProvider>
    );
    expect(container).toBeTruthy();
  });

  it('renders the title elements', () => {
    render(
      <AuthProvider>
        <MemoryRouter>
          <HeroCar />
        </MemoryRouter>
      </AuthProvider>
    );
    expect(screen.getByText(/WAKALA/i)).toBeInTheDocument();
  });

  it('renders CTA button', () => {
    render(
      <AuthProvider>
        <MemoryRouter>
          <HeroCar />
        </MemoryRouter>
      </AuthProvider>
    );
    expect(screen.getByText(/Explorer les véhicules/i)).toBeInTheDocument();
  });

  it('renders the scroll hint initially', () => {
    render(
      <AuthProvider>
        <MemoryRouter>
          <HeroCar />
        </MemoryRouter>
      </AuthProvider>
    );
    const scrollBtn = screen.queryByLabelText(/Défiler vers le bas/i);
    expect(scrollBtn).toBeInTheDocument();
  });
});
