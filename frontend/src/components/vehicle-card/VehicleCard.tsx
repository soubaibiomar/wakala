/**
 * components/vehicle-card/VehicleCard.tsx — Carte véhicule réutilisable.
 * Utilisée dans Home (featured) et Catalogue (grille).
 */

import { Link } from 'react-router-dom';
import { Scale, Gauge } from 'lucide-react';
import type { Vehicle } from '../../types/vehicle';
import fr from '../../i18n/fr';
import MatchScoreBadge from '../recommendation-form/MatchScoreBadge';
import { useCompare } from '../../context/CompareContext';
import './VehicleCard.css';

interface VehicleCardProps {
  vehicle: Vehicle;
  animationDelay?: number;
  matchScore?: number;
  badges?: string[];
}

function getFallbackImage(brand: string): string {
  const b = brand.toLowerCase();
  if (b.includes('dacia')) return '/assets/dacia-logan.jpg';
  if (b.includes('mercedes') || b.includes('benz')) return '/assets/mercedes-cla.jpg';
  if (b.includes('jeep') || b.includes('dodge')) return '/assets/jeep-grand-cherokee.jpg';
  return '/assets/clio5.jpg';
}

function getSourceName(url?: string): string | null {
  if (!url) return null;
  try {
    const hostname = new URL(url).hostname.replace('www.', '');
    const name = hostname.split('.')[0];
    // Special formatting for known sources
    if (name.toLowerCase() === 'kifal-auto') return 'Kifal Auto';
    if (name.toLowerCase() === 'globaloccaz') return 'Global Occaz';
    return name.charAt(0).toUpperCase() + name.slice(1);
  } catch {
    return null;
  }
}


export default function VehicleCard({ vehicle, matchScore, badges }: VehicleCardProps) {
  const { addVehicle, compareList } = useCompare();
  const isCompared = compareList.some((v) => v.id === vehicle.id);

  // Format price securely
  const formattedPrice = new Intl.NumberFormat('fr-MA', {
    style: 'currency',
    currency: 'MAD',
    maximumFractionDigits: 0,
  }).format(vehicle.price);

  return (
    <Link to={`/vehicule/${vehicle.id}`} className="vehicle-card">
      
      {/* ─── Image Header ──────────────────────────────────────── */}
      <div className="vehicle-card__image">
        {vehicle.images && vehicle.images.length > 0 && vehicle.images[0].file_path ? (
          <img
            src={vehicle.images[0].file_path}
            alt={`${vehicle.brand} ${vehicle.model}`}
            loading="lazy"
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        ) : (
          <img
            src={getFallbackImage(vehicle.brand)}
            alt={`${vehicle.brand} ${vehicle.model}`}
            loading="lazy"
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        )}

        {/* Badges container: Trust Score & Source */}
        <div style={{
          position: 'absolute', top: 12, left: 12, 
          display: 'flex', flexDirection: 'column', gap: '8px', zIndex: 2
        }}>

          {/* Source Badge */}
          {getSourceName(vehicle.source_url) && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.9)', color: '#111827', 
              padding: '2px 8px', borderRadius: '12px', 
              fontSize: '0.7rem', fontWeight: 700,
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', gap: '4px', width: 'fit-content'
            }}>
              <span>🔗 {getSourceName(vehicle.source_url)}</span>
            </div>
          )}
        </div>
        
        {/* Render dynamic NLP matching badges if provided */}
        {badges && badges.length > 0 && (
          <div style={{ position: 'absolute', bottom: 12, left: 12, display: 'flex', gap: '4px', flexWrap: 'wrap', zIndex: 2 }}>
            {badges.map((b, idx) => (
              <span key={idx} style={{ 
                backgroundColor: 'var(--color-accent-purple, #8B5CF6)', 
                color: 'white', 
                fontSize: '0.7rem', 
                padding: '2px 8px', 
                borderRadius: '12px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
              }}>
                ✨ {b}
              </span>
            ))}
          </div>
        )}

        {matchScore !== undefined && <MatchScoreBadge score={matchScore} />}
        
        {/* Compare Button */}
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            addVehicle(vehicle);
          }}
          disabled={isCompared || compareList.length >= 4}
          style={{
            position: 'absolute', top: 12, right: 12,
            background: isCompared ? 'var(--accent-gold)' : 'rgba(0,0,0,0.5)',
            color: isCompared ? 'var(--bg-card)' : 'white',
            border: 'none', borderRadius: '50%',
            width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: (isCompared || compareList.length >= 4) ? 'not-allowed' : 'pointer',
            backdropFilter: 'blur(4px)',
            transition: 'all 0.2s ease',
            zIndex: 2
          }}
          title={isCompared ? "Déjà dans le comparateur" : "Comparer"}
        >
          <Scale size={16} />
        </button>
      </div>

      {/* ─── Body Content ──────────────────────────────────────── */}
      <div className="vehicle-card__content">
        
        {/* Header: Title + Meta */}
        <div className="vehicle-card__header">
          <div style={{ flex: 1 }}>
            <h3 className="vehicle-card__title">
              {vehicle.brand} {vehicle.model}
            </h3>
            <span className="vehicle-card__subtitle">
              Modèle {vehicle.year}
            </span>
          </div>
        </div>

        {/* Fiche Technique */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: '8px',
          marginTop: '12px',
          padding: '12px',
          background: 'rgba(255, 255, 255, 0.03)',
          borderRadius: '8px',
          border: '1px solid rgba(255, 255, 255, 0.05)',
          fontSize: '0.75rem',
          color: 'var(--text-secondary)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ color: 'var(--accent-gold)' }}>⛽</span> 
            <span style={{ textTransform: 'capitalize' }}>{vehicle.fuel_type}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ color: 'var(--accent-gold)' }}>⚙️</span> 
            <span style={{ textTransform: 'capitalize' }}>{vehicle.transmission}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ color: 'var(--accent-gold)' }}>🚗</span> 
            <span style={{ textTransform: 'capitalize' }}>{vehicle.body_type || 'Berline'}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ color: 'var(--accent-gold)' }}><Gauge size={16} /></span> 
            <span>
              {vehicle.description?.toLowerCase().includes('véhicule neuf officiel')
                ? 'Neuf' 
                : vehicle.mileage === 0 || vehicle.mileage === -1 
                  ? 'N/C' 
                  : `${vehicle.mileage.toLocaleString('fr-FR')} km`}
            </span>
          </div>
        </div>

        {/* Description Snippet */}
        {vehicle.description && (
          <p style={{
            fontSize: '0.8rem',
            color: 'var(--text-secondary)',
            margin: '8px 0 0 0',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            lineHeight: '1.4'
          }}>
            {vehicle.description}
          </p>
        )}

        {/* Footer: Price & AI Estimate */}
        <div className="vehicle-card__footer">
          <span className="vehicle-card__price">{formattedPrice}</span>
          
          {vehicle.predicted_price != null && (
            <div className="vehicle-card__estimate">
              <span>{fr.vehicle.estimatedPrice} (IA)</span>
              <strong>
                {new Intl.NumberFormat('fr-MA').format(vehicle.predicted_price)} MAD
              </strong>
            </div>
          )}
        </div>

      </div>
    </Link>
  );
}
