interface MatchScoreBadgeProps {
  score: number;
}

export default function MatchScoreBadge({ score }: MatchScoreBadgeProps) {
  const safeScore = Math.max(0, Math.min(100, Math.round(score)));
  return (
    <span className="vehicle-card__match-score" title={`Compatibilité Matchmaker : ${safeScore}%`}>
      {safeScore}% compatible
    </span>
  );
}
