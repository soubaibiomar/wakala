import { useCallback, useState, useRef, useEffect, useMemo, type FormEvent, type KeyboardEvent } from 'react';
import { Search, Mic, Square, X, Sparkles } from 'lucide-react';
import { useVoiceInput } from '../../hooks/useVoiceInput';
import { isRecommendationQuery } from '../../utils/recommendationIntentDetector';
import './CatalogueSearchBar.css';

interface CatalogueSearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  variant?: 'sidebar' | 'mobile';
  ariaLabel?: string;
}

const SEARCH_SUGGESTIONS = [
  'Une voiture familiale sous 250 000 MAD',
  'SUV automatique économique',
  'Voiture électrique pour la ville',
  'Je cherche une voiture fiable',
];

export default function CatalogueSearchBar({
  value,
  onChange,
  placeholder,
  variant = 'sidebar',
  ariaLabel = 'Rechercher un véhicule ou demander un conseil IA',
}: CatalogueSearchBarProps) {
  const [isFocused, setIsFocused] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Détection en temps réel de l'intention : Recommandation / Conseil IA vs Recherche directe
  const isRecommendation = useMemo(() => isRecommendationQuery(value), [value]);

  // Web Speech API hook (identique à l'accueil)
  const voice = useVoiceInput({
    defaultLang: 'fr-FR',
    onTranscript: (text) => {
      const separator = value.trim() ? ' ' : '';
      const updated = value + separator + text;
      onChange(updated);
    },
  });

  // Bascule automatique de la langue vocale si texte en Arabe / Darija
  useEffect(() => {
    const hasArabic = /[\u0600-\u06FF]/.test(value);
    if (hasArabic && voice.lang !== 'ar-MA') {
      voice.setLang('ar-MA');
    } else if (!hasArabic && value.trim().length > 0 && voice.lang !== 'fr-FR' && voice.lang !== 'en-US') {
      voice.setLang('fr-FR');
    }
  }, [value, voice]);

  const triggerRecommendation = useCallback((queryText: string) => {
    const trimmed = queryText.trim();
    if (!trimmed) {
      window.dispatchEvent(new CustomEvent('wakala:open-chat'));
      return;
    }
    window.dispatchEvent(
      new CustomEvent('wakala:recommendation-search', { detail: { message: trimmed } })
    );
  }, []);

  const handleSubmit = useCallback(
    async (e?: FormEvent) => {
      if (e) e.preventDefault();
      const trimmed = value.trim();
      setIsFocused(false);
      if (!trimmed) return;

      // Aiguillage intelligent selon l'intention détectée
      if (isRecommendationQuery(trimmed)) {
        // Demande de recommandation / besoin IA -> Lancer l'expérience conversationnelle IA
        triggerRecommendation(trimmed);
      } else {
        // Recherche catalogue directe (marque, modèle, version, ville)
        onChange(trimmed);
      }
    },
    [value, onChange, triggerRecommendation]
  );

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      void handleSubmit();
    }
  };

  const handleClear = () => {
    onChange('');
  };

  const handleSuggestionClick = (suggestion: string) => {
    onChange(suggestion);
    setIsFocused(false);
    triggerRecommendation(suggestion);
  };

  const dynamicPlaceholder =
    voice.status === 'listening'
      ? 'Parlez maintenant...'
      : placeholder || (variant === 'mobile' ? 'Marque, modèle ou besoin IA...' : 'Que recherchez-vous ? (ex: Golf ou besoin IA)');

  return (
    <div
      ref={containerRef}
      className={`catalogue-search-container catalogue-search-container--${variant}`}
    >
      {/* Search Suggestions Popover on focus */}
      {isFocused && (
        <div
          className="catalogue-search-suggestions"
          role="listbox"
          aria-label="Suggestions de recherche par IA"
        >
          <p className="catalogue-search-suggestions__label">
            <Sparkles size={13} className="sparkles-icon" /> Suggestions de recherche IA
          </p>
          {SEARCH_SUGGESTIONS.map((suggestion) => (
            <button
              type="button"
              className="catalogue-search-suggestion"
              key={suggestion}
              onMouseDown={(event) => event.preventDefault()}
              onClick={() => handleSuggestionClick(suggestion)}
            >
              <Sparkles size={13} />
              <span>{suggestion}</span>
            </button>
          ))}
        </div>
      )}

      <form 
        className={`catalogue-search-bar ${isRecommendation ? 'catalogue-search-bar--recommendation' : ''}`} 
        onSubmit={handleSubmit} 
        role="search"
      >
        <div className="catalogue-search-bar__left-icon" aria-hidden="true">
          {isRecommendation ? (
            <Sparkles size={16} className="catalogue-search-bar__left-sparkle" />
          ) : (
            <Search size={17} />
          )}
        </div>

        <input
          type="text"
          className="catalogue-search-bar__input"
          placeholder={dynamicPlaceholder}
          value={voice.interimTranscript ? value + (value ? ' ' : '') + voice.interimTranscript : value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setIsFocused(true)}
          onBlur={() => window.setTimeout(() => setIsFocused(false), 150)}
          aria-label={ariaLabel}
          autoComplete="off"
        />

        {/* Badge visuel d'indication d'intention IA en temps réel */}
        {isRecommendation && (
          <div className="catalogue-search-bar__ai-tag" title="Intention de conseil IA détectée">
            <span>Conseil IA</span>
          </div>
        )}

        <div className="catalogue-search-bar__actions">
          {value.length > 0 && (
            <button
              type="button"
              className="catalogue-search-btn catalogue-search-btn--clear"
              onClick={handleClear}
              title="Effacer la recherche"
              aria-label="Effacer la recherche"
            >
              <X size={14} />
            </button>
          )}

          {voice.isSupported && (
            <button
              type="button"
              className={`catalogue-search-btn catalogue-search-btn--mic ${
                voice.status === 'listening' ? 'catalogue-search-btn--mic-listening' : ''
              }`}
              onClick={voice.toggleListening}
              title={voice.status === 'listening' ? "Arrêter l'écoute" : 'Recherche vocale (Français / Darija)'}
              aria-label={voice.status === 'listening' ? 'Arrêter la reconnaissance vocale' : 'Activer la recherche vocale'}
            >
              {voice.status === 'listening' ? <Square size={13} fill="currentColor" /> : <Mic size={15} />}
            </button>
          )}

          <button
            type="submit"
            className={`catalogue-search-btn ${
              isRecommendation ? 'catalogue-search-btn--recommendation' : 'catalogue-search-btn--search'
            }`}
            onClick={handleSubmit}
            title={isRecommendation ? "Lancer le Conseil IA Wakala (Entrée)" : "Rechercher dans le catalogue"}
            aria-label={isRecommendation ? "Recommander avec l'IA" : "Rechercher"}
          >
            {isRecommendation ? (
              <Sparkles size={15} className="catalogue-search-btn__sparkle-icon" />
            ) : (
              <Search size={15} />
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
