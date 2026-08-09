import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { vehicleService, reviewService } from '../services/vehicleService';
import { pricingService } from '../services/pricingService';
import { messageService } from '../services/messageService';
import { favoriteService } from '../services/favoriteService';

import { formatDistanceToNow } from 'date-fns';
import { fr as dateFnsFr } from 'date-fns/locale';
import type { Vehicle } from '../types/vehicle';
import type { Review } from '../types/listing';
import type { PricePredictionResult } from '../services/pricingService';
import { FUEL_LABELS, BODY_LABELS, TRANSMISSION_LABELS } from '../types/vehicle';
import { useAuth } from '../context/AuthContext';
import fr from '../i18n/fr';
import PriceBadge from '../components/pricing/PriceBadge';
import VehicleSEO from '../components/seo/VehicleSEO';
import FormattedDescription from '../components/formatted-description/FormattedDescription';

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
        Aperçu Rapide
      </h3>
      <table className="vehicle-specs">
        <tbody>
          {specs.slice(0, 5).map((s) => (
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

function DetailedTechSpecs({ vehicle }: { vehicle: Vehicle }) {
  const specs = [
    {
      category: "Informations Générales",
      items: [
        { label: "Marque", value: vehicle.brand },
        { label: "Modèle", value: vehicle.model },
        { label: "Année", value: String(vehicle.year) },
        { label: "Kilométrage", value: vehicle.mileage === 0 && vehicle.year >= new Date().getFullYear() - 2 ? "Neuf" : vehicle.mileage === 0 || vehicle.mileage === -1 ? "N/C" : `${vehicle.mileage.toLocaleString('fr-FR')} km` },
        { label: "Ville", value: vehicle.city },
      ]
    },
    {
      category: "Moteur & Performances",
      items: [
        { label: "Énergie", value: FUEL_LABELS[vehicle.fuel_type] || vehicle.fuel_type },
        { label: "Puissance fiscale", value: vehicle.engine_power_hp ? `${vehicle.engine_power_hp} CV` : '—' },
        { label: "Boîte de vitesses", value: TRANSMISSION_LABELS[vehicle.transmission] || vehicle.transmission },
      ]
    },
    {
      category: "Carrosserie & Dimensions",
      items: [
        { label: "Type", value: BODY_LABELS[vehicle.body_type] || vehicle.body_type },
        { label: "Nombre de portes", value: String(vehicle.doors) },
        { label: "Nombre de places", value: String(vehicle.seats) },
        { label: "Couleur", value: vehicle.color || '—' },
      ]
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.25 }}
      style={{
        padding: '32px',
        background: '#f7f6f2',
        borderRadius: '12px',
        marginBottom: '32px',
        color: '#1a202c'
      }}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        {specs.map((section) => (
          <div key={section.category}>
            <div style={{ 
              backgroundColor: '#efece1',
              padding: '16px 20px',
              borderRadius: '8px',
              borderLeft: '5px solid #bba14f',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center'
            }}>
              <h4 style={{ 
                fontSize: '1.2rem', 
                fontWeight: 700, 
                color: '#1a202c', 
                margin: 0
              }}>
                {section.category}
              </h4>
            </div>
            
            <div style={{ padding: '0 20px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '1rem' }}>
                <tbody>
                  {section.items.map((item) => (
                    <tr key={item.label}>
                      <td style={{ padding: '16px 0', color: '#7b8b9a', width: '40%', fontWeight: 500 }}>
                        {item.label}
                      </td>
                      <td style={{ padding: '16px 0', color: '#101820', fontWeight: 700 }}>
                        {item.value}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

export default function VehicleDetail() {
  const { id: routeId, brandName, modelName, versionSlug } = useParams<{ id?: string, brandName?: string, modelName?: string, versionSlug?: string }>();
  
  // Extrait le short ID de 8 caractères à la fin de l'URL pour les occasions (ex: renault-clio-2015-8d284cc3)
  const shortIdRegex = /-([0-9a-f]{8})$/i;
  // Ou l'ancien UUID pour compatibilité
  const uuidRegex = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  
  const extractedId = routeId ? (routeId.match(uuidRegex)?.[0] || routeId.match(shortIdRegex)?.[1] || routeId) : undefined;

  
  const { user, isAuthenticated } = useAuth();
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [marketPrice, setMarketPrice] = useState<PricePredictionResult | null>(null);
  
  // Offer modal state
  const [showOfferModal, setShowOfferModal] = useState(false);
  const [offerAmount, setOfferAmount] = useState('');
  const [offerMessage, setOfferMessage] = useState('');
  const [offerLoading, setOfferLoading] = useState(false);
  
  // Chat Modal State
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatSending, setChatSending] = useState(false);
  const [chatSuccess, setChatSuccess] = useState(false);
  
  const [priceLoading, setPriceLoading] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  useEffect(() => {
    if (!extractedId && !versionSlug) return;
    setLoading(true);
    setError(null);

    const fetchVehicle = brandName && modelName && versionSlug
      ? vehicleService.getVehicleBySlug(brandName, modelName, versionSlug)
      : vehicleService.getVehicleById(extractedId!);

    fetchVehicle
      .then((v) => {
        setVehicle(v);
        if (isAuthenticated) {
          favoriteService.getFavorites().then(favorites => {
            setIsFavorite(favorites.some(fav => fav.id === v.id));
          }).catch(console.error);
        }
        return reviewService.getReviews({ vehicle_id: v.id, limit: 10 }).catch(() => []);
      })
      .then((r) => {
        setReviews(r);
      })
      .catch((err) => {
        console.error('Erreur chargement véhicule:', err);
        setError(err.response?.status === 404 ? fr.error.notFound : fr.error.generic);
      })
      .finally(() => setLoading(false));
  }, [extractedId, versionSlug, brandName, modelName, isAuthenticated]);

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
                  <h3 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-display)', fontWeight: 700, marginBottom: 16, color: 'var(--text-primary)' }}>
                    Description & Fiche Technique
                  </h3>
                  <div className="markdown-content">
                    <FormattedDescription text={vehicle.description} />
                  </div>
                </motion.div>
              )}

              <DetailedTechSpecs vehicle={vehicle} />

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
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 8 }}>
                    {vehicle.version}
                  </p>
                )}
                
                {/* Indicateur de fraîcheur GEO */}
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 16 }}>
                  Mise à jour {vehicle.updated_at ? formatDistanceToNow(new Date(vehicle.updated_at), { addSuffix: true, locale: dateFnsFr }) : 'récemment'}
                </p>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: 4 }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent-gold)' }}>
                    {vehicle.price.toLocaleString('fr-FR')} {fr.vehicle.mad}
                  </div>
                </div>



                <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
                  <button
                    id="cta-contact-seller"
                    style={{
                      flex: 1, padding: '14px 24px', background: 'var(--accent-gold)',
                      color: '#0f1a2b', border: 'none', borderRadius: 'var(--radius-pill)',
                      fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer',
                    }}
                    onClick={() => {
                      if (!isAuthenticated) window.location.href = '/login';
                      else setIsChatOpen(true);
                    }}
                  >
                    {isAuthenticated ? fr.vehicle.contact : fr.auth.loginTitle}
                  </button>
                  
                  <button
                    onClick={() => {
                      if (!isAuthenticated) window.location.href = '/login';
                      else {
                        setOfferAmount(vehicle.price.toString());
                        setShowOfferModal(true);
                      }
                    }}
                    style={{
                      flex: 1, padding: '14px 24px', background: 'transparent',
                      color: 'var(--text-primary)', border: '2px solid var(--accent-gold)', 
                      borderRadius: 'var(--radius-pill)',
                      fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer',
                    }}
                  >
                    Faire une offre
                  </button>
                </div>


                <button
                  onClick={async () => {
                    if (!isAuthenticated) {
                      window.location.href = `/login?returnUrl=/vehicle/${vehicle.id}`;
                      return;
                    }
                    try {
                      setFavoriteLoading(true);
                      if (isFavorite) {
                        await favoriteService.removeFavorite(vehicle.id);
                        setIsFavorite(false);
                      } else {
                        await favoriteService.addFavorite(vehicle.id);
                        setIsFavorite(true);
                      }
                    } catch (error) {
                      console.error("Failed to toggle favorite:", error);
                    } finally {
                      setFavoriteLoading(false);
                    }
                  }}
                  disabled={favoriteLoading}
                  style={{
                    width: '100%', padding: '12px 24px', background: 'transparent',
                    color: isFavorite ? 'var(--accent-red)' : 'var(--text-secondary)', border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-pill)', fontWeight: 600, fontSize: '0.9rem',
                    cursor: favoriteLoading ? 'wait' : 'pointer',
                  }}>
                  {isFavorite ? '♥' : '♡'} {fr.general.save}
                </button>



                <SpecsGrid vehicle={vehicle} />
              </motion.div>
            </div>
          </div>
        </div>
      </div>

      {/* Offer Modal */}
      {showOfferModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000 }}>
          <div style={{ background: 'var(--bg-surface)', padding: 32, borderRadius: 'var(--radius-card)', width: 400, border: '1px solid var(--border-subtle)' }}>
            <h3 style={{ margin: '0 0 16px 0' }}>Faire une offre</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 24, fontSize: '0.9rem' }}>Proposez un prix au vendeur. Si l'offre est acceptée, vous pourrez finaliser la transaction.</p>
            
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', marginBottom: 8, fontWeight: 600, fontSize: '0.9rem' }}>Votre prix (DH)</label>
              <input 
                type="number" 
                value={offerAmount} 
                onChange={e => setOfferAmount(e.target.value)}
                style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-input)', border: '1px solid var(--border-subtle)', background: 'var(--bg-elevated)', color: 'white', fontSize: '1.1rem', fontWeight: 600 }}
              />
            </div>
            
            <div style={{ marginBottom: 24 }}>
              <label style={{ display: 'block', marginBottom: 8, fontWeight: 600, fontSize: '0.9rem' }}>Message (optionnel)</label>
              <textarea 
                value={offerMessage} 
                onChange={e => setOfferMessage(e.target.value)}
                rows={3}
                placeholder="Ex: Je suis très intéressé, paiement comptant."
                style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-input)', border: '1px solid var(--border-subtle)', background: 'var(--bg-elevated)', color: 'white' }}
              />
            </div>
            
            <div style={{ display: 'flex', gap: 12 }}>
              <button 
                onClick={() => setShowOfferModal(false)}
                style={{ flex: 1, padding: '12px', background: 'transparent', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-pill)', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                Annuler
              </button>
              <button 
                onClick={async () => {
                  try {
                    setOfferLoading(true);
                    const { offerService } = await import('../services/offerService');
                    await offerService.createOffer({
                      vehicle_id: vehicle.id,
                      amount: Number(offerAmount),
                      message: offerMessage
                    });
                    setShowOfferModal(false);
                    alert("Offre envoyée avec succès ! Vous pouvez la suivre dans votre tableau de bord.");
                  } catch (e: any) {
                    alert(e.response?.data?.detail || "Erreur lors de l'envoi de l'offre.");
                  } finally {
                    setOfferLoading(false);
                  }
                }}
                disabled={offerLoading || !offerAmount}
                style={{ flex: 1, padding: '12px', background: 'var(--accent-gold)', border: 'none', borderRadius: 'var(--radius-pill)', color: '#111827', fontWeight: 600, cursor: offerLoading ? 'wait' : 'pointer' }}>
                {offerLoading ? 'Envoi...' : 'Envoyer l\'offre'}
              </button>
            </div>
          </div>
        </div>
      )}

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
