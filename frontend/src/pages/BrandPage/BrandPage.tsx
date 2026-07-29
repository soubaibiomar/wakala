import { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
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
  const initialTab = (searchParams.get('tab') as 'all' | 'neuf' | 'occasion') || 'neuf';

  const [activeTab, setActiveTab] = useState<'all' | 'neuf' | 'occasion'>(initialTab);

  const brandInfo = POPULAR_BRANDS.find(b => b.name.toLowerCase() === brandName?.toLowerCase());

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

    if (activeTab === 'neuf' || activeTab === 'occasion') {
      filters.condition = activeTab;
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

  const handleTabChange = (tab: 'all' | 'neuf' | 'occasion') => {
    setActiveTab(tab);
    setSearchParams({ tab });
    setPage(1);
  };

  const pagesCount = Math.max(1, Math.ceil(total / PAGE_SIZE));

  if (!brandInfo && !loading && vehicles.length === 0) {
    return (
      <div className="brand-page brand-page--not-found">
        <h2>Marque introuvable</h2>
        <Link to="/catalogue" className="btn btn--primary">Retour au catalogue</Link>
      </div>
    );
  }

  return (
    <div className="brand-page">
      <div className="brand-hero">
        <div className="brand-hero__content">
          {brandInfo?.logo ? (
            <img src={brandInfo.logo} alt={brandName} className="brand-hero__logo" />
          ) : (
            <h1 className="brand-hero__title">{brandName}</h1>
          )}
          <p className="brand-hero__subtitle">
            Découvrez tous les modèles {brandName} disponibles sur Wakala
          </p>
        </div>
      </div>

      <div className="brand-content container">
        <div className="brand-filters">
          <button 
            className={`brand-filter-btn ${activeTab === 'all' ? 'active' : ''}`}
            onClick={() => handleTabChange('all')}
          >
            Tous ({activeTab === 'all' && !loading ? total : '...'})
          </button>
          <button 
            className={`brand-filter-btn ${activeTab === 'neuf' ? 'active' : ''}`}
            onClick={() => handleTabChange('neuf')}
          >
            Neuf
          </button>
          <button 
            className={`brand-filter-btn ${activeTab === 'occasion' ? 'active' : ''}`}
            onClick={() => handleTabChange('occasion')}
          >
            Occasion
          </button>
        </div>

        {error && <div className="brand-error">{error}</div>}

        {loading && vehicles.length === 0 ? (
          <div className="brand-loading">Chargement des véhicules...</div>
        ) : (
          <>
            <div className="brand-grid">
              {vehicles.map((vehicle, idx) => (
                <motion.div
                  key={vehicle.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: (idx % PAGE_SIZE) * 0.05 }}
                >
                  <VehicleCard vehicle={vehicle} />
                </motion.div>
              ))}
            </div>

            {vehicles.length === 0 && !loading && (
              <div className="brand-empty">
                <p>Aucun véhicule ne correspond à vos critères pour cette marque.</p>
              </div>
            )}

            {pagesCount > 1 && (
              <div className="brand-pagination">
                <button
                  className="btn btn--outline"
                  disabled={page === 1}
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                >
                  Précédent
                </button>
                <span className="brand-pagination-info">
                  Page {page} sur {pagesCount}
                </span>
                <button
                  className="btn btn--outline"
                  disabled={page === pagesCount}
                  onClick={() => setPage(p => Math.min(pagesCount, p + 1))}
                >
                  Suivant
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
