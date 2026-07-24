import React from 'react';
import './TrustScoreBar.css';

export interface TrustScoreBarProps {
  score: number; // 0 to 100
  confidence: string;
}

export default function TrustScoreBar({ score, confidence }: TrustScoreBarProps) {
  const getScoreColor = (s: number) => {
    if (s >= 80) return 'var(--color-accent-green, #10B981)';
    if (s >= 60) return 'var(--color-accent-gold, #F59E0B)';
    return '#EF4444'; // Red
  };

  const getLabel = (s: number) => {
    if (s >= 80) return 'Très Fiable';
    if (s >= 60) return 'Vigilance Recommandée';
    return 'Risque Élevé';
  };

  const color = getScoreColor(score);
  const label = getLabel(score);

  return (
    <div className="trust-score-bar-container">
      <div className="trust-score-header">
        <span className="trust-score-title">Score de Confiance IA</span>
        <span className="trust-score-value" style={{ color }}>{score}% - {label}</span>
      </div>
      <div className="trust-score-track">
        <div 
          className="trust-score-fill" 
          style={{ width: `${score}%`, backgroundColor: color }}
        ></div>
      </div>
      {confidence === 'low' && (
        <p className="trust-score-warning">⚠️ Note indicative (données insuffisantes pour une analyse complète).</p>
      )}
    </div>
  );
}
