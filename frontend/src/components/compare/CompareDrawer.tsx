import React, { useState } from 'react';
import { X, Scale } from 'lucide-react';
import { useCompare } from '../../context/CompareContext';
import VehicleComparator from './VehicleComparator';

export default function CompareDrawer() {
  const { compareList, removeVehicle, clearCompare, isDrawerOpen, setDrawerOpen } = useCompare();
  const [showComparator, setShowComparator] = useState(false);

  if (!isDrawerOpen || compareList.length === 0) return null;

  return (
    <>
      <div style={{
        position: 'fixed',
        bottom: 'calc(70px + env(safe-area-inset-bottom, 0px) + 12px)',
        right: 16,
        zIndex: 1050,
        background: 'var(--bg-elevated)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-card)',
        boxShadow: '0 12px 40px rgba(0,0,0,0.18)',
        padding: '14px 16px',
        width: 'calc(100vw - 32px)',
        maxWidth: 340,
        display: 'flex',
        flexDirection: 'column',
        gap: 12
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Scale size={18} color="var(--accent-gold)" />
            Comparateur ({compareList.length}/4)
          </h4>
          <button 
            type="button"
            onClick={() => setDrawerOpen(false)}
            aria-label="Fermer le comparateur"
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-muted)',
              minWidth: 40,
              minHeight: 40,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: 8
            }}
          >
            <X size={20} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {compareList.map((v) => (
            <div key={v.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
              <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '80%', fontWeight: 500 }}>
                {v.brand} {v.model}
              </div>
              <button 
                type="button"
                onClick={() => removeVehicle(v.id)}
                aria-label={`Retirer ${v.brand} ${v.model}`}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--accent-red)',
                  minWidth: 36,
                  minHeight: 36,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <X size={16} />
              </button>
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', gap: 8, marginTop: 4 }}>
          <button 
            type="button"
            onClick={clearCompare}
            className="btn btn--outline" 
            style={{ flex: 1, minHeight: 44, padding: '10px 0', fontSize: '0.85rem' }}
          >
            Vider
          </button>
          <button 
            type="button"
            onClick={() => setShowComparator(true)}
            disabled={compareList.length < 2}
            className="btn btn--primary" 
            style={{ flex: 2, minHeight: 44, padding: '10px 0', fontSize: '0.85rem' }}
          >
            Comparer les véhicules
          </button>
        </div>
      </div>

      {showComparator && (
        <VehicleComparator onClose={() => setShowComparator(false)} />
      )}
    </>
  );
}
