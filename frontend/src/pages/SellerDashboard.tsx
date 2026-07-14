import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { vehicleService } from '../services/vehicleService';
import type { Vehicle } from '../types/vehicle';
import PriceEstimator from '../components/pricing/PriceEstimator';
import fr from '../i18n/fr';

const MOCK_METRICS = {
  totalViews: 1247,
  avgTrustScore: 82,
  avgPriceDiff: -5,
  activeListings: 3,
  soldListings: 1,
  pendingListings: 2,
};

export default function SellerDashboard() {
  const [listings, setListings] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [predictedPrice, setPredictedPrice] = useState<number | null>(null);

  useEffect(() => {
    vehicleService.getVehicles({ page_size: 20 })
      .then((res) => setListings(res.items))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div style={{
      background: 'var(--bg-primary)', minHeight: '100vh',
      paddingTop: 'calc(var(--nav-height) + var(--space-xl))',
    }}>
      <div style={{ maxWidth: 'var(--max-width, 1280px)', margin: '0 auto', padding: '0 var(--space-lg)' }}>
        <h1 style={{
          fontFamily: 'var(--font-display)', fontSize: '1.8rem',
          fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4,
        }}>
          {fr.dashboard.title}
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: 'var(--space-xl)' }}>
          Suivi des performances, score de confiance, alertes.
        </p>

        <div style={{
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--space-lg)', marginBottom: 'var(--space-2xl)',
        }}>
          {[
            { label: fr.dashboard.totalViews, value: MOCK_METRICS.totalViews, suffix: '' },
            { label: fr.dashboard.avgTrustScore, value: MOCK_METRICS.avgTrustScore, suffix: '%' },
            { label: fr.dashboard.priceComparison, value: MOCK_METRICS.avgPriceDiff, suffix: '%' },
            { label: fr.dashboard.activeListings, value: MOCK_METRICS.activeListings, suffix: '' },
          ].map((metric, i) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              style={{
                textAlign: 'center', padding: 'var(--space-xl)',
                background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <div style={{
                fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-display)',
                color: metric.value < 0 ? 'var(--accent-red)' : 'var(--accent-gold)',
              }}>
                {metric.value.toLocaleString('fr-FR')}{metric.suffix}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: 4 }}>
                {metric.label}
              </div>
            </motion.div>
          ))}
        </div>

        <div style={{
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          marginBottom: 'var(--space-lg)',
        }}>
          <h2 style={{
            fontFamily: 'var(--font-display)', fontSize: '1.2rem',
            fontWeight: 700, color: 'var(--text-primary)',
          }}>
            {fr.dashboard.myListings}
          </h2>
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={() => setShowCreateForm(true)} style={{
              padding: '10px 20px', background: 'var(--accent-gold)', color: '#0f1a2b',
              border: 'none', borderRadius: 'var(--radius-pill)', fontWeight: 600,
              fontSize: '0.85rem', cursor: 'pointer',
            }}>
              {fr.dashboard.createListing}
            </button>
            <button onClick={() => setShowCreateForm(true)} style={{
              padding: '10px 20px', background: 'transparent', color: 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-pill)',
              fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer',
            }}>
              {fr.dashboard.estimatePrice}
            </button>
          </div>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 'var(--space-2xl)', color: 'var(--text-muted)' }}>
            {fr.general.loading}
          </div>
        ) : listings.length === 0 ? (
          <div style={{
            textAlign: 'center', padding: 'var(--space-3xl)',
            background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
            border: '1px solid var(--border-subtle)', color: 'var(--text-muted)',
          }}>
            <p style={{ fontSize: '2rem', marginBottom: 12, opacity: 0.3 }}>📋</p>
            <p>{fr.dashboard.noListings}</p>
          </div>
        ) : (
          <div style={{
            background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
            border: '1px solid var(--border-subtle)', overflow: 'hidden',
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  {['Véhicule', 'Prix', 'Statut', 'Vues', 'Action'].map((h) => (
                    <th key={h} style={{
                      textAlign: 'left', padding: '12px 16px',
                      fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)',
                      textTransform: 'uppercase', letterSpacing: '0.05em',
                    }}>
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {listings.map((v) => (
                  <tr key={v.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.9rem' }}>
                        {v.brand} {v.model}
                      </span>
                      <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {v.year} · {v.city}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', fontWeight: 600, color: 'var(--accent-gold)' }}>
                      {v.price.toLocaleString('fr-FR')} MAD
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{
                        padding: '3px 10px', borderRadius: 'var(--radius-pill)', fontSize: '0.7rem',
                        fontWeight: 600,
                        background: v.status === 'active' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                        color: v.status === 'active' ? 'var(--accent-green)' : 'var(--accent-red)',
                      }}>
                        {v.status === 'active' ? fr.dashboard.statusActive : fr.dashboard.statusSold}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                      {Math.floor(Math.random() * 200) + 10}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <button style={{
                        padding: '4px 12px', background: 'transparent', color: 'var(--text-muted)',
                        border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-pill)',
                        fontSize: '0.75rem', cursor: 'pointer',
                      }}>
                        Modifier
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <AnimatePresence>
        {showCreateForm && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed', inset: 0, zIndex: 1000,
              background: 'rgba(0,0,0,0.6)', display: 'flex',
              alignItems: 'center', justifyContent: 'center',
              padding: 24,
            }}
            onClick={() => setShowCreateForm(false)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              onClick={(e) => e.stopPropagation()}
              style={{
                width: '100%', maxWidth: 720, maxHeight: '90vh', overflowY: 'auto',
                background: 'var(--bg-primary)', borderRadius: 'var(--radius-card)',
                border: '1px solid var(--border-subtle)', padding: 'var(--space-xl)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                <h2 style={{ fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Nouvelle annonce
                </h2>
                <button onClick={() => setShowCreateForm(false)} style={{
                  width: 32, height: 32, borderRadius: '50%', border: 'none',
                  background: 'var(--bg-elevated)', color: 'var(--text-muted)',
                  fontSize: '1.1rem', cursor: 'pointer', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                }}>
                  ✕
                </button>
              </div>

              <PriceEstimator onPriceChange={setPredictedPrice} />

              {predictedPrice && (
                <div style={{
                  marginTop: 16, padding: 12, textAlign: 'center',
                  background: 'var(--bg-elevated)', borderRadius: 'var(--radius-card)',
                }}>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Prix suggéré par l'IA :
                  </span>
                  <span style={{
                    display: 'block', fontSize: '1.5rem', fontWeight: 800,
                    color: 'var(--accent-gold)', marginTop: 4,
                  }}>
                    {predictedPrice.toLocaleString('fr-FR')} MAD
                  </span>
                </div>
              )}

              <button onClick={() => setShowCreateForm(false)} style={{
                width: '100%', marginTop: 20, padding: '12px 24px',
                background: 'var(--accent-gold)', color: '#0f1a2b',
                border: 'none', borderRadius: 'var(--radius-pill)',
                fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer',
              }}>
                Publier l'annonce
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
