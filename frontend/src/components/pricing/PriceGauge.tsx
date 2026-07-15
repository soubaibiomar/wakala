import React from 'react';
import styles from './PriceGauge.module.css';

interface PriceGaugeProps {
  currentPrice: number;
  argusPrice: number;
  lowerBound?: number;
  upperBound?: number;
  trend?: string;
}

export const PriceGauge: React.FC<PriceGaugeProps> = ({ 
  currentPrice, 
  argusPrice,
  trend 
}) => {
  // Calcul du ratio pour la couleur
  const ratio = currentPrice / argusPrice;
  
  let statusClass = styles.grey;
  let label = "Prix du marché";

  if (ratio <= 0.95) {
    statusClass = styles.green;
    label = "Bonne affaire";
  } else if (ratio >= 1.05) {
    statusClass = styles.red;
    label = "Au-dessus du marché";
  }

  // Formatage du prix
  const formatMAD = (val: number) => {
    return new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD', maximumFractionDigits: 0 }).format(val);
  };

  return (
    <div className={`${styles.gaugeContainer} ${statusClass}`}>
      <div className={styles.gaugeHeader}>
        <span className={styles.gaugeTitle}>Cote Wakala (Argus)</span>
        <span className={styles.gaugeValue}>{formatMAD(argusPrice)}</span>
      </div>
      
      <div className={styles.progressBarBg}>
        <div 
          className={styles.progressBarFill} 
          style={{ width: `${Math.min(100, Math.max(10, (1 - Math.abs(1 - ratio)) * 100))}%` }}
        />
      </div>

      <div className={styles.gaugeFooter}>
        <span className={styles.statusLabel}>{label}</span>
        {trend && <span className={styles.trendLabel}>Tendance: {trend}</span>}
      </div>
    </div>
  );
};
