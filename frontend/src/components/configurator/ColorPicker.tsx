/**
 * components/configurator/ColorPicker.tsx
 * =======================================
 * Composant générique de sélection de couleur pour le configurateur.
 */

import React from 'react';
import type { VehicleColorItem } from '../../services/vehicleOptionsService';

export interface ColorPickerProps {
  colors: VehicleColorItem[];
  selectedColor: VehicleColorItem | null;
  onSelectColor: (color: VehicleColorItem) => void;
}

export const ColorPicker: React.FC<ColorPickerProps> = ({
  colors,
  selectedColor,
  onSelectColor,
}) => {
  if (!colors || colors.length === 0) return null;

  return (
    <div style={{ marginBottom: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
          Teinte de Carrosserie
        </h4>
        {selectedColor && (
          <span style={{ fontSize: '0.85rem', color: 'var(--accent-gold)', fontWeight: 600 }}>
            {selectedColor.color_name} {selectedColor.price_delta > 0 ? `(+${selectedColor.price_delta.toLocaleString('fr-FR')} DH)` : '(Inclus)'}
          </span>
        )}
      </div>

      <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
        {colors.map((c) => {
          const isSelected = selectedColor?.id === c.id;
          return (
            <button
              key={c.id}
              type="button"
              onClick={() => onSelectColor(c)}
              title={`${c.color_name} ${c.price_delta > 0 ? `(+${c.price_delta} DH)` : '(De série)'}`}
              style={{
                position: 'relative',
                width: 44,
                height: 44,
                borderRadius: '50%',
                background: c.hex_code,
                border: isSelected ? '3px solid var(--accent-gold)' : '2px solid rgba(255,255,255,0.3)',
                boxShadow: isSelected ? '0 0 12px rgba(200, 169, 106, 0.6)' : '0 2px 6px rgba(0,0,0,0.3)',
                cursor: 'pointer',
                transform: isSelected ? 'scale(1.15)' : 'scale(1)',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                padding: 0,
                outline: 'none',
              }}
            >
              {isSelected && (
                <span
                  style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: '#fff',
                    boxShadow: '0 0 4px rgba(0,0,0,0.5)',
                  }}
                />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};
