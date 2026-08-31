import { useEffect, useState, useCallback } from 'react';
import { useLocation, useSearchParams } from 'react-router-dom';
import { Plus, Edit3, Trash2, Image as ImageIcon, CheckCircle2, AlertCircle, X, ShieldCheck } from 'lucide-react';
import { vehicleService } from '../services/vehicleService';
import { useAuth } from '../context/AuthContext';
import type { Vehicle, VehicleFilters, FuelType, BodyType } from '../types/vehicle';
import { FUEL_LABELS, BODY_LABELS } from '../types/vehicle';
import VehicleCard from '../components/vehicle-card/VehicleCard';
import { recommendationService, type RecommendationResponse } from '../services/recommendationService';
import fr from '../i18n/fr';
import './Catalogue.css';
import PriorityTubes from '../components/priority-tubes/PriorityTubes';
import { ALL_CRITERIA, getIntelligentCriteria } from '../utils/priorityUtils';

const PAGE_SIZE = 12;

export default function Catalogue() {
  const { user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Admin Vehicle CRUD State
  const [showVehicleModal, setShowVehicleModal] = useState(false);
  const [editingVehicleId, setEditingVehicleId] = useState<string | null>(null);
  const [isSubmittingVehicle, setIsSubmittingVehicle] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null);

  const [vehicleForm, setVehicleForm] = useState({
    brand: 'Dacia',
    model: '',
    version: '',
    year: 2026,
    price: 250000,
    fuel_type: 'hybride',
    transmission: 'automatique',
    body_type: 'suv',
    engine_power_hp: 130,
    city: 'Casablanca',
    image_url: '',
    source_url: '',
    description: '',
  });

  const showToast = (text: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  const openCreateModal = () => {
    setEditingVehicleId(null);
    setVehicleForm({
      brand: 'Dacia',
      model: '',
      version: '',
      year: 2026,
      price: 250000,
      fuel_type: 'hybride',
      transmission: 'automatique',
      body_type: 'suv',
      engine_power_hp: 130,
      city: 'Casablanca',
      image_url: '',
      source_url: '',
      description: '',
    });
    setShowVehicleModal(true);
  };

  const openEditModal = (v: Vehicle) => {
    setEditingVehicleId(v.id);
    const firstImg = v.images && v.images.length > 0 ? v.images[0] : '';
    const existingImg = typeof firstImg === 'string' ? firstImg : ((firstImg as any)?.file_path || '');
    setVehicleForm({
      brand: v.brand || '',
      model: v.model || '',
      version: v.version || '',
      year: v.year || 2026,
      price: v.price || 0,
      fuel_type: v.fuel_type || 'hybride',
      transmission: v.transmission || 'automatique',
      body_type: v.body_type || 'suv',
      engine_power_hp: v.engine_power_hp || 130,
      city: v.city || 'Casablanca',
      image_url: existingImg,
      source_url: v.source_url || '',
      description: v.description || '',
    });
    setShowVehicleModal(true);
  };

  const handleImageFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        showToast('L’image est trop volumineuse (max 10 Mo).', 'error');
        return;
      }
      const reader = new FileReader();
      reader.onload = (event) => {
        const base64Url = event.target?.result as string;
        setVehicleForm((prev) => ({ ...prev, image_url: base64Url }));
        showToast('Photo chargée depuis l’ordinateur avec succès !', 'success');
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSaveVehicle = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!vehicleForm.brand || !vehicleForm.model) {
      showToast('Veuillez renseigner la marque et le modèle.', 'error');
      return;
    }
    setIsSubmittingVehicle(true);
    try {
      const url = editingVehicleId 
        ? `http://localhost:8000/api/v1/admin/vehicles/${editingVehicleId}` 
        : 'http://localhost:8000/api/v1/admin/vehicles';
      const method = editingVehicleId ? 'PUT' : 'POST';
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(vehicleForm)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erreur lors de l’enregistrement');
      showToast(data.message || 'Véhicule enregistré avec succès !', 'success');
      setShowVehicleModal(false);
      fetchVehicles(page);
    } catch (err: any) {
      showToast(err.message || 'Erreur réseau', 'error');
    } finally {
      setIsSubmittingVehicle(false);
    }
  };

  const handleDeleteVehicle = async (v: Vehicle) => {
    const confirmDelete = window.confirm(`Supprimer définitivement ${v.brand} ${v.model} (${v.version || ''}) du catalogue ?`);
    if (!confirmDelete) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/admin/vehicles/${v.id}`, {
        method: 'DELETE'
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Erreur suppression');
      showToast(data.message || 'Véhicule supprimé du catalogue.', 'success');
      fetchVehicles(page);
    } catch (err: any) {
      showToast(err.message || 'Erreur suppression', 'error');
    }
  };

  const [searchParams, setSearchParams] = useSearchParams();
  const location = useLocation();
  const initialRecommendations = (location.state as { recommendations?: RecommendationResponse } | null)?.recommendations;
  
  // Keep local state for recommendations so we can clear them when filters change
  const [activeRecommendations, setActiveRecommendations] = useState<RecommendationResponse | null>(initialRecommendations || null);
  
  const recMap = Object.fromEntries(
    (activeRecommendations?.items ?? []).map((item) => [item.vehicle_id, item]),
  );

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
  const [activeCondition, setActiveCondition] = useState('');  // PIVOT: default to all (was 'occasion')
  const [savedSearch, setSavedSearch] = useState(false);
  const [activeModel, setActiveModel] = useState('');

  const [lastQuery, setLastQuery] = useState<string | null>(null);
  
  // Priority Tubes State
  const [activeCriteria, setActiveCriteria] = useState<{id: string, label: string, colorClass: string, value: number}[]>([]);
  const [budget, setBudget] = useState<number | null>(null);
  const [isUpdatingAI, setIsUpdatingAI] = useState(false);

  // Initialize from URL params
  useEffect(() => {
    const q = searchParams.get('q');
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

    if (q && q !== lastQuery) {
      setLastQuery(q);
      setLoading(true);
      
      // Setup intelligent tubes
      let initialCriteria: {id: string, label: string, colorClass: string, value: number}[] = [];
      let urlBudget = searchParams.get('budget');
      setBudget(urlBudget ? Number(urlBudget) : 250000);
      
      searchParams.forEach((value, key) => {
        if (key.startsWith('prio_')) {
          const id = key.replace('prio_', '');
          const cDef = ALL_CRITERIA.find(c => c.id === id);
          if (cDef) {
            initialCriteria.push({ ...cDef, value: Number(value) });
          }
        }
      });
      
      if (initialCriteria.length > 0) {
        setActiveCriteria(initialCriteria);
      } else {
        setActiveCriteria(getIntelligentCriteria(null));
      }

      recommendationService.search({ query: q, page_size: 3 })
        .then((res) => {
          if (res && res.items && res.items.length > 0) {
            setActiveRecommendations(res);
          } else {
            setActiveRecommendations(null);
            if (q.trim().split(/\s+/).length <= 2) {
              setSearchTerm(q);
            }
          }
        })
        .catch((err) => {
          console.error("Erreur récupération recommandations IA:", err);
          setActiveRecommendations(null);
          if (q.trim().split(/\s+/).length <= 2) {
            setSearchTerm(q);
          }
        });
    } else if (!q && lastQuery) {
      setLastQuery(null);
      setActiveRecommendations(null);
    }
  }, [searchParams, lastQuery]);

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
          // If we have recommendations, load them safely
          const recommendedVehicles = await Promise.all(
            activeRecommendations.items.map((item) =>
              vehicleService.getVehicleById(item.vehicle_id).catch(() => null)
            ),
          );
          const validVehicles = recommendedVehicles.filter((v): v is Vehicle => v !== null);
          setVehicles(validVehicles);
          setTotal(activeRecommendations.total || validVehicles.length);
          setPages(Math.max(1, Math.ceil((activeRecommendations.total || validVehicles.length) / PAGE_SIZE)));
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
    setLastQuery(null);
    setSearchParams({});
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
                {/* PIVOT: mileage sort removed */}
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
          
          {/* Toast Notification */}
          {toastMessage && (
            <div className={`catalogue-admin-toast ${toastMessage.type}`}>
              {toastMessage.type === 'success' && <CheckCircle2 size={16} />}
              {toastMessage.type === 'error' && <AlertCircle size={16} />}
              <span>{toastMessage.text}</span>
            </div>
          )}

          {/* Admin Mode Floating Header */}
          {isAdmin && (
            <div className="catalogue__admin-bar">
              <div className="catalogue__admin-bar-left">
                <span className="admin-status-chip">
                  <ShieldCheck size={14} /> Mode Administrateur Wakala
                </span>
                <p>Gestion directe du catalogue national ({total} véhicules disponibles)</p>
              </div>
              <button 
                type="button" 
                className="btn-admin-add-vehicle"
                onClick={openCreateModal}
              >
                <Plus size={16} /> Ajouter un Véhicule
              </button>
            </div>
          )}

          {/* Active filters summary */}
          <div className="catalogue__main-header">
            <h1 className="catalogue__main-title">
              {activeRecommendations 
                ? 'Véhicules Recommandés par l\'IA'
                  : activeModel && searchTerm 
                    ? `${searchTerm} ${activeModel}`
                    : 'Voitures neuves au Maroc'}
            </h1>
            <span className="catalogue__main-count">1 - {vehicles.length} sur {total} annonces</span>
          </div>

          {activeRecommendations && (
            <div className="catalogue__ai-banner" style={{ display: 'block' }}>
              <div className="catalogue__ai-banner-content" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <span className="catalogue__ai-banner-badge">✨ Match IA Wakala</span>
                  <p className="catalogue__ai-banner-text">
                    Résultats optimisés et classés par pertinence pour : <strong>"{searchParams.get('q') || 'votre recherche'}"</strong>
                  </p>
                </div>
                <button 
                  className="catalogue__ai-banner-reset" 
                  onClick={handleClearFilters}
                  title="Revenir à la vue générale"
                >
                  Fermer ✕
                </button>
              </div>
              
              <div className="catalogue__ai-priorities">
                <h3>Ajustez vos priorités</h3>
                <PriorityTubes 
                  criteria={activeCriteria}
                  budget={budget}
                  onCriteriaChange={(idx, val) => {
                    const newC = [...activeCriteria];
                    newC[idx].value = val;
                    setActiveCriteria(newC);
                  }}
                  onBudgetChange={setBudget}
                />
                <div style={{ textAlign: 'center' }}>
                  <button 
                    className="catalogue__ai-priorities-btn"
                    onClick={() => {
                      setIsUpdatingAI(true);
                      const prioText = activeCriteria.map(c => `${c.label}:${c.value}%`).join(', ');
                      const fullQuery = `${searchParams.get('q')} Priorités strictes: ${prioText}. Budget max: ${budget} MAD`;
                      recommendationService.search({ query: fullQuery, page_size: 3 })
                        .then(res => {
                          if (res?.items) setActiveRecommendations(res);
                        })
                        .finally(() => setIsUpdatingAI(false));
                    }}
                    disabled={isUpdatingAI}
                  >
                    {isUpdatingAI ? 'Mise à jour en cours...' : 'Mettre à jour les recommandations'}
                  </button>
                </div>
              </div>
            </div>
          )}

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
                      keyFacts={recMap[v.id]?.key_facts}
                      budgetMargin={recMap[v.id]?.budget_margin}
                      bestVersionName={recMap[v.id]?.best_version_name}
                    />

                    {/* Admin Action Buttons for each vehicle card */}
                    {isAdmin && (
                      <div className="catalogue__card-admin-bar">
                        <button 
                          type="button" 
                          className="btn-card-admin-edit"
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            openEditModal(v);
                          }}
                          title="Modifier les données et l'image du véhicule"
                        >
                          <Edit3 size={13} /> Modifier & Photo
                        </button>
                        <button 
                          type="button" 
                          className="btn-card-admin-delete"
                          onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            handleDeleteVehicle(v);
                          }}
                          title="Supprimer du catalogue"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    )}
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

      {/* ─── Admin Vehicle Create / Edit Modal ────────────────────── */}
      {showVehicleModal && (
        <div className="catalogue-modal-backdrop" onClick={() => setShowVehicleModal(false)}>
          <div className="catalogue-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="catalogue-modal-header">
              <div>
                <h2>{editingVehicleId ? 'Modifier les données du véhicule' : 'Ajouter un véhicule au catalogue'}</h2>
                <p>Mettez à jour les spécifications techniques et la photo studio détourée.</p>
              </div>
              <button className="btn-modal-close" onClick={() => setShowVehicleModal(false)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleSaveVehicle} className="catalogue-modal-form">
              <div className="form-grid-2">
                <div className="form-group">
                  <label>Marque *</label>
                  <input
                    type="text"
                    required
                    placeholder="Ex: Dacia, Renault, Hyundai..."
                    value={vehicleForm.brand}
                    onChange={(e) => setVehicleForm({ ...vehicleForm, brand: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Modèle *</label>
                  <input
                    type="text"
                    required
                    placeholder="Ex: Duster 3, Clio 5, Tucson..."
                    value={vehicleForm.model}
                    onChange={(e) => setVehicleForm({ ...vehicleForm, model: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-grid-2">
                <div className="form-group">
                  <label>Version / Finition</label>
                  <input
                    type="text"
                    placeholder="Ex: Journey dCi 115 4x2, Techno E-Tech..."
                    value={vehicleForm.version}
                    onChange={(e) => setVehicleForm({ ...vehicleForm, version: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Prix Clé en Main (MAD) *</label>
                  <input
                    type="number"
                    required
                    min="0"
                    step="1000"
                    placeholder="Ex: 245000"
                    value={vehicleForm.price}
                    onChange={(e) => setVehicleForm({ ...vehicleForm, price: Number(e.target.value) })}
                  />
                </div>
              </div>

              <div className="form-grid-3">
                <div className="form-group">
                  <label>Année Modèle</label>
                  <input
                    type="number"
                    min="2020"
                    max="2030"
                    value={vehicleForm.year}
                    onChange={(e) => setVehicleForm({ ...vehicleForm, year: Number(e.target.value) })}
                  />
                </div>
                <div className="form-group">
                  <label>Carburant</label>
                  <select
                    value={vehicleForm.fuel_type}
                    onChange={(e) => setVehicleForm({ ...vehicleForm, fuel_type: e.target.value })}
                  >
                    <option value="hybride">Hybride (HEV/PHEV)</option>
                    <option value="essence">Essence</option>
                    <option value="diesel">Diesel</option>
                    <option value="electrique">100% Électrique</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Boîte de Vitesse</label>
                  <select
                    value={vehicleForm.transmission}
                    onChange={(e) => setVehicleForm({ ...vehicleForm, transmission: e.target.value })}
                  >
                    <option value="automatique">Automatique (BVA/EDC)</option>
                    <option value="manuelle">Manuelle (BVM)</option>
                  </select>
                </div>
              </div>

              <div className="form-grid-3">
                <div className="form-group">
                  <label>Carrosserie</label>
                  <select
                    value={vehicleForm.body_type}
                    onChange={(e) => setVehicleForm({ ...vehicleForm, body_type: e.target.value })}
                  >
                    <option value="suv">SUV / 4x4</option>
                    <option value="berline">Berline</option>
                    <option value="citadine">Citadine</option>
                    <option value="break">Break</option>
                    <option value="coupe">Coupé</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Puissance DIN (ch)</label>
                  <input
                    type="number"
                    value={vehicleForm.engine_power_hp}
                    onChange={(e) => setVehicleForm({ ...vehicleForm, engine_power_hp: Number(e.target.value) })}
                  />
                </div>
                <div className="form-group">
                  <label>Ville Showroom</label>
                  <input
                    type="text"
                    value={vehicleForm.city}
                    onChange={(e) => setVehicleForm({ ...vehicleForm, city: e.target.value })}
                  />
                </div>
              </div>

              {/* Photo Studio Management (File Upload or URL) with Live Image Preview */}
              <div className="form-group vehicle-image-upload-group">
                <label>Photo du Véhicule (Upload Local ou URL HD)</label>
                
                <div className="image-input-dual-mode">
                  <div className="file-upload-subbox">
                    <label className="btn-file-select-label">
                      Choisir une image sur votre ordinateur
                      <input
                        type="file"
                        accept="image/png, image/jpeg, image/webp"
                        style={{ display: 'none' }}
                        onChange={handleImageFileChange}
                      />
                    </label>
                  </div>
                  <div className="url-upload-subbox">
                    <input
                      type="text"
                      placeholder="Ou collez une URL d'image (ex: https://...)"
                      value={vehicleForm.image_url}
                      onChange={(e) => setVehicleForm({ ...vehicleForm, image_url: e.target.value })}
                    />
                  </div>
                </div>

                {vehicleForm.image_url && (
                  <div className="image-live-preview-box">
                    <div className="preview-top-bar">
                      <span className="preview-tag">Prévisualisation en direct :</span>
                      <button
                        type="button"
                        className="btn-clear-img"
                        onClick={() => setVehicleForm({ ...vehicleForm, image_url: '' })}
                      >
                        Effacer la photo
                      </button>
                    </div>
                    <img
                      src={vehicleForm.image_url}
                      alt="Aperçu Studio"
                      className="live-preview-img"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  </div>
                )}
              </div>

              <div className="form-group">
                <label>Lien Officiel Constructeur (.ma)</label>
                <input
                  type="url"
                  placeholder="https://www.dacia.ma/gamme/duster.html"
                  value={vehicleForm.source_url}
                  onChange={(e) => setVehicleForm({ ...vehicleForm, source_url: e.target.value })}
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="btn-modal-cancel"
                  onClick={() => setShowVehicleModal(false)}
                >
                  Annuler
                </button>
                <button
                  type="submit"
                  className="btn-modal-save"
                  disabled={isSubmittingVehicle}
                >
                  {isSubmittingVehicle ? 'Enregistrement...' : (editingVehicleId ? 'Sauvegarder les modifications' : 'Ajouter au catalogue')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

