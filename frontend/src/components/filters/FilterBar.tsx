/**
 * components/filters/FilterBar.tsx — Barre de filtres latérale pour le catalogue.
 *
 * Lit les query params d'URL pour préremplir les filtres venant du Hero.
 * Émet les changements via un callback onFiltersChange.
 */

import { useEffect, useState, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import type { VehicleFilters, FuelType, BodyType } from '../../types/vehicle';
import './FilterBar.css';

interface FilterBarProps {
  onFiltersChange: (filters: VehicleFilters) => void;
  total: number;
}

// ─── Options ──────────────────────────────────────────────────

const FUEL_OPTIONS: { value: FuelType | ''; label: string }[] = [
  { value: '', label: 'Tous' },
  { value: 'essence', label: 'Essence' },
  { value: 'diesel', label: 'Diesel' },
  { value: 'hybride', label: 'Hybride' },
  { value: 'electrique', label: 'Électrique' },
  { value: 'gpl', label: 'GPL' },
];

const BODY_OPTIONS: { value: BodyType | ''; label: string }[] = [
  { value: '', label: 'Tous' },
  { value: 'citadine', label: 'Citadine' },
  { value: 'berline', label: 'Berline' },
  { value: 'suv', label: 'SUV' },
  { value: 'break', label: 'Break' },
  { value: 'coupe', label: 'Coupé' },
  { value: 'monospace', label: 'Monospace' },
  { value: 'utilitaire', label: 'Utilitaire' },
];

const SORT_OPTIONS = [
  { value: 'created_at', label: 'Plus récents' },
  { value: 'price', label: 'Prix' },
  { value: 'year', label: 'Année' },
  { value: 'mileage', label: 'Kilométrage' },
];

// ─── État interne des filtres ─────────────────────────────────

interface LocalFilters {
  brand: string;
  city: string;
  fuel_type: string;
  body_type: string;
  price_min: string;
  price_max: string;
  year_min: string;
  year_max: string;
  sort_by: string;
  sort_order: 'asc' | 'desc';
}

const INITIAL: LocalFilters = {
  brand: '', city: '', fuel_type: '', body_type: '',
  price_min: '', price_max: '', year_min: '', year_max: '',
  sort_by: 'created_at', sort_order: 'desc',
};

// ─── Composant ────────────────────────────────────────────────

export default function FilterBar({ onFiltersChange, total }: FilterBarProps) {
  const [searchParams] = useSearchParams();
  const [filters, setFilters] = useState<LocalFilters>(INITIAL);

  // Préremplir depuis les query params d'URL (provenant du Hero)
  useEffect(() => {
    const fromURL: Partial<LocalFilters> = {};
    const q = searchParams.get('q') || searchParams.get('query');
    if (q) fromURL.brand = q; // Fallback : on traite la query comme une marque
    if (searchParams.get('brand')) fromURL.brand = searchParams.get('brand')!;
    if (searchParams.get('city')) fromURL.city = searchParams.get('city')!;
    if (searchParams.get('fuel_type')) fromURL.fuel_type = searchParams.get('fuel_type')!;
    if (searchParams.get('body_type')) fromURL.body_type = searchParams.get('body_type')!;
    if (searchParams.get('price_min')) fromURL.price_min = searchParams.get('price_min')!;
    if (searchParams.get('price_max')) fromURL.price_max = searchParams.get('price_max')!;

    if (Object.keys(fromURL).length > 0) {
      setFilters((prev) => ({ ...prev, ...fromURL }));
    }
  }, [searchParams]);

  // Émettre les filtres nettoyés vers le parent
  const emitFilters = useCallback(
    (f: LocalFilters) => {
      const clean: VehicleFilters = {
        sort_by: f.sort_by,
        sort_order: f.sort_order,
      };
      if (f.brand) clean.brand = f.brand;
      if (f.city) clean.city = f.city;
      if (f.fuel_type) clean.fuel_type = f.fuel_type as FuelType;
      if (f.body_type) clean.body_type = f.body_type as BodyType;
      if (f.price_min) clean.price_min = Number(f.price_min);
      if (f.price_max) clean.price_max = Number(f.price_max);
      if (f.year_min) clean.year_min = Number(f.year_min);
      if (f.year_max) clean.year_max = Number(f.year_max);
      onFiltersChange(clean);
    },
    [onFiltersChange]
  );

  useEffect(() => {
    emitFilters(filters);
  }, [filters, emitFilters]);

  const handleChange = (key: keyof LocalFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => setFilters(INITIAL);

  const activeCount = Object.entries(filters).filter(
    ([k, v]) => v && k !== 'sort_by' && k !== 'sort_order'
  ).length;

  return (
    <aside className="filter-bar">
      <div className="filter-bar__header">
        <h3 className="filter-bar__title">Filtres</h3>
        {activeCount > 0 && (
          <button className="btn btn--ghost btn--sm" onClick={resetFilters}>
            Réinitialiser
          </button>
        )}
      </div>

      {/* Marque */}
      <div className="filter-bar__group">
        <label className="input-label">Marque</label>
        <input
          className="input"
          placeholder="Ex : Peugeot"
          value={filters.brand}
          onChange={(e) => handleChange('brand', e.target.value)}
        />
      </div>

      {/* Ville */}
      <div className="filter-bar__group">
        <label className="input-label">Ville</label>
        <input
          className="input"
          placeholder="Ex : Casablanca"
          value={filters.city}
          onChange={(e) => handleChange('city', e.target.value)}
        />
      </div>

      {/* Carburant */}
      <div className="filter-bar__group">
        <label className="input-label">Carburant</label>
        <select
          className="input select"
          value={filters.fuel_type}
          onChange={(e) => handleChange('fuel_type', e.target.value)}
        >
          {FUEL_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* Carrosserie */}
      <div className="filter-bar__group">
        <label className="input-label">Carrosserie</label>
        <select
          className="input select"
          value={filters.body_type}
          onChange={(e) => handleChange('body_type', e.target.value)}
        >
          {BODY_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* Budget */}
      <div className="filter-bar__group">
        <label className="input-label">Budget (MAD)</label>
        <div className="filter-bar__range">
          <input
            className="input"
            type="number"
            placeholder="Min"
            value={filters.price_min}
            onChange={(e) => handleChange('price_min', e.target.value)}
          />
          <input
            className="input"
            type="number"
            placeholder="Max"
            value={filters.price_max}
            onChange={(e) => handleChange('price_max', e.target.value)}
          />
        </div>
      </div>

      {/* Année */}
      <div className="filter-bar__group">
        <label className="input-label">Année</label>
        <div className="filter-bar__range">
          <input
            className="input"
            type="number"
            placeholder="De"
            value={filters.year_min}
            onChange={(e) => handleChange('year_min', e.target.value)}
          />
          <input
            className="input"
            type="number"
            placeholder="À"
            value={filters.year_max}
            onChange={(e) => handleChange('year_max', e.target.value)}
          />
        </div>
      </div>

      {/* Tri */}
      <div className="filter-bar__group">
        <label className="input-label">Trier par</label>
        <select
          className="input select"
          value={filters.sort_by}
          onChange={(e) => handleChange('sort_by', e.target.value)}
        >
          {SORT_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      <div className="filter-bar__group">
        <label className="input-label">Ordre</label>
        <div className="filter-bar__range">
          <button
            className={`btn btn--sm ${filters.sort_order === 'desc' ? 'btn--primary' : 'btn--secondary'}`}
            style={{ flex: 1 }}
            onClick={() => handleChange('sort_order', 'desc')}
          >
            ↓ Desc
          </button>
          <button
            className={`btn btn--sm ${filters.sort_order === 'asc' ? 'btn--primary' : 'btn--secondary'}`}
            style={{ flex: 1 }}
            onClick={() => handleChange('sort_order', 'asc')}
          >
            ↑ Asc
          </button>
        </div>
      </div>

      {/* Résumé */}
      <div className="filter-bar__summary">
        {total} résultat{total !== 1 ? 's' : ''}
        {activeCount > 0 && (
          <span className="badge badge--cyan" style={{ marginLeft: '8px' }}>
            {activeCount} filtre{activeCount > 1 ? 's' : ''}
          </span>
        )}
      </div>
    </aside>
  );
}
