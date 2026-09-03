import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './chatbot.module.css';
import { PriceGauge } from '../pricing/PriceGauge';
import api from '../../services/api';
import { resolveVehicleImage, CATALOGUE_IMAGE_FALLBACK } from '../../utils/vehicleImageResolver';

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
  const [argusData, setArgusData] = useState<{ price: number; trend: string } | null>(null);
  const [vehicleExists, setVehicleExists] = useState<boolean>(true);
  const [backendImage, setBackendImage] = useState<string | undefined>(image);

  const displayImage = useMemo(() => {
    return resolveVehicleImage(brand, model, backendImage ? [{ file_path: backendImage }] : undefined);
  }, [backendImage, brand, model]);

  useEffect(() => {
    const fetchArgus = async () => {
      try {
        const { data } = await api.post('/vehicles/predict-price', {
          brand,
          model,
          year,
          mileage: 0,
          fuel_type: 'diesel',
          body_type: 'berline',
          transmission: 'manuelle',
          city: 'Casablanca',
        });
        setArgusData({ price: data.predicted_price, trend: data.market_trend });
      } catch (err) {
        // Optionnel
      }
    };
    fetchArgus();
  }, [brand, model, year]);

  useEffect(() => {
    if (id) {
      const fetchVehicle = async () => {
        try {
          const { data } = await api.get(`/vehicles/${id}`);
          if (data && data.images && data.images.length > 0) {
            setBackendImage(data.images[0].file_path || data.images[0]);
          }
          setVehicleExists(true);
        } catch (err: any) {
          if (err.response && err.response.status === 404) {
            setVehicleExists(false);
          }
        }
      };
      fetchVehicle();
    }
  }, [id]);

  const handleNavigateDetail = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (id && vehicleExists) {
      navigate(`/vehicule/${id}`);
    } else {
      navigate(`/neuf/${brand.toLowerCase()}/${model.toLowerCase().replace(/\s+/g, '-')}`);
    }
  };

  return (
    <div className={styles.sourceCard} onClick={handleNavigateDetail}>
      <div
        style={{
          width: 90,
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'rgba(15, 23, 42, 0.04)',
          borderRadius: 10,
          overflow: 'hidden',
          padding: 4,
          flexShrink: 0,
        }}
      >
        {displayImage ? (
          <img
            src={displayImage}
            alt={`${brand} ${model}`}
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            loading="lazy"
            onError={(event) => {
              event.currentTarget.onerror = null;
              event.currentTarget.src = CATALOGUE_IMAGE_FALLBACK;
            }}
          />
        ) : (
          <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#94A3B8' }}>{brand}</span>
        )}
      </div>

      <div className={styles.sourceCardInfo}>
        <span className={styles.sourceCardTitle}>
          {brand} {model} {year ? `(${year})` : ''}
        </span>
        <span className={styles.sourceCardPrice}>
          {price > 0 ? `${price.toLocaleString('fr-FR')} MAD` : 'Prix sur demande'}
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, paddingRight: 8, alignItems: 'flex-end' }}>
        <button
          onClick={handleNavigateDetail}
          type="button"
          style={{
            background: 'rgba(18, 33, 53, 0.08)',
            color: '#122135',
            border: '1px solid rgba(18, 33, 53, 0.12)',
            padding: '6px 12px',
            borderRadius: '8px',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Fiche
        </button>
      </div>

      {argusData && (
        <div style={{ gridColumn: '1 / -1', padding: '0 8px 8px 8px' }}>
          <PriceGauge currentPrice={price} argusPrice={argusData.price} trend={argusData.trend} />
        </div>
      )}
    </div>
  );
}
