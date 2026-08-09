interface MatchScoreBadgeProps {
  score: number;
  label?: string;
}

export default function MatchScoreBadge({ score, label }: MatchScoreBadgeProps) {
  const safeScore = Math.max(0, Math.min(100, Math.round(score)));

  let colorClass = '#10B981'; // Green
  if (safeScore < 70) {
    colorClass = '#F59E0B'; // Amber
  } else if (safeScore < 85) {
    colorClass = '#3B82F6'; // Blue
  }

  return (
    <span
      className="vehicle-card__match-score"
      style={{
        background: `linear-gradient(135deg, ${colorClass} 0%, #1e293b 100%)`,
        color: '#ffffff',
        fontWeight: 700,
        boxShadow: '0 2px 8px rgba(0,0,0,0.25)',
      }}
      title={`Score Wakala : ${safeScore}/100 (57% Qualité + 25% Budget + 18% Pratique)`}
    >
      🎯 {safeScore}% {label || 'compatible'}
    </span>
  );
}

