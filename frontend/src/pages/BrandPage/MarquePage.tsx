import React, { useEffect, useState, useCallback } from 'react';
import { useParams, Link, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ChevronRight,
  Sparkles,
  Car,
  ShieldCheck,
  Award,
  HelpCircle,
  ArrowRight,
  Scale
} from 'lucide-react';
import PageMeta from '../../components/seo/PageMeta';
import FAQStructuredData from '../../components/seo/FAQStructuredData';
import BreadcrumbStructuredData from '../../components/seo/BreadcrumbStructuredData';
import seoService, { BrandSeoData } from '../../services/seoService';
import { resolveVehicleImage } from '../../utils/vehicleImageResolver';
import { POPULAR_BRANDS } from '../../constants/brands';
import './BrandPage.css';

export const MarquePage: React.FC = () => {
  const { brandName } = useParams<{ brandName: string }>();
  const [seoData, setSeoData] = useState<BrandSeoData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  const normalize = (s?: string) => (s || '').toLowerCase().replace(/[\s-_]/g, '');
  const brandInfo = POPULAR_BRANDS.find(
    (b) => normalize(b.name) === normalize(brandName) || b.name.toLowerCase() === brandName?.toLowerCase()
  );
  const displayBrandName = brandInfo?.name || brandName || '';

  useEffect(() => {
    if (!brandName) return;
    setLoading(true);
    setError(null);
    seoService
      .getBrandData(brandName)
      .then((res) => {
        setSeoData(res);
      })
      .catch((err) => {
        console.warn('Could not load dynamic SEO data for brand, fallback standard:', err);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [brandName]);

  const breadcrumbs = [
    { name: 'Accueil', item: 'https://wakala.ma/' },
    { name: "Guide d'Achat", item: 'https://wakala.ma/guide-achat-voiture-maroc' },
    { name: 'Toutes les Marques', item: 'https://wakala.ma/marque' },
    { name: displayBrandName, item: `https://wakala.ma/marque/${brandName?.toLowerCase()}` },
  ];

  const brandDescription = seoData?.self_contained_answer || (
    `${displayBrandName} propose une large gamme de véhicules neufs au Maroc. ` +
    `Retrouvez tous les modèles, finitions et fiches techniques officielles certifiées avec calcul de prix clé en main.`
  );

  return (
    <div className="brand-page">
      <PageMeta
        title={seoData?.title || `Voitures ${displayBrandName} Neuves au Maroc (Prix 2026) | Wakala`}
        description={seoData?.meta_description || `Découvrez tous les modèles ${displayBrandName} neufs au Maroc. Fiches techniques, prix clé en main et garantie constructeur.`}
        canonicalUrl={`https://wakala.ma/marque/${brandName?.toLowerCase()}`}
        ogType="website"
      />
      <BreadcrumbStructuredData items={breadcrumbs} />
      {seoData?.faqs && <FAQStructuredData faqs={seoData.faqs} />}

      {/* Hero Section Premium */}
      <div className="brand-hero" style={{ background: 'linear-gradient(135deg, #09111b 0%, #101e30 60%, #182e4a 100%)', padding: '50px 20px 40px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div className="brand-hero__inner" style={{ maxWidth: '1140px', margin: '0 auto' }}>
          <div className="brand-breadcrumbs" style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '20px' }}>
            <Link to="/" style={{ color: '#94a3b8', textDecoration: 'none' }}>Accueil</Link>
            <ChevronRight size={14} />
            <Link to="/marque" style={{ color: '#94a3b8', textDecoration: 'none' }}>Marques</Link>
            <ChevronRight size={14} />
            <span style={{ color: '#d4a017' }}>{displayBrandName}</span>
          </div>

          <div className="brand-hero__content">
            <span className="brand-hero__tag" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 12px', background: 'rgba(212, 160, 23, 0.15)', border: '1px solid rgba(212, 160, 23, 0.4)', borderRadius: '20px', color: '#d4a017', fontSize: '0.8rem', fontWeight: 600, marginBottom: '14px' }}>
              <Sparkles size={13} />
              Catalogue Officiel Neuf
            </span>

            {brandInfo?.logo && (
              <div className="brand-hero__logo-wrapper" style={{ margin: '10px 0 16px' }}>
                <img
                  src={brandInfo.logo}
                  alt={displayBrandName}
                  className="brand-hero__logo"
                  style={{ height: '48px', objectFit: 'contain' }}
                  onError={(e) => {
                    (e.currentTarget as HTMLElement).style.display = 'none';
                  }}
                />
              </div>
            )}

            <h1 className="brand-hero__title" style={{ fontSize: 'clamp(2rem, 4vw, 3rem)', color: '#fff', fontWeight: 800, margin: '0 0 14px' }}>
              Gamme {displayBrandName} Neuve au Maroc (2026)
            </h1>

            {/* GEO Self-Contained Answer */}
            <div style={{ background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: '14px', padding: '18px 22px', color: '#e2e8f0', fontSize: '1rem', lineHeight: 1.7, maxWidth: '900px' }}>
              <p style={{ margin: 0 }}>
                <strong>Présentation constructeur :</strong> {brandDescription}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="brand-content container" style={{ maxWidth: '1140px', margin: '40px auto', padding: '0 20px' }}>
        
        {loading && (
          <div className="brand-loading" style={{ textAlign: 'center', padding: '60px 0' }}>
            <div className="spinner" style={{ margin: '0 auto 16px' }}></div>
            <p style={{ color: '#94a3b8' }}>Chargement des modèles {displayBrandName}...</p>
          </div>
        )}

        {/* Modèles Neufs de la Marque */}
        {seoData?.models && seoData.models.length > 0 && (
          <section style={{ marginBottom: '50px' }}>
            <h2 style={{ fontSize: '1.6rem', color: '#fff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Car color="#d4a017" /> Tous les Modèles {displayBrandName} ({seoData.models_count})
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '22px' }}>
              {seoData.models.map((m) => (
                <Link
                  key={m.id}
                  to={`/neuf/${m.slug}`}
                  style={{
                    textDecoration: 'none',
                    background: 'var(--bg-surface, #141f2d)',
                    borderRadius: '16px',
                    overflow: 'hidden',
                    border: '1px solid var(--border-subtle)',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'transform 0.2s ease, border-color 0.2s ease'
                  }}
                >
                  <div style={{ height: '180px', background: '#0a1118', overflow: 'hidden' }}>
                    <img
                      src={m.hero_image_url || resolveVehicleImage(displayBrandName, m.name)}
                      alt={`${displayBrandName} ${m.name}`}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      onError={(e) => {
                        (e.currentTarget as HTMLImageElement).src = resolveVehicleImage(displayBrandName, m.name);
                      }}
                    />
                  </div>
                  <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>{displayBrandName} • {m.body_type || 'Modèle Neuf'}</span>
                      <h3 style={{ fontSize: '1.25rem', color: '#ffffff', margin: '4px 0 10px' }}>{m.name}</h3>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                      <div>
                        <span style={{ fontSize: '0.7rem', color: '#94a3b8', display: 'block' }}>À partir de</span>
                        <strong style={{ color: '#d4a017', fontSize: '1.1rem' }}>{m.starting_price_mad.toLocaleString('fr-FR')} MAD</strong>
                      </div>
                      <span style={{ padding: '6px 12px', background: 'rgba(212, 160, 23, 0.1)', color: '#d4a017', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 600 }}>
                        Fiche &amp; Finitions →
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Maillage vers Guide d'Achat & Comparatifs */}
        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '50px' }}>
          <div style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '16px', border: '1px solid var(--border-subtle)', padding: '24px' }}>
            <h3 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Scale size={20} color="#d4a017" /> Comparatifs {displayBrandName}
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '16px' }}>
              Comparez {displayBrandName} avec ses concurrents directs sur le marché marocain (prix, consommation, coffre).
            </p>
            <Link to="/comparateur" style={{ color: '#d4a017', fontWeight: 700, textDecoration: 'none', fontSize: '0.9rem' }}>
              Ouvrir le Comparateur Radar 8D →
            </Link>
          </div>

          <div style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '16px', border: '1px solid var(--border-subtle)', padding: '24px' }}>
            <h3 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ShieldCheck size={20} color="#10b981" /> Guide Achat &amp; Vignette DGI
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', lineHeight: 1.6, marginBottom: '16px' }}>
              Consultez notre guide complet pour connaître la fiscalité et les démarches d'immatriculation pour {displayBrandName}.
            </p>
            <Link to="/guide-achat-voiture-maroc" style={{ color: '#10b981', fontWeight: 700, textDecoration: 'none', fontSize: '0.9rem' }}>
              Lire le Guide d'Achat Maroc →
            </Link>
          </div>
        </section>

        {/* FAQs Marque */}
        {seoData?.faqs && (
          <section style={{ marginBottom: '60px' }}>
            <h2 style={{ fontSize: '1.5rem', color: '#fff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <HelpCircle color="#d4a017" /> Questions Fréquentes sur {displayBrandName} au Maroc
            </h2>
            <div style={{ display: 'grid', gap: '12px' }}>
              {seoData.faqs.map((faq, idx) => {
                const isOpen = activeFaq === idx;
                return (
                  <div key={idx} style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '12px', border: '1px solid var(--border-subtle)', overflow: 'hidden' }}>
                    <button
                      onClick={() => setActiveFaq(isOpen ? null : idx)}
                      style={{ width: '100%', padding: '16px 20px', background: 'none', border: 'none', color: '#fff', fontSize: '1rem', fontWeight: 600, textAlign: 'left', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                    >
                      <span>{faq.question}</span>
                      <span style={{ color: '#d4a017', fontSize: '1.2rem' }}>{isOpen ? '−' : '+'}</span>
                    </button>
                    {isOpen && (
                      <div style={{ padding: '0 20px 20px', color: '#cbd5e1', fontSize: '0.95rem', lineHeight: 1.7, borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '10px' }}>
                        {faq.answer}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>
        )}

      </div>
    </div>
  );
};

export default MarquePage;
