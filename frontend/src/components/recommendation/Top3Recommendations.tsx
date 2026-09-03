import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Trophy, ShieldCheck, Sparkles, AlertCircle, ChevronDown, ChevronUp, CheckCircle, Info } from 'lucide-react';
import type { Top3Response, Top3VehicleItem } from '../../services/recommendationService';
import './Top3Recommendations.css';
import { CATALOGUE_IMAGE_FALLBACK, resolveVehicleImage } from '../../utils/vehicleImageResolver';

interface Top3RecommendationsProps {
  data: Top3Response;
  onSelectVehicle?: (vehicleId: string) => void;
}

const CRITERIA_LABELS: Record<string, string> = {
  espace_coffre: 'Espace & Coffre',
  economie_usage: "Économie d'usage",
  performance: 'Performance',
  securite: 'Sécurité',
  confort: 'Confort',
  technologie: 'Technologie',
  robustesse: 'Robustesse',
  fiabilite: 'Fiabilité',
  design: 'Design',
};

export const Top3Recommendations: React.FC<Top3RecommendationsProps> = ({ data, onSelectVehicle }) => {
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  if (!data || !data.items || data.items.length === 0) {
    return null;
  }

  const toggleExpand = (id: string) => {
    setExpandedCard(prev => (prev === id ? null : id));
  };

  return (
    <div className="top3-container">
      {/* ─── Header ────────────────────────────────────────────── */}
      <div className="top3-header">
        <div className="top3-badge">
          <Trophy size={16} className="text-amber-400" />
          <span>Algorithme Certifié Wakala</span>
        </div>
        <h2 className="top3-title">Votre Top 3 Recommandé</h2>
        <p className="top3-subtitle">
          Chaque modèle est représenté par sa <strong>meilleure finition</strong>, avec une stricte <strong>diversité de marques</strong> et des preuves chiffrées.
        </p>
      </div>

      {/* ─── Cascade relaxation alert ──────────────────────────── */}
      {data.message && (
        <div className="top3-alert">
          <Info size={18} className="top3-alert-icon" />
          <span>{data.message}</span>
        </div>
      )}

      {/* ─── Cards Grid ────────────────────────────────────────── */}
      <div className="top3-grid">
        {data.items.map((item: Top3VehicleItem, index: number) => {
          const rank = index + 1;
          const isExpanded = expandedCard === item.vehicle_id;
          const rankTitles = ['1er Choix Idéal', '2ème Challenger', '3ème Alternative'];
          const rankColors = ['rank-gold', 'rank-silver', 'rank-bronze'];

          const formattedPrice = new Intl.NumberFormat('fr-MA', {
            style: 'currency',
            currency: 'MAD',
            maximumFractionDigits: 0,
          }).format(item.price);

          return (
            <div key={item.vehicle_id} className={`top3-card ${rankColors[index] || ''}`}>
              {/* Rank Tag */}
              <div className="top3-rank-tag">
                <span className="rank-num">#{rank}</span>
                <span className="rank-label">{rankTitles[index]}</span>
              </div>

              {/* Vehicle Image */}
              <div className="top3-image-wrap">
                <img
                  src={item.image_url || resolveVehicleImage(item.brand, item.model)}
                  alt={`${item.brand} ${item.model}`}
                  className="top3-image"
                  loading="lazy"
                  onError={(event) => {
                    event.currentTarget.onerror = null;
                    event.currentTarget.src = CATALOGUE_IMAGE_FALLBACK;
                  }}
                />
                <div className="top3-score-bubble">
                  <div className="score-val">{Math.round(item.match_score)}%</div>
                  <div className="score-lbl">Score Wakala</div>
                </div>
              </div>

              {/* Card Body */}
              <div className="top3-body">
                <div className="top3-titles">
                  <h3 className="top3-model-name">{item.brand} {item.model}</h3>
                  <div className="top3-version-name">{item.version_name || `Modèle ${item.year}`}</div>
                </div>

                {/* Price & Budget Margin */}
                <div className="top3-pricing">
                  <div className="top3-price">{formattedPrice}</div>
                  {item.budget_margin !== undefined && item.budget_margin !== null && (
                    <div className={`top3-margin ${item.budget_margin >= 0 ? 'margin-positive' : 'margin-negative'}`}>
                      {item.budget_margin >= 0
                        ? `✓ +${Math.round(item.budget_margin).toLocaleString('fr-FR')} MAD sous budget`
                        : `${Math.round(item.budget_margin).toLocaleString('fr-FR')} MAD`}
                    </div>
                  )}
                </div>

                {/* Key Tangible Facts (2 proof points) */}
                {item.key_facts && item.key_facts.length > 0 && (
                  <div className="top3-facts">
                    {item.key_facts.map((fact, fIdx) => (
                      <div key={fIdx} className="top3-fact-item">
                        <CheckCircle size={14} className="fact-icon" />
                        <span>{fact}</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Expandable Breakdown Button */}
                <button
                  type="button"
                  className="top3-expand-btn"
                  onClick={() => toggleExpand(item.vehicle_id)}
                >
                  <span>Pourquoi cette note ? (Formule 57/25/18)</span>
                  {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                </button>

                {/* Detailed Breakdown */}
                {isExpanded && (
                  <div className="top3-details">
                    <div className="top3-ingredients">
                      <div className="ingredient-item">
                        <span className="ing-name">Qualité (57%) :</span>
                        <span className="ing-val">{item.score_breakdown.qualite}/100</span>
                      </div>
                      <div className="ingredient-item">
                        <span className="ing-name">Budget (25%) :</span>
                        <span className="ing-val">{item.score_breakdown.budget}/100</span>
                      </div>
                      <div className="ingredient-item">
                        <span className="ing-name">Pratique (18%) :</span>
                        <span className="ing-val">{item.score_breakdown.pratique}/100</span>
                      </div>
                    </div>

                    <div className="top3-criteria-list">
                      <div className="criteria-header">Rangs percentiles face au marché :</div>
                      {Object.entries(item.score_breakdown.criteria || {}).map(([key, val]) => {
                        const label = CRITERIA_LABELS[key] || key;
                        if (val === null) {
                          return (
                            <div key={key} className="criteria-row criteria-na" title="Règle d'honnêteté : poids redistribué">
                              <span className="crit-label">{label}</span>
                              <span className="crit-val-na">Non mesuré (Poids redistribué)</span>
                            </div>
                          );
                        }
                        return (
                          <div key={key} className="criteria-row">
                            <span className="crit-label">{label}</span>
                            <div className="crit-bar-wrap">
                              <div
                                className="crit-bar-fill"
                                style={{ width: `${Math.min(100, Math.max(5, val))}%` }}
                              />
                            </div>
                            <span className="crit-val">{Math.round(val)}/100</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Action CTA */}
                <div className="top3-actions">
                  <Link
                    to={`/catalogue?search=${encodeURIComponent(`${item.brand} ${item.model}`)}`}
                    className="top3-view-btn"
                    onClick={() => onSelectVehicle && onSelectVehicle(item.vehicle_id)}
                  >
                    Découvrir ce modèle
                  </Link>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Top3Recommendations;
