/**
 * components/vehicle-card/VehicleCard.tsx — Carte véhicule réutilisable.
 * Utilisée dans Home (featured) et Catalogue (grille).
 */

import { Link } from 'react-router-dom';
import { Scale } from 'lucide-react';
import type { Vehicle } from '../../types/vehicle';
import fr from '../../i18n/fr';
import MatchScoreBadge from '../recommendation-form/MatchScoreBadge';
import { useCompare } from '../../context/CompareContext';
import './VehicleCard.css';

interface VehicleCardProps {
  vehicle: Vehicle;
  animationDelay?: number;
  matchScore?: number;
}

export default function VehicleCard({ vehicle, matchScore }: VehicleCardProps) {
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
        {vehicle.images && vehicle.images.length > 0 ? (
          <img
            src={vehicle.images[0].file_path}
            alt={`${vehicle.brand} ${vehicle.model}`}
            loading="lazy"
            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
          />
        ) : (
          <div className="vehicle-card__image-placeholder">🚗</div>
        )}

        {/* Condition score as a micro-badge over image if very high */}
        {vehicle.condition_score && vehicle.condition_score >= 80 && (
          <div className="badge badge--gold vehicle-card__popular">
            ⭐ Premium
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
              {vehicle.year} • {vehicle.mileage.toLocaleString('fr-FR')} km
            </span>
          </div>
        </div>

        {/* Specs row */}
        <div className="vehicle-card__specs">
          <span>⛽ {vehicle.fuel_type}</span>
          <span>⚙️ {vehicle.transmission}</span>
        </div>

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
