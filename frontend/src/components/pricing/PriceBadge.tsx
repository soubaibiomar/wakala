import { TrendingDown, TrendingUp, CheckCircle } from 'lucide-react';

interface PriceBadgeProps {
  price: number;
  predictedPrice?: number;
}

export default function PriceBadge({ price, predictedPrice }: PriceBadgeProps) {
  if (!predictedPrice) return null;

  const diffPercent = ((price - predictedPrice) / predictedPrice) * 100;

  let status: 'good' | 'fair' | 'high' = 'fair';
  if (diffPercent <= -10) status = 'good';
  else if (diffPercent >= 10) status = 'high';

  const config = {
    good: {
      label: 'Bonne affaire',
      color: 'var(--accent-green)',
      bg: 'rgba(16, 185, 129, 0.1)',
      icon: <TrendingDown size={14} />
    },
    fair: {
      label: 'Prix conforme',
      color: 'var(--accent-gold)',
      bg: 'rgba(234, 179, 8, 0.1)',
      icon: <CheckCircle size={14} />
    },
    high: {
      label: 'Prix élevé',
      color: 'var(--accent-red)',
      bg: 'rgba(239, 68, 68, 0.1)',
      icon: <TrendingUp size={14} />
    }
  };

  const current = config[status];

  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '4px 8px',
        borderRadius: 'var(--radius-pill)',
        background: current.bg,
        color: current.color,
        fontSize: '0.75rem',
        fontWeight: 600,
        fontFamily: 'var(--font-sans)',
        border: `1px solid ${current.color}40`,
        boxShadow: `0 2px 8px ${current.bg}`,
      }}
      title={`Estimé à ${predictedPrice.toLocaleString('fr-FR')} MAD`}
    >
      {current.icon}
      {current.label}
    </div>
  );
}
