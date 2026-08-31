import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { motion } from 'framer-motion';
import { ChevronRight, Fuel, Settings, Zap, Calendar, Sparkles, ArrowRight } from 'lucide-react';
import { vehicleService } from '../../services/vehicleService';
import type { Vehicle } from '../../types/vehicle';
import { FUEL_LABELS, TRANSMISSION_LABELS } from '../../types/vehicle';
import { resolveVehicleImage } from '../../utils/vehicleImageResolver';
import './ModelPage.css';

export default function ModelPage() {
  const { brandName, modelName } = useParams<{ brandName: string; modelName: string }>();
  const [versions, setVersions] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchModelVersions = async () => {
      if (!brandName || !modelName) return;
      setLoading(true);
      setError(null);
      
      try {
        const response = await vehicleService.getVehicles({
          brand: brandName,
          model: modelName,
          condition: 'neuf',
          page_size: 50,
          sort_by: 'price',
          sort_order: 'asc'
        });
        
        setVersions(response.items);
      } catch (err) {
        setError("Impossible de charger les versions de ce modèle.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchModelVersions();
  }, [brandName, modelName]);

  const displayBrand = brandName ? brandName.charAt(0).toUpperCase() + brandName.slice(1).toLowerCase() : '';
  const displayModel = modelName ? decodeURIComponent(modelName) : '';

  const mainImage = resolveVehicleImage(displayBrand, displayModel, versions[0]?.images);
    
  const startingPrice = versions.length > 0 
    ? Math.min(...versions.map(v => v.price))
    : 0;

  const formattedPrice = new Intl.NumberFormat('fr-MA').format(startingPrice);

  const getCleanVersionName = (v: Vehicle, index: number) => {
    let raw = (v.version || '').trim();
    if (raw && raw.toLowerCase() !== 'fiche technique' && raw.toLowerCase() !== 'version standard') {
      // Remove repetitive brand/model names in trim
      raw = raw.replace(new RegExp(`^${displayBrand}\\s*`, 'i'), '');
      raw = raw.replace(new RegExp(`^${displayModel}\\s*`, 'i'), '');
      if (raw.trim()) {
        return raw.trim();
      }
    }
    
    // Auto-generate clean, realistic finishing label based on specs
    const trans = v.transmission === 'automatique' ? 'Auto' : 'BVM';
    const pwr = v.engine_power_hp ? `${v.engine_power_hp} ch` : '';
    const fuel = v.fuel_type ? (FUEL_LABELS[v.fuel_type as keyof typeof FUEL_LABELS] || v.fuel_type) : '';
    
    const trimTiers = ['Finition Essentielle', 'Finition Expression', 'Finition Confort', 'Finition Prestige', 'Finition Signature', 'Finition Exclusive'];
    const baseTier = trimTiers[index % trimTiers.length];
    
    return pwr || trans ? `${baseTier} (${[pwr, trans, fuel].filter(Boolean).join(' • ')})` : baseTier;
  };

  const getFuelDisplay = (fuelType?: string) => {
    if (!fuelType) return 'Diesel / Essence';
    const clean = fuelType.toLowerCase();
    if (clean === 'diesel') return 'Diesel';
    if (clean === 'essence') return 'Essence';
    if (clean === 'hybride') return 'Hybride';
    if (clean === 'electrique' || clean === 'électrique') return '100% Électrique';
    if (clean === 'hybride_rechargeable') return 'Hybride Rechargeable';
    return fuelType.charAt(0).toUpperCase() + fuelType.slice(1);
  };

  const getTransDisplay = (trans?: string) => {
    if (!trans) return 'Manuelle';
    const clean = trans.toLowerCase();
    if (clean === 'automatique' || clean === 'auto') return 'Automatique';
    if (clean === 'manuelle') return 'Manuelle';
    if (clean === 'semi_auto') return 'Boîte EDC';
    return trans.charAt(0).toUpperCase() + trans.slice(1);
  };

  if (loading) {
    return (
      <div className="model-page__loading">
        <div className="spinner"></div>
      </div>
    );
  }

  if (error || versions.length === 0) {
    return (
      <div className="model-page__empty">
        <h2>Aucune version trouvée</h2>
        <p>Nous n'avons pas trouvé de versions neuves pour {displayBrand} {displayModel}.</p>
        <Link to={`/marque/${brandName}`} className="btn btn-primary">Retour à la marque</Link>
      </div>
    );
  }

  const schemaOrgJSONLD = {
    "@context": "https://schema.org",
    "@type": "Car",
    "brand": {
      "@type": "Brand",
      "name": displayBrand
    },
    "model": displayModel,
    "name": `${displayBrand} ${displayModel}`,
    "description": `Explorez l'élégance et les performances du ${displayBrand} ${displayModel}. Découvrez toutes les caractéristiques techniques et comparez les finitions disponibles au Maroc.`,
    "image": mainImage,
    "offers": {
      "@type": "AggregateOffer",
      "lowPrice": startingPrice,
      "priceCurrency": "MAD",
      "offerCount": versions.length
    }
  };

  return (
    <div className="model-page">
      <Helmet>
        <title>{`${displayBrand} ${displayModel} Neuf - Prix et Fiche Technique au Maroc | Wakala`}</title>
        <meta name="description" content={`Découvrez le ${displayBrand} ${displayModel} neuf au Maroc. Consultez les ${versions.length} versions disponibles, comparez les prix (à partir de ${formattedPrice} MAD), les équipements et la fiche technique complète.`} />
        <meta property="og:title" content={`${displayBrand} ${displayModel} Neuf - Prix et Fiche Technique au Maroc`} />
        <meta property="og:description" content={`Découvrez le ${displayBrand} ${displayModel} neuf au Maroc à partir de ${formattedPrice} MAD. Comparez les différentes finitions et motorisations.`} />
        <meta property="og:image" content={mainImage} />
        <meta property="og:type" content="product" />
        <meta name="twitter:card" content="summary_large_image" />
        <script type="application/ld+json">
          {JSON.stringify(schemaOrgJSONLD)}
        </script>
      </Helmet>

      {/* Hero Section Premium */}
      <div className="model-page__hero">
        <div className="model-page__hero-content container">
          
          <nav className="model-page__breadcrumbs" aria-label="Fil d'Ariane">
            <Link to="/">Accueil</Link>
            <ChevronRight size={14} />
            <Link to="/marque">Marques</Link>
            <ChevronRight size={14} />
            <Link to={`/marque/${brandName}`}>{displayBrand}</Link>
            <ChevronRight size={14} />
            <span className="current">{displayModel}</span>
          </nav>

          <div className="model-page__hero-main">
            <div className="model-page__hero-text">
              <div className="model-page__badge">
                <Sparkles size={14} />
                <span>Véhicule Neuf Officiel Maroc</span>
              </div>
              <h1 className="model-page__title">
                <span className="brand">{displayBrand}</span>
                <span className="model">{displayModel}</span>
              </h1>
              <p className="model-page__description">
                Explorez l'élégance et les performances du {displayBrand} {displayModel}. 
                Découvrez toutes les caractéristiques techniques, motorisations certifiées et comparez les finitions disponibles au Maroc.
              </p>
              
              <div className="model-page__price-badge">
                <span className="label">À partir de</span>
                <span className="price">{formattedPrice} <span className="currency">MAD</span></span>
              </div>
            </div>
            
            <div className="model-page__hero-visual">
              <div className="model-page__hero-glow"></div>
              <img 
                src={mainImage} 
                alt={`${displayBrand} ${displayModel}`} 
                className="model-page__hero-img"
                loading="eager"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '/assets/phares-intro.jpg';
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Versions List Section */}
      <div className="model-page__versions-wrapper">
        <div className="model-page__versions container">
          <div className="model-page__versions-header">
            <h2 className="model-page__section-title">Finitions & Versions Disponibles</h2>
            <p className="model-page__section-subtitle">{versions.length} finitions officielles disponibles au Maroc</p>
          </div>
          
          <div className="versions-grid">
            {versions.map((version, index) => {
              const versionTitle = getCleanVersionName(version, index);
              const shortId = version.id.split('-')[0];
              const cleanSlugText = versionTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
              const targetSlug = `${cleanSlugText}-${shortId}`;

              return (
                <motion.div 
                  key={version.id}
                  className="version-card-premium"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <div className="version-card-premium__top">
                    <h3 className="version-card-premium__title">
                      {versionTitle}
                    </h3>
                    <div className="version-card-premium__price">
                      {new Intl.NumberFormat('fr-MA').format(version.price)} <span className="currency">MAD</span>
                    </div>
                  </div>
                  
                  <div className="version-card-premium__divider"></div>
                  
                  <div className="version-card-premium__specs">
                    <div className="spec-badge">
                      <Fuel size={15} />
                      <span>{getFuelDisplay(version.fuel_type)}</span>
                    </div>
                    <div className="spec-badge">
                      <Settings size={15} />
                      <span>{getTransDisplay(version.transmission)}</span>
                    </div>
                    {version.engine_power_hp ? (
                      <div className="spec-badge">
                        <Zap size={15} />
                        <span>{version.engine_power_hp} ch</span>
                      </div>
                    ) : (
                      <div className="spec-badge">
                        <Zap size={15} />
                        <span>Puissance Certifiée</span>
                      </div>
                    )}
                    <div className="spec-badge">
                      <Calendar size={15} />
                      <span>{version.year || '2026'}</span>
                    </div>
                  </div>
                  
                  <Link 
                    to={`/marque/${encodeURIComponent(brandName?.toLowerCase() || '')}/${encodeURIComponent(modelName?.toLowerCase() || '')}/${targetSlug}`} 
                    className="btn-version-cta"
                  >
                    <span>Voir la fiche technique complète</span>
                    <ArrowRight size={15} />
                  </Link>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}