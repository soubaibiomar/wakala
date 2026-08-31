import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useVehicleConfig } from '../useVehicleConfig';
import type { VehicleColorItem, VehicleOptionItem } from '../../../services/vehicleOptionsService';

describe('useVehicleConfig', () => {
  const mockColors: VehicleColorItem[] = [
    {
      id: 'col-1',
      vehicle_id: 'veh-1',
      color_name: 'Blanc Glacier',
      hex_code: '#FFFFFF',
      price_delta: 0,
      is_default: true,
    },
    {
      id: 'col-2',
      vehicle_id: 'veh-1',
      color_name: 'Bleu Iron Métallisé',
      hex_code: '#1D3557',
      price_delta: 5500,
      is_default: false,
    },
  ];

  const mockOptions: VehicleOptionItem[] = [
    {
      id: 'opt-1',
      vehicle_id: 'veh-1',
      category: 'jante',
      name: 'Jantes alliage 16" diamantées',
      price_delta: 3500,
      is_default: false,
    },
    {
      id: 'opt-2',
      vehicle_id: 'veh-1',
      category: 'accessoire',
      name: 'Barres de toit transversales',
      price_delta: 2200,
      is_default: false,
    },
    {
      id: 'opt-3',
      vehicle_id: 'veh-1',
      category: 'pack',
      name: 'Pack Sécurité Série',
      price_delta: 0,
      is_default: true,
    },
  ];

  it('initialise avec la couleur de série et calcule le prix de base exact', () => {
    const { result } = renderHook(() =>
      useVehicleConfig({
        basePrice: 150000,
        availableColors: mockColors,
        availableOptions: mockOptions,
      })
    );

    expect(result.current.selectedColor?.id).toBe('col-1');
    expect(result.current.colorPrice).toBe(0);
    expect(result.current.optionsPrice).toBe(0);
    expect(result.current.totalPrice).toBe(150000);
  });

  it('met à jour le prix total lors de la sélection d\'une teinte optionnelle', () => {
    const { result } = renderHook(() =>
      useVehicleConfig({
        basePrice: 150000,
        availableColors: mockColors,
        availableOptions: mockOptions,
      })
    );

    act(() => {
      result.current.selectColor(mockColors[1]);
    });

    expect(result.current.selectedColor?.id).toBe('col-2');
    expect(result.current.colorPrice).toBe(5500);
    expect(result.current.totalPrice).toBe(155500);
  });

  it('ajoute et retire des options avec recalcul dynamique du prix', () => {
    const { result } = renderHook(() =>
      useVehicleConfig({
        basePrice: 150000,
        availableColors: mockColors,
        availableOptions: mockOptions,
      })
    );

    // Sélection de l'option Jantes (+3500)
    act(() => {
      result.current.toggleOption('opt-1');
    });

    expect(result.current.isOptionSelected('opt-1')).toBe(true);
    expect(result.current.optionsPrice).toBe(3500);
    expect(result.current.totalPrice).toBe(153500);

    // Sélection de l'option Barres de toit (+2200)
    act(() => {
      result.current.toggleOption('opt-2');
    });

    expect(result.current.optionsPrice).toBe(5700);
    expect(result.current.totalPrice).toBe(155700);

    // Désélection des Jantes (-3500)
    act(() => {
      result.current.toggleOption('opt-1');
    });

    expect(result.current.isOptionSelected('opt-1')).toBe(false);
    expect(result.current.optionsPrice).toBe(2200);
    expect(result.current.totalPrice).toBe(152200);
  });

  it('ne permet pas de désélectionner une option de série (is_default = true)', () => {
    const { result } = renderHook(() =>
      useVehicleConfig({
        basePrice: 150000,
        availableColors: mockColors,
        availableOptions: mockOptions,
      })
    );

    expect(result.current.isOptionSelected('opt-3')).toBe(true);

    act(() => {
      result.current.toggleOption('opt-3');
    });

    expect(result.current.isOptionSelected('opt-3')).toBe(true);
    expect(result.current.totalPrice).toBe(150000);
  });

  it('réinitialise aux valeurs de série', () => {
    const { result } = renderHook(() =>
      useVehicleConfig({
        basePrice: 150000,
        availableColors: mockColors,
        availableOptions: mockOptions,
      })
    );

    act(() => {
      result.current.selectColor(mockColors[1]);
      result.current.toggleOption('opt-1');
    });

    expect(result.current.totalPrice).toBe(159000);

    act(() => {
      result.current.resetToDefaults();
    });

    expect(result.current.selectedColor?.id).toBe('col-1');
    expect(result.current.isOptionSelected('opt-1')).toBe(false);
    expect(result.current.totalPrice).toBe(150000);
  });
});
