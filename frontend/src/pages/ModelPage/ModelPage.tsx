import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { motion } from 'framer-motion';
import { ChevronRight, Fuel, Settings, Power, Calendar } from 'lucide-react';
import { vehicleService } from '../../services/vehicleService';
import type { Vehicle } from '../../types/vehicle';
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

  const mainImage = versions.length > 0 && versions[0].images?.[0]?.file_path
    ? versions[0].images[0].file_path 
    : 'https://via.placeholder.com/800x400?text=Pas+d%27image';
    
  const startingPrice = versions.length > 0 
    ? Math.min(...versions.map(v => v.price))
    : 0;

  const formattedPrice = new Intl.NumberFormat('fr-MA').format(startingPrice);
  const displayBrand = brandName ? brandName.charAt(0).toUpperCase() + brandName.slice(1).toLowerCase() : '';
  const displayModel = modelName ? decodeURIComponent(modelName) : '';

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
          
          <div className="model-page__breadcrumbs">
            <Link to="/">Accueil</Link>
            <ChevronRight size={14} />
            <Link to="/catalogue">Neuf</Link>
            <ChevronRight size={14} />
            <Link to={`/marque/${brandName}`}>{displayBrand}</Link>
            <ChevronRight size={14} />
            <span className="current">{displayModel}</span>
          </div>

          <div className="model-page__hero-main">
            <div className="model-page__hero-text">
              <h1 className="model-page__title">
                <span className="brand">{displayBrand}</span>
                <span className="model">{displayModel}</span>
              </h1>
              <p className="model-page__description">
                Explorez l'élégance et les performances du {displayBrand} {displayModel}. 
                Découvrez toutes les caractéristiques techniques et comparez les finitions disponibles au Maroc.
              </p>
              
              <div className="model-page__price-badge">
                <span className="label">Prix de départ</span>
                <span className="price">{formattedPrice} <span className="currency">MAD</span></span>
              </div>
            </div>
            
            <div className="model-page__hero-visual">
              <div className="model-page__hero-glow"></div>
              <img src={mainImage} alt={`${displayBrand} ${displayModel}`} className="model-page__hero-img" />
            </div>
          </div>
        </div>
      </div>

      {/* Versions List Section */}
      <div className="model-page__versions-wrapper">
        <div className="model-page__versions container">
          <div className="model-page__versions-header">
            <h2 className="model-page__section-title">Finitions & Versions</h2>
            <p className="model-page__section-subtitle">{versions.length} versions disponibles pour ce modèle</p>
          </div>
          
          <div className="versions-grid">
            {versions.map((version, index) => (
              <motion.div 
                key={version.id}
                className="version-card-premium"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <div className="version-card-premium__top">
                  <h3 className="version-card-premium__title">
                    {version.version || "Finition Standard"}
                  </h3>
                  <div className="version-card-premium__price">
                    {new Intl.NumberFormat('fr-MA').format(version.price)} <span className="currency">MAD</span>
                  </div>
                </div>
                
                <div className="version-card-premium__divider"></div>
                
                <div className="version-card-premium__specs">
                  <div className="spec-badge">
                    <Fuel size={14} />
                    <span>{version.fuel_type || '-'}</span>
                  </div>
                  <div className="spec-badge">
                    <Settings size={14} />
                    <span>{version.transmission || '-'}</span>
                  </div>
                  {version.engine_power_hp && (
                    <div className="spec-badge">
                      <Power size={14} />
                      <span>{version.engine_power_hp} Ch</span>
                    </div>
                  )}
                  {version.year && (
                    <div className="spec-badge">
                      <Calendar size={14} />
                      <span>{version.year}</span>
                    </div>
                  )}
                </div>
                
                <Link 
                  to={`/marque/${encodeURIComponent(brandName?.toLowerCase() || '')}/${encodeURIComponent(modelName?.toLowerCase() || '')}/${[
                    version.version !== 'Fiche Technique' ? version.version : '', 
                    version.year || ''
                  ].filter(Boolean).join('-').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')}`} 
                  className="btn btn-outline-gold full-width"
                >
                  Voir la fiche technique complète
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}