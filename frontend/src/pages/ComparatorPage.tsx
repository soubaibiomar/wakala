import React, { useEffect, useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { 
  Scale, 
  ChevronRight, 
  SlidersHorizontal, 
  ShieldCheck, 
  Check, 
  Plus, 
  Trophy, 
  Award,
  TrendingDown,
  TrendingUp,
  Fuel,
  Coins,
  Package,
  Zap,
  Sparkles,
  Car,
  Layers,
  ArrowRightLeft,
  X,
  Gauge,
  CircleDot,
  ExternalLink
} from 'lucide-react';
import { newCatalogService, ComparatorResponse, ModelListItem, BrandItem } from '../services/newCatalogService';
import { TestDriveModal } from '../components/modals/TestDriveModal';
import { resolveVehicleImage } from '../utils/vehicleImageResolver';
import { resolveBrandLogo } from '../utils/brandLogoResolver';
import './ComparatorPage.css';

export const ComparatorPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [comparatorData, setComparatorData] = useState<ComparatorResponse | null>(null);
  const [allModels, setAllModels] = useState<ModelListItem[]>([]);
  const [allBrands, setAllBrands] = useState<BrandItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [diffOnly, setDiffOnly] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'all' | 'pricing' | 'specs' | 'tco' | 'radar' | 'equipment'>('all');
  const [selectedTrimForTestDrive, setSelectedTrimForTestDrive] = useState<{ id: string; name: string; brand: string } | null>(null);

  // Cascading selector state for adding a new car slot
  const [selectedBrandSlug, setSelectedBrandSlug] = useState<string>('');
  const [filteredModels, setFilteredModels] = useState<ModelListItem[]>([]);
  const [selectedModelSlug, setSelectedModelSlug] = useState<string>('');
  const [modelTrims, setModelTrims] = useState<Array<{ id: string; name: string; slug: string; price_new_mad: number }>>([]);
  const [loadingTrims, setLoadingTrims] = useState<boolean>(false);

  const trimIdsParam = searchParams.get('trims') || '';

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (trimIdsParam) {
      const ids = trimIdsParam.split(',').filter(Boolean);
      if (ids.length >= 2) {
        loadComparison(ids);
      } else if (ids.length === 1 && allModels.length > 0) {
        autoSuggestSecondVehicle(ids[0]);
      } else {
        setLoading(false);
      }
    } else {
      // Default initial comparison between Duster and Captur
      loadComparison(['duster-3-2024-journey', 'captur-restyle-techno-dci-edc']);
    }
  }, [trimIdsParam, allModels]);

  const loadInitialData = async () => {
    try {
      const [models, brands] = await Promise.all([
        newCatalogService.getModels(),
        newCatalogService.getBrands()
      ]);
      setAllModels(models);
      setAllBrands(brands);
    } catch (err) {
      console.error('Failed to load catalog metadata', err);
    }
  };

  const autoSuggestSecondVehicle = async (firstIdOrSlug: string) => {
    try {
      const defaultRivals = ['duster-3-2024-journey', 'captur-restyle-techno-dci-edc', '2008-restyle-allure-pack-hdi'];
      const secondId = defaultRivals.find(r => r !== firstIdOrSlug) || defaultRivals[0];
      setSearchParams({ trims: `${firstIdOrSlug},${secondId}` });
    } catch (err) {
      console.error('Auto suggest error', err);
    }
  };

  const loadComparison = async (trimIds: string[]) => {
    setLoading(true);
    try {
      const data = await newCatalogService.compareTrims(trimIds);
      setComparatorData(data);
    } catch (err) {
      console.error('Error fetching comparator data', err);
    } finally {
      setLoading(false);
    }
  };

  // Cascading handler: Brand changed
  const handleBrandChange = (brandSlug: string) => {
    setSelectedBrandSlug(brandSlug);
    setSelectedModelSlug('');
    setModelTrims([]);
    if (!brandSlug) {
      setFilteredModels([]);
      return;
    }
    const matching = allModels.filter(m => m.brand.slug === brandSlug || m.brand.name.toLowerCase() === brandSlug.toLowerCase());
    setFilteredModels(matching);
  };

  // Cascading handler: Model changed
  const handleModelChange = async (modelSlug: string) => {
    setSelectedModelSlug(modelSlug);
    setModelTrims([]);
    if (!modelSlug) return;

    setLoadingTrims(true);
    try {
      const detail = await newCatalogService.getModelDetail(modelSlug);
      if (detail && detail.trims) {
        setModelTrims(detail.trims.map(t => ({
          id: t.id,
          name: t.name,
          slug: t.slug,
          price_new_mad: t.price_new_mad
        })));
      }
    } catch (err) {
      console.error('Failed to load model trims', err);
    } finally {
      setLoadingTrims(false);
    }
  };

  // Cascading handler: Trim selected -> Add to comparison
  const handleTrimSelect = (trimSlugOrId: string) => {
    if (!trimSlugOrId || !comparatorData) return;
    const currentIds = comparatorData.vehicles.map(v => v.id);
    if (currentIds.length < 4 && !currentIds.includes(trimSlugOrId)) {
      setSearchParams({ trims: [...currentIds, trimSlugOrId].join(',') });
      // Reset selector
      setSelectedBrandSlug('');
      setSelectedModelSlug('');
      setModelTrims([]);
    }
  };

  const handleRemoveVehicle = (vehicleId: string) => {
    if (!comparatorData) return;
    const remaining = comparatorData.vehicles.filter(v => v.id !== vehicleId).map(v => v.id);
    if (remaining.length >= 1) {
      setSearchParams({ trims: remaining.join(',') });
    }
  };

  // Dedicated image resolution with official studio priority
  const getVehicleImage = (v: { image_url?: string | null; brand_name: string; model_name: string }) => {
    const studio = resolveVehicleImage(v.brand_name, v.model_name);
    if (studio && !studio.includes('placeholder') && !studio.includes('unsplash')) {
      return studio;
    }
    if (v.image_url && !v.image_url.includes('placeholder') && !v.image_url.includes('cdn.group.renault.com') && (v.image_url.startsWith('/') || v.image_url.startsWith('http'))) {
      return v.image_url;
    }
    return studio || '/assets/hero-car.png';
  };

  const getBrandLogo = (brandName: string) => {
    return resolveBrandLogo(brandName);
  };

  // Numeric parser helper
  const parseNum = (str: string | number | null | undefined): number => {
    if (typeof str === 'number') return str;
    if (!str) return 0;
    const m = String(str).match(/(\d+[\.,]?\d*)/);
    return m ? parseFloat(m[1].replace(',', '.')) : 0;
  };

  const renderStars = (starsStr: string | null | undefined) => {
    const count = parseInt(starsStr || '0', 10);
    if (!count || isNaN(count)) return <span className="text-muted">Non testé</span>;
    return (
      <span className="ncap-stars-display">
        <span className="stars-active">{'★'.repeat(count)}</span>
        <span className="stars-inactive">{'★'.repeat(Math.max(0, 5 - count))}</span>
        <span className="stars-count">({count}/5)</span>
      </span>
    );
  };

  if (loading) {
    return (
      <div className="comparator-page">
        <div className="comparator-container">
          <div className="comparator-loading">
            <div className="spinner"></div>
            <p>Chargement de la matrice comparative officielle...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!comparatorData || comparatorData.vehicles.length < 2) {
    return (
      <div className="comparator-page">
        <div className="comparator-container">
          <div className="comparator-empty">
            <h2>Comparateur de Véhicules Neufs</h2>
            <p>Veuillez sélectionner au moins 2 véhicules dans le catalogue neuf pour démarrer la comparaison.</p>
            <Link to="/catalogue" className="btn-primary">
              Explorer le Catalogue Neuf
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const { vehicles, equipment_matrix } = comparatorData;

  // Calculs comparatifs (Best in Class)
  const minPriceOTR = Math.min(...vehicles.map(v => v.clef_en_main_mad || v.price_new_mad));
  const maxTrunk = Math.max(...vehicles.map(v => parseNum(v.specs.trunk_capacity_l)));
  const minConso = Math.min(...vehicles.map(v => parseNum(v.specs.consumption_l_100)).filter(n => n > 0));
  const maxPower = Math.max(...vehicles.map(v => parseNum(v.specs.engine_power_hp)));

  // Estimation du coût de carburant annuel (sur 20 000 km/an à 13.50 DH/L)
  const calculateAnnualFuelCost = (consoL: number): number => {
    if (!consoL || consoL <= 0) return 0;
    return Math.round((consoL / 100) * 20000 * 13.5);
  };

  // Résumé d'équipements par catégorie pour chaque véhicule
  const getCategoryStats = (catFeatures: typeof equipment_matrix[0]['features'], vehicleId: string) => {
    let serieCount = 0;
    let optionCount = 0;
    let nonDispoCount = 0;
    catFeatures.forEach((feat) => {
      const val = feat.values_per_vehicle[vehicleId];
      if (val?.status === 'SERIE') serieCount++;
      else if (val?.status === 'OPTION') optionCount++;
      else nonDispoCount++;
    });
    return { serieCount, optionCount, nonDispoCount, total: catFeatures.length };
  };

  return (
    <div className="comparator-page">
      <div className="comparator-container">
        {/* Breadcrumb */}
        <nav className="comparator-breadcrumb">
          <Link to="/">Accueil</Link> 
          <ChevronRight size={13} className="bc-sep" />
          <Link to="/catalogue">Catalogue Neuf</Link> 
          <ChevronRight size={13} className="bc-sep" />
          <span className="current">Comparateur Face-à-Face</span>
        </nav>

        {/* ─── HEADER & CONTROLS ───────────────────────────── */}
        <div className="comparator-header">
          <div className="header-left">
            <div className="comparator-badge">
              <Scale size={13} />
              <span>Outil Décisionnel Showroom</span>
            </div>
            <h1>Comparateur de Voitures Neuves au Maroc</h1>
            <p className="comparator-subtitle">
              Audit comparatif neutre : fiches techniques certifiées, écarts tarifaires clés en main réels et matrice d'équipements officielle.
            </p>
          </div>

          <div className="comparator-controls-bar">
            <label className="diff-toggle-pill">
              <input
                type="checkbox"
                checked={diffOnly}
                onChange={(e) => setDiffOnly(e.target.checked)}
              />
              <span className="toggle-indicator"></span>
              <span className="toggle-text">Différences uniquement</span>
            </label>
          </div>
        </div>

        {/* ─── NAVIGATION TABS PAR RUBRIQUE ─────────────────── */}
        <div className="comparator-nav-bar">
          <div className="comparator-nav-tabs">
            <button 
              className={`tab-btn ${activeTab === 'all' ? 'active' : ''}`}
              onClick={() => setActiveTab('all')}
            >
              Vue d'ensemble
            </button>
            <button 
              className={`tab-btn ${activeTab === 'pricing' ? 'active' : ''}`}
              onClick={() => setActiveTab('pricing')}
            >
              Tarifs &amp; Clé en main
            </button>
            <button 
              className={`tab-btn ${activeTab === 'specs' ? 'active' : ''}`}
              onClick={() => setActiveTab('specs')}
            >
              Moteur &amp; Performances
            </button>
            <button 
              className={`tab-btn ${activeTab === 'tco' ? 'active' : ''}`}
              onClick={() => setActiveTab('tco')}
            >
              Consommation &amp; Coût d'usage
            </button>
            <button 
              className={`tab-btn ${activeTab === 'radar' ? 'active' : ''}`}
              onClick={() => setActiveTab('radar')}
            >
              Benchmark 8D
            </button>
            <button 
              className={`tab-btn ${activeTab === 'equipment' ? 'active' : ''}`}
              onClick={() => setActiveTab('equipment')}
            >
              Équipements &amp; Options
            </button>
          </div>
        </div>

        {/* ─── TABLEAU COMPARATIF MULTI-COLONNES STICKY ─────── */}
        <div className="comparator-table-wrapper">
          <table className="comparator-table">
            <thead>
              <tr>
                <th className="feature-col-header">
                  <span className="feature-header-title">Critères &amp; Équipements</span>
                  <span className="feature-header-desc">Matrice comparative officielle</span>
                </th>
                {vehicles.map((v) => {
                  const carImg = getVehicleImage(v);
                  const logoSrc = getBrandLogo(v.brand_name);
                  const otrPrice = v.clef_en_main_mad || v.price_new_mad;
                  const isBestPrice = otrPrice === minPriceOTR;
                  const priceDiff = otrPrice - minPriceOTR;

                  return (
                    <th key={v.id} className="vehicle-col-header">
                      <div className="vehicle-card-head">
                        {vehicles.length > 2 && (
                          <button
                            className="btn-remove-col"
                            onClick={() => handleRemoveVehicle(v.id)}
                            title="Retirer de la comparaison"
                          >
                            <X size={14} />
                          </button>
                        )}
                        <div className="veh-img-box">
                          <img 
                            src={carImg} 
                            alt={v.name} 
                            className="veh-head-img" 
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              const fallback = resolveVehicleImage(v.brand_name, v.model_name);
                              if (target.src !== fallback) {
                                target.src = fallback;
                              }
                            }}
                          />
                        </div>
                        <div className="veh-head-info">
                          <div className="veh-brand-row">
                            <img 
                              src={logoSrc} 
                              alt={v.brand_name} 
                              className="brand-mini-logo" 
                              onError={(e) => { (e.target as HTMLElement).style.display = 'none'; }}
                            />
                            {v.brand_url ? (
                              <a
                                href={v.brand_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="veh-brand-link"
                                title={`Portail officiel ${v.brand_name}`}
                              >
                                <span className="veh-brand">{v.brand_name}</span>
                                <ExternalLink size={10} className="inline-link-icon" />
                              </a>
                            ) : (
                              <span className="veh-brand">{v.brand_name}</span>
                            )}
                          </div>

                          {v.model_url ? (
                            <a
                              href={v.model_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="veh-title-link"
                              title={`Fiche officielle modèle ${v.model_name}`}
                            >
                              <h3 className="veh-title">
                                {v.model_name}
                                <ExternalLink size={12} className="inline-title-icon" />
                              </h3>
                            </a>
                          ) : (
                            <h3 className="veh-title">{v.model_name}</h3>
                          )}

                          {v.trim_url ? (
                            <a
                              href={v.trim_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="veh-trim-badge-link"
                              title={`Fiche équipement finition ${v.trim_name}`}
                            >
                              <span className="veh-trim-badge">
                                {v.trim_name}
                                <ExternalLink size={9} style={{ marginLeft: 3 }} />
                              </span>
                            </a>
                          ) : (
                            <span className="veh-trim-badge">{v.trim_name}</span>
                          )}
                        </div>
                        <div className={`veh-pricing-block ${isBestPrice ? 'best-price-block' : ''}`}>
                          {isBestPrice ? (
                            <span className="best-tag">Meilleur Prix</span>
                          ) : (
                            <span className="diff-price-tag">+{priceDiff.toLocaleString()} DH</span>
                          )}
                          <span className="veh-price-label">Prix Catalogue :</span>
                          <div className="veh-price-val">
                            {(v.promo_price_mad || v.price_new_mad).toLocaleString()} DH
                          </div>
                          <div className="veh-otr-chip">
                            Clé en main : <strong>{otrPrice.toLocaleString()} DH</strong>
                          </div>
                        </div>
                        <button
                          className="btn-testdrive-col"
                          onClick={() => setSelectedTrimForTestDrive({ id: v.id, name: v.name, brand: v.brand_name })}
                        >
                          Réserver un Essai
                        </button>
                      </div>
                    </th>
                  );
                })}

                {/* EMPLACEMENT D'AJOUT INTERACTIF (Marque -> Modèle -> Version) */}
                {vehicles.length < 4 && (
                  <th className="vehicle-col-header add-slot-col">
                    <div className="add-slot-card">
                      <div className="add-slot-icon">
                        <Plus size={22} />
                      </div>
                      <h3>Ajouter une voiture</h3>
                      <p>Comparez jusqu'à 4 modèles simultanément</p>

                      {/* Étape 1 : Choisir la Marque */}
                      <div className="slot-select-group">
                        <label>1. Marque</label>
                        <select 
                          value={selectedBrandSlug} 
                          onChange={(e) => handleBrandChange(e.target.value)}
                        >
                          <option value="">:: Choisir Marque ::</option>
                          {allBrands.map((b) => (
                            <option key={b.id} value={b.slug || b.name.toLowerCase()}>
                              {b.name}
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Étape 2 : Choisir le Modèle */}
                      <div className="slot-select-group">
                        <label>2. Modèle</label>
                        <select 
                          value={selectedModelSlug} 
                          onChange={(e) => handleModelChange(e.target.value)}
                          disabled={!selectedBrandSlug || filteredModels.length === 0}
                        >
                          <option value="">:: Choisir Modèle ::</option>
                          {filteredModels.map((m) => (
                            <option key={m.id} value={m.slug}>
                              {m.name} (dès {m.starting_price_mad?.toLocaleString()} DH)
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Étape 3 : Choisir la Version / Finition */}
                      <div className="slot-select-group">
                        <label>3. Finition / Version</label>
                        <select 
                          onChange={(e) => handleTrimSelect(e.target.value)}
                          value=""
                          disabled={!selectedModelSlug || modelTrims.length === 0 || loadingTrims}
                        >
                          <option value="">
                            {loadingTrims ? 'Chargement...' : ':: Choisir Version ::'}
                          </option>
                          {modelTrims.map((t) => (
                            <option key={t.id} value={t.slug || t.id}>
                              {t.name} ({t.price_new_mad?.toLocaleString()} DH)
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </th>
                )}
              </tr>
            </thead>

            <tbody>
              {/* ══════════════════════════════════════════════════
                  RUBRIQUE 1: PRIX & FRAIS CLÉS EN MAIN AU MAROC
                  ══════════════════════════════════════════════════ */}
              {(activeTab === 'all' || activeTab === 'pricing') && (
                <>
                  <tr className="table-section-row">
                    <td colSpan={vehicles.length + (vehicles.length < 4 ? 2 : 1)}>
                      <div className="section-title-box">
                        <Coins size={16} className="sec-icon" />
                        <span>TARIFICATION &amp; FRAIS CLÉ EN MAIN CERTIFIÉS (MAD)</span>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td className="row-title">Prix Catalogue Neuf</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value font-bold">
                        {v.price_new_mad.toLocaleString()} DH
                      </td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Vignette Annuelle DGI</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value font-bold text-emerald">
                        {v.vignette_dgi_mad === 0 ? (
                          <span className="vignette-free-tag">Exonérée (0 DH)</span>
                        ) : (
                          `${v.vignette_dgi_mad.toLocaleString()} DH / an`
                        )}
                      </td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Total Clé en Main Certifié</td>
                    {vehicles.map((v) => {
                      const otr = v.clef_en_main_mad || v.price_new_mad;
                      const isWinner = otr === minPriceOTR;
                      return (
                        <td key={v.id} className={`row-value font-bold ${isWinner ? 'winner-cell' : ''}`}>
                          <div className="val-main font-bold" style={{ color: '#122135', fontSize: '1.05rem' }}>
                            {otr.toLocaleString()} DH
                          </div>
                          {isWinner && <span className="winner-pill">Tarif le plus bas</span>}
                        </td>
                      );
                    })}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Liens &amp; Fiches Officielles</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value">
                        <div className="official-links-group">
                          {v.trim_url && (
                            <a
                              href={v.trim_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="official-ext-pill"
                              title="Consulter la fiche finition officielle"
                            >
                              Fiche Modèle <ExternalLink size={10} style={{ marginLeft: 3 }} />
                            </a>
                          )}
                          {v.brand_url && (
                            <a
                              href={v.brand_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="official-ext-pill secondary-pill"
                              title={`Portail officiel ${v.brand_name}`}
                            >
                              {v.brand_name}.ma <ExternalLink size={10} style={{ marginLeft: 3 }} />
                            </a>
                          )}
                        </div>
                      </td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                </>
              )}

              {/* ══════════════════════════════════════════════════
                  RUBRIQUE 2: MOTORISATION & PERFORMANCES
                  ══════════════════════════════════════════════════ */}
              {(activeTab === 'all' || activeTab === 'specs') && (
                <>
                  <tr className="table-section-row">
                    <td colSpan={vehicles.length + (vehicles.length < 4 ? 2 : 1)}>
                      <div className="section-title-box">
                        <Gauge size={16} className="sec-icon" />
                        <span>MOTORISATION &amp; TRANSMISSION</span>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td className="row-title">Type de Carburant</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value font-bold">{v.specs.fuel_type}</td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Transmission / Boîte</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value">{v.specs.transmission}</td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Puissance Fiscale &amp; Réelle</td>
                    {vehicles.map((v) => {
                      const power = parseNum(v.specs.engine_power_hp);
                      const isWinner = power === maxPower && maxPower > 0;
                      const diff = power - Math.min(...vehicles.map(o => parseNum(o.specs.engine_power_hp)));
                      return (
                        <td key={v.id} className={`row-value ${isWinner ? 'winner-cell' : ''}`}>
                          <div className="val-main font-bold">{v.specs.fiscal_power_cv} ({v.specs.engine_power_hp})</div>
                          {isWinner && diff > 0 && (
                            <span className="winner-pill">+{diff} ch d'écart</span>
                          )}
                        </td>
                      );
                    })}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Couple Moteur (Nm)</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value">{v.specs.torque_nm}</td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Garantie Constructeur</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value">{v.warranty}</td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                </>
              )}

              {/* ══════════════════════════════════════════════════
                  RUBRIQUE 3: CONSOMMATIONS & COÛT D'USAGE (TCO)
                  ══════════════════════════════════════════════════ */}
              {(activeTab === 'all' || activeTab === 'tco') && (
                <>
                  <tr className="table-section-row">
                    <td colSpan={vehicles.length + (vehicles.length < 4 ? 2 : 1)}>
                      <div className="section-title-box">
                        <Fuel size={16} className="sec-icon" />
                        <span>CONSOMMATION &amp; COÛT RÉEL D'USAGE (TCO MAROC)</span>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td className="row-title">Consommation Mixte</td>
                    {vehicles.map((v) => {
                      const conso = parseNum(v.specs.consumption_l_100);
                      const isWinner = conso === minConso && minConso > 0;
                      return (
                        <td key={v.id} className={`row-value ${isWinner ? 'winner-cell' : ''}`}>
                          <div className="val-main font-bold">{v.specs.consumption_l_100}</div>
                          {isWinner && <span className="winner-pill">Plus sobre</span>}
                          {v.real_conso_url && (
                            <a
                              href={v.real_conso_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="metric-source-link"
                              title="Voir les données réelles sur Spritmonitor / EV-Database"
                            >
                              Source Réelle <ExternalLink size={9} style={{ marginLeft: 2 }} />
                            </a>
                          )}
                        </td>
                      );
                    })}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Volume du Coffre (VDA)</td>
                    {vehicles.map((v) => {
                      const trunk = parseNum(v.specs.trunk_capacity_l);
                      const isWinner = trunk === maxTrunk && maxTrunk > 0;
                      const minTrunk = Math.min(...vehicles.map(o => parseNum(o.specs.trunk_capacity_l)));
                      const diff = trunk - minTrunk;
                      return (
                        <td key={v.id} className={`row-value ${isWinner ? 'winner-cell' : ''}`}>
                          <div className="val-main font-bold">{v.specs.trunk_capacity_l}</div>
                          {isWinner && diff > 0 && (
                            <span className="winner-pill">+{diff} L de chargement</span>
                          )}
                        </td>
                      );
                    })}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Sécurité Euro NCAP</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value">
                        <div>{renderStars(v.specs.euro_ncap_stars)}</div>
                        {v.ncap_report_url && (
                          <a
                            href={v.ncap_report_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="metric-source-link"
                            title="Consulter le rapport officiel de crash-test Euro NCAP"
                          >
                            Rapport Crash-Test <ExternalLink size={9} style={{ marginLeft: 2 }} />
                          </a>
                        )}
                      </td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                </>
              )}

              {/* ══════════════════════════════════════════════════
                  RUBRIQUE 4: BENCHMARK RADAR SCORING (8D WAKALA)
                  ══════════════════════════════════════════════════ */}
              {(activeTab === 'all' || activeTab === 'radar') && (
                <>
                  <tr className="table-section-row">
                    <td colSpan={vehicles.length + (vehicles.length < 4 ? 2 : 1)}>
                      <div className="section-title-box">
                        <Sparkles size={16} className="sec-icon" />
                        <span>BENCHMARK COMPARATIF WAKALA (0 - 100)</span>
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td className="row-title">Économie de Carburant</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value">
                        <div className="radar-bar-container">
                          <div className="radar-bar-track">
                            <div className="radar-bar-fill" style={{ width: `${v.radar_scores.economie}%` }}></div>
                          </div>
                          <span className="radar-bar-score">{v.radar_scores.economie}</span>
                        </div>
                      </td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Puissance &amp; Reprises</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value">
                        <div className="radar-bar-container">
                          <div className="radar-bar-track">
                            <div className="radar-bar-fill" style={{ width: `${v.radar_scores.puissance}%` }}></div>
                          </div>
                          <span className="radar-bar-score">{v.radar_scores.puissance}</span>
                        </div>
                      </td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Habitabilité &amp; Espace</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value">
                        <div className="radar-bar-container">
                          <div className="radar-bar-track">
                            <div className="radar-bar-fill" style={{ width: `${v.radar_scores.espace}%` }}></div>
                          </div>
                          <span className="radar-bar-score">{v.radar_scores.espace}</span>
                        </div>
                      </td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                  <tr>
                    <td className="row-title">Sécurité &amp; Aide Conduite</td>
                    {vehicles.map((v) => (
                      <td key={v.id} className="row-value">
                        <div className="radar-bar-container">
                          <div className="radar-bar-track">
                            <div className="radar-bar-fill" style={{ width: `${v.radar_scores.securite}%` }}></div>
                          </div>
                          <span className="radar-bar-score">{v.radar_scores.securite}</span>
                        </div>
                      </td>
                    ))}
                    {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                  </tr>
                </>
              )}

              {/* ══════════════════════════════════════════════════
                  RUBRIQUE 5: MATRICE DES ÉQUIPEMENTS & OPTIONS
                  ══════════════════════════════════════════════════ */}
              {(activeTab === 'all' || activeTab === 'equipment') && (
                <>
                  {equipment_matrix.map((cat, cIdx) => (
                    <React.Fragment key={cIdx}>
                      <tr className="table-section-row">
                        <td colSpan={vehicles.length + (vehicles.length < 4 ? 2 : 1)}>
                          <div className="section-title-box">
                            <Layers size={15} className="sec-icon" />
                            <span>{cat.icon} {cat.category_name.toUpperCase()}</span>
                          </div>
                        </td>
                      </tr>
                      {/* Résumé chiffré par modèle */}
                      <tr className="category-summary-row">
                        <td className="row-title" style={{ fontSize: '0.8rem', color: '#64748B' }}>
                          Équipements inclus :
                        </td>
                        {vehicles.map((v) => {
                          const stats = getCategoryStats(cat.features, v.id);
                          return (
                            <td key={v.id} className="row-value" style={{ fontSize: '0.82rem', color: '#475569' }}>
                              <span style={{ color: '#059669', fontWeight: 700 }}>{stats.serieCount}</span> de série
                              {stats.optionCount > 0 && (
                                <span style={{ color: '#AE8C4E', marginLeft: '6px' }}>· {stats.optionCount} opt.</span>
                              )}
                            </td>
                          );
                        })}
                        {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                      </tr>
                      {cat.features
                        .filter((feat) => !diffOnly || feat.has_difference)
                        .map((feat) => (
                          <tr key={feat.feature_id} className={feat.has_difference ? 'diff-highlight' : ''}>
                            <td className="row-title">
                              {feat.feature_name}
                              {feat.has_difference && (
                                <span className="diff-badge-indicator" title="Différence entre modèles">Diff</span>
                              )}
                            </td>
                            {vehicles.map((v) => {
                              const val = feat.values_per_vehicle[v.id];
                              return (
                                <td key={v.id} className="row-value equip-val">
                                  {val?.status === 'SERIE' && (
                                    <span className="status-serie">
                                      <Check size={12} style={{ marginRight: '4px', verticalAlign: 'middle' }} />
                                      De série
                                    </span>
                                  )}
                                  {val?.status === 'OPTION' && (
                                    <span className="status-option">
                                      <Plus size={11} style={{ marginRight: '3px', verticalAlign: 'middle' }} />
                                      Option {val.option_price_mad ? `(+${val.option_price_mad.toLocaleString()} DH)` : ''}
                                    </span>
                                  )}
                                  {(!val || val.status === 'NON_DISPO') && (
                                    <span className="status-nondispo">—</span>
                                  )}
                                </td>
                              );
                            })}
                            {vehicles.length < 4 && <td className="row-value slot-empty-cell">—</td>}
                          </tr>
                        ))}
                    </React.Fragment>
                  ))}
                </>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ─── TEST DRIVE MODAL ─────────────────────────────── */}
      {selectedTrimForTestDrive && (
        <TestDriveModal
          isOpen={Boolean(selectedTrimForTestDrive)}
          onClose={() => setSelectedTrimForTestDrive(null)}
          trimId={selectedTrimForTestDrive.id}
          vehicleName={selectedTrimForTestDrive.name}
          brandName={selectedTrimForTestDrive.brand}
        />
      )}
    </div>
  );
};
