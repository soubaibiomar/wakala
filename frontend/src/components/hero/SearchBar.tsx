import { useCallback, useState, type FormEvent } from 'react';
import { Mic, Square, X, Search, Sparkles } from 'lucide-react';
import { useVoiceInput } from '../../hooks/useVoiceInput';
import type { RecommendationResponse } from '../../services/recommendationService';

interface SearchBarProps {
  userId?: string | null;
  onResults?: (query: string, result?: RecommendationResponse | null) => void;
  onActiveChange?: (active: boolean) => void;
}

const SEARCH_SUGGESTIONS = [
  'Une voiture familiale sous 250 000 MAD',
  'SUV automatique économique',
  'Voiture électrique pour la ville',
  'Je cherche une voiture fiable',
];

export default function SearchBar({ userId, onResults, onActiveChange }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);

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
    setSearchLoading(true);
    setIsFocused(false);
    onActiveChange?.(false);
    if (onResults) {
      onResults(trimmed, null);
    } else {
      window.dispatchEvent(new CustomEvent('wakala:recommendation-search', { detail: { message: trimmed } }));
    }
    setSearchLoading(false);
  }, [onResults, onActiveChange]);

  const handleSubmitForm = (e: FormEvent) => {
    e.preventDefault();
    void submitSearch(query);
  };

  const handleClear = () => {
    setQuery('');
  };

  return (
    <>
      <div className="search-bar-container">
      {isFocused && (
        <div className="search-suggestions" role="listbox" aria-label="Suggestions de recherche">
          <p className="search-suggestions__label">Essayez une recherche</p>
          {SEARCH_SUGGESTIONS.map((suggestion) => (
            <button
              type="button"
              className="search-suggestion"
              key={suggestion}
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => { setQuery(suggestion); setIsFocused(false); }}
            >
              <Sparkles size={14} />
              <span>{suggestion}</span>
            </button>
          ))}
        </div>
      )}

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
            const hasArabic = /[\u0600-\u06FF]/.test(val);
            if (hasArabic && voice.lang !== 'ar-MA') {
              voice.setLang('ar-MA');
            } else if (!hasArabic && val.trim().length > 0 && voice.lang !== 'fr-FR' && voice.lang !== 'en-US') {
              voice.setLang('fr-FR');
            }
          }}
          readOnly={voice.status === 'listening'}
          onFocus={() => {
            setIsFocused(true);
            onActiveChange?.(true);
          }}
          onBlur={() => window.setTimeout(() => {
            setIsFocused(false);
            onActiveChange?.(false);
          }, 150)}
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
            {searchLoading ? 'Analyse...' : 'Rechercher'}
          </span>
        </button>
      </form>
    </div>
    </>
  );
}
