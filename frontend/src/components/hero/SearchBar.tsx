import { useCallback, useState, type FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mic, Square, X, Search, Sparkles } from 'lucide-react';
import type { RecommendationResponse } from '../../services/recommendationService';
import { parseSearchQuery, type NlpExtractionResult } from '../../services/searchParseService';
import { useMatchmaker } from '../recommendation-form/useMatchmaker';
import { useVoiceInput } from '../../hooks/useVoiceInput';
import PriorityModal from '../../pages/PriorityForm/PriorityModal';

interface SearchBarProps {
  userId?: string | null;
  onResults?: (query: string, result?: RecommendationResponse | null) => void;
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
  const [clarificationAnswer, setClarificationAnswer] = useState('');
  const navigate = useNavigate();
  
  const { isLoading, recommend } = useMatchmaker();
  const [nlpResult, setNlpResult] = useState<NlpExtractionResult | null>(null);
  const [nlpLoading, setNlpLoading] = useState(false);
  const [showPriorityModal, setShowPriorityModal] = useState(false);

  // ─── Saisie vocale (Web Speech API) ───────────────────────
  const voice = useVoiceInput({
    defaultLang: 'fr-FR',
    onTranscript: (text) => {
      setQuery((prev) => {
        const separator = prev.trim() ? ' ' : '';
        return prev + separator + text;
      });
    },
  });

  const submitSearch = useCallback(async (textToSearch: string) => {
    const trimmed = textToSearch.trim();
    if (!trimmed) return;

    // Si on a déjà une question de clarification et une réponse, on les concatène
    let finalQuery = trimmed;
    if (nlpResult?.statut === 'clarification_requise' && clarificationAnswer.trim()) {
      finalQuery = `${trimmed} ${clarificationAnswer.trim()}`;
      setQuery(finalQuery);
      setClarificationAnswer('');
    }

    setNlpLoading(true);
    let parsedResult = nlpResult;
    try {
      parsedResult = await parseSearchQuery(finalQuery);
      setNlpResult(parsedResult);
    } catch (err) {
      console.error("Erreur NLP:", err);
    } finally {
      setNlpLoading(false);
    }

    // Au lieu de naviguer directement, on affiche la modale des priorités
    setShowPriorityModal(true);
  }, [nlpResult, clarificationAnswer]);

  const handleModalSubmit = (priorities: {name: string, value: number}[], budget: number | null) => {
    setShowPriorityModal(false);
    
    // Construct the query parameters
    const params = new URLSearchParams();
    if (nlpResult?.question) {
      params.append('q', nlpResult.question);
    } else {
      params.append('q', query);
    }
    
    // Add dynamic priorities
    priorities.forEach(p => {
      params.append(`prio_${p.name}`, p.value.toString());
    });
    
    if (budget) {
      params.append('budget', budget.toString());
    }
    
    // Redirect to Catalogue instead of chat
    navigate(`/catalogue?${params.toString()}`);
  };

  const handleSubmitForm = (e: FormEvent) => {
    e.preventDefault();
    void submitSearch(query);
  };

  const handleClear = () => {
    setQuery('');
    setNlpResult(null);
    setClarificationAnswer('');
  };

  const hasBadges = nlpResult && (
    nlpResult.budget !== null ||
    nlpResult.usage_prevu !== null ||
    nlpResult.priorites.length > 0 ||
    nlpResult.profil_passagers !== null
  );

  const needsClarification = nlpResult?.statut === 'clarification_requise';

  return (
    <>
      <PriorityModal 
        isOpen={showPriorityModal} 
        onClose={() => setShowPriorityModal(false)}
        onSubmitPriorities={handleModalSubmit}
        nlpResult={nlpResult}
      />
      <div className="search-bar-container">
      {/* ─── NLP Badges ──────────────────────────────────── */}
      {nlpLoading && (
        <div className="nlp-badges nlp-badges--loading" aria-live="polite">
          <div className="nlp-badge-skeleton" />
          <div className="nlp-badge-skeleton" />
          <div className="nlp-badge-skeleton" />
        </div>
      )}
      
      {hasBadges && !nlpLoading && !needsClarification && (
        <div className="nlp-badges" aria-live="polite" aria-label="Critères extraits par IA">
          {nlpResult.budget !== null && (
            <span className="nlp-badge nlp-badge--budget">
              <span className="nlp-badge__icon">{BADGE_ICONS.budget}</span>
              <span className="nlp-badge__label">Budget</span>
              <span className="nlp-badge__value">{formatBudget(nlpResult.budget)}</span>
            </span>
          )}
          {nlpResult.usage_prevu !== null && (
            <span className="nlp-badge nlp-badge--usage">
              <span className="nlp-badge__icon">{BADGE_ICONS.usage}</span>
              <span className="nlp-badge__label">Usage</span>
              <span className="nlp-badge__value">{humanize(nlpResult.usage_prevu)}</span>
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

      {/* ─── Clarification Loop ──────────────────────────── */}
      {needsClarification && !nlpLoading && (
        <div className="clarification-box">
          <p className="clarification-box__question">
            <strong>🤖 Assistant :</strong> {nlpResult.question}
          </p>
          <div className="clarification-box__form">
            <input
              type="text"
              className="clarification-box__input"
              value={clarificationAnswer}
              onChange={(e) => setClarificationAnswer(e.target.value)}
              placeholder="Votre réponse..."
              onKeyDown={(e) => { if (e.key === 'Enter') void submitSearch(query); }}
            />
            <button 
              className="clarification-box__btn"
              onClick={() => void submitSearch(query)}
            >
              Répondre
            </button>
          </div>
        </div>
      )}

      {/* ─── Search Input ────────────────────────────────── */}
      <form className="search-bar" onSubmit={handleSubmitForm}>
        <div className="search-icon" aria-hidden="true">
          <Search size={20} />
        </div>
        <input
          type="text"
          className="search-input"
          id="nlp-search-input"
          placeholder={
            voice.status === 'listening'
              ? 'Parlez maintenant...'
              : 'Décrivez vos besoins (ex: Bébé en route, 260 000 DH max, sécurité prioritaire...)'
          }
          autoComplete="off"
          value={voice.interimTranscript ? query + (query ? ' ' : '') + voice.interimTranscript : query}
          onChange={(event) => {
            const val = event.target.value;
            setQuery(val);
            if (needsClarification) setNlpResult(null);
            
            const hasArabic = /[\u0600-\u06FF]/.test(val);
            if (hasArabic && voice.lang !== 'ar-MA') {
              voice.setLang('ar-MA');
            } else if (!hasArabic && val.trim().length > 0 && voice.lang !== 'fr-FR' && voice.lang !== 'en-US') {
              voice.setLang('fr-FR');
            }
          }}
          readOnly={voice.status === 'listening'}
        />
        
        {/* ─── Bouton Clear (X) ───────────────────────── */}
        {query.length > 0 && (
          <button
            type="button"
            className="search-clear-btn"
            onClick={handleClear}
            title="Effacer la recherche"
            aria-label="Effacer la recherche"
          >
            <X size={16} />
          </button>
        )}

        {/* ─── Bouton micro (masqué si non supporté) ──── */}
        {voice.isSupported && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <button
              className={`mic-btn ${voice.status === 'listening' ? 'mic-btn--listening' : ''}`}
              onClick={voice.toggleListening}
              title={voice.status === 'listening' ? 'Arrêter l\'écoute' : 'Recherche vocale'}
              type="button"
              aria-label={voice.status === 'listening' ? 'Arrêter la reconnaissance vocale' : 'Activer la reconnaissance vocale'}
            >
              {voice.status === 'listening' ? <Square size={16} fill="currentColor" /> : <Mic size={19} />}
            </button>
          </div>
        )}

        <button
          type="submit"
          className="search-btn"
          id="nlp-search-submit"
          disabled={!query.trim()}
        >
          <Sparkles size={16} />
          <span>
            {nlpLoading ? 'Analyse...' : 'Rechercher'}
          </span>
        </button>
      </form>
    </div>
    </>
  );
}
