import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import CatalogueSearchBar from '../CatalogueSearchBar';

describe('CatalogueSearchBar Component with Recommendation Sensing', () => {
  it('renders input, search icon, and submit button in direct search mode', () => {
    const handleChange = vi.fn();
    render(
      <CatalogueSearchBar
        value=""
        onChange={handleChange}
      />
    );

    const input = screen.getByRole('textbox', { name: /Rechercher un véhicule/i });
    expect(input).toBeTruthy();

    const searchButton = screen.getByRole('button', { name: /Rechercher/i });
    expect(searchButton).toBeTruthy();
  });

  it('triggers onChange for direct catalogue search when typing a brand/model', () => {
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

  it('intelligently senses a recommendation query and dispatches wakala:recommendation-search on submit', () => {
    const dispatchSpy = vi.spyOn(window, 'dispatchEvent');
    const handleChange = vi.fn();
    render(
      <CatalogueSearchBar
        value="SUV familial économique"
        onChange={handleChange}
      />
    );

    // Should sense recommendation intent and update button role/aria-label
    const aiButton = screen.getByRole('button', { name: /Recommander avec l'IA/i });
    expect(aiButton).toBeTruthy();
    fireEvent.click(aiButton);

    expect(dispatchSpy).toHaveBeenCalled();
    const event = dispatchSpy.mock.calls.find(
      (call) => call[0] instanceof CustomEvent && call[0].type === 'wakala:recommendation-search'
    )?.[0] as CustomEvent;

    expect(event).toBeDefined();
    expect(event.detail.message).toBe('SUV familial économique');
    dispatchSpy.mockRestore();
  });

  it('senses a Darija / Arabic recommendation request and triggers recommendation on submit', () => {
    const dispatchSpy = vi.spyOn(window, 'dispatchEvent');
    const handleChange = vi.fn();
    render(
      <CatalogueSearchBar
        value="bghit tomobil sghira 9tisadiya"
        onChange={handleChange}
      />
    );

    const aiButton = screen.getByRole('button', { name: /Recommander avec l'IA/i });
    expect(aiButton).toBeTruthy();
    fireEvent.click(aiButton);

    expect(dispatchSpy).toHaveBeenCalled();
    const event = dispatchSpy.mock.calls.find(
      (call) => call[0] instanceof CustomEvent && call[0].type === 'wakala:recommendation-search'
    )?.[0] as CustomEvent;

    expect(event).toBeDefined();
    expect(event.detail.message).toBe('bghit tomobil sghira 9tisadiya');
    dispatchSpy.mockRestore();
  });

  it('senses a question query (with question mark) and triggers recommendation', () => {
    const dispatchSpy = vi.spyOn(window, 'dispatchEvent');
    const handleChange = vi.fn();
    render(
      <CatalogueSearchBar
        value="Golf ou Clio 5 que choisir ?"
        onChange={handleChange}
      />
    );

    const aiButton = screen.getByRole('button', { name: /Recommander avec l'IA/i });
    expect(aiButton).toBeTruthy();
    fireEvent.click(aiButton);

    expect(dispatchSpy).toHaveBeenCalled();
    const event = dispatchSpy.mock.calls.find(
      (call) => call[0] instanceof CustomEvent && call[0].type === 'wakala:recommendation-search'
    )?.[0] as CustomEvent;

    expect(event).toBeDefined();
    expect(event.detail.message).toBe('Golf ou Clio 5 que choisir ?');
    dispatchSpy.mockRestore();
  });

  it('submits direct catalogue search via onChange when query is a simple vehicle name', () => {
    const dispatchSpy = vi.spyOn(window, 'dispatchEvent');
    const handleChange = vi.fn();
    render(
      <CatalogueSearchBar
        value="Clio 5"
        onChange={handleChange}
      />
    );

    const searchButton = screen.getByRole('button', { name: /Rechercher/i });
    expect(searchButton).toBeTruthy();
    fireEvent.click(searchButton);

    // Direct search should update catalogue filter via onChange, NOT trigger recommendation
    expect(handleChange).toHaveBeenCalledWith('Clio 5');
    const recommendationCall = dispatchSpy.mock.calls.find(
      (call) => call[0] instanceof CustomEvent && call[0].type === 'wakala:recommendation-search'
    );
    expect(recommendationCall).toBeUndefined();
    dispatchSpy.mockRestore();
  });
});