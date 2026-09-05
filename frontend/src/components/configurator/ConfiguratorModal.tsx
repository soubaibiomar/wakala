/**
 * components/configurator/ConfiguratorModal.tsx
 * =============================================
 * Modale immersive de configuration 3D temps réel pour le véhicule sélectionné.
 */

import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, RotateCcw, Check } from 'lucide-react';
import { StudioViewer360 } from './StudioViewer360';
import { ColorPicker } from './ColorPicker';
import { OptionsPanel } from './OptionsPanel';
import { useVehicleConfig } from './useVehicleConfig';
import type { VehicleColorItem, VehicleOptionItem } from '../../services/vehicleOptionsService';
import './ConfiguratorModal.css';

export interface ConfiguratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  vehicleIdOrSlug: string;
  vehicleName: string;
  basePrice: number;
  availableColors?: VehicleColorItem[];
  availableOptions?: VehicleOptionItem[];
  optionsByCategory?: Record<string, VehicleOptionItem[]>;
  onApplyConfiguration?: (totalPrice: number, selectedColor: VehicleColorItem | null, selectedOptions: VehicleOptionItem[]) => void;
}

export const ConfiguratorModal: React.FC<ConfiguratorModalProps> = ({
  isOpen,
  onClose,
  vehicleIdOrSlug,
  vehicleName,
  basePrice,
  availableColors = [],
  availableOptions = [],
  optionsByCategory = {},
  onApplyConfiguration,
}) => {
  const computedColors = useMemo(() => {
    if (availableColors && availableColors.length > 0) return availableColors;
    return [
      { id: 'col-1', vehicle_id: 'default', color_name: 'Kaki Lichen', hex_code: '#4E5442', price_delta: 0, is_default: true },
      { id: 'col-2', vehicle_id: 'default', color_name: 'Blanc Glacier', hex_code: '#FFFFFF', price_delta: 0, is_default: false },
      { id: 'col-3', vehicle_id: 'default', color_name: 'Gris Schiste', hex_code: '#4A4F55', price_delta: 3800, is_default: false },
      { id: 'col-4', vehicle_id: 'default', color_name: 'Vert Cèdre', hex_code: '#294038', price_delta: 3800, is_default: false },
      { id: 'col-5', vehicle_id: 'default', color_name: 'Brun Terracotta', hex_code: '#944E38', price_delta: 3800, is_default: false },
      { id: 'col-6', vehicle_id: 'default', color_name: 'Noir Nacré', hex_code: '#141414', price_delta: 3800, is_default: false },
    ];
  }, [availableColors]);

  const computedOptionsByCategory = useMemo(() => {
    if (optionsByCategory && Object.keys(optionsByCategory).length > 0) {
      return optionsByCategory;
    }
    const defaultList = [
      { id: 'opt-1', vehicle_id: 'default', category: 'jante', name: 'Jantes alliage 16" Mahalia diamantées', price_delta: 0, is_default: true },
      { id: 'opt-2', vehicle_id: 'default', category: 'accessoire', name: 'Barres de toit longitudinales modulables Stepway', price_delta: 0, is_default: true },
      { id: 'opt-3', vehicle_id: 'default', category: 'pack', name: 'Pack Media Nav : Écran tactile 8" + GPS Maroc + CarPlay', price_delta: 4500, is_default: false },
      { id: 'opt-4', vehicle_id: 'default', category: 'sellerie', name: 'Sellerie TEP Stepway avec surpiqûres orange cuivré', price_delta: 2500, is_default: false },
      { id: 'opt-5', vehicle_id: 'default', category: 'pack', name: 'Pack City : Caméra de recul + Radars de stationnement AV/AR', price_delta: 3200, is_default: false },
      { id: 'opt-6', vehicle_id: 'default', category: 'accessoire', name: 'Marchepieds latéraux en acier inoxydable brossé', price_delta: 2800, is_default: false },
    ];
    const grouped: Record<string, VehicleOptionItem[]> = {};
    defaultList.forEach((opt) => {
      if (!grouped[opt.category]) grouped[opt.category] = [];
      grouped[opt.category].push(opt);
    });
    return grouped;
  }, [optionsByCategory]);

  const computedFlatOptions = useMemo(() => {
    if (availableOptions && availableOptions.length > 0) return availableOptions;
    return Object.values(computedOptionsByCategory).flat();
  }, [availableOptions, computedOptionsByCategory]);

  const {
    selectedColor,
    selectedOptionIds,
    selectColor,
    toggleOption,
    isOptionSelected,
    resetToDefaults,
    totalPrice,
    selectedOptionsList,
  } = useVehicleConfig({
    basePrice,
    availableColors: computedColors,
    availableOptions: computedFlatOptions,
  });

  const selectedOptionNames = useMemo(() => {
    return selectedOptionsList.map((o) => o.name);
  }, [selectedOptionsList]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="configurator-modal__overlay">
        <motion.div
          className="configurator-modal__dialog"
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.25 }}
        >
          {/* Header */}
          <div className="configurator-modal__header">
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                  Configurateur 3D Studio
                </h3>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{vehicleName}</span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <button
                type="button"
                onClick={resetToDefaults}
                title="Réinitialiser aux options de série"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '8px 14px',
                  borderRadius: '8px',
                  border: '1px solid var(--border-subtle)',
                  background: 'var(--bg-surface)',
                  color: 'var(--text-secondary)',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                <RotateCcw size={15} />
                Réinitialiser
              </button>

              <button
                type="button"
                onClick={onClose}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-muted)',
                  cursor: 'pointer',
                  padding: 8,
                  borderRadius: '8px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <X size={24} />
              </button>
            </div>
          </div>

          {/* Body: 3D Canvas Left + Customization Controls Right */}
          <div className="configurator-modal__body">
            {/* Colonne Visualiseur 360° Studio */}
            <div className="configurator-modal__viewer-col">
              <StudioViewer360
                vehicleIdOrSlug={vehicleIdOrSlug}
                vehicleName={vehicleName}
                selectedColorHex={selectedColor?.hex_code}
                selectedColorName={selectedColor?.color_name}
                selectedOptionNames={selectedOptionNames}
                height="100%"
              />
            </div>

            {/* Colonne Contrôles */}
            <div className="configurator-modal__controls-col">
              <div className="configurator-modal__controls-scroll">
                <ColorPicker
                  colors={computedColors}
                  selectedColor={selectedColor}
                  onSelectColor={selectColor}
                />

                <OptionsPanel
                  optionsByCategory={computedOptionsByCategory}
                  isOptionSelected={isOptionSelected}
                  onToggleOption={toggleOption}
                />
              </div>

              {/* Footer avec Prix Total et Validation */}
              <div className="configurator-modal__footer">
                <div className="configurator-modal__footer-price">
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block' }}>
                    Prix Total Configuré (TTC)
                  </span>
                  <span style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-gold)' }}>
                    {totalPrice.toLocaleString('fr-FR')} DH
                  </span>
                </div>

                <button
                  type="button"
                  className="configurator-modal__validate-btn"
                  onClick={() => {
                    if (onApplyConfiguration) {
                      onApplyConfiguration(totalPrice, selectedColor, selectedOptionsList);
                    }
                    onClose();
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    padding: '12px 24px',
                    borderRadius: '12px',
                    border: 'none',
                    background: 'var(--accent-gold)',
                    color: '#000',
                    fontWeight: 700,
                    fontSize: '0.95rem',
                    cursor: 'pointer',
                    boxShadow: '0 4px 16px rgba(200, 169, 106, 0.4)',
                  }}
                >
                  <Check size={18} />
                  Valider cette configuration
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
