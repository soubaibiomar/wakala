import { useEffect, useState, useCallback, useRef, type ReactNode, type Dispatch, type SetStateAction } from 'react';
import { useLocation, useSearchParams } from 'react-router-dom';
import { Plus, Edit3, Trash2, Image as ImageIcon, CheckCircle2, AlertCircle, X, ShieldCheck, SlidersHorizontal } from 'lucide-react';
import { vehicleService } from '../services/vehicleService';
import { useAuth } from '../context/AuthContext';
import type { Vehicle, VehicleFilters, FuelType, BodyType, TransmissionType } from '../types/vehicle';
import { FUEL_LABELS, BODY_LABELS, TRANSMISSION_LABELS } from '../types/vehicle';
import VehicleCard from '../components/vehicle-card/VehicleCard';
import type { RecommendationResponse } from '../services/recommendationService';
import fr from '../i18n/fr';
import './Catalogue.css';
import { resolveVehicleImage } from '../utils/vehicleImageResolver';

import { extractMaximumBudget, extractBrandPreference } from '../components/recommendation-experience/recommendationClient';

const PAGE_SIZE = 12;

const BUDGET_BROWSE_OPTIONS = [
  { label: 'Moins de 150 000 MAD', max: 150000, brand: 'Dacia', model: 'Sandero' },
  { label: 'Moins de 250 000 MAD', max: 250000, brand: 'Renault', model: 'Clio' },
  { label: 'Moins de 350 000 MAD', max: 350000, brand: 'Peugeot', model: '208' },
  { label: 'Moins de 500 000 MAD', max: 500000, brand: 'Toyota', model: 'Corolla' },
  { label: 'Moins de 750 000 MAD', max: 750000, brand: 'BMW', model: 'X3' },
  { label: 'Tous les budgets', max: null, brand: 'Aston Martin', model: 'DB12' },
];

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
        ? `/api/v1/admin/vehicles/${editingVehicleId}` 
        : '/api/v1/admin/vehicles';
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
      const res = await fetch(`/api/v1/admin/vehicles/${v.id}`, {
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
  const [catalogueResetKey, setCatalogueResetKey] = useState(0);
  
  const recMap = Object.fromEntries(
    (activeRecommendations?.items ?? []).map((item) => [item.vehicle_id, item]),
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
  const [yearMin, setYearMin] = useState('');
  const [yearMax, setYearMax] = useState('');
  const [mileageMax, setMileageMax] = useState('');
  const [activeTransmission, setActiveTransmission] = useState<TransmissionType | ''>('');
  const [doors, setDoors] = useState('');
  const [seats, setSeats] = useState('');
  const [color, setColor] = useState('');
  const [minEnginePower, setMinEnginePower] = useState('');
  const [is4x4, setIs4x4] = useState(false);
  const [openFilterSections, setOpenFilterSections] = useState<Record<string, boolean>>({ availability: false, body: false, specification: false });
  const [savedSearch, setSavedSearch] = useState(false);
  const [showAssistantHint, setShowAssistantHint] = useState(true);
  const [activeModel, setActiveModel] = useState('');
  const [isMobileFiltersOpen, setIsMobileFiltersOpen] = useState(false);

  const activeFiltersCount = [
    activeFuel, activeBody, city, priceMin, priceMax, searchTerm,
    activeCondition, yearMin, yearMax, mileageMax, activeTransmission,
    doors, seats, color, minEnginePower, is4x4 ? '4x4' : '',
  ].filter(Boolean).length;

  const [lastQuery, setLastQuery] = useState<string | null>(null);
  const fetchRequestRef = useRef(0);
  
  // Initialize from URL params
  useEffect(() => {
    const q = searchParams.get('q');
    const fuel = searchParams.get('fuel_type') as FuelType | '';
    const body = searchParams.get('body_type') as BodyType | '';
    const isNew = searchParams.get('is_new');
    const brand = searchParams.get('brand');
    const model = searchParams.get('model');
    const maxPrice = searchParams.get('price_max');
    
    if (fuel) setActiveFuel(fuel);
    if (body) setActiveBody(body);
    if (isNew === 'true') setActiveCondition('neuf');
    if (brand) setSearchTerm(brand);
    if (model) setActiveModel(model);
    const queryBudget = q ? extractMaximumBudget(q) : null;
    if (maxPrice) setPriceMax(maxPrice);
    else if (queryBudget !== null) setPriceMax(String(queryBudget));

    if (q && q !== lastQuery) {
      setLastQuery(q);
      // The recommendation bar and the chatbot share one qualification flow.
      // Do not fetch three cars here: the assistant must ask its criteria first.
      setActiveRecommendations(null);
      const detectedBrand = extractBrandPreference(q);
      if (detectedBrand) {
        setSearchTerm(detectedBrand.apiValue);
        if (detectedBrand.model) {
          setActiveModel(detectedBrand.model);
        }
      } else {
        const cleanQ = q.replace(/[^\p{L}\p{N}\s-]/gu, ' ').trim().replace(/\s+/g, ' ');
        if (cleanQ.split(/\s+/).length <= 2) {
          setSearchTerm(cleanQ);
        } else {
          setLoading(true);
          fetchVehicles(1);
        }
      }
    } else if (!q && lastQuery) {
      const clearedQuery = lastQuery;
      setLastQuery(null);
      setActiveRecommendations(null);
      // These values may have been derived from the assistant's `q` URL
      // parameter. Once that parameter is removed by the chatbot reset, do
      // not leave an invisible budget/brand filter constraining the catalogue.
      if (!searchParams.has('price_max')) setPriceMax('');
      setSearchTerm((current) => current === clearedQuery ? '' : current);
    }
  }, [searchParams, lastQuery]);

  useEffect(() => {
    const handleAssistantVisibility = (event: Event) => {
      const isOpen = (event as CustomEvent<{ open?: boolean }>).detail?.open;
      if (typeof isOpen === 'boolean') setShowAssistantHint(!isOpen);
    };
    window.addEventListener('wakala:assistant-visibility', handleAssistantVisibility);
    return () => window.removeEventListener('wakala:assistant-visibility', handleAssistantVisibility);
  }, []);

  useEffect(() => {
    const handleRecommendationResults = (event: Event) => {
      const detail = (event as CustomEvent<{
        cars?: Vehicle[];
        total?: number;
        final?: boolean;
        empty?: boolean;
        reset?: boolean;
        filters?: { fuel_type?: string; body_type?: string; transmission?: string; price_max?: number };
      }>).detail;
      if (detail?.reset) {
        setActiveRecommendations(null);
        setActiveFuel('');
        setActiveBody('');
        setActiveTransmission('');
        setPriceMin('');
        setPriceMax('');
        setSearchTerm('');
        setPage(1);
        setCatalogueResetKey((current) => current + 1);
        return;
      }
      if (detail?.filters) {
        if (detail.filters.fuel_type) setActiveFuel(detail.filters.fuel_type as FuelType);
        if (detail.filters.body_type) setActiveBody(detail.filters.body_type as BodyType);
        if (detail.filters.transmission) setActiveTransmission(detail.filters.transmission as TransmissionType);
        if (detail.filters.price_max) setPriceMax(String(detail.filters.price_max));
      }
      // `cars` is the actual recommendation pool. Rendering is paginated
      // later, so never use the 20-card display cap as the recommendation
      // total.
      const cars = detail?.cars || [];
      if (!cars.length && !detail?.empty) return;
      const total = typeof detail?.total === 'number' ? detail.total : cars.length;
      setActiveRecommendations({
        items: cars.map((car) => ({
          vehicle_id: car.id,
          match_score: (car as Vehicle & { match_score?: number }).match_score || 0,
          score_breakdown: { content: 0, collaborative: 0 },
          eight_dimension_scores: (car as Vehicle & { eight_dimension_scores?: Record<string, number> }).eight_dimension_scores,
          total_8d_score: (car as Vehicle & { total_8d_score?: number }).total_8d_score,
          total_8d_percent: (car as Vehicle & { total_8d_percent?: number }).total_8d_percent,
        })),
        total,
        page: 1,
        page_size: PAGE_SIZE,
        method: 'content-based',
      });
      setPage(1);
    };
    window.addEventListener('wakala:recommendation-results', handleRecommendationResults);
    return () => window.removeEventListener('wakala:recommendation-results', handleRecommendationResults);
  }, []);

  const handleFilterChange = (setter: any, value: any) => {
    setter(value);
    setPage(1);
    // If the user manually changes a filter, we drop the NLP recommendations
    // and switch to standard backend filtering.
    setActiveRecommendations(null);
  };

  const fetchVehicles = useCallback(
    async (currentPage: number) => {
      const requestId = ++fetchRequestRef.current;
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
      if (yearMin) filters.year_min = parseInt(yearMin, 10);
      if (yearMax) filters.year_max = parseInt(yearMax, 10);
      if (mileageMax) filters.mileage_max = parseInt(mileageMax, 10);
      if (activeTransmission) filters.transmission = activeTransmission;
      if (doors) filters.doors = parseInt(doors, 10);
      if (seats) filters.seats = parseInt(seats, 10);
      if (color) filters.color = color;
      if (minEnginePower) filters.min_engine_power = parseInt(minEnginePower, 10);
      if (is4x4) filters.is_4x4 = true;

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
          const start = (currentPage - 1) * PAGE_SIZE;
          const pageItems = activeRecommendations.items.slice(start, start + PAGE_SIZE);
          const recommendedVehicles = await Promise.all(
            pageItems.map((item) =>
              vehicleService.getVehicleById(item.vehicle_id).catch(() => null)
            ),
          );
          const validVehicles = recommendedVehicles.filter((v): v is Vehicle => v !== null);
          if (requestId !== fetchRequestRef.current) return;
          setVehicles(validVehicles);
          setTotal(activeRecommendations.total ?? validVehicles.length);
          setPages(Math.max(1, Math.ceil((activeRecommendations.total ?? validVehicles.length) / PAGE_SIZE)));
          return;
        }
        
        const res = await vehicleService.getVehicles({
          ...filters,
          page: currentPage,
          page_size: PAGE_SIZE,
        });
        if (requestId !== fetchRequestRef.current) return;
        setVehicles(res.items);
        setTotal(res.total);
        setPages(res.pages);
      } catch (err) {
        if (requestId !== fetchRequestRef.current) return;
        console.error('Erreur chargement catalogue:', err);
        setError("Impossible de charger les véhicules. Vérifiez que le backend est lancé.");
        setVehicles([]);
        setTotal(0);
      } finally {
        if (requestId === fetchRequestRef.current) setLoading(false);
      }
    },
    [activeFuel, activeBody, city, priceMin, priceMax, searchTerm, activeModel, yearMin, yearMax, mileageMax, activeTransmission, doors, seats, color, minEnginePower, is4x4, activeSort, activeCondition, activeRecommendations, catalogueResetKey]
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
    setYearMin('');
    setYearMax('');
    setMileageMax('');
    setActiveTransmission('');
    setDoors('');
    setSeats('');
    setColor('');
    setMinEnginePower('');
    setIs4x4(false);
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
        
        {/* Mobile Filter & Sort Toggle Button */}
        <div className="catalogue__mobile-filter-bar">
          <button
            type="button"
            className={`catalogue__mobile-filter-btn ${isMobileFiltersOpen ? 'catalogue__mobile-filter-btn--active' : ''}`}
            onClick={() => setIsMobileFiltersOpen(!isMobileFiltersOpen)}
            aria-expanded={isMobileFiltersOpen}
          >
            <SlidersHorizontal size={16} />
            <span>Filtres & Tri</span>
            {activeFiltersCount > 0 && (
              <span className="catalogue__filter-badge">{activeFiltersCount}</span>
            )}
            <span className="catalogue__mobile-filter-arrow">
              {isMobileFiltersOpen ? '▲' : '▼'}
            </span>
          </button>
        </div>

        {/* ─── Sidebar Filters (Avito Style) ────────────────────── */}
        <aside className={`catalogue__sidebar${isMobileFiltersOpen ? ' catalogue__sidebar--mobile-open' : ''}`}>
          
          <div className="catalogue__sidebar-top">
            <div className="catalogue__save-search">
              <div className="catalogue__save-search-info">
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
            {(activeFuel || activeBody || city || priceMin || priceMax || searchTerm || activeCondition || yearMin || yearMax || mileageMax || activeTransmission || doors || seats || color || minEnginePower || is4x4) && (
              <button className="catalogue__clear-btn" onClick={handleClearFilters}>
                Effacer
              </button>
            )}
          </div>

          <div className="catalogue__filter-block">
            <div className="catalogue__search-input-wrapper">
              <input 
                type="text" 
                placeholder="Que recherchez-vous ?" 
                className="catalogue__input"
                value={searchTerm}
                onChange={(e) => handleFilterChange(setSearchTerm, e.target.value)}
              />
            </div>
          </div>

          <div className="catalogue__filter-block catalogue__filter-block--state">
            <span className="catalogue__label">État du véhicule</span>
            <div className="catalogue__choice-group" role="group" aria-label="État du véhicule">
              <button
                type="button"
                className={`catalogue__choice ${activeCondition === '' ? 'catalogue__choice--active' : ''}`}
                onClick={() => handleFilterChange(setActiveCondition, '')}
              >
                Tous
              </button>
              <button
                type="button"
                className={`catalogue__choice ${activeCondition === 'neuf' ? 'catalogue__choice--active' : ''}`}
                onClick={() => handleFilterChange(setActiveCondition, 'neuf')}
              >
                Neufs
              </button>
              <button
                type="button"
                className={`catalogue__choice ${activeCondition === 'occasion' ? 'catalogue__choice--active' : ''}`}
                onClick={() => handleFilterChange(setActiveCondition, 'occasion')}
              >
                Occasion
              </button>
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
              <select 
                className="catalogue__select"
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

          <FilterSection
            title="Disponibilité & âge"
            sectionKey="availability"
            openSections={openFilterSections}
            setOpenSections={setOpenFilterSections}
          >
            <div className="catalogue__advanced-grid">
              <label>Année min.</label>
              <label>Année max.</label>
              <select value={yearMin} onChange={(e) => handleFilterChange(setYearMin, e.target.value)}>
                <option value="">Toutes</option>
                {[2026, 2025, 2024, 2023, 2022, 2021, 2020].map((year) => <option key={year} value={year}>{year}</option>)}
              </select>
              <select value={yearMax} onChange={(e) => handleFilterChange(setYearMax, e.target.value)}>
                <option value="">Toutes</option>
                {[2026, 2025, 2024, 2023, 2022, 2021, 2020].map((year) => <option key={year} value={year}>{year}</option>)}
              </select>
            </div>
            <label className="catalogue__field-label" htmlFor="mileage-max">Kilométrage maximum</label>
            <div className="catalogue__input-with-suffix">
              <input id="mileage-max" type="number" min="0" placeholder="Illimité" value={mileageMax} onChange={(e) => handleFilterChange(setMileageMax, e.target.value)} />
              <span>km</span>
            </div>
          </FilterSection>

          <FilterSection
            title="Carrosserie & motorisation"
            sectionKey="body"
            openSections={openFilterSections}
            setOpenSections={setOpenFilterSections}
          >
            <label className="catalogue__field-label">Boîte de vitesses</label>
            <select value={activeTransmission} onChange={(e) => handleFilterChange(setActiveTransmission, e.target.value as TransmissionType)}>
              <option value="">Toutes les boîtes</option>
              {Object.entries(TRANSMISSION_LABELS).map(([key, label]) => <option key={key} value={key}>{label}</option>)}
            </select>
            <label className="catalogue__field-label">Puissance minimale</label>
            <select value={minEnginePower} onChange={(e) => handleFilterChange(setMinEnginePower, e.target.value)}>
              <option value="">Toutes les puissances</option>
              <option value="100">100 ch et plus</option>
              <option value="130">130 ch et plus</option>
              <option value="160">160 ch et plus</option>
              <option value="200">200 ch et plus</option>
            </select>
            <label className="catalogue__check-row">
              <input type="checkbox" checked={is4x4} onChange={(e) => handleFilterChange(setIs4x4, e.target.checked)} />
              Transmission intégrale (4x4)
            </label>
          </FilterSection>

          <FilterSection
            title="Spécifications"
            sectionKey="specification"
            openSections={openFilterSections}
            setOpenSections={setOpenFilterSections}
          >
            <div className="catalogue__advanced-grid">
              <label>Portes</label>
              <label>Places</label>
              <select value={doors} onChange={(e) => handleFilterChange(setDoors, e.target.value)}>
                <option value="">Toutes</option>
                {[2, 3, 4, 5].map((value) => <option key={value} value={value}>{value}</option>)}
              </select>
              <select value={seats} onChange={(e) => handleFilterChange(setSeats, e.target.value)}>
                <option value="">Toutes</option>
                {[2, 4, 5, 7, 8, 9].map((value) => <option key={value} value={value}>{value}</option>)}
              </select>
            </div>
            <label className="catalogue__field-label" htmlFor="vehicle-color">Couleur</label>
            <input id="vehicle-color" type="text" placeholder="Ex. blanc, noir, gris" value={color} onChange={(e) => handleFilterChange(setColor, e.target.value)} />
          </FilterSection>

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
            <span className="catalogue__main-count">
              1 - {vehicles.length} sur {total} {activeRecommendations ? 'finitions recommandées' : 'annonces'}
            </span>
          </div>

          {!activeRecommendations && !activeFuel && !activeBody && !city && !priceMin && !priceMax && !searchTerm && !activeModel && (
            <section className="catalogue__budget-browser" aria-labelledby="budget-browser-title">
              <div className="catalogue__budget-heading">
                <span className="catalogue__budget-kicker">EXPLORER LE CATALOGUE</span>
                <h2 id="budget-browser-title">Parcourir par budget</h2>
              </div>
              <div className="catalogue__budget-grid">
                {BUDGET_BROWSE_OPTIONS.map((option) => (
                  <button
                    type="button"
                    className="catalogue__budget-card"
                    key={option.label}
                    onClick={() => {
                      handleFilterChange(setPriceMax, option.max ? String(option.max) : '');
                      setPriceMin('');
                    }}
                  >
                    <span className="catalogue__budget-image">
                      <img
                        src={resolveVehicleImage(option.brand, option.model)}
                        alt=""
                        aria-hidden="true"
                        onError={(event) => {
                          event.currentTarget.onerror = null;
                          event.currentTarget.src = '/assets/car-side-fallback.svg';
                        }}
                      />
                    </span>
                    <span className="catalogue__budget-label">{option.label}</span>
                  </button>
                ))}
              </div>
            </section>
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
                      isGrouped={activeCondition === 'neuf' && !activeModel}
                      keyFacts={recMap[v.id]?.key_facts}
                      budgetMargin={recMap[v.id]?.budget_margin}
                      bestVersionName={recMap[v.id]?.best_version_name}
                      eightDimensionScores={recMap[v.id]?.eight_dimension_scores}
                      total8dScore={recMap[v.id]?.total_8d_score}
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
      {showAssistantHint && (
        <aside className="catalogue__assistant-hint" aria-label="Assistant de recherche">
          <button
            type="button"
            className="catalogue__assistant-close"
            aria-label="Fermer le message de l'assistant"
            onClick={() => setShowAssistantHint(false)}
          >
            <X size={15} aria-hidden="true" />
          </button>
          <img src="/assets/chatlogo.png" alt="" className="catalogue__assistant-avatar" />
          <p
            role="button"
            tabIndex={0}
            onClick={() => {
              setShowAssistantHint(false);
              window.dispatchEvent(new CustomEvent('wakala:open-chat-from-hint'));
            }}
            onKeyDown={(event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                setShowAssistantHint(false);
                window.dispatchEvent(new CustomEvent('wakala:open-chat-from-hint'));
              }
            }}
          >
            Je peux vous aider à trouver la voiture idéale. Une question&nbsp;?
          </p>
        </aside>
      )}
    </div>
  );
}

function FilterSection({
  title,
  sectionKey,
  openSections,
  setOpenSections,
  children,
}: {
  title: string;
  sectionKey: string;
  openSections: Record<string, boolean>;
  setOpenSections: Dispatch<SetStateAction<Record<string, boolean>>>;
  children: ReactNode;
}) {
  const isOpen = openSections[sectionKey];
  return (
    <section className={`catalogue__filter-section ${isOpen ? 'catalogue__filter-section--open' : ''}`}>
      <button
        type="button"
        className="catalogue__filter-section-toggle"
        aria-expanded={isOpen}
        onClick={() => setOpenSections((current) => ({ ...current, [sectionKey]: !current[sectionKey] }))}
      >
        <span>{title}</span>
        <span aria-hidden="true">{isOpen ? '−' : '+'}</span>
      </button>
      {isOpen && <div className="catalogue__filter-section-content">{children}</div>}
    </section>
  );
}

