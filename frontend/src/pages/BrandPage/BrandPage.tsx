import { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useSearchParams } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { motion } from 'framer-motion';
import { ChevronRight, Sparkles, Car } from 'lucide-react';
import { POPULAR_BRANDS } from '../../constants/brands';
import { vehicleService } from '../../services/vehicleService';
import type { Vehicle } from '../../types/vehicle';
import VehicleCard from '../../components/vehicle-card/VehicleCard';
import './BrandPage.css';

const PAGE_SIZE = 12;

export default function BrandPage() {
  const { brandName } = useParams<{ brandName: string }>();
  
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const initialTab = (searchParams.get('tab') as 'all' | 'neuf') || 'neuf';  // PIVOT: removed 'occasion'

  const [activeTab, setActiveTab] = useState<'all' | 'neuf'>(initialTab);

  const normalize = (s?: string) => (s || '').toLowerCase().replace(/[\s-_]/g, '');
  const brandInfo = POPULAR_BRANDS.find(b => 
    normalize(b.name) === normalize(brandName) ||
    b.name.toLowerCase() === brandName?.toLowerCase()
  );
  const displayBrandName = brandInfo?.name || brandName || '';

  const fetchVehicles = useCallback(async (currentPage: number) => {
    if (!brandName) return;
    setLoading(true);
    setError(null);

    const filters: any = {
      brand: brandName,
      page: currentPage,
      page_size: PAGE_SIZE,
      sort_by: 'created_at',
      sort_order: 'desc'
    };

    if (activeTab === 'neuf') {
      filters.condition = activeTab;
    }
    
    // Pour les véhicules neufs ou tous, grouper par modèle (pour n'afficher qu'une carte par modèle avec lien vers la page versions)
    if (activeTab === 'neuf' || activeTab === 'all') {
      filters.group_by_model = true;
    }

    try {
      const res = await vehicleService.getVehicles(filters);
      setVehicles(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error('Erreur lors du chargement des véhicules:', err);
      setError('Impossible de charger les véhicules de cette marque.');
    } finally {
      setLoading(false);
    }
  }, [brandName, activeTab]);

  useEffect(() => {
    fetchVehicles(page);
  }, [fetchVehicles, page]);

  const handleTabChange = (tab: 'all' | 'neuf') => {  // PIVOT: removed 'occasion'
    setActiveTab(tab);
    setSearchParams({ tab });
    setPage(1);
  };

  const pagesCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const schemaOrgJSONLD = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": `Véhicules ${displayBrandName} - Wakala`,
    "description": `Découvrez tous les modèles ${displayBrandName} neufs disponibles sur Wakala, la marketplace automobile au Maroc.`,
    "url": window.location.href,
    "mainEntity": {
      "@type": "ItemList",
      "itemListElement": vehicles.map((v, index) => ({
        "@type": "ListItem",
        "position": index + 1,
        "item": {
          "@type": "Vehicle",
          "name": `${v.brand} ${v.model}`,
          "modelDate": v.year,
          "mileageFromOdometer": {
            "@type": "QuantitativeValue",
            "value": v.mileage,
            "unitCode": "KMT"
          },
          "offers": {
            "@type": "Offer",
            "price": v.price,
            "priceCurrency": "MAD"
          }
        }
      }))
    }
  };

  return (
    <div className="brand-page">
      <Helmet>
        <title>{`Voitures ${displayBrandName} Neuves au Maroc | Wakala`}</title>
        <meta name="description" content={`Découvrez tous les modèles ${displayBrandName} disponibles sur Wakala. Achetez votre ${displayBrandName} neuve avec fiche technique au meilleur prix au Maroc.`} />
        <script type="application/ld+json">
          {JSON.stringify(schemaOrgJSONLD)}
        </script>
      </Helmet>

      {/* Hero Section Premium avec Breadcrumbs et Logo */}
      <div className="brand-hero">
        <div className="brand-hero__inner">
          <div className="brand-breadcrumbs">
            <Link to="/">Accueil</Link>
            <ChevronRight size={14} />
            <Link to="/marque">Toutes les Marques</Link>
            <ChevronRight size={14} />
            <span className="current">{displayBrandName}</span>
          </div>

          <div className="brand-hero__content">
            <span className="brand-hero__tag">
              <Sparkles size={13} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
              Marque Officielle
            </span>
            
            {brandInfo?.logo ? (
              <div className="brand-hero__logo-wrapper">
                <img 
                  src={brandInfo.logo} 
                  alt={displayBrandName} 
                  className="brand-hero__logo" 
                  onError={(e) => {
                    (e.currentTarget as HTMLElement).style.display = 'none';
                  }}
                />
              </div>
            ) : null}

            <h1 className="brand-hero__title">{displayBrandName}</h1>
            <p className="brand-hero__subtitle">
              Découvrez la gamme complète {displayBrandName} au Maroc : modèles neufs avec fiches techniques détaillées.
            </p>
          </div>
        </div>
      </div>

      {/* Main Content & Filters */}
      <div className="brand-content container">
        <div className="brand-filters">
          <button 
            className={`brand-filter-btn ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => handleTabChange('all')}
          >
            <Car size={16} />
            <span>Tous les véhicules</span>
            <span className="badge-count">{activeTab === 'all' && !loading ? total : '•'}</span>
          </button>
          
          <button 
            className={`brand-filter-btn ${activeTab === 'neuf' ? 'active' : ''}`}
            onClick={() => handleTabChange('neuf')}
          >
            <Sparkles size={15} />
            <span>Modèles Neufs</span>
            <span className="badge-count">{activeTab === 'neuf' && !loading ? total : '•'}</span>
          </button>
          
          {/* PIVOT: Occasion Certifiée tab removed */}
        </div>

        {error && <div className="brand-error">{error}</div>}

        {loading && vehicles.length === 0 ? (
          <div className="brand-loading">
            <div className="spinner"></div>
            <p>Chargement des véhicules {displayBrandName}...</p>
          </div>
        ) : (
          <>
            <div className="brand-grid">
              {vehicles.map((vehicle, idx) => (
                <motion.div
                  key={vehicle.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.35, delay: (idx % PAGE_SIZE) * 0.04 }}
                >
                  <VehicleCard vehicle={vehicle} isGrouped={activeTab === 'neuf'} />
                </motion.div>
              ))}
            </div>

            {vehicles.length === 0 && !loading && (
              <div className="brand-empty">
                <div className="brand-empty__icon">🚗</div>
                <h3 className="brand-empty__title">
                  {activeTab === 'neuf'
                    ? `Aucun modèle neuf ${displayBrandName} disponible`
                    : `Aucun véhicule ${displayBrandName} trouvé`}
                </h3>
                <p className="brand-empty__text">
                  {activeTab === 'neuf'
                    ? `Nous mettons notre catalogue à jour régulièrement. Découvrez nos marques les plus demandées :`
                    : `Nous mettons notre catalogue à jour régulièrement. Découvrez nos marques les plus demandées :`}
                </p>
                
                <div className="brand-empty__suggestions">
                  {POPULAR_BRANDS.filter(b => normalize(b.name) !== normalize(brandName)).slice(0, 8).map((b) => (
                    <Link key={b.name} to={`/marque/${encodeURIComponent(b.name.toLowerCase())}`} className="brand-empty__chip">
                      <img src={b.logo} alt={b.name} className="brand-empty__chip-logo" />
                      <span>{b.name}</span>
                    </Link>
                  ))}
                </div>

                <div className="brand-empty__actions">
                {/* PIVOT: removed occasion fallback buttons */}
                  <Link to="/catalogue" className="btn btn--primary">
                    Explorer tout le catalogue
                  </Link>
                </div>
              </div>
            )}

            {pagesCount > 1 && (
              <div className="brand-pagination">
                <button
                  className="btn btn--outline"
                  disabled={page === 1}
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                >
                  ← Précédent
                </button>
                <span className="brand-pagination-info">
                  Page {page} sur {pagesCount}
                </span>
                <button
                  className="btn btn--outline"
                  disabled={page === pagesCount}
                  onClick={() => setPage(p => Math.min(pagesCount, p + 1))}
                >
                  Suivant →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
