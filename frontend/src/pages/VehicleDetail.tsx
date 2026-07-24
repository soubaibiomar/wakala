import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { vehicleService, reviewService } from '../services/vehicleService';
import { pricingService } from '../services/pricingService';
import type { Vehicle } from '../types/vehicle';
import type { Review } from '../types/listing';
import type { PricePredictionResult } from '../services/pricingService';
import { FUEL_LABELS, BODY_LABELS, TRANSMISSION_LABELS } from '../types/vehicle';
import TrustScore from '../components/trust-score/TrustScore';
import { useAuth } from '../context/AuthContext';
import fr from '../i18n/fr';
import PriceBadge from '../components/pricing/PriceBadge';
import VehicleSEO from '../components/seo/VehicleSEO';
import './VehicleDetail.css';

function DetailSkeleton() {
  return (
    <div style={{ maxWidth: 'var(--max-width, 1280px)', margin: '0 auto', padding: 'var(--space-xl)' }}>
      <div className="vehicle-detail-grid">
        <div>
          <div style={{ height: 420, borderRadius: 'var(--radius-card)', marginBottom: 24, background: 'var(--bg-surface)' }} />
          <div style={{ height: 150, borderRadius: 'var(--radius-card)', background: 'var(--bg-surface)' }} />
        </div>
        <div style={{ height: 550, borderRadius: 'var(--radius-card)', background: 'var(--bg-surface)' }} />
      </div>
    </div>
  );
}

function DetailError({ message }: { message: string }) {
  return (
    <div style={{ maxWidth: 'var(--max-width, 1280px)', margin: '0 auto', textAlign: 'center', padding: '80px 24px' }}>
      <p style={{ fontSize: '3rem', marginBottom: 16 }}>⚠️</p>
      <h2 style={{ fontFamily: 'var(--font-display)', marginBottom: 8, color: 'var(--text-primary)' }}>{message}</h2>
      <Link to="/catalogue" style={{
        display: 'inline-flex', padding: '12px 24px', background: 'var(--accent-gold)',
        color: '#0f1a2b', borderRadius: 'var(--radius-pill)', fontWeight: 600,
        textDecoration: 'none', marginTop: 16,
      }}>
        {fr.general.back}
      </Link>
    </div>
  );
}

function ReviewsList({ reviews }: { reviews: Review[] }) {
  if (reviews.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      style={{
        padding: 'var(--space-lg)', marginTop: 'var(--space-lg)',
        background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
        border: '1px solid var(--border-subtle)',
      }}
    >
      <h3 style={{ fontSize: '1rem', fontFamily: 'var(--font-display)', fontWeight: 700, marginBottom: 16, color: 'var(--text-primary)' }}>
        Avis ({reviews.length})
      </h3>
      {reviews.map((r) => (
        <div key={r.id} style={{
          padding: '12px 0', borderBottom: '1px solid var(--border-subtle)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
            <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-gold)' }}>
              {'★'.repeat(r.rating)}{'☆'.repeat(5 - r.rating)}
            </span>
            {r.sentiment_label && (
              <span style={{
                padding: '2px 8px', borderRadius: 'var(--radius-pill)',
                fontSize: '0.65rem', fontWeight: 600, textTransform: 'uppercase',
                background: r.sentiment_label === 'positive' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                color: r.sentiment_label === 'positive' ? 'var(--accent-green)' : 'var(--accent-red)',
              }}>
                {r.sentiment_label}
              </span>
            )}
          </div>
          {r.title && <p style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 4, color: 'var(--text-primary)' }}>{r.title}</p>}
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{r.comment}</p>
          {r.author && (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4, display: 'block' }}>
              — {r.author.name}
            </span>
          )}
        </div>
      ))}
    </motion.div>
  );
}

