import { useCallback, useState } from 'react';
import type { RecommendationResponse } from '../../services/recommendationService';
import { useMatchmaker } from '../recommendation-form/useMatchmaker';

interface SearchBarProps {
  userId?: string | null;
  onResults: (query: string, result: RecommendationResponse) => void;
}

export default function SearchBar({ userId, onResults }: SearchBarProps) {
  const [query, setQuery] = useState('');
  const { isLoading, recommend } = useMatchmaker();
  const submit = useCallback(async () => {
    const trimmed = query.trim();
    if (!trimmed || isLoading) return;
    const result = await recommend({ query: trimmed, user_id: userId });
    if (result) onResults(trimmed, result);
  }, [isLoading, onResults, query, recommend, userId]);

  return (
    <div className="search-bar">
      <div className="search-icon" aria-hidden="true">⌕</div>
      <input type="text" className="search-input" placeholder="Décrivez le véhicule que vous cherchez — budget, usage, carburant..." autoComplete="off" value={query} onChange={(event) => setQuery(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter') void submit(); }} />
      <button className="search-btn" onClick={() => void submit()} disabled={isLoading || !query.trim()}>
        <span>{isLoading ? 'Recherche...' : 'Rechercher'}</span>
      </button>
    </div>
  );
}
