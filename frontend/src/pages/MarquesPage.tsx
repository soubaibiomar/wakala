import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { Search, X, Sparkles, ChevronRight, ArrowRight, ShieldCheck } from 'lucide-react';
import { POPULAR_BRANDS, BrandInfo } from '../constants/brands';
import { newCatalogService, BrandItem, ModelListItem } from '../services/newCatalogService';
import './MarquesPage.css';

interface BrandCardData extends BrandInfo {
  modelsCount: number;
  startingPrice: number;
}

const ORIGIN_FILTERS = [
  { id: 'all', label: 'Toutes', flag: '🌍' },
  { id: 'fr', label: 'Françaises', flag: '🇫🇷', countries: ['France', 'France / Roumanie'] },
  { id: 'de', label: 'Allemandes', flag: '🇩🇪', countries: ['Allemagne'] },
  { id: 'jp', label: 'Japonaises', flag: '🇯🇵', countries: ['Japon'] },
  { id: 'kr', label: 'Sud-Coréennes', flag: '🇰🇷', countries: ['Corée du Sud'] },
  { id: 'cn', label: 'Chinoises & Électriques', flag: '🇨🇳', countries: ['Chine', 'Royaume-Uni / Chine'] },
  { id: 'it', label: 'Italiennes', flag: '🇮🇹', countries: ['Italie'] },
  { id: 'gb', label: 'Britanniques', flag: '🇬🇧', countries: ['Royaume-Uni', 'Royaume-Uni / Chine'] },
  { id: 'us', label: 'Américaines', flag: '🇺🇸', countries: ['USA'] },
  { id: 'other', label: 'Autres (Espagne, Suède...)', flag: '🌐', countries: ['Espagne', 'Suède', 'Rép. Tchèque', 'Inde'] },
];

const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

