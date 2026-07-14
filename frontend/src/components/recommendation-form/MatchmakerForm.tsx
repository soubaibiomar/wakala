import { useState } from 'react';
import type { RecommendationResponse } from '../../services/recommendationService';
import { useMatchmaker } from './useMatchmaker';

interface MatchmakerFormProps {
  userId?: string | null;
  onResults?: (result: RecommendationResponse) => void;
}

export default function MatchmakerForm({ userId, onResults }: MatchmakerFormProps) {
  const [query, setQuery] = useState('');
  const { isLoading, error, recommend } = useMatchmaker();

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    const result = await recommend({ query: trimmed, user_id: userId });
    if (result) onResults?.(result);
  };

  return (
    <form onSubmit={submit} className="matchmaker-form">
      <label htmlFor="matchmaker-query">Parlez-nous de votre quotidien</label>
      <textarea
        id="matchmaker-query"
        value={query}
        onChange={(event) => setQuery(event.target.value)}
        placeholder="Ex. Longs trajets avec deux enfants, budget 250 000 MAD et faible consommation."
        rows={3}
      />
      {error && <p role="alert">{error}</p>}
      <button type="submit" className="search-btn" disabled={isLoading || !query.trim()}>
        {isLoading ? 'Analyse...' : 'Trouver mon match'}
      </button>
    </form>
  );
}
