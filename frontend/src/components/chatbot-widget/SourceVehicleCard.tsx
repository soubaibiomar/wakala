import { useNavigate } from 'react-router-dom';
import type { SourceRef } from './useChatSession';
import styles from './chatbot.module.css';
import { CATALOGUE_IMAGE_FALLBACK } from '../../utils/vehicleImageResolver';

interface SourceVehicleCardProps {
  source: SourceRef;
}

export default function SourceVehicleCard({ source }: SourceVehicleCardProps) {
  const navigate = useNavigate();

  const scorePercent = Math.round(source.relevance_score * 100);
  const scoreColor =
    scorePercent >= 70 ? 'var(--color-accent-green)' :
    scorePercent >= 40 ? 'var(--color-accent-gold)' :
    'var(--color-accent-red)';

  return (
    <button
      className={styles.sourceCard}
      onClick={() => navigate(`/vehicule/${source.vehicle_id}`)}
      title={`Voir le détail de ${source.vehicle_title || 'ce véhicule'}`}
    >
      {source.image_url ? (
        <img
          src={source.image_url}
          alt={source.vehicle_title}
          className={styles.sourceCardImage}
          onError={(event) => {
            event.currentTarget.onerror = null;
            event.currentTarget.src = CATALOGUE_IMAGE_FALLBACK;
          }}
        />
      ) : (
        <div className={styles.sourceCardIcon}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <rect x="3" y="3" width="18" height="14" rx="2" />
            <path d="M8 21h8M12 17v4" />
          </svg>
        </div>
      )}

      <div className={styles.sourceCardInfo}>
        <span className={styles.sourceCardTitle}>
          {source.vehicle_title || 'Véhicule'}
        </span>
        {source.price && (
          <span className={styles.sourceCardPrice}>{source.price} MAD</span>
        )}
      </div>

      <div className={styles.sourceCardBadge} style={{ color: scoreColor }}>
        <svg width="28" height="28" viewBox="0 0 40 40" className={styles.sourceCardRing}>
          <circle cx="20" cy="20" r="17" fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="3" />
          <circle
            cx="20" cy="20" r="17"
            fill="none"
            stroke={scoreColor}
            strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray="106.8"
            strokeDashoffset={106.8 * (1 - scorePercent / 100)}
            transform="rotate(-90 20 20)"
          />
        </svg>
        <span className={styles.sourceCardScore}>{scorePercent}%</span>
      </div>
    </button>
  );
}
