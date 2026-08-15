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

function cleanVehicleTitle(brand: string, model: string): { brand: string; model: string } {
  let cleanBrand = (brand || '').trim();
  let cleanModel = (model || '').trim();

  // If brand is "MAN" (scraped artifact from "MAN Citroën..."), fix brand
  if (cleanBrand.toUpperCase() === 'MAN' && cleanModel.toLowerCase().includes('citroën')) {
    cleanBrand = 'Citroën';
    cleanModel = cleanModel.replace(/^citro[eë]n\s*/i, '');
  }

  // Remove duplicate brand prefix in model (e.g. "Volkswagen Touareg" where brand is "Volkswagen")
  const brandRegex = new RegExp(`^${cleanBrand}\\s+`, 'i');
  cleanModel = cleanModel.replace(brandRegex, '');

  // Remove noisy words from scraped titles
  cleanModel = cleanModel
    .replace(/^vente\s+(voiture|auto)?\s*/i, '')
    .replace(/^vente\s+/i, '')
    .replace(/\s*à\s+[A-Za-zÀ-ÿ\-]+$/i, '')
    .replace(/\s*en\s+(très\s+)?bon\s+état.*$/i, '')
    .replace(/\s*[–\-]\s*(très|bon état|première main).*$/i, '')
    .replace(/\s+\d+\s*(km|kms|000\s*km).*$/i, '')
    .replace(/\s+(diesel|essence|hybride|electrique|électrique)\s+(manuelle|automatique|auto|bva|bvm).*$/i, '')
    .replace(/\s+(manuelle|automatique|diesel|essence)\s+\d{4}.*$/i, '')
    .replace(/\s+\d{4}$/, '')
    .trim();

  if (!cleanModel) {
    cleanModel = model.split(' ')[0] || 'Modèle';
  }

  return { brand: cleanBrand, model: cleanModel };
}

function getDisplayBodyType(brand: string, model: string, currentBodyType?: string): string {
  const name = `${brand} ${model}`.toLowerCase();
  
  if (name.includes('r 1250') || name.includes('f 900') || name.includes('f 850') || name.includes('tmax') || name.includes('xmax') || name.includes('ninja') || name.includes('moto')) {
    return 'Moto';
  }
  
  const suvKeywords = [
    'duster', 'touareg', 'qashqai', 'sportage', 'tucson', 'tiguan', 't-roc', 't-cross', 'glc', 'gle', 'gla', 'glb', 'gls',
    'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', '3008', '2008', '5008', 'kuga', 'puma', 'captur', 'kadjar', 'austral',
    'ateca', 'arona', 'tarraco', 'karoq', 'kamiq', 'kodiaq', 'juke', 'rav4', 'c-hr', 'cr-v', 'hr-v', 'renegade',
    'compass', 'cherokee', 'grandland', 'crossland', 'mokka', 'macan', 'cayenne', 'q2', 'q3', 'q5', 'q7', 'q8',
    'suv', '4x4', 'crossover', 'range rover', 'defender', 'discovery', 'evoque', 'velar', 'stelvio', 'tonale'
  ];
  if (suvKeywords.some(kw => name.includes(kw))) {
    return 'SUV';
  }
  
  const citadineKeywords = [
    'clio', '208', '207', '206', 'c3', 'sandero', 'fiesta', 'polo', 'golf', 'yaris', 'i10', 'i20', 'picanto',
    'rio', 'micra', 'swift', 'c1', '108', '107', 'aygo', 'twingo', 'fiat 500', 'panda', 'punto', 'ibiza', 'fabia', 'citadine'
  ];
  if (citadineKeywords.some(kw => name.includes(kw))) {
    return 'Citadine';
  }

  if (currentBodyType && currentBodyType.toLowerCase() !== 'berline') {
    return currentBodyType.charAt(0).toUpperCase() + currentBodyType.slice(1);
  }

  return 'Berline';
}

function getFallbackImage(brand: string, model: string): string {
  const b = (brand || '').toLowerCase();
  const m = (model || '').toLowerCase();
  
  if (b.includes('dacia')) {
    if (m.includes('duster')) return 'https://images.unsplash.com/photo-1533473359331-0135ef1b58bf?q=80&w=600';
    if (m.includes('sandero')) return 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?q=80&w=600';
    return '/assets/dacia-logan.jpg';
  }
  if (b.includes('mercedes') || b.includes('benz')) {
    return '/assets/mercedes-cla.jpg';
  }
  if (b.includes('jeep') || b.includes('dodge')) {
    return '/assets/jeep-grand-cherokee.jpg';
  }
  if (b.includes('renault')) {
    return '/assets/clio5.jpg';
  }
  if (b.includes('volkswagen') || b.includes('vw')) {
    return 'https://images.unsplash.com/photo-1541899481282-d53bffe3c35d?q=80&w=600';
  }
  if (b.includes('peugeot')) {
    return 'https://images.unsplash.com/photo-1552519507-da3b142c6e3d?q=80&w=600';
  }
  if (b.includes('bmw')) {
    return 'https://images.unsplash.com/photo-1555215695-3004980ad54e?q=80&w=600';
  }
  if (b.includes('audi')) {
    return 'https://images.unsplash.com/photo-1603584173870-7f23fdae1b7a?q=80&w=600';
  }
  if (b.includes('toyota') || b.includes('nissan') || b.includes('hyundai') || b.includes('kia')) {
    return 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=600';
  }
  return '/assets/phares-intro.jpg';
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

  // Clean brand and model for crisp presentation
  const { brand: cleanBrand, model: cleanModel } = cleanVehicleTitle(vehicle.brand, vehicle.model);
  const displayBodyType = getDisplayBodyType(cleanBrand, cleanModel, vehicle.body_type);
  const fallbackImg = getFallbackImage(cleanBrand, cleanModel);

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
  const occSlug = `${cleanBrand.toLowerCase()}-${cleanModel.toLowerCase()}-${vehicle.year || '0'}-${shortId}`
    .replace(/[^a-z0-9\-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
  
  // Clean model name for clean URL
  const cleanModelForUrl = cleanModel.toLowerCase().trim();
  
  const linkTo = isNewOfficial 
    ? `/marque/${encodeURIComponent(cleanBrand.toLowerCase())}/${encodeURIComponent(cleanModelForUrl)}` 
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
    <Link to={linkTo} className="vehicle-card" title={isNewOfficial ? `Voir les versions de ${cleanBrand} ${cleanModel}` : `${cleanBrand} ${cleanModel}`}>
      
      {/* ─── Image Header ──────────────────────────────────────── */}
      <div className="vehicle-card__image">
        {vehicle.images && vehicle.images.length > 0 && vehicle.images[0].file_path ? (
          <img
            src={vehicle.images[0].file_path}
            alt={`${cleanBrand} ${cleanModel}`}
            loading="lazy"
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.src = fallbackImg;
            }}
          />
        ) : (
          <img
            src={fallbackImg}
            alt={`${cleanBrand} ${cleanModel}`}
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
            {cleanBrand} {cleanModel}
          </h3>
          <div className="vehicle-card__subtitle">
            {bestVersionName || (vehicle.year ? `Modèle ${vehicle.year}` : 'Véhicule')}
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
            <span style={{ textTransform: 'capitalize' }}>{displayBodyType}</span>
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