export default function MarquesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedOrigin, setSelectedOrigin] = useState('all');
  const [selectedLetter, setSelectedLetter] = useState<string | null>(null);
  const [models, setModels] = useState<ModelListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCatalogData();
  }, []);

  const loadCatalogData = async () => {
    try {
      setLoading(true);
      const modelsData = await newCatalogService.getModels({});
      setModels(modelsData || []);
    } catch (err) {
      console.error('Failed to load catalog data for brands:', err);
    } finally {
      setLoading(false);
    }
  };

  // Compute model stats per brand
  const brandsList: BrandCardData[] = useMemo(() => {
    const modelStatsByBrand: Record<string, { count: number; minPrice: number }> = {};
    
    models.forEach((m) => {
      const bName = (m.brand?.name || '').toLowerCase().trim();
      const price = m.starting_price_mad || 0;
      if (!modelStatsByBrand[bName]) {
        modelStatsByBrand[bName] = { count: 0, minPrice: price > 0 ? price : 999999999 };
      }
      modelStatsByBrand[bName].count += 1;
      if (price > 0 && price < modelStatsByBrand[bName].minPrice) {
        modelStatsByBrand[bName].minPrice = price;
      }
    });

    // The API catalogue is the source of truth. The static list only supplies
    // presentation metadata, so aliases or brands outside the imported Excel
    // catalogue must never create extra cards.
    return POPULAR_BRANDS.filter((b) => modelStatsByBrand[b.name.toLowerCase().trim()]).map((b) => {
      const bLower = b.name.toLowerCase().trim();
      const stats = modelStatsByBrand[bLower] || { count: 0, minPrice: 0 };
      return {
        ...b,
        modelsCount: stats.count,
        startingPrice: stats.minPrice === 999999999 ? 0 : stats.minPrice,
      };
    }).filter((brand, index, brands) => brands.findIndex((candidate) => candidate.name.toLowerCase().trim() === brand.name.toLowerCase().trim()) === index)
      .sort((a, b) => a.name.localeCompare(b.name, 'fr', { sensitivity: 'base' }));
  }, [models]);

  // Available letters in the dataset
  const availableLetters = useMemo(() => {
    const letters = new Set<string>();
    brandsList.forEach((b) => {
      const first = b.name.charAt(0).toUpperCase();
      letters.add(first);
    });
    return letters;
  }, [brandsList]);

  // Filtered brands
  const filteredBrands = useMemo(() => {
    return brandsList.filter((b) => {
      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const matchesName = b.name.toLowerCase().includes(q);
        const matchesCountry = b.country.toLowerCase().includes(q);
        if (!matchesName && !matchesCountry) return false;
      }

      // Origin filter
      if (selectedOrigin !== 'all') {
        const filterDef = ORIGIN_FILTERS.find((f) => f.id === selectedOrigin);
        if (filterDef && filterDef.countries) {
          const matched = filterDef.countries.some((c) => b.country.includes(c));
          if (!matched) return false;
        }
      }

      // Alphabet letter
      if (selectedLetter) {
        if (!b.name.toUpperCase().startsWith(selectedLetter)) {
          return false;
        }
      }

      return true;
    });
  }, [brandsList, searchQuery, selectedOrigin, selectedLetter]);

  const resetFilters = () => {
    setSearchQuery('');
    setSelectedOrigin('all');
    setSelectedLetter(null);
  };

  return (
    <div className="marques-page">
      <Helmet>
        <title>Toutes les Marques Automobiles au Maroc | Wakala</title>
        <meta 
          name="description" 
          content="Découvrez les 55 marques automobiles commercialisées au Maroc. Fiches techniques, prix clés en main, gammes complètes et finitions officielles." 
        />
      </Helmet>

      {/* ─── HERO HEADER ─────────────────────────────────────── */}
      <section className="marques-hero">
        <div className="marques-hero-inner">
          <nav className="marques-breadcrumbs" aria-label="Fil d'Ariane">
            <Link to="/">Accueil</Link>
            <ChevronRight size={14} />
            <span className="current">Toutes les Marques</span>
          </nav>

          <div className="marques-badge">
            <Sparkles size={14} />
            <span>55 Marques Officielles au Maroc</span>
          </div>

          <h1 className="marques-title">
            Explorez les <span>Marques Automobiles</span>
          </h1>
          <p className="marques-subtitle">
            Consultez les gammes complètes, fiches techniques et prix clés en main de tous les constructeurs officiellement commercialisés au Maroc.
          </p>

          {/* Quick Search */}
          <div className="marques-search-bar">
            <Search size={18} className="marques-search-icon" />
            <input
              type="text"
              className="marques-search-input"
              placeholder="Rechercher une marque (ex: Dacia, Porsche, BYD, Hyundai...)"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                if (selectedLetter) setSelectedLetter(null);
              }}
            />
            {searchQuery && (
              <button 
                className="marques-search-clear" 
                onClick={() => setSearchQuery('')}
                aria-label="Effacer"
              >
                <X size={16} />
              </button>
            )}
          </div>
        </div>
      </section>

      {/* ─── ORIGIN PILLS ────────────────────────────────────── */}
      <div className="marques-filters-wrapper">
        <div className="marques-pills-row">
          {ORIGIN_FILTERS.map((f) => {
            const count = brandsList.filter((b) => {
              if (f.id === 'all') return true;
              return f.countries?.some((c) => b.country.includes(c));
            }).length;

            return (
              <button
                key={f.id}
                className={`marques-pill-btn ${selectedOrigin === f.id ? 'active' : ''}`}
                onClick={() => {
                  setSelectedOrigin(f.id);
                  if (selectedLetter) setSelectedLetter(null);
                }}
              >
                <span>{f.flag}</span>
                <span>{f.label}</span>
                <span className="marques-pill-count">{count}</span>
              </button>
            );
          })}
        </div>

        {/* Alphabet Navigation */}
        <div className="marques-alpha-bar">
          <button
            className={`alpha-letter-btn ${selectedLetter === null ? 'active' : ''}`}
            onClick={() => setSelectedLetter(null)}
          >
            Tous
          </button>
          {ALPHABET.map((letter) => {
            const hasBrands = availableLetters.has(letter);
            return (
              <button
                key={letter}
                className={`alpha-letter-btn ${selectedLetter === letter ? 'active' : ''}`}
                disabled={!hasBrands}
                onClick={() => {
                  setSelectedLetter(selectedLetter === letter ? null : letter);
                  if (selectedOrigin !== 'all') setSelectedOrigin('all');
                }}
              >
                {letter}
              </button>
            );
          })}
        </div>
      </div>

      {/* ─── CONTENT GRID ────────────────────────────────────── */}
      <main className="marques-content-wrapper">
        <div className="marques-results-meta">
          <span className="marques-results-count">
            Affichage de <strong>{filteredBrands.length}</strong> marques trouvées
          </span>
          {(searchQuery || selectedOrigin !== 'all' || selectedLetter) && (
            <button 
              onClick={resetFilters}
              style={{ background: 'none', border: 'none', color: '#AE8C4E', cursor: 'pointer', fontWeight: 600, fontSize: '0.88rem' }}
            >
              Réinitialiser les filtres ✕
            </button>
          )}
        </div>

        {filteredBrands.length === 0 ? (
          <div className="marques-empty-state">
            <div className="marques-empty-icon">🔍</div>
            <h3 className="marques-empty-title">Aucune marque ne correspond à votre recherche</h3>
            <p className="marques-empty-desc">
              Vérifiez l'orthographe ou réinitialisez les filtres pour découvrir l'ensemble des 55 marques disponibles.
            </p>
            <button className="btn-reset-search" onClick={resetFilters}>
              Voir toutes les marques
            </button>
          </div>
        ) : (
          <div className="marques-grid">
            {filteredBrands.map((b) => (
              <Link
                key={b.slug}
                to={`/marque/${encodeURIComponent(b.name)}`}
                className="brand-card-link"
              >
                <div className="brand-card">
                  <span className="brand-card-flag-badge" title={b.country}>
                    {b.flag}
                  </span>

                  <div className="brand-card-logo-box">
                    <img
                      src={b.logo}
                      alt={`Logo ${b.name}`}
                      className="brand-card-logo"
                      loading="lazy"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = '/assets/wakala-logo.png';
                      }}
                    />
                  </div>

                  <h2 className="brand-card-name">{b.name}</h2>
                  <span className="brand-card-origin">{b.country}</span>

                  <div className="brand-card-divider" />

                  <div className="brand-card-stats">
                    <div className="brand-card-stat-item">
                      <span className="brand-card-stat-label">Gamme</span>
                      <span className="brand-card-stat-value">
                        {b.modelsCount > 0 ? `${b.modelsCount} modèles` : 'Modèles 2026'}
                      </span>
                    </div>

                    <div className="brand-card-stat-item" style={{ alignItems: 'flex-end' }}>
                      <span className="brand-card-stat-label">Prix dès</span>
                      <span className="brand-card-stat-value price">
                        {b.startingPrice > 0 ? `${b.startingPrice.toLocaleString()} DH` : 'Consulter'}
                      </span>
                    </div>
                  </div>

                  <div className="brand-card-cta">
                    <span>Découvrir les modèles</span>
                    <ArrowRight size={14} />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
