/**
 * components/vehicle-card/VehicleCard.tsx — Carte véhicule réutilisable.
 * Utilisée dans Home (featured), Catalogue (grille) et BrandPage.
 */

import { Link } from 'react-router-dom';
import { Scale, Gauge, ArrowRight } from 'lucide-react';
import type { Vehicle } from '../../types/vehicle';
import MatchScoreBadge from '../recommendation-form/MatchScoreBadge';
import { useCompare } from '../../context/CompareContext';
import './VehicleCard.css';

interface VehicleCardProps {
  vehicle: Vehicle;
  animationDelay?: number;
  matchScore?: number;
  badges?: string[];
  isGrouped?: boolean;
  keyFacts?: string[];
  budgetMargin?: number | null;
  bestVersionName?: string | null;
}

function getFallbackImage(brand: string, model: string): string {
  const b = brand.toLowerCase();
  if (b.includes('dacia')) return '/assets/dacia-logan.jpg';
  if (b.includes('mercedes') || b.includes('benz')) return '/assets/mercedes-cla.jpg';
  if (b.includes('jeep') || b.includes('dodge')) return '/assets/jeep-grand-cherokee.jpg';
  return `https://placehold.co/600x400/f8fafc/64748b?text=${encodeURIComponent(brand)}+${encodeURIComponent(model)}`;
}

function getSourceName(url?: string): string | null {
  if (!url) return null;
  try {
    const hostname = new URL(url).hostname.replace('www.', '');
    const name = hostname.split('.')[0];
    if (name.toLowerCase() === 'kifal-auto') return 'Kifal Auto';
    if (name.toLowerCase() === 'globaloccaz') return 'Global Occaz';
    return name.charAt(0).toUpperCase() + name.slice(1);
  } catch {
    return null;
  }
}

