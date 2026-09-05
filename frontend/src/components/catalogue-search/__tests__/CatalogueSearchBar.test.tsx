import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CatalogueSearchBar from '../CatalogueSearchBar';

describe('CatalogueSearchBar Component', () => {
  it('renders input, search icon, and AI recommendation button', () => {
    const handleChange = vi.fn();
    render(
      <CatalogueSearchBar
        value=""
        onChange={handleChange}
      />
    );

    const input = screen.getByRole('textbox', { name: /Rechercher un véhicule/i });
    expect(input).toBeTruthy();

    const aiButton = screen.getByRole('button', { name: /Recommander avec l'IA/i });
    expect(aiButton).toBeTruthy();
  });

  it('triggers onChange for real-time simple search when typing', () => {
    const handleChange = vi.fn();
    render(
      <CatalogueSearchBar
        value="m"
        onChange={handleChange}
      />
    );

    const input = screen.getByRole('textbox', { name: /Rechercher un véhicule/i });
    fireEvent.change(input, { target: { value: 'mercedes' } });
    expect(handleChange).toHaveBeenCalledWith('mercedes');
  });

  it('clears the search term when clicking the clear button', () => {
    const handleChange = vi.fn();
    render(
      <CatalogueSearchBar
        value="golf"
        onChange={handleChange}
      />
    );

    const clearBtn = screen.getByRole('button', { name: /Effacer la recherche/i });
    expect(clearBtn).toBeTruthy();
    fireEvent.click(clearBtn);
    expect(handleChange).toHaveBeenCalledWith('');
  });

  it('dispatches wakala:recommendation-search when clicking the AI button with a query', () => {
    const dispatchSpy = vi.spyOn(window, 'dispatchEvent');
    const handleChange = vi.fn();
    render(
      <CatalogueSearchBar
        value="SUV familial économique"
        onChange={handleChange}
      />
    );

    const aiButton = screen.getByRole('button', { name: /Recommander avec l'IA/i });
    fireEvent.click(aiButton);

    expect(dispatchSpy).toHaveBeenCalled();
    const event = dispatchSpy.mock.calls.find(
      (call) => call[0] instanceof CustomEvent && call[0].type === 'wakala:recommendation-search'
    )?.[0] as CustomEvent;

    expect(event).toBeDefined();
    expect(event.detail.message).toBe('SUV familial économique');
    dispatchSpy.mockRestore();
  });
});
