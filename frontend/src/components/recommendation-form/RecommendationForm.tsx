/**
 * RecommendationForm — Formulaire de critères pour le moteur
 * de recommandation hybride (content-based + collaborative filtering).
 */

import { useState } from 'react';

interface RecommendationCriteria {
  budget_min?: number;
  budget_max?: number;
  fuel_type?: string;
  usage?: string;
  brand_preference?: string;
  body_type?: string;
}

export default function RecommendationForm() {
  const [criteria, setCriteria] = useState<RecommendationCriteria>({});

  const handleChange = (field: keyof RecommendationCriteria, value: string | number) => {
    setCriteria((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Appel API /api/v1/recommendations
    console.log('Critères soumis:', criteria);
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '500px' }}>
      <h3>Affiner vos critères</h3>

      <label>
        Budget max (MAD)
        <input
          type="number"
          placeholder="25000"
          onChange={(e) => handleChange('budget_max', Number(e.target.value))}
        />
      </label>

      <label>
        Carburant
        <select onChange={(e) => handleChange('fuel_type', e.target.value)}>
          <option value="">Tous</option>
          <option value="essence">Essence</option>
          <option value="diesel">Diesel</option>
          <option value="hybride">Hybride</option>
          <option value="electrique">Électrique</option>
        </select>
      </label>

      <label>
        Usage
        <select onChange={(e) => handleChange('usage', e.target.value)}>
          <option value="">Sélectionner</option>
          <option value="urbain">Trajet urbain</option>
          <option value="familial">Famille</option>
          <option value="long_trajet">Longs trajets</option>
          <option value="sportif">Sportif</option>
        </select>
      </label>

      <button type="submit" className="search-btn" style={{ alignSelf: 'flex-start' }}>
        Obtenir des recommandations
      </button>
    </form>
  );
}
