import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './chatbot.module.css';
import { PriceGauge } from '../pricing/PriceGauge';

interface CarRecommendationProps {
  id: string;
  brand: string;
  model: string;
  year: number;
  price: number;
  image?: string;
}

export default function CarRecommendation({ id, brand, model, year, price, image }: CarRecommendationProps) {
  const navigate = useNavigate();
  const [argusData, setArgusData] = useState<{ price: number, trend: string } | null>(null);

  useEffect(() => {
    const fetchArgus = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/vehicles/estimate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            brand,
            model,
            year,
            mileage: 60000, // Valeur par défaut pour l'instant
            fuel_type: "diesel",
            body_type: "berline",
            transmission: "manuelle",
            city: "Casablanca"
          })
        });
        if (response.ok) {
          const data = await response.json();
          setArgusData({ price: data.predicted_price, trend: data.market_trend });
        }
      } catch (err) {
        console.error("Error fetching argus:", err);
      }
    };
    fetchArgus();
  }, [brand, model, year]);

  return (
    <div className={styles.sourceCard} onClick={() => navigate(`/vehicule/${id}`)}>
      {image ? (
        <img src={image} alt={`${brand} ${model}`} className={styles.sourceCardImage} />
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
          {brand} {model} ({year})
        </span>
        <span className={styles.sourceCardPrice}>{price.toLocaleString('fr-FR')} MAD</span>
      </div>
      
      <div style={{ padding: '0 12px 0 0', display: 'flex', alignItems: 'center' }}>
        <button style={{ 
          background: 'var(--color-accent-gold)', color: '#fff', border: 'none', 
          padding: '4px 12px', borderRadius: '4px', fontSize: '0.7rem', cursor: 'pointer',
          fontWeight: 600
        }}>
          Voir l'annonce
        </button>
      </div>

      {argusData && (
        <div style={{ gridColumn: '1 / -1', padding: '0 12px 12px 12px' }}>
          <PriceGauge 
            currentPrice={price} 
            argusPrice={argusData.price} 
            trend={argusData.trend} 
          />
        </div>
      )}
    </div>
  );
}
