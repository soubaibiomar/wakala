import { useCallback, useState } from 'react';
import type { RecommendationResponse } from '../../services/recommendationService';
import { parseSearchQuery, type NlpExtractionResult } from '../../services/searchParseService';
import { useMatchmaker } from '../recommendation-form/useMatchmaker';

interface SearchBarProps {
  userId?: string | null;
  onResults: (query: string, result: RecommendationResponse) => void;
}

/** Formatte un budget en MAD avec séparateurs de milliers */
function formatBudget(budget: number): string {
  return budget.toLocaleString('fr-MA') + ' MAD';
}

/** Labels lisibles pour les champs NLP */
const LABEL_MAP: Record<string, string> = {
  familial: 'Familial',
  urbain: 'Urbain',
  longue_distance: 'Longue distance',
  professionnel: 'Professionnel',
  sportif: 'Sportif',
  utilitaire: 'Utilitaire',
  tout_terrain: 'Tout-terrain',
  quotidien: 'Quotidien',
  famille: 'Famille',
  célibataire: 'Célibataire',
  couple: 'Couple',
  jeune_conducteur: 'Jeune conducteur',
  retraité: 'Retraité',
  économique: 'Économique',
  fiabilité: 'Fiabilité',
  confort: 'Confort',
  sécurité: 'Sécurité',
  performance: 'Performance',
  luxe: 'Luxe',
  espace: 'Espace',
  faible_consommation: 'Faible conso.',
  revente: 'Revente',
  modernité: 'Modernité',
};

function humanize(value: string): string {
  return LABEL_MAP[value] || value.charAt(0).toUpperCase() + value.slice(1).replace(/_/g, ' ');
}

/** Icône emoji pour chaque type de badge */
const BADGE_ICONS: Record<string, string> = {
  budget: '💰',
  usage: '🎯',
  priorite: '⭐',
  profil: '👤',
};

export default function SearchBar({ userId, onResults }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const { isLoading, recommend } = useMatchmaker();
  const [nlpResult, setNlpResult] = useState<NlpExtractionResult | null>(null);
  const [nlpLoading, setNlpLoading] = useState(false);

  const submit = useCallback(async () => {
    const trimmed = query.trim();
    if (!trimmed || isLoading) return;

    // Lancer les deux appels en parallèle
    setNlpLoading(true);
    setNlpResult(null);

    const [recResult, nlpData] = await Promise.all([
      recommend({ query: trimmed, user_id: userId }),
      parseSearchQuery(trimmed),
    ]);

    // Afficher les badges NLP
    if (nlpData && !nlpData.erreur) {
      setNlpResult(nlpData);
    } else {
      setNlpResult(null);
    }
    setNlpLoading(false);

    // Naviguer vers les résultats
    if (recResult) onResults(trimmed, recResult);
  }, [isLoading, onResults, query, recommend, userId]);

  const hasBadges = nlpResult && (
    nlpResult.budget !== null ||
    nlpResult.usage !== null ||
    nlpResult.priorites.length > 0 ||
    nlpResult.profil_passagers !== null
  );

  return (
    <div className="search-bar-container">
      {/* ─── NLP Badges ──────────────────────────────────── */}
      {nlpLoading && (
        <div className="nlp-badges nlp-badges--loading" aria-live="polite">
          <div className="nlp-badge-skeleton" />
          <div className="nlp-badge-skeleton" />
          <div className="nlp-badge-skeleton" />
        </div>
      )}
      {hasBadges && !nlpLoading && (
        <div className="nlp-badges" aria-live="polite" aria-label="Critères extraits par IA">
          {nlpResult.budget !== null && (
            <span className="nlp-badge nlp-badge--budget">
              <span className="nlp-badge__icon">{BADGE_ICONS.budget}</span>
              <span className="nlp-badge__label">Budget</span>
              <span className="nlp-badge__value">{formatBudget(nlpResult.budget)}</span>
            </span>
          )}
          {nlpResult.usage !== null && (
            <span className="nlp-badge nlp-badge--usage">
              <span className="nlp-badge__icon">{BADGE_ICONS.usage}</span>
              <span className="nlp-badge__label">Usage</span>
              <span className="nlp-badge__value">{humanize(nlpResult.usage)}</span>
            </span>
          )}
          {nlpResult.priorites.map((p, i) => (
            <span className="nlp-badge nlp-badge--priorite" key={`prio-${i}`}>
              <span className="nlp-badge__icon">{BADGE_ICONS.priorite}</span>
              <span className="nlp-badge__value">{humanize(p)}</span>
            </span>
          ))}
          {nlpResult.profil_passagers !== null && (
            <span className="nlp-badge nlp-badge--profil">
              <span className="nlp-badge__icon">{BADGE_ICONS.profil}</span>
              <span className="nlp-badge__label">Profil</span>
              <span className="nlp-badge__value">{humanize(nlpResult.profil_passagers)}</span>
            </span>
          )}
        </div>
      )}

      {/* ─── Search Input ────────────────────────────────── */}
      <div className="search-bar">
        <div className="search-icon" aria-hidden="true">⌕</div>
        <input
          type="text"
          className="search-input"
          id="nlp-search-input"
          placeholder="Décrivez le véhicule que vous cherchez — budget, usage, carburant..."
          autoComplete="off"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => { if (event.key === 'Enter') void submit(); }}
        />
        <button
          className="search-btn"
          id="nlp-search-submit"
          onClick={() => void submit()}
          disabled={isLoading || nlpLoading || !query.trim()}
        >
          <span>
            {isLoading || nlpLoading ? 'Analyse...' : 'Rechercher'}
          </span>
        </button>
      </div>
    </div>
  );
}
