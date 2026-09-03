import type { EightDimensionScores as ScoreMap } from '../../services/recommendationService';
import './eight-dimension-scores.css';

const DIMENSIONS: Array<[string, string]> = [
  ['espace', 'Espace'],
  ['securite', 'Sécurité'],
  ['cout_reel', 'Coût réel'],
  ['prix_acces', "Prix d'accès"],
  ['praticite_urbaine', 'Praticité urbaine'],
  ['performance', 'Performance'],
  ['ecologie', 'Écologie'],
  ['motricite', 'Motricité'],
];

interface EightDimensionScoresProps {
  scores?: ScoreMap;
  total?: number;
}

export function EightDimensionScores({ scores, total }: EightDimensionScoresProps) {
  if (!scores || typeof total !== 'number') return null;

  return (
    <div className="eight-dimension-scores" aria-label="Scores Wakala des 8 dimensions">
      <div className="eight-dimension-scores__header">
        <span>Scores 8D</span>
        <strong>{total.toFixed(1)} / 5</strong>
      </div>
      <div className="eight-dimension-scores__grid">
        {DIMENSIONS.map(([key, label]) => (
          <div className="eight-dimension-scores__item" key={key}>
            <span>{label}</span>
            <strong>{Number(scores[key] ?? 0).toFixed(1)} / 5</strong>
          </div>
        ))}
      </div>
    </div>
  );
}
