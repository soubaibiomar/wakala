/**
 * components/configurator/OptionsPanel.tsx
 * ========================================
 * Panneau de sélection des options & équipements avec gestion réactive des clics
 * et mise à jour instantanée du prix et de la vue studio.
 */

import React from 'react';
import type { VehicleOptionItem } from '../../services/vehicleOptionsService';

export interface OptionsPanelProps {
  optionsByCategory: Record<string, VehicleOptionItem[]>;
  isOptionSelected: (optionId: string) => boolean;
  onToggleOption: (optionId: string) => void;
}

const CATEGORY_NAMES: Record<string, { label: string; icon: string }> = {
  accessoire: { label: "Accessoires & Équipements", icon: "🔧" },
  jante: { label: "Jantes & Roues", icon: "🛞" },
  sellerie: { label: "Sellerie & Intérieur", icon: "💺" },
  pack: { label: "Packs Technologie & Confort", icon: "✨" },
  couleur: { label: "Options Peinture", icon: "🎨" },
};

export const OptionsPanel: React.FC<OptionsPanelProps> = ({
  optionsByCategory,
  isOptionSelected,
  onToggleOption,
}) => {
  const categories = Object.keys(optionsByCategory);
  if (categories.length === 0) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {categories.map((catKey) => {
        const catOptions = optionsByCategory[catKey] || [];
        if (catOptions.length === 0) return null;

        const info = CATEGORY_NAMES[catKey] || { label: catKey.toUpperCase(), icon: "📦" };

        return (
          <div
            key={catKey}
            style={{
              background: 'var(--bg-elevated)',
              borderRadius: '12px',
              padding: '16px 20px',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <h4
              style={{
                fontSize: '0.95rem',
                fontWeight: 700,
                color: 'var(--text-primary)',
                margin: '0 0 14px 0',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <span>{info.icon}</span>
              <span>{info.label}</span>
            </h4>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {catOptions.map((opt) => {
                const selected = isOptionSelected(opt.id);
                return (
                  <div
                    key={opt.id}
                    role="button"
                    tabIndex={opt.is_default ? -1 : 0}
                    onClick={() => {
                      if (!opt.is_default) {
                        onToggleOption(opt.id);
                      }
                    }}
                    onKeyDown={(e) => {
                      if (!opt.is_default && (e.key === ' ' || e.key === 'Enter')) {
                        e.preventDefault();
                        onToggleOption(opt.id);
                      }
                    }}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '12px 14px',
                      borderRadius: '8px',
                      background: selected ? 'rgba(200, 169, 106, 0.14)' : 'var(--bg-surface)',
                      border: selected ? '1px solid var(--accent-gold)' : '1px solid var(--border-subtle)',
                      cursor: opt.is_default ? 'default' : 'pointer',
                      transition: 'all 0.15s ease',
                      userSelect: 'none',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <input
                        type="checkbox"
                        checked={selected}
                        disabled={opt.is_default}
                        onChange={(e) => {
                          e.stopPropagation();
                          if (!opt.is_default) {
                            onToggleOption(opt.id);
                          }
                        }}
                        style={{
                          width: 18,
                          height: 18,
                          accentColor: 'var(--accent-gold)',
                          cursor: opt.is_default ? 'default' : 'pointer',
                        }}
                      />
                      <span
                        style={{
                          fontSize: '0.9rem',
                          fontWeight: selected ? 600 : 500,
                          color: 'var(--text-primary, #0f172a)',
                        }}
                      >
                        {opt.name}
                      </span>
                    </div>

                    <span
                      style={{
                        fontSize: '0.85rem',
                        fontWeight: 700,
                        color: opt.is_default ? 'var(--text-muted, #64748b)' : 'var(--accent-gold, #b89a44)',
                        whiteSpace: 'nowrap',
                        marginLeft: 12,
                      }}
                    >
                      {opt.is_default ? 'De série' : `+${Number(opt.price_delta).toLocaleString('fr-FR')} DH`}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};
