import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { vehicleService, reviewService } from '../services/vehicleService';
import { pricingService } from '../services/pricingService';
import { messageService } from '../services/messageService';
import type { Vehicle } from '../types/vehicle';
import type { Review } from '../types/listing';
import type { PricePredictionResult } from '../services/pricingService';
import { FUEL_LABELS, BODY_LABELS, TRANSMISSION_LABELS } from '../types/vehicle';
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
    { label: fr.vehicle.mileage, value: vehicle.mileage === 0 && vehicle.year >= new Date().getFullYear() - 2 ? "Neuf" : vehicle.mileage === 0 || vehicle.mileage === -1 ? "N/C" : `${vehicle.mileage.toLocaleString('fr-FR')} km` },
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
  
  // Chat Modal State
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatSending, setChatSending] = useState(false);
  const [chatSuccess, setChatSuccess] = useState(false);
  
  const [priceLoading, setPriceLoading] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

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
      .catch(() => { })
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
                {vehicle.images && vehicle.images.length > 0 ? (
                  <>
                    <img src={vehicle.images[currentImageIndex].file_path} alt={vehicle.model} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    {vehicle.images.length > 1 && (
                      <div style={{ position: 'absolute', bottom: 16, right: 16, display: 'flex', gap: 8 }}>
                        <button onClick={() => setCurrentImageIndex(prev => (prev > 0 ? prev - 1 : vehicle.images!.length - 1))} style={{ padding: '8px 12px', background: 'rgba(0,0,0,0.6)', color: '#fff', border: 'none', borderRadius: 'var(--radius-pill)', cursor: 'pointer', fontFamily: 'var(--font-sans)', fontWeight: 600 }}>◀</button>
                        <button onClick={() => setCurrentImageIndex(prev => (prev < vehicle.images!.length - 1 ? prev + 1 : 0))} style={{ padding: '8px 12px', background: 'rgba(0,0,0,0.6)', color: '#fff', border: 'none', borderRadius: 'var(--radius-pill)', cursor: 'pointer', fontFamily: 'var(--font-sans)', fontWeight: 600 }}>▶</button>
                      </div>
                    )}
                    <div style={{ position: 'absolute', bottom: 16, left: 16, background: 'rgba(0,0,0,0.6)', color: 'white', padding: '4px 10px', borderRadius: 'var(--radius-pill)', fontSize: '0.8rem', fontWeight: 600 }}>
                      {currentImageIndex + 1} / {vehicle.images.length}
                    </div>
                  </>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: 0.4 }}>
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
                      <circle cx="7" cy="17" r="2" />
                      <path d="M9 17h6" />
                      <circle cx="17" cy="17" r="2" />
                    </svg>
                    <span style={{ marginTop: 12, fontWeight: 600, fontSize: '0.9rem' }}>Image non disponible</span>
                  </div>
                )}

                <div style={{ position: 'absolute', top: 16, left: 16, display: 'flex', gap: 8 }}>
                  {vehicle.mileage === 0 && vehicle.year >= new Date().getFullYear() - 2 ? (
                    <span style={{
                      padding: '8px 14px', borderRadius: 'var(--radius-pill)',
                      fontSize: '0.8rem', fontWeight: 600,
                      background: 'var(--accent-gold)', color: '#000',
                      boxShadow: 'var(--shadow-sm)',
                    }}>
                      Neuf
                    </span>
                  ) : (
                    <span style={{
                      padding: '8px 14px', borderRadius: 'var(--radius-pill)',
                      fontSize: '0.8rem', fontWeight: 600,
                      background: 'var(--bg-surface)', color: 'var(--text-primary)',
                      border: '1px solid var(--border-subtle)',
                      boxShadow: 'var(--shadow-sm)',
                    }}>
                      Occasion
                    </span>
                  )}
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
                    display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 8, marginBottom: 20, fontSize: '0.85rem',
                    padding: '12px 16px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-card)',
                  }}>
                    <span style={{
                      padding: '4px 10px', borderRadius: 'var(--radius-pill)', fontSize: '0.65rem',
                      fontWeight: 700, background: 'rgba(16,185,129,0.15)', color: 'var(--accent-green)', textTransform: 'uppercase', letterSpacing: '0.02em',
                      flexShrink: 0
                    }}>
                      Marché
                    </span>
                    <span style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>
                      Prix marché estimé : {marketPrice.predicted_price.toLocaleString('fr-FR')} {fr.vehicle.mad}
                    </span>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem', flexShrink: 0 }}>
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
                    else setIsChatOpen(true);
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
                        {(vehicle.seller.name || vehicle.seller.full_name || 'V').charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: 6 }}>
                          {vehicle.seller.name || vehicle.seller.full_name}
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

      <AnimatePresence>
        {isChatOpen && vehicle?.seller && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
              background: 'rgba(0,0,0,0.8)', zIndex: 9999,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              padding: 20
            }}
            onClick={() => setIsChatOpen(false)}
          >
            <motion.div
              initial={{ y: 20, scale: 0.95 }}
              animate={{ y: 0, scale: 1 }}
              exit={{ y: 20, scale: 0.95 }}
              style={{
                background: 'var(--bg-primary)',
                borderRadius: 'var(--radius-card)',
                width: '100%', maxWidth: '400px',
                padding: '24px',
                boxShadow: '0 10px 40px rgba(0,0,0,0.5)'
              }}
              onClick={e => e.stopPropagation()}
            >
              <h3 style={{ margin: '0 0 16px 0', fontSize: '1.2rem' }}>
                Contacter {vehicle.seller.name || vehicle.seller.full_name}
              </h3>
              {chatSuccess ? (
                <div style={{ color: 'var(--accent-green)', textAlign: 'center', padding: '20px 0' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '10px' }}>✓</div>
                  Votre message a été envoyé avec succès. Le vendeur vous répondra dans votre Espace Messagerie.
                  <button onClick={() => setIsChatOpen(false)} style={{ marginTop: '20px', width: '100%', padding: '12px', background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: 'none', borderRadius: 'var(--radius-pill)', cursor: 'pointer' }}>
                    Fermer
                  </button>
                </div>
              ) : (
                <form onSubmit={async (e) => {
                  e.preventDefault();
                  if (!chatMessage.trim()) return;
                  setChatSending(true);
                  try {
                    await messageService.sendMessage({
                      recipient_id: vehicle.seller!.id,
                      listing_id: vehicle.id, // Assuming listing ID is same as vehicle ID for this mock or closely related
                      content: chatMessage
                    });
                    setChatSuccess(true);
                  } catch(err) {
                    console.error(err);
                    alert("Erreur lors de l'envoi du message.");
                  } finally {
                    setChatSending(false);
                  }
                }}>
                  <textarea
                    value={chatMessage}
                    onChange={e => setChatMessage(e.target.value)}
                    placeholder={`Bonjour, je suis intéressé par votre ${vehicle.brand} ${vehicle.model}...`}
                    rows={5}
                    style={{
                      width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)',
                      background: 'var(--bg-elevated)', color: 'var(--text-primary)', outline: 'none', resize: 'vertical',
                      marginBottom: '16px'
                    }}
                    required
                  />
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <button type="button" onClick={() => setIsChatOpen(false)} style={{ flex: 1, padding: '12px', background: 'transparent', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)', borderRadius: 'var(--radius-pill)', cursor: 'pointer' }}>
                      Annuler
                    </button>
                    <button type="submit" disabled={chatSending || !chatMessage.trim()} style={{ flex: 1, padding: '12px', background: 'var(--accent-gold)', border: 'none', color: '#0f1a2b', fontWeight: 600, borderRadius: 'var(--radius-pill)', cursor: 'pointer', opacity: (chatSending || !chatMessage.trim()) ? 0.5 : 1 }}>
                      {chatSending ? 'Envoi...' : 'Envoyer'}
                    </button>
                  </div>
                </form>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