function stripMarkdown(text?: string | null): string {
  if (!text) return '';
  return text
    .replace(/[#*_~`>=\|]/g, '')
    .replace(/-{2,}/g, '')
    .replace(/\n+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export default function VehicleCard({
  vehicle,
  matchScore,
  badges,
  isGrouped = false,
  keyFacts,
  budgetMargin,
  bestVersionName,
}: VehicleCardProps) {
  const { addVehicle, compareList } = useCompare();
  const isCompared = compareList.some((v) => v.id === vehicle.id);

  // Format price securely
  const formattedPrice = new Intl.NumberFormat('fr-MA', {
    style: 'currency',
    currency: 'MAD',
    maximumFractionDigits: 0,
  }).format(vehicle.price);

  // Determine if this vehicle is a new model or grouped model
  const isNewOfficial = Boolean(
    isGrouped || 
    vehicle.description?.toLowerCase().includes('véhicule neuf officiel') ||
    vehicle.mileage === 0
  );

  const finalPrice = isNewOfficial ? `À partir de ${formattedPrice}` : formattedPrice;
  const shortId = vehicle.id.split('-')[0];
  const occSlug = `${vehicle.brand.toLowerCase()}-${vehicle.model.toLowerCase()}-${vehicle.year || '0'}-${shortId}`
    .replace(/[^a-z0-9\-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
  
  // Clean model name for clean URL
  const cleanModelForUrl = vehicle.model.toLowerCase().trim();
  
  const linkTo = isNewOfficial 
    ? `/marque/${encodeURIComponent(vehicle.brand.toLowerCase())}/${encodeURIComponent(cleanModelForUrl)}` 
    : `/vehicule/${occSlug}`;

  let displayDescription = vehicle.description || '';
  let versionsCount: string | null = null;
  
  if (displayDescription) {
    const regex = /À partir de.*?(\d+)\s*Versions/i;
    const match = displayDescription.match(regex);
    if (match) {
      versionsCount = match[1];
      displayDescription = displayDescription.replace(regex, '').trim();
    }
  }

  return (
    <Link to={linkTo} className="vehicle-card" title={isNewOfficial ? `Voir les versions de ${vehicle.brand} ${vehicle.model}` : `${vehicle.brand} ${vehicle.model}`}>
      
      {/* ─── Image Header ──────────────────────────────────────── */}
      <div className="vehicle-card__image">
        {vehicle.images && vehicle.images.length > 0 && vehicle.images[0].file_path ? (
          <img
            src={vehicle.images[0].file_path}
            alt={`${vehicle.brand} ${vehicle.model}`}
            loading="lazy"
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.src = getFallbackImage(vehicle.brand, vehicle.model);
            }}
          />
        ) : (
          <img
            src={getFallbackImage(vehicle.brand, vehicle.model)}
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
          {isNewOfficial && (
            <div style={{
              background: 'linear-gradient(135deg, #122135 0%, #1e3a5f 100%)',
              color: '#AE8C4E', 
              padding: '3px 10px', 
              borderRadius: '12px', 
              fontSize: '0.72rem', 
              fontWeight: 700,
              boxShadow: '0 2px 6px rgba(0,0,0,0.15)', 
              display: 'flex', 
              alignItems: 'center', 
              gap: '4px',
              border: '1px solid rgba(174, 140, 78, 0.4)'
            }}>
              <span>✨ Neuf</span>
            </div>
          )}

          {/* Source Badge */}
          {getSourceName(vehicle.source_url) && (
            <div style={{
              background: 'rgba(255, 255, 255, 0.92)', color: '#111827', 
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
            background: isCompared ? '#bba14f' : '#6b7280',
            color: 'white',
            border: 'none', borderRadius: '50%',
            width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: (isCompared || compareList.length >= 4) ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s ease',
            zIndex: 2,
            opacity: 0.9
          }}
          title={isCompared ? "Déjà dans le comparateur" : "Comparer"}
        >
          <Scale size={14} />
        </button>
      </div>

      {/* ─── Body Content ──────────────────────────────────────── */}
      <div className="vehicle-card__content">
        
        {/* Header: Title + Meta */}
        <div className="vehicle-card__header">
          <h3 className="vehicle-card__title">
            {vehicle.brand} {vehicle.model}
          </h3>
          <div className="vehicle-card__subtitle">
            {bestVersionName || `Modèle ${vehicle.year}`}
          </div>
        </div>

        {/* Fiche Technique Grid */}
        <div className="vehicle-card__specs">
          <div className="vehicle-card__specs-item">
            <span style={{ color: '#e11d48' }}>⛽</span> 
            <span style={{ textTransform: 'capitalize' }}>{vehicle.fuel_type}</span>
          </div>
          <div className="vehicle-card__specs-item">
            <span style={{ color: '#8b5cf6' }}>⚙️</span> 
            <span style={{ textTransform: 'capitalize' }}>{vehicle.transmission}</span>
          </div>
          <div className="vehicle-card__specs-item">
            <span style={{ color: '#e11d48' }}>🚗</span> 
            <span style={{ textTransform: 'capitalize' }}>{vehicle.body_type || 'Berline'}</span>
          </div>
          <div className="vehicle-card__specs-item">
            <span style={{ color: '#bba14f' }}><Gauge size={14} /></span> 
            <span>
              {isNewOfficial
                ? 'Neuf' 
                : vehicle.mileage === 0 || vehicle.mileage === -1 
                  ? 'N/C' 
                  : `${vehicle.mileage.toLocaleString('fr-FR')} km`}
            </span>
          </div>
        </div>

        {/* Faits tangibles chiffrés Wakala */}
        {keyFacts && keyFacts.length > 0 && (
          <div style={{
            margin: '8px 0 4px 0',
            padding: '6px 8px',
            background: 'rgba(59, 130, 246, 0.05)',
            borderLeft: '3px solid #3b82f6',
            borderRadius: '4px',
            display: 'flex',
            flexDirection: 'column',
            gap: '2px',
          }}>
            {keyFacts.map((fact, idx) => (
              <span key={idx} style={{ fontSize: '0.72rem', color: '#1e3a8a', fontWeight: 600 }}>
                ✓ {fact}
              </span>
            ))}
          </div>
        )}

        {/* Description Snippet (si pas de faits chiffrés) */}
        {(!keyFacts || keyFacts.length === 0) && displayDescription && !isNewOfficial && (
          <p style={{
            fontSize: '0.75rem',
            color: '#64748b',
            margin: '8px 0 0 0',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            lineHeight: '1.4'
          }}>
            {stripMarkdown(displayDescription)}
          </p>
        )}

        {/* Footer: Price + Budget Margin + Versions CTA */}
        <div className="vehicle-card__footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: '12px' }}>
          <div>
            <span className="vehicle-card__price">{finalPrice}</span>
            {budgetMargin !== undefined && budgetMargin !== null && (
              <div style={{
                fontSize: '0.68rem',
                fontWeight: 700,
                color: budgetMargin >= 0 ? '#10b981' : '#f59e0b',
                marginTop: '2px',
              }}>
                {budgetMargin >= 0
                  ? `+${Math.round(budgetMargin).toLocaleString('fr-FR')} MAD sous votre budget`
                  : `${Math.round(budgetMargin).toLocaleString('fr-FR')} MAD`}
              </div>
            )}
          </div>

          
          {isNewOfficial && (
            <span style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '0.78rem',
              fontWeight: 700,
              color: 'var(--color-accent-gold, #AE8C4E)',
              background: 'rgba(174, 140, 78, 0.08)',
              padding: '4px 10px',
              borderRadius: '999px',
              border: '1px solid rgba(174, 140, 78, 0.2)'
            }}>
              Voir les versions <ArrowRight size={13} />
            </span>
          )}
        </div>

      </div>
    </Link>
  );
}
