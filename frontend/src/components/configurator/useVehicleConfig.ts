/**
 * components/configurator/useVehicleConfig.ts
 * ===========================================
 * Hook personnalisé gérant l'état de configuration d'un véhicule :
 * - Couleur active sélectionnée
 * - Options et accessoires cochés
 * - Calcul dynamique du prix total (prix de base + delta couleur + deltas options)
 * 
 * Totalement indépendant du moteur 3D (fonctionne que le 3D soit actif ou non).
 */

import { useState, useMemo, useCallback } from 'react';
import type { VehicleColorItem, VehicleOptionItem } from '../../services/vehicleOptionsService';

export interface UseVehicleConfigProps {
  basePrice: number;
  availableColors?: VehicleColorItem[];
  availableOptions?: VehicleOptionItem[];
}

export interface UseVehicleConfigReturn {
  selectedColor: VehicleColorItem | null;
  selectedOptionIds: string[];
  selectColor: (color: VehicleColorItem) => void;
  toggleOption: (optionId: string) => void;
  isOptionSelected: (optionId: string) => boolean;
  resetToDefaults: () => void;
  colorPrice: number;
  optionsPrice: number;
  totalPrice: number;
  selectedOptionsList: VehicleOptionItem[];
}

const DEFAULT_FALLBACK_COLORS: VehicleColorItem[] = [
  { id: 'col-1', vehicle_id: 'default', color_name: 'Kaki Lichen', hex_code: '#4E5442', price_delta: 0, is_default: true },
  { id: 'col-2', vehicle_id: 'default', color_name: 'Blanc Glacier', hex_code: '#FFFFFF', price_delta: 0, is_default: false },
  { id: 'col-3', vehicle_id: 'default', color_name: 'Gris Schiste', hex_code: '#4A4F55', price_delta: 3800, is_default: false },
  { id: 'col-4', vehicle_id: 'default', color_name: 'Vert Cèdre', hex_code: '#294038', price_delta: 3800, is_default: false },
  { id: 'col-5', vehicle_id: 'default', color_name: 'Brun Terracotta', hex_code: '#944E38', price_delta: 3800, is_default: false },
  { id: 'col-6', vehicle_id: 'default', color_name: 'Noir Nacré', hex_code: '#141414', price_delta: 3800, is_default: false },
];

const DEFAULT_FALLBACK_OPTIONS: VehicleOptionItem[] = [
  { id: 'opt-1', vehicle_id: 'default', category: 'jante', name: 'Jantes alliage 16" Mahalia diamantées', price_delta: 0, is_default: true },
  { id: 'opt-2', vehicle_id: 'default', category: 'accessoire', name: 'Barres de toit longitudinales modulables Stepway', price_delta: 0, is_default: true },
  { id: 'opt-3', vehicle_id: 'default', category: 'pack', name: 'Pack Media Nav : Écran tactile 8" + GPS Maroc + CarPlay', price_delta: 4500, is_default: false },
  { id: 'opt-4', vehicle_id: 'default', category: 'sellerie', name: 'Sellerie TEP Stepway avec surpiqûres orange cuivré', price_delta: 2500, is_default: false },
  { id: 'opt-5', vehicle_id: 'default', category: 'pack', name: 'Pack City : Caméra de recul + Radars de stationnement AV/AR', price_delta: 3200, is_default: false },
  { id: 'opt-6', vehicle_id: 'default', category: 'accessoire', name: 'Marchepieds latéraux en acier inoxydable brossé', price_delta: 2800, is_default: false },
];

export function useVehicleConfig({
  basePrice,
  availableColors = [],
  availableOptions = [],
}: UseVehicleConfigProps): UseVehicleConfigReturn {
  const safeColors = availableColors.length > 0 ? availableColors : DEFAULT_FALLBACK_COLORS;
  const safeOptions = availableOptions.length > 0 ? availableOptions : DEFAULT_FALLBACK_OPTIONS;

  // 1. Détermination de la couleur par défaut
  const defaultColor = useMemo(() => {
    return safeColors.find((c) => c.is_default) || safeColors[0] || null;
  }, [safeColors]);

  // 2. Détermination des options par défaut
  const defaultOptionIds = useMemo(() => {
    return safeOptions.filter((o) => o.is_default).map((o) => o.id);
  }, [safeOptions]);

  const [selectedColor, setSelectedColor] = useState<VehicleColorItem | null>(defaultColor);
  const [selectedOptionIds, setSelectedOptionIds] = useState<string[]>(defaultOptionIds);

  const selectColor = useCallback((color: VehicleColorItem) => {
    setSelectedColor(color);
  }, []);

  const toggleOption = useCallback((optionId: string) => {
    const opt = safeOptions.find((o) => o.id === optionId);
    if (opt?.is_default) {
      // Les options de série ne peuvent pas être désélectionnées
      return;
    }
    setSelectedOptionIds((prev) =>
      prev.includes(optionId)
        ? prev.filter((id) => id !== optionId)
        : [...prev, optionId]
    );
  }, [safeOptions]);

  const isOptionSelected = useCallback(
    (optionId: string) => {
      const opt = safeOptions.find((o) => o.id === optionId);
      if (opt?.is_default) return true;
      return selectedOptionIds.includes(optionId);
    },
    [safeOptions, selectedOptionIds]
  );

  const resetToDefaults = useCallback(() => {
    setSelectedColor(defaultColor);
    setSelectedOptionIds(defaultOptionIds);
  }, [defaultColor, defaultOptionIds]);

  // Calculs des prix
  const colorPrice = useMemo(() => {
    return selectedColor ? Number(selectedColor.price_delta) || 0 : 0;
  }, [selectedColor]);

  const selectedOptionsList = useMemo(() => {
    return safeOptions.filter((opt) =>
      opt.is_default || selectedOptionIds.includes(opt.id)
    );
  }, [safeOptions, selectedOptionIds]);

  const optionsPrice = useMemo(() => {
    return selectedOptionsList.reduce(
      (sum, opt) => sum + (Number(opt.price_delta) || 0),
      0
    );
  }, [selectedOptionsList]);

  const totalPrice = useMemo(() => {
    return Number(basePrice) + colorPrice + optionsPrice;
  }, [basePrice, colorPrice, optionsPrice]);

  return {
    selectedColor,
    selectedOptionIds,
    selectColor,
    toggleOption,
    isOptionSelected,
    resetToDefaults,
    colorPrice,
    optionsPrice,
    totalPrice,
    selectedOptionsList,
  };
}
