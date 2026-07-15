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
    <div className="trust-score" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
      <svg width="80" height="80" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="46" fill="none" stroke="#E2E8F0" strokeWidth="2" />
        <circle
          cx="50" cy="50" r="46"
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeDasharray={289} /* 2 * PI * 46 */
          strokeDashoffset={289 * (1 - score / 100)}
          style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%', transition: 'stroke-dashoffset 1s ease' }}
        />
        <text x="50" y="50" textAnchor="middle" dominantBaseline="central"
              fill="var(--color-primary)" fontSize="20" fontWeight="600" fontFamily="ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace">
          {score}%
        </text>
      </svg>
      <span style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-secondary)', fontWeight: 600 }}>{label}</span>
    </div>
  );
}
