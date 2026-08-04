import { useEffect, useState, useCallback } from 'react';
import { useLocation, useSearchParams } from 'react-router-dom';
import { vehicleService } from '../services/vehicleService';
import type { Vehicle, VehicleFilters, FuelType, BodyType } from '../types/vehicle';
import { FUEL_LABELS, BODY_LABELS } from '../types/vehicle';
import VehicleCard from '../components/vehicle-card/VehicleCard';
import type { RecommendationResponse } from '../services/recommendationService';
import fr from '../i18n/fr';
import './Catalogue.css';

const PAGE_SIZE = 12;

export default function Catalogue() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [searchParams] = useSearchParams();
  const location = useLocation();
  const initialRecommendations = (location.state as { recommendations?: RecommendationResponse } | null)?.recommendations;
  
  // Keep local state for recommendations so we can clear them when filters change
  const [activeRecommendations, setActiveRecommendations] = useState<RecommendationResponse | null>(initialRecommendations || null);
  
  const matchScores = Object.fromEntries(
    (activeRecommendations?.items ?? []).map((item) => [item.vehicle_id, item.match_score]),
  );
  
  // Filter States
  const [searchTerm, setSearchTerm] = useState('');
  const [activeFuel, setActiveFuel] = useState<FuelType | ''>('');
  const [activeBody, setActiveBody] = useState<BodyType | ''>('');
  const [city, setCity] = useState('');
  const [priceMin, setPriceMin] = useState('');
  const [priceMax, setPriceMax] = useState('');
  const [activeSort, setActiveSort] = useState('created_at-desc');
  const [activeCondition, setActiveCondition] = useState('occasion');
  const [savedSearch, setSavedSearch] = useState(false);
  const [activeModel, setActiveModel] = useState('');

  // Initialize from URL params
  useEffect(() => {
    const fuel = searchParams.get('fuel_type') as FuelType | '';
    const body = searchParams.get('body_type') as BodyType | '';
    const isNew = searchParams.get('is_new');
    const brand = searchParams.get('brand');
    const model = searchParams.get('model');
    
    if (fuel) setActiveFuel(fuel);
    if (body) setActiveBody(body);
    if (isNew === 'true') setActiveCondition('neuf');
    if (brand) setSearchTerm(brand);
    if (model) setActiveModel(model);
  }, [searchParams]);

  const handleFilterChange = (setter: any, value: any) => {
    setter(value);
    setPage(1);
    // If the user manually changes a filter, we drop the NLP recommendations
    // and switch to standard backend filtering.
    setActiveRecommendations(null);
  };

  const fetchVehicles = useCallback(
    async (currentPage: number) => {
      setLoading(true);
      setError(null);
      
      const filters: VehicleFilters = {};
      if (activeFuel) filters.fuel_type = activeFuel;
      if (activeBody) filters.body_type = activeBody;
      if (city) filters.city = city;
      if (priceMin) filters.price_min = parseInt(priceMin, 10);
      if (priceMax) filters.price_max = parseInt(priceMax, 10);
      if (searchTerm) filters.brand = searchTerm; // Simplified search mapping for now
      if (activeModel) filters.model = activeModel;

      const [sort_by, sort_order] = activeSort.split('-');
      filters.sort_by = sort_by;
      filters.sort_order = sort_order as 'asc' | 'desc';
      
      if (activeCondition === 'neuf' || activeCondition === 'occasion') {
        filters.condition = activeCondition;
      }

      if (activeCondition === 'neuf' && !activeModel) {
        filters.group_by_model = true;
      }

      try {
        if (activeRecommendations) {
          // If we have recommendations, just show them (no pagination implemented yet for NLP)
          const recommendedVehicles = await Promise.all(
            activeRecommendations.items.map((item) => vehicleService.getVehicleById(item.vehicle_id)),
          );
          setVehicles(recommendedVehicles.filter(v => v !== null) as Vehicle[]);
          setTotal(activeRecommendations.total);
          setPages(Math.max(1, Math.ceil(activeRecommendations.total / PAGE_SIZE)));
          return;
        }
        
        const res = await vehicleService.getVehicles({
          ...filters,
          page: currentPage,
          page_size: PAGE_SIZE,
        });
        setVehicles(res.items);
        setTotal(res.total);
        setPages(res.pages);
      } catch (err) {
        console.error('Erreur chargement catalogue:', err);
        setError("Impossible de charger les véhicules. Vérifiez que le backend est lancé.");
        setVehicles([]);
        setTotal(0);
      } finally {
        setLoading(false);
      }
    },
    [activeFuel, activeBody, city, priceMin, priceMax, searchTerm, activeModel, activeSort, activeCondition, activeRecommendations]
  );

  useEffect(() => {
    fetchVehicles(page);
  }, [page, fetchVehicles]);

  const handleClearFilters = () => {
    setSearchTerm('');
    setActiveFuel('');
    setActiveBody('');
    setCity('');
    setPriceMin('');
    setPriceMax('');
    setActiveSort('created_at-desc');
    setActiveCondition('');
    setActiveModel('');
    setPage(1);
    setActiveRecommendations(null);
  };

  const getPaginationRange = (): (number | '...')[] => {
    if (pages <= 7) return Array.from({ length: pages }, (_, i) => i + 1);
    const range: (number | '...')[] = [1];
    const start = Math.max(2, page - 1);
    const end = Math.min(pages - 1, page + 1);
    if (start > 2) range.push('...');
    for (let i = start; i <= end; i++) range.push(i);
    if (end < pages - 1) range.push('...');
    range.push(pages);
    return range;
  };

  return (
    <div className="catalogue">
      <div className="catalogue__container">
        
        {/* ─── Sidebar Filters (Avito Style) ────────────────────── */}
        <aside className="catalogue__sidebar">
          
          <div className="catalogue__sidebar-top">
            <div className="catalogue__save-search">
              <div className="catalogue__save-search-info">
                <span className="catalogue__save-icon">⭐</span>
                <span>Sauvegarder la recherche</span>
              </div>
              <label className="catalogue__toggle">
                <input 
                  type="checkbox" 
                  checked={savedSearch} 
                  onChange={(e) => setSavedSearch(e.target.checked)}
                />
                <span className="catalogue__toggle-slider"></span>
              </label>
            </div>
            {(activeFuel || activeBody || city || priceMin || priceMax || searchTerm || activeCondition) && (
              <button className="catalogue__clear-btn" onClick={handleClearFilters}>
                Effacer
              </button>
            )}
          </div>

          <div className="catalogue__filter-block">
            <div className="catalogue__search-input-wrapper">
              <span className="catalogue__search-icon">🔍</span>
              <input 
                type="text" 
                placeholder="Que recherchez-vous ?" 
                className="catalogue__input"
                value={searchTerm}
                onChange={(e) => handleFilterChange(setSearchTerm, e.target.value)}
              />
            </div>
          </div>

          <div className="catalogue__filter-block">
            <label className="catalogue__label">Carburant</label>
            <div className="catalogue__select-wrapper">
              <select 
                className="catalogue__select"
                value={activeFuel}
                onChange={(e) => handleFilterChange(setActiveFuel, e.target.value as FuelType)}
              >
                <option value="">Tous les carburants</option>
                {Object.entries(FUEL_LABELS).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="catalogue__filter-block">
            <label className="catalogue__label">Catégorie</label>
            <div className="catalogue__select-wrapper">
              <select 
                className="catalogue__select"
                value={activeBody}
                onChange={(e) => handleFilterChange(setActiveBody, e.target.value as BodyType)}
              >
                <option value="">Toutes les catégories</option>
                {Object.entries(BODY_LABELS).map(([key, label]) => (
                  <option key={key} value={key}>{label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="catalogue__filter-block">
            <label className="catalogue__label">État du véhicule</label>
            <div className="catalogue__select-wrapper">
              <select 
                className="catalogue__select"
                value={activeCondition}
                onChange={(e) => handleFilterChange(setActiveCondition, e.target.value)}
              >
                <option value="">Tous les véhicules</option>
                <option value="neuf">Neuf</option>
                <option value="occasion">Occasion</option>
              </select>
            </div>
          </div>

          <div className="catalogue__filter-block">
            <label className="catalogue__label">Ville - Secteur</label>
            <div className="catalogue__select-wrapper">
              <span className="catalogue__input-prefix-icon">📍</span>
              <select 
                className="catalogue__select catalogue__select--with-icon"
                value={city}
                onChange={(e) => handleFilterChange(setCity, e.target.value)}
              >
                <option value="">Choisir ville - secteur</option>
                <option value="Casablanca">Casablanca</option>
                <option value="Rabat">Rabat</option>
                <option value="Marrakech">Marrakech</option>
                <option value="Tanger">Tanger</option>
                <option value="Fès">Fès</option>
              </select>
            </div>
          </div>

          <div className="catalogue__filter-block">
            <label className="catalogue__label">Prix</label>
            <div className="catalogue__price-inputs">
              <div className="catalogue__price-input-wrapper">
                <input 
                  type="number" 
                  placeholder="Min" 
                  className="catalogue__input catalogue__input--price"
                  value={priceMin}
                  onChange={(e) => handleFilterChange(setPriceMin, e.target.value)}
                />
                <span className="catalogue__price-suffix">MAD</span>
              </div>
              <div className="catalogue__price-input-wrapper">
                <input 
                  type="number" 
                  placeholder="Max" 
                  className="catalogue__input catalogue__input--price"
                  value={priceMax}
                  onChange={(e) => handleFilterChange(setPriceMax, e.target.value)}
                />
                <span className="catalogue__price-suffix">MAD</span>
              </div>
            </div>
          </div>

          <div className="catalogue__filter-block">
            <label className="catalogue__label">Trier par</label>
            <div className="catalogue__select-wrapper">
              <select 
                className="catalogue__select"
                value={activeSort}
                onChange={(e) => handleFilterChange(setActiveSort, e.target.value)}
              >
                <option value="created_at-desc">Plus récentes</option>
                <option value="price-asc">Prix croissant</option>
                <option value="price-desc">Prix décroissant</option>
                <option value="mileage-asc">Kilométrage</option>
                <option value="year-desc">Année</option>
              </select>
            </div>
          </div>
          
          <div className="catalogue__sidebar-footer">
            <button className="catalogue__submit-btn">
              {loading ? 'Chargement...' : `(${total}) annonces`}
            </button>
          </div>
        </aside>

        {/* ─── Main Content ─────────────────────────────────────── */}
        <main className="catalogue__main">
          
          {/* Active filters summary */}
          <div className="catalogue__main-header">
            <h1 className="catalogue__main-title">
              {activeModel && searchTerm 
                ? `${searchTerm} ${activeModel}`
                : activeCondition === 'neuf' 
                  ? 'Voitures neuves au Maroc' 
                  : activeCondition === 'occasion' 
                    ? "Voitures d'occasion au Maroc" 
                    : 'Voitures au Maroc'}
            </h1>
            <span className="catalogue__main-count">1 - {vehicles.length} sur {total} annonces</span>
          </div>

          {error ? (
            <div className="catalogue__error">
              <div className="catalogue__error-icon">⚠️</div>
              <p className="catalogue__error-msg">{error}</p>
              <button
                className="catalogue__error-retry"
                onClick={() => fetchVehicles(page)}
              >
                🔄 Réessayer
              </button>
            </div>
          ) : loading ? (
            <div className="catalogue__grid">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="catalogue__skeleton">
                  <div className="catalogue__skeleton-image" />
                  <div className="catalogue__skeleton-body">
                    <div className="catalogue__skeleton-line catalogue__skeleton-line--title" />
                    <div className="catalogue__skeleton-line catalogue__skeleton-line--subtitle" />
                    <div className="catalogue__skeleton-line catalogue__skeleton-line--specs" />
                  </div>
                </div>
              ))}
            </div>
          ) : vehicles.length > 0 ? (
            <>
              <div className="catalogue__grid">
                {vehicles.map((v) => (
                  <div key={v.id} className="catalogue__card-wrapper">
                    <VehicleCard 
                      vehicle={v} 
                      animationDelay={0} 
                      matchScore={matchScores[v.id]} 
                      isGrouped={activeCondition === 'neuf' && !activeModel}
                    />
                  </div>
                ))}
              </div>

              {pages > 1 && (
                <nav className="catalogue__pagination">
                  <button
                    className="catalogue__page-btn catalogue__page-btn--nav"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    ← Précédent
                  </button>

                  {getPaginationRange().map((p, idx) =>
                    p === '...' ? (
                      <span key={`dots-${idx}`} className="catalogue__page-dots">…</span>
                    ) : (
                      <button
                        key={p}
                        className={`catalogue__page-btn ${p === page ? 'catalogue__page-btn--active' : ''}`}
                        onClick={() => setPage(p as number)}
                      >
                        {p}
                      </button>
                    )
                  )}

                  <button
                    className="catalogue__page-btn catalogue__page-btn--nav"
                    disabled={page >= pages}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    Suivant →
                  </button>
                </nav>
              )}
            </>
          ) : (
            <div className="catalogue__empty">
              <div className="catalogue__empty-icon">🚗</div>
              <h2 className="catalogue__empty-title">Aucun résultat trouvé</h2>
              <p className="catalogue__empty-desc">Modifiez vos filtres pour voir plus d'annonces.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
