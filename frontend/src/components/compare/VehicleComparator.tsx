import React, { useEffect, useState } from 'react';
import { X, Sparkles, AlertCircle } from 'lucide-react';
import { useCompare } from '../../context/CompareContext';
import { compareService, CompareResponse } from '../../services/compareService';

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
  
  const conditionScores = data?.vehicles.map(v => v.condition_score || 0) || [];
  const maxCondition = conditionScores.length ? Math.max(...conditionScores) : 0;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
      zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        background: 'var(--bg-surface)', width: '100%', maxWidth: '1200px',
        maxHeight: '90vh', borderRadius: 'var(--radius-card)',
        display: 'flex', flexDirection: 'column', overflow: 'hidden',
        boxShadow: '0 24px 60px rgba(0,0,0,0.2)'
      }}>
        {/* Header */}
        <div style={{
          padding: '20px 24px', borderBottom: '1px solid var(--border-subtle)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          background: 'var(--bg-elevated)'
        }}>
          <h2 style={{ margin: 0, fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: 10 }}>
            <Sparkles color="var(--accent-gold)" />
            Comparateur Intelligent
          </h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
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
              <div style={{ color: 'var(--text-muted)' }}>Génération de la synthèse IA (Llama 3.3)...</div>
            </div>
          ) : error ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent-red)', padding: 20 }}>
              <AlertCircle />
              {error}
            </div>
          ) : data && (
            <>
              {/* Verdict IA */}
              <div style={{
                background: 'rgba(234,179,8,0.05)', border: '1px solid var(--accent-gold)',
                borderRadius: 'var(--radius-card)', padding: '20px', marginBottom: '32px'
              }}>
                <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Sparkles size={18} /> Verdict IA
                </h3>
                <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: '0.95rem' }}>
                  {data.ai_verdict.split('\n').map((line, i) => (
                    <p key={i} style={{ margin: line ? '0 0 8px 0' : 0 }}>{line}</p>
                  ))}
                </div>
              </div>

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
                      {v.images?.[0] ? (
                        <img src={v.images[0].file_path} alt={v.model} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                      ) : (
                        <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>Sans image</div>
                      )}
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

                        {/* Score IA (Carrosserie) */}
                        <div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>Score Carrosserie (IA)</div>
                          <div style={{ 
                            fontSize: '1rem', fontWeight: 600,
                            color: (v.condition_score || 0) === maxCondition && maxCondition > 0 ? 'var(--accent-gold)' : 'var(--text-primary)'
                          }}>
                            {v.condition_score ? `${v.condition_score} / 100` : 'N/A'}
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
