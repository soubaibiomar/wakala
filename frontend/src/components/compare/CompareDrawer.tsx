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
        bottom: 24,
        right: 24,
        zIndex: 100,
        background: 'var(--bg-elevated)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-card)',
        boxShadow: '0 12px 40px rgba(0,0,0,0.15)',
        padding: 16,
        width: 320,
        display: 'flex',
        flexDirection: 'column',
        gap: 12
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Scale size={18} color="var(--accent-gold)" />
            Comparateur ({compareList.length}/4)
          </h4>
          <button 
            onClick={() => setDrawerOpen(false)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}
          >
            <X size={20} />
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {compareList.map((v) => (
            <div key={v.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
              <div style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '80%' }}>
                {v.brand} {v.model}
              </div>
              <button 
                onClick={() => removeVehicle(v.id)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--accent-red)' }}
              >
                <X size={14} />
              </button>
            </div>
          ))}
        </div>

        <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
          <button 
            onClick={clearCompare}
            className="btn btn--outline" 
            style={{ flex: 1, padding: '6px 0', fontSize: '0.85rem' }}
          >
            Vider
          </button>
          <button 
            onClick={() => setShowComparator(true)}
            disabled={compareList.length < 2}
            className="btn btn--primary" 
            style={{ flex: 2, padding: '6px 0', fontSize: '0.85rem' }}
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