function SpecsGrid({ vehicle }: { vehicle: Vehicle }) {
  const specs = [
    { label: fr.vehicle.year, value: String(vehicle.year) },
    { label: fr.vehicle.mileage, value: `${vehicle.mileage.toLocaleString('fr-FR')} km` },
    { label: fr.vehicle.fuel, value: FUEL_LABELS[vehicle.fuel_type] || vehicle.fuel_type },
    { label: fr.vehicle.bodyType, value: BODY_LABELS[vehicle.body_type] || vehicle.body_type },
    { label: fr.vehicle.transmission, value: TRANSMISSION_LABELS[vehicle.transmission] || vehicle.transmission },
    { label: fr.vehicle.power, value: vehicle.engine_power_hp ? `${vehicle.engine_power_hp} ch` : '—' },
    { label: fr.vehicle.doors, value: String(vehicle.doors) },
    { label: fr.vehicle.seats, value: String(vehicle.seats) },
    { label: fr.vehicle.color, value: vehicle.color || '—' },
    { label: fr.vehicle.city, value: vehicle.city },
  ];

  return (
    <div style={{ marginTop: 20 }}>
      <h3 style={{
        fontSize: '0.85rem', fontFamily: 'var(--font-display)', fontWeight: 700,
        marginBottom: 12, color: 'var(--text-secondary)',
      }}>
        Caractéristiques
      </h3>
      <table className="vehicle-specs">
        <tbody>
          {specs.map((s) => (
            <tr key={s.label}>
              <th>{s.label}</th>
              <td>{s.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function VehicleDetail() {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated } = useAuth();
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [marketPrice, setMarketPrice] = useState<PricePredictionResult | null>(null);
  const [priceLoading, setPriceLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);

    Promise.all([
      vehicleService.getVehicleById(id),
      reviewService.getReviews({ vehicle_id: id, limit: 10 }).catch(() => []),
    ])
      .then(([v, r]) => {
        setVehicle(v);
        setReviews(r);
      })
      .catch((err) => {
        console.error('Erreur chargement véhicule:', err);
        setError(err.response?.status === 404 ? fr.error.notFound : fr.error.generic);
      })
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (!vehicle) return;
    setPriceLoading(true);
    pricingService.predict({
      brand: vehicle.brand,
      model: vehicle.model,
      year: vehicle.year,
      mileage: vehicle.mileage,
      fuel_type: vehicle.fuel_type,
      body_type: vehicle.body_type,
      transmission: vehicle.transmission,
      engine_power_hp: vehicle.engine_power_hp ?? null,
      doors: vehicle.doors,
      seats: vehicle.seats,
      city: vehicle.city,
    })
      .then(setMarketPrice)
      .catch(() => {})
      .finally(() => setPriceLoading(false));
  }, [vehicle]);

  if (loading) return <DetailSkeleton />;
  if (error || !vehicle) return <DetailError message={error || fr.error.notFound} />;

  return (
    <>
      <VehicleSEO vehicle={vehicle} />
      <div style={{ background: 'var(--bg-primary)', minHeight: '100vh', paddingTop: 'calc(var(--nav-height) + var(--space-xl))' }}>
      <div style={{ maxWidth: 'var(--max-width, 1280px)', margin: '0 auto', padding: '0 var(--space-lg)' }}>
        <nav style={{ marginBottom: 'var(--space-lg)', fontSize: '0.85rem' }} aria-label="Fil d'Ariane">
          <Link to="/" style={{ color: 'var(--text-muted)' }}>{fr.nav.home}</Link>
          <span style={{ margin: '0 8px', color: 'var(--text-muted)' }}>/</span>
          <Link to="/catalogue" style={{ color: 'var(--text-muted)' }}>{fr.nav.catalogue}</Link>
          <span style={{ margin: '0 8px', color: 'var(--text-muted)' }}>/</span>
          <span style={{ color: 'var(--text-secondary)' }}>{vehicle.brand} {vehicle.model}</span>
        </nav>

        <div className="vehicle-detail-grid">
          <div>
            <motion.div
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              style={{
                height: 420,
                background: 'linear-gradient(135deg, var(--bg-elevated), var(--bg-surface))',
                borderRadius: 'var(--radius-card)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                border: '1px solid var(--border-subtle)', position: 'relative',
                marginBottom: 'var(--space-lg)', overflow: 'hidden',
              }}
            >
              <span style={{ fontSize: '5rem', opacity: 0.15 }}>🚗</span>
              <div style={{
                position: 'absolute', bottom: 12, left: '50%', transform: 'translateX(-50%)',
                padding: '4px 12px', background: 'rgba(0,0,0,0.7)',
                borderRadius: 'var(--radius-pill)', fontSize: '0.65rem',
                color: 'var(--accent-gold)', display: 'flex', alignItems: 'center', gap: 6,
              }}>
                <span style={{ opacity: 0.6 }}>🛡️</span>
                {fr.vehicle.plateBlurred}
              </div>
              {vehicle.condition_score != null && (
                <span style={{
                  position: 'absolute', top: 16, right: 16,
                  padding: '8px 14px', borderRadius: 'var(--radius-pill)',
                  fontSize: '0.8rem', fontWeight: 600,
                  background: 'rgba(16,185,129,0.15)', color: 'var(--accent-green)',
                }}>
                  État IA : {vehicle.condition_score}/100
                </span>
              )}
            </motion.div>

            {vehicle.description && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                style={{
                  padding: 'var(--space-lg)',
                  background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
                  border: '1px solid var(--border-subtle)', marginBottom: 'var(--space-lg)',
                }}
              >
                <h3 style={{ fontSize: '1rem', fontFamily: 'var(--font-display)', fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)' }}>
                  Description
                </h3>
                <p style={{ color: 'var(--text-secondary)', lineHeight: 1.8, fontSize: '0.9rem', whiteSpace: 'pre-line' }}>
                  {vehicle.description}
                </p>
              </motion.div>
            )}

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
              style={{
                padding: 'var(--space-lg)',
                background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
                border: '1px solid var(--border-subtle)', marginBottom: 'var(--space-lg)',
              }}
            >
              <h3 style={{
                fontSize: '1rem', fontFamily: 'var(--font-display)', fontWeight: 700,
                marginBottom: 16, color: 'var(--text-primary)',
              }}>
                {fr.vehicle.trustScore}
              </h3>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 'var(--space-lg)',
                flexWrap: 'wrap',
              }}>
                <TrustScore score={vehicle.condition_score ?? 85} />
                <div style={{ flex: 1, minWidth: 200 }}>
                  {[
                    { label: fr.trust.verifiedSeller, value: vehicle.seller?.is_verified ? 100 : 50 },
                    { label: fr.trust.documentedMaintenance, value: 80 },
                    { label: fr.trust.availableHistory, value: 70 },
                  ].map((item) => (
                    <div key={item.label} style={{ marginBottom: 8 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 3 }}>
                        <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                        <span style={{ color: 'var(--accent-gold)', fontWeight: 600 }}>{item.value}%</span>
                      </div>
                      <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2 }}>
                        <div style={{
                          width: `${item.value}%`, height: '100%',
                          background: 'var(--accent-gold)', borderRadius: 2,
                          transition: 'width 1s ease',
                        }} />
                      </div>
                    </div>
                  ))}
                  <div style={{ marginTop: 8, fontSize: '0.7rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                    <span>🛡️</span> {fr.trust.cndpCompliant}
                  </div>
                </div>
              </div>
            </motion.div>

            <ReviewsList reviews={reviews} />
          </div>

          <div style={{ position: 'sticky', top: 'calc(var(--nav-height) + 24px)' }}>
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              style={{
                padding: 'var(--space-xl)',
                background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              <h1 style={{ fontSize: '1.6rem', fontFamily: 'var(--font-display)', fontWeight: 800, marginBottom: 4, color: 'var(--text-primary)' }}>
                {vehicle.brand} {vehicle.model} - {vehicle.year}
              </h1>
              {vehicle.version && (
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 16 }}>
                  {vehicle.version}
                </p>
              )}

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: 4 }}>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent-gold)' }}>
                  {vehicle.price.toLocaleString('fr-FR')} {fr.vehicle.mad}
                </div>
                {marketPrice && (
                  <PriceBadge price={vehicle.price} predictedPrice={marketPrice.predicted_price} />
                )}
              </div>

              {vehicle.predicted_price != null && !marketPrice && (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8, fontSize: '0.85rem' }}>
                  <span style={{
                    padding: '2px 8px', borderRadius: 'var(--radius-pill)', fontSize: '0.65rem',
                    fontWeight: 600, background: 'rgba(91,192,222,0.15)', color: 'var(--accent-cyan)',
                  }}>
                    IA
                  </span>
                  <span style={{ color: 'var(--text-secondary)' }}>
                    {fr.vehicle.estimatedPrice} : {vehicle.predicted_price.toLocaleString('fr-FR')} {fr.vehicle.mad}
                  </span>
                  {vehicle.price_confidence != null && (
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                      ({(vehicle.price_confidence * 100).toFixed(0)}%)
                    </span>
                  )}
                </div>
              )}
              {priceLoading ? (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 20 }}>
                  Estimation marché en cours...
                </div>
              ) : marketPrice && (
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 8, marginBottom: 20, fontSize: '0.85rem',
                  padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-card)',
                }}>
                  <span style={{
                    padding: '2px 8px', borderRadius: 'var(--radius-pill)', fontSize: '0.65rem',
                    fontWeight: 600, background: 'rgba(16,185,129,0.15)', color: 'var(--accent-green)',
                  }}>
                    Marché
                  </span>
                  <span style={{ color: 'var(--text-secondary)' }}>
                    Prix marché estimé : {marketPrice.predicted_price.toLocaleString('fr-FR')} {fr.vehicle.mad}
                  </span>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                    ({marketPrice.confidence_interval.low.toLocaleString('fr-FR', { maximumFractionDigits: 0 })} – {marketPrice.confidence_interval.high.toLocaleString('fr-FR', { maximumFractionDigits: 0 })})
                  </span>
                </div>
              )}

              <button
                id="cta-contact-seller"
                style={{
                  width: '100%', padding: '14px 24px', background: 'var(--accent-gold)',
                  color: '#0f1a2b', border: 'none', borderRadius: 'var(--radius-pill)',
                  fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer',
                  marginBottom: 12,
                }}
                onClick={() => {
                  if (!isAuthenticated) window.location.href = '/login';
                  else alert('Contacter le vendeur (Simulation)');
                }}
              >
                {isAuthenticated ? fr.vehicle.contact : fr.auth.loginTitle}
              </button>

              <button 
                onClick={() => alert('Véhicule sauvegardé !')}
                style={{
                  width: '100%', padding: '12px 24px', background: 'transparent',
                  color: 'var(--text-secondary)', border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-pill)', fontWeight: 600, fontSize: '0.9rem',
                  cursor: 'pointer',
              }}>
                ♡ {fr.general.save}
              </button>

              {vehicle.seller && (
                <div style={{
                  marginTop: 20, padding: 16,
                  background: 'var(--bg-elevated)',
                  borderRadius: 'var(--radius-card)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <div style={{
                      width: 40, height: 40, borderRadius: '50%',
                      background: 'var(--accent-gold)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontWeight: 700, fontSize: '1rem', color: '#0f1a2b',
                    }}>
                      {vehicle.seller.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                        {vehicle.seller.name}
                        {vehicle.seller.is_verified && (
                          <span style={{
                            padding: '2px 6px', borderRadius: 'var(--radius-pill)', fontSize: '0.6rem',
                            fontWeight: 600, background: 'rgba(16,185,129,0.15)', color: 'var(--accent-green)',
                          }}>
                            ✓ {fr.trust.verifiedSeller}
                          </span>
                        )}
                      </div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                        {vehicle.seller.role === 'seller' ? 'Vendeur professionnel' : vehicle.seller.role}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <SpecsGrid vehicle={vehicle} />
            </motion.div>
          </div>
        </div>
      </div>
    </div>
    </>
  );
}
