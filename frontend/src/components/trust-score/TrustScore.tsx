/**
 * TrustScore — Composant d'affichage du score de confiance vendeur.
 * Basé sur le module anomaly detection (Isolation Forest) du backend.
 */
export interface TrustScoreProps {
  score: number;  // 0-100
  label?: string;
}

export default function TrustScore({ score, label = 'Score de confiance' }: TrustScoreProps) {
  const color = score >= 80 ? 'var(--color-accent-green)' : score >= 50 ? 'var(--color-accent-gold)' : '#F87171';
  const circumference = 2 * Math.PI * 40;
  const offset = circumference * (1 - score / 100);

  return (
    <div className="trust-score" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="6" />
        <circle
          cx="50" cy="50" r="40"
          fill="none"
          stroke={color}
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%', transition: 'stroke-dashoffset 1s ease' }}
        />
        <text x="50" y="50" textAnchor="middle" dominantBaseline="central"
              fill={color} fontSize="22" fontWeight="700" fontFamily="var(--font-display)">
          {score}%
        </text>
      </svg>
      <span style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary)' }}>{label}</span>
    </div>
  );
}
