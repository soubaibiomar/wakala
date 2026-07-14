import React from 'react';
import './TrustBadge.css';

interface TrustBadgeProps {
  isVerified: boolean;
  className?: string;
}

/**
 * TrustBadge component (CIN / Identity Verification)
 * Conformité CNDP: Affiche l'état de vérification sans exposer de données sensibles.
 */
export const TrustBadge: React.FC<TrustBadgeProps> = ({ isVerified, className = '' }) => {
  if (!isVerified) {
    return (
      <div className={`trust-badge trust-badge--unverified ${className}`} title="Identité non vérifiée">
        <span className="trust-badge__icon">⚠️</span>
        <span className="trust-badge__text">Non Vérifié</span>
      </div>
    );
  }

  return (
    <div className={`trust-badge trust-badge--verified ${className}`} title="Identité vérifiée (CIN)">
      <span className="trust-badge__icon">✅</span>
      <span className="trust-badge__text">Vendeur de Confiance</span>
    </div>
  );
};
