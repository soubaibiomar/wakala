import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronRight, ShieldCheck, Sparkles, Scale, MapPin, CreditCard, Compass } from 'lucide-react';
import { newCatalogService, ModelDetail, TrimDetail } from '../services/newCatalogService';
import { TestDriveModal } from '../components/modals/TestDriveModal';
import { VehicleStructuredData } from '../components/seo/VehicleStructuredData';
import { PageMeta } from '../components/seo/PageMeta';
import { BreadcrumbStructuredData } from '../components/seo/BreadcrumbStructuredData';
import { resolveVehicleImage } from '../utils/vehicleImageResolver';
import { resolveBrandLogo } from '../utils/brandLogoResolver';
import './NewCarDetailPage.css';

export const NewCarDetailPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();

  const [model, setModel] = useState<ModelDetail | null>(null);
  const [activeTrimId, setActiveTrimId] = useState<string>('');
  const [trimDetail, setTrimDetail] = useState<TrimDetail | null>(null);
  const [selectedColor, setSelectedColor] = useState<{ name: string; hex: string; price_mad: number } | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [trimLoading, setTrimLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isTestDriveOpen, setIsTestDriveOpen] = useState<boolean>(false);

  useEffect(() => {
    loadModelDetail();
  }, [slug]);

  const loadModelDetail = async () => {
    if (!slug) return;
    setLoading(true);
    setError(null);
    try {
      const data = await newCatalogService.getModelDetail(slug);
      setModel(data);
      if (data.trims && data.trims.length > 0) {
        const firstTrim = data.trims[0];
        setActiveTrimId(firstTrim.id);
        await loadTrimDetail(firstTrim.id);
      }
    } catch (err) {
      console.error('Error fetching model detail', err);
      setError('Impossible de charger les informations de ce véhicule.');
    } finally {
      setLoading(false);
    }
  };

  const loadTrimDetail = async (trimId: string) => {
    setTrimLoading(true);
    try {
      const detail = await newCatalogService.getTrimDetail(trimId);
      setTrimDetail(detail);
      if (detail.available_colors && detail.available_colors.length > 0) {
        setSelectedColor(detail.available_colors[0]);
      }
    } catch (err) {
      console.error('Error fetching trim detail', err);
    } finally {
      setTrimLoading(false);
    }
  };

  const handleSelectTrim = (id: string) => {
    setActiveTrimId(id);
    loadTrimDetail(id);
  };

  const getBrandLogo = (brandName: string, logoUrl?: string | null) => {
    return resolveBrandLogo(brandName, logoUrl);
  };

  const getModelImage = (brandName: string, modelName: string, _currentImg?: string | null) => {
    // Official catalogue pages use the curated side-profile model image.
    // Stored listing/Wakala images are intentionally not used here.
    return resolveVehicleImage(brandName, modelName);
  };

  if (loading) {
    return (
      <div className="newcar-detail-loading">
        <div className="spinner"></div>
        <p>Chargement du Digital Showroom...</p>
      </div>
    );
  }

  if (error || !model) {
    return (
      <div className="newcar-detail-error">
        <h2>Modèle introuvable</h2>
        <p>{error || "Ce modèle n'est plus disponible dans le catalogue neuf."}</p>
        <Link to="/catalogue" className="btn-back">
          ← Retour au Catalogue Neuf
        </Link>
      </div>
    );
  }

  const currentTrim = trimDetail;
  const otr = currentTrim?.on_the_road_breakdown;
  const pt = currentTrim?.powertrain;
  const currentCataloguePrice = Number(currentTrim?.promo_price_mad || currentTrim?.price_new_mad || 0);
  const hasCurrentCataloguePrice = Number.isFinite(currentCataloguePrice) && currentCataloguePrice > 0;
  const hasOtrPrice = Number(otr?.total_clef_en_main_mad || 0) > 0;
  const mainImgSrc = getModelImage(model.brand.name, model.name, currentTrim?.image_url || model.hero_image_url);
  const brandLogoSrc = getBrandLogo(model.brand.name, model.brand.logo_url);

  const breadcrumbs = [
    { name: 'Accueil', item: 'https://wakala.ma/' },
    { name: 'Catalogue Neuf', item: 'https://wakala.ma/catalogue' },
    { name: model.brand.name, item: `https://wakala.ma/marque/${model.brand.slug}` },
    { name: model.name, item: `https://wakala.ma/neuf/${model.slug}` },
  ];

  const pageTitle = `${model.brand.name} ${model.name} Neuf au Maroc — Prix, Fiche & Vignette DGI`;
  const pageDesc = `Découvrez la nouvelle ${model.brand.name} ${model.name} au Maroc. Fiche technique officielle, motorisation${hasCurrentCataloguePrice ? `, prix clé en main à partir de ${currentCataloguePrice.toLocaleString()} MAD` : ''} et réservation d'essai.`;

  return (
    <div className="newcar-detail-page">
      <PageMeta
        title={pageTitle}
        description={pageDesc}
        canonicalUrl={`https://wakala.ma/neuf/${model.slug}`}
        ogType="product"
        ogImage={mainImgSrc}
      />
      <BreadcrumbStructuredData items={breadcrumbs} />
      <VehicleStructuredData model={model} trim={currentTrim || undefined} />

      {/* ─── BREADCRUMB & HEADER ──────────────────────────── */}
      <div className="newcar-container">
        <div className="newcar-breadcrumb">
          <Link to="/">Accueil</Link> 
          <ChevronRight size={13} />
          <Link to="/catalogue">Catalogue Neuf</Link> 
          <ChevronRight size={13} />
          <Link to={`/marque/${model.brand.slug}`}>{model.brand.name}</Link> 
          <ChevronRight size={13} />
          <span className="current">{model.name}</span>
        </div>

        {/* ─── HERO SHOWROOM SECTION ────────────────────────── */}
        <div className="newcar-hero-grid">
          {/* Visual Studio */}
          <div className="newcar-visual-studio">
            <div className="studio-badges">
              <span className="badge-new">100% NEUF MAROC</span>
              {currentTrim?.is_promo && <span className="badge-promo">OFFRE SPÉCIALE</span>}
              <span className="badge-warranty">Garantie {currentTrim?.warranty_years || 3} ans</span>
            </div>

            <div className="studio-image-wrapper">
              <img
                src={mainImgSrc}
                alt={`${model.brand.name} ${model.name} ${currentTrim?.name || ''}`}
                className="studio-main-image"
                onError={(e) => {
                  const image = e.currentTarget;
                  image.onerror = null;
                  image.src = '/assets/car-side-fallback.svg';
                }}
              />
            </div>

            {/* Color Studio Picker */}
            {currentTrim?.available_colors && currentTrim.available_colors.length > 0 && (
              <div className="color-studio-bar">
                <span className="color-studio-label">
                  Couleur : <strong>{selectedColor?.name}</strong>
                  {selectedColor?.price_mad ? ` (+${selectedColor.price_mad.toLocaleString()} DH)` : ' (Inclus)'}
                </span>
                <div className="color-dots-row">
                  {currentTrim.available_colors.map((c, i) => (
                    <button
                      key={i}
                      className={`color-dot-btn ${selectedColor?.name === c.name ? 'active' : ''}`}
                      style={{ backgroundColor: c.hex }}
                      onClick={() => setSelectedColor(c)}
                      title={c.name}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Quick Info & Pricing Box */}
          <div className="newcar-hero-summary">
            <div className="brand-header">
              <img 
                src={brandLogoSrc} 
                alt={model.brand.name} 
                className="brand-logo-img" 
                onError={(e) => {
                  (e.target as HTMLElement).style.display = 'none';
                }}
              />
              <div>
                <h1 className="model-title">{model.brand.name} {model.name}</h1>
                <span className="model-body-badge">{model.body_type} • Année modèle {model.year_start}</span>
              </div>
            </div>

            {/* Trim Selection Pills */}
            <div className="trim-selector-box">
              <label className="section-label">Finitions officielles au Maroc :</label>
              <div className="trim-pills-row">
                {model.trims.map((t) => (
                  <button
                    key={t.id}
                    className={`trim-pill ${activeTrimId === t.id ? 'active' : ''}`}
                    onClick={() => handleSelectTrim(t.id)}
                  >
                    <span className="trim-pill-name">{t.name}</span>
                    {(Number(t.promo_price_mad || t.price_new_mad || 0) > 0) && (
                      <span className="trim-pill-price">
                        {(t.promo_price_mad || t.price_new_mad).toLocaleString()} DH
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Moroccan Pricing & OTR Breakdown */}
            {hasCurrentCataloguePrice && (
            <div className="price-card-morocco">
              <div className="price-main-row">
                <div>
                  <span className="price-label">Prix Catalogue TTC :</span>
                  <div className="price-val">
                    {currentCataloguePrice.toLocaleString()} <span className="currency">MAD</span>
                  </div>
                  {currentTrim?.is_promo && currentTrim.promo_price_mad && (
                    <span className="old-price">
                      {currentTrim.price_new_mad.toLocaleString()} MAD
                    </span>
                  )}
                </div>
                {hasOtrPrice && <div className="otr-badge-box">
                  <span className="otr-badge-title">Clé en Main Estimé</span>
                  <span className="otr-badge-amount">
                    {otr?.total_clef_en_main_mad.toLocaleString()} MAD
                  </span>
                </div>}
              </div>

              {/* Tax Accordion / Mini details */}
              {otr && (
                <div className="tax-mini-breakdown">
                  <div className="tax-row">
                    <span>Vignette DGI (CGI Art. 262) :</span>
                    <strong>{otr.vignette_dgi_mad === 0 ? 'Exonérée (0 DH)' : `${otr.vignette_dgi_mad.toLocaleString()} DH`}</strong>
                  </div>
                  <div className="tax-row">
                    <span>Frais Immatriculation & Carte Grise :</span>
                    <strong>{otr.immatriculation_carte_grise_mad.toLocaleString()} DH</strong>
                  </div>
                  {otr.luxury_tax_mad > 0 && (
                    <div className="tax-row">
                      <span>Taxe sur Véhicules de Luxe :</span>
                      <strong>{otr.luxury_tax_mad.toLocaleString()} DH</strong>
                    </div>
                  )}
                  <div className="tax-row">
                    <span>Frais de dossier & plaques :</span>
                    <strong>{otr.frais_dossier_plaques_mad.toLocaleString()} DH</strong>
                  </div>
                </div>
              )}

              {/* CTAs */}
              <div className="hero-cta-buttons">
                <button
                  className="btn-hero-testdrive"
                  onClick={() => setIsTestDriveOpen(true)}
                >
                  ⚡ Réserver un Essai Showroom
                </button>
                <button
                  className="btn-hero-compare"
                  onClick={() => navigate(`/comparateur?trims=${currentTrim?.id}`)}
                >
                  <Scale size={16} style={{ display: 'inline', marginRight: '6px' }} />
                  Comparer ce modèle
                </button>
              </div>
            </div>
            )}
          </div>
        </div>

        {/* ─── KEY SPECS GRID ──────────────────────────────── */}
        {pt && (
          <div className="specs-highlight-grid">
            <div className="spec-tile">
              <span className="spec-name">Carburant</span>
              <span className="spec-val">{pt.fuel_type}</span>
            </div>
            <div className="spec-tile">
              <span className="spec-name">Transmission</span>
              <span className="spec-val">{pt.transmission}</span>
            </div>
            <div className="spec-tile">
              <span className="spec-name">Puissance Fiscale</span>
              <span className="spec-val">{pt.fiscal_power_cv} CV ({pt.engine_power_hp || 100} ch)</span>
            </div>
            <div className="spec-tile">
              <span className="spec-name">Consommation Mixte</span>
              <span className="spec-val">{pt.consumption_l_100 || '4.5'} L / 100 km</span>
            </div>
            <div className="spec-tile">
              <span className="spec-name">Volume du Coffre</span>
              <span className="spec-val">{currentTrim?.trunk_capacity_l || 380} Litres</span>
            </div>
            <div className="spec-tile">
              <span className="spec-name">Sécurité Euro NCAP</span>
              <span className="spec-val">{currentTrim?.euro_ncap_stars || 4} / 5 étoiles</span>
            </div>
          </div>
        )}

        {/* ─── EQUIPMENT BY CATEGORY MATRIX ────────────────── */}
        <div className="equipment-showroom-section">
          <h2 className="section-title">Équipements & Options de série</h2>
          <p className="section-desc">
            Détail des équipements certifiés pour la finition <strong>{currentTrim?.name}</strong>.
          </p>

          <div className="equipment-categories-grid">
            {currentTrim?.equipment_by_category?.map((cat, idx) => (
              <div key={idx} className="equipment-cat-card">
                <div className="cat-header">
                  <span className="cat-title">{cat.category_name}</span>
                </div>
                <div className="features-list">
                  {cat.features.map((feat, fIdx) => (
                    <div key={fIdx} className="feature-row">
                      <div className="feature-text">
                        <span className="feat-name">{feat.name}</span>
                        {feat.description && (
                          <span className="feat-desc">{feat.description}</span>
                        )}
                      </div>
                      <div className="feature-status">
                        {feat.status === 'SERIE' && (
                          <span className="badge-serie">De série</span>
                        )}
                        {feat.status === 'OPTION' && (
                          <span className="badge-option">
                            Option {feat.option_price_mad ? `(+${feat.option_price_mad.toLocaleString()} DH)` : ''}
                          </span>
                        )}
                        {feat.status === 'NON_DISPO' && (
                          <span className="badge-nondispo">—</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ─── CONTEXTUAL SEMANTIC MESH (SEO & GEO) ────────── */}
        <div style={{ marginTop: '40px', padding: '28px', background: 'var(--bg-surface, #141f2d)', borderRadius: '16px', border: '1px solid var(--border-subtle)' }}>
          <h3 style={{ fontSize: '1.2rem', color: '#fff', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Compass size={20} color="#d4a017" /> Explorer autour de la {model.brand.name} {model.name}
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
            <Link
              to={`/marque/${model.brand.slug}`}
              style={{ padding: '14px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', textDecoration: 'none', color: '#e2e8f0', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '10px' }}
            >
              <Sparkles size={16} color="#d4a017" />
              <span>Tous les modèles <strong>{model.brand.name}</strong></span>
            </Link>

            <Link
              to="/comparateur"
              style={{ padding: '14px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', textDecoration: 'none', color: '#e2e8f0', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '10px' }}
            >
              <Scale size={16} color="#60a5fa" />
              <span>Comparer avec ses concurrents directs</span>
            </Link>

            <Link
              to="/voitures-neuves/casablanca"
              style={{ padding: '14px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', textDecoration: 'none', color: '#e2e8f0', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '10px' }}
            >
              <MapPin size={16} color="#ef4444" />
              <span>Showrooms &amp; Réseau concessionnaires</span>
            </Link>

            <Link
              to="/financement-auto-maroc"
              style={{ padding: '14px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.06)', textDecoration: 'none', color: '#e2e8f0', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '10px' }}
            >
              <CreditCard size={16} color="#a855f7" />
              <span>Simuler le financement &amp; mensualités</span>
            </Link>
          </div>
        </div>
      </div>

      {/* ─── TEST DRIVE MODAL ─────────────────────────────── */}
      {currentTrim && (
        <TestDriveModal
          isOpen={isTestDriveOpen}
          onClose={() => setIsTestDriveOpen(false)}
          trimId={currentTrim.id}
          vehicleName={`${model.brand.name} ${model.name} (${currentTrim.name})`}
          brandName={model.brand.name}
        />
      )}
    </div>
  );
};
