import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './chatbot.module.css';
import { PriceGauge } from '../pricing/PriceGauge';
import api from '../../services/api';

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
  const [actualImage, setActualImage] = useState<string | undefined>(image);
  const [argusData, setArgusData] = useState<{ price: number, trend: string } | null>(null);
  const [vehicleExists, setVehicleExists] = useState<boolean>(true);

  useEffect(() => {
    const fetchArgus = async () => {
      try {
        const { data } = await api.post('/vehicles/predict-price', {
          brand,
          model,
          year,
          mileage: 60000, // Valeur par défaut pour l'instant
          fuel_type: "diesel",
          body_type: "berline",
          transmission: "manuelle",
          city: "Casablanca"
        });
        setArgusData({ price: data.predicted_price, trend: data.market_trend });
      } catch (err) {
        console.error("Error fetching argus:", err);
      }
    };
    fetchArgus();
  }, [brand, model, year]);

  useEffect(() => {
    if (id) {
      const fetchVehicle = async () => {
        try {
          const { data } = await api.get(`/vehicles/${id}`);
          if (!actualImage && data && data.images && data.images.length > 0) {
            setActualImage(data.images[0].file_path || data.images[0]);
          }
          setVehicleExists(true);
        } catch (err: any) {
          console.error("Error fetching vehicle:", err);
          if (err.response && err.response.status === 404) {
            setVehicleExists(false);
          }
        }
      };
      fetchVehicle();
    }
  }, [id, actualImage]);

  return (
    <div 
      className={styles.sourceCard} 
      onClick={() => { if (vehicleExists) navigate(`/vehicule/${id}`); }}
      style={{ opacity: vehicleExists ? 1 : 0.6, cursor: vehicleExists ? 'pointer' : 'not-allowed' }}
    >
      {actualImage ? (
        <img src={actualImage} alt={`${brand} ${model}`} className={styles.sourceCardImage} />
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
        <button 
          disabled={!vehicleExists}
          style={{ 
            background: vehicleExists ? 'var(--color-accent-gold)' : 'var(--bg-surface)', 
            color: vehicleExists ? '#fff' : 'var(--text-muted)', 
            border: vehicleExists ? 'none' : '1px solid var(--border-subtle)', 
            padding: '4px 12px', borderRadius: '4px', fontSize: '0.7rem', 
            cursor: vehicleExists ? 'pointer' : 'not-allowed',
            fontWeight: 600
          }}>
          {vehicleExists ? "Voir l'annonce" : "Annonce expirée"}
        </button>
      </div>

      {argusData && vehicleExists && (
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
