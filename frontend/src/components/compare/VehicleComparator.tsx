import React, { useEffect, useState } from 'react';
import { X, Scale, AlertCircle } from 'lucide-react';
import { useCompare } from '../../context/CompareContext';
import { compareService, CompareResponse } from '../../services/compareService';
import { resolveVehicleImage } from '../../utils/vehicleImageResolver';
import type { Vehicle } from '../../types/vehicle';

export default function VehicleComparator({ onClose }: { onClose: () => void }) {
  const { compareList } = useCompare();
  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchComparison = async () => {
      try {
        const response = await compareService.getComparison(compareList.map(v => v.id));
        setData(response);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Erreur lors de la comparaison.");
      } finally {
        setLoading(false);
      }
    };
    fetchComparison();
  }, [compareList]);

  // Find min/max for highlighting
  const prices = data?.vehicles.map(v => v.price) || [];
  const minPrice = prices.length ? Math.min(...prices) : 0;
  
  const mileages = data?.vehicles.map(v => v.mileage || 0) || [];
  const minMileage = mileages.length ? Math.min(...mileages) : 0;

  const getVehicleImage = (vehicle: Vehicle) => {
    const storedImage = vehicle.images?.[0]?.file_path;
    return storedImage || resolveVehicleImage(vehicle.brand, vehicle.model) || '/assets/car-side-fallback.svg';
  };
  
  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
      zIndex: 1200, display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 'min(20px, 2.5vw)'
    }}>
      <div style={{
        background: 'var(--bg-surface)', width: '100%', maxWidth: '1200px',
        maxHeight: 'min(92dvh, 900px)', borderRadius: 'var(--radius-card)',
        display: 'flex', flexDirection: 'column', overflow: 'hidden',
        boxShadow: '0 24px 60px rgba(0,0,0,0.2)'
      }}>
        {/* Header */}
        <div style={{
          padding: '14px 18px',
          paddingTop: 'calc(14px + env(safe-area-inset-top, 0px))',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          background: 'var(--bg-elevated)'
        }}>
          <h2 style={{ margin: 0, fontSize: '1.15rem', display: 'flex', alignItems: 'center', gap: 10 }}>
            <Scale color="var(--accent-gold)" />
            Comparateur de véhicules
          </h2>
          <button 
            type="button"
            onClick={onClose} 
            aria-label="Fermer le comparateur"
            style={{ 
              background: 'none', 
              border: 'none', 
              cursor: 'pointer', 
              color: 'var(--text-muted)',
              minWidth: 44,
              minHeight: 44,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: 8
            }}
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px', overflowY: 'auto', flex: 1 }}>
          {loading ? (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200, flexDirection: 'column', gap: 16 }}>
              <div className="spinner" style={{
                width: 40, height: 40, border: '3px solid var(--border-subtle)',
                borderTopColor: 'var(--accent-gold)', borderRadius: '50%', animation: 'spin 1s linear infinite'
              }} />
              <div style={{ color: 'var(--text-muted)' }}>Chargement des données des véhicules...</div>
            </div>
          ) : error ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent-red)', padding: 20 }}>
              <AlertCircle />
              {error}
            </div>
          ) : data && (
            <>
              {/* Data Grid */}
              <div style={{
                display: 'flex', gap: '24px', overflowX: 'auto', paddingBottom: '16px'
              }}>
                {data.vehicles.map((v) => (
                  <div key={v.id} style={{
                    minWidth: '280px', flex: 1, background: 'var(--bg-elevated)',
                    border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-card)',
                    overflow: 'hidden'
                  }}>
                    <div style={{ height: 160, background: 'var(--bg-card)', position: 'relative' }}>
                      <img
                        src={getVehicleImage(v)}
                        alt={`${v.brand} ${v.model}`}
                        style={{ width: '100%', height: '100%', objectFit: 'contain', padding: 18 }}
                        onError={(event) => {
                          const target = event.currentTarget;
                          if (!target.src.endsWith('/assets/car-side-fallback.svg')) {
                            target.src = '/assets/car-side-fallback.svg';
                          }
                        }}
                      />
                    </div>
                    
                    <div style={{ padding: '20px' }}>
                      <h4 style={{ margin: '0 0 4px 0', fontSize: '1.1rem' }}>{v.brand} {v.model}</h4>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 16 }}>{v.year} • {v.fuel_type} • {v.transmission}</div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {/* Prix */}
                        <div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>Prix</div>
                          <div style={{ 
                            fontSize: '1.2rem', fontWeight: 700, 
                            color: v.price === minPrice ? 'var(--accent-green)' : 'var(--text-primary)'
                          }}>
                            {v.price.toLocaleString('fr-FR')} MAD
                          </div>
                        </div>

                        {/* Kilométrage */}
                        <div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>Kilométrage</div>
                          <div style={{ 
                            fontSize: '1rem', fontWeight: 600,
                            color: v.mileage === minMileage ? 'var(--accent-green)' : 'var(--text-primary)'
                          }}>
                            {v.mileage?.toLocaleString('fr-FR') || '0'} km
                          </div>
                        </div>

                        {/* Caractéristiques factuelles */}
                        <div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>Caractéristiques</div>
                          <div style={{ fontSize: '0.9rem', fontWeight: 600, lineHeight: 1.65 }}>
                            {v.body_type || '—'} · {v.engine_power_hp ? `${v.engine_power_hp} ch` : 'Puissance —'}<br />
                            {v.doors || '—'} portes · {v.seats || '—'} places<br />
                            {v.city || 'Ville non renseignée'}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>
      <style>{`@keyframes spin { 100% { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
