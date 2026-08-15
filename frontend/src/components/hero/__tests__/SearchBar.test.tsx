import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Hero from '../Hero';
import { AuthProvider } from '../../../context/AuthContext';

vi.mock('../../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
}));

describe('Hero (SearchBar)', () => {
  it('renders the search input', () => {
    render(
      <AuthProvider>
        <MemoryRouter>
          <Hero />
        </MemoryRouter>
      </AuthProvider>
    );

    const searchInput = screen.queryByPlaceholderText(/Décrivez vos besoins/i);
    expect(searchInput).toBeTruthy();
  });

  it('renders the search button', () => {
    render(
      <AuthProvider>
        <MemoryRouter>
          <Hero />
        </MemoryRouter>
      </AuthProvider>
    );
    const searchBtn = screen.queryByRole('button', { name: /recherche/i });
    expect(searchBtn).toBeTruthy();
  });
});
