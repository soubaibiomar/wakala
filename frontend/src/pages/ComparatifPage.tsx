import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Scale,
  ShieldCheck,
  CheckCircle,
  HelpCircle,
  ArrowRight,
  TrendingDown,
  Sparkles,
  Award,
  Zap,
  Gauge,
  ShoppingBag,
  ExternalLink
} from 'lucide-react';
import PageMeta from '../components/seo/PageMeta';
import FAQStructuredData from '../components/seo/FAQStructuredData';
import BreadcrumbStructuredData from '../components/seo/BreadcrumbStructuredData';
import seoService, { ComparatifSeoData } from '../services/seoService';
import { CATALOGUE_IMAGE_FALLBACK, resolveVehicleImage } from '../utils/vehicleImageResolver';
import './ComparatorPage.css';

export const ComparatifPage: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [data, setData] = useState<ComparatifSeoData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    setError(null);
    seoService.getComparatifData(slug)
      .then((res) => {
        setData(res);
      })
      .catch((err) => {
        console.error('Erreur chargement comparatif SEO:', err);
        setError("Ce comparatif n'est pas disponible ou les véhicules spécifiés sont introuvables.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [slug]);

  if (loading) {
    return (
      <div style={{ maxWidth: '1100px', margin: '80px auto', textAlign: 'center', padding: '0 20px' }}>
        <div className="spinner" style={{ margin: '0 auto 20px' }}></div>
        <p style={{ color: 'var(--text-secondary, #94a3b8)' }}>Chargement du comparatif certifié...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div style={{ maxWidth: '800px', margin: '80px auto', textAlign: 'center', padding: '40px 20px', background: 'var(--bg-surface, #141f2d)', borderRadius: '16px', border: '1px solid var(--border-subtle)' }}>
        <Scale size={48} color="#d4a017" style={{ marginBottom: '16px' }} />
        <h1 style={{ color: '#fff', fontSize: '1.6rem', marginBottom: '12px' }}>Comparatif introuvable</h1>
        <p style={{ color: '#94a3b8', marginBottom: '24px' }}>{error || "Nous n'avons pas pu charger ce comparatif."}</p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <Link to="/comparateur" className="btn btn--primary" style={{ padding: '10px 20px', borderRadius: '24px', textDecoration: 'none', background: '#d4a017', color: '#0f172a', fontWeight: 600 }}>
            Utiliser le Comparateur Libre
          </Link>
          <Link to="/guide-achat-voiture-maroc" className="btn btn--outline" style={{ padding: '10px 20px', borderRadius: '24px', textDecoration: 'none', border: '1px solid #d4a017', color: '#d4a017', fontWeight: 600 }}>
            Consulter le Guide d'Achat
          </Link>
        </div>
      </div>
    );
  }

  const { vehicle1: v1, vehicle2: v2 } = data;

  return (
    <div className="comparatif-seo-page" style={{ paddingBottom: '80px' }}>
      <PageMeta
        title={data.title}
        description={data.meta_description}
        canonicalUrl={`https://wakala.ma/comparer/${data.slug}`}
        ogType="article"
      />
      <BreadcrumbStructuredData items={data.breadcrumbs} />
      <FAQStructuredData faqs={data.faqs} />

      {/* Header & Hero */}
      <section style={{ background: 'linear-gradient(135deg, #09111b 0%, #101e30 60%, #182e4a 100%)', padding: '50px 20px 40px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ maxWidth: '1140px', margin: '0 auto' }}>
          
          {/* Breadcrumbs visuels */}
          <nav style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '20px' }}>
            <Link to="/" style={{ color: '#94a3b8', textDecoration: 'none' }}>Accueil</Link>
            <span>/</span>
            <Link to="/guide-achat-voiture-maroc" style={{ color: '#94a3b8', textDecoration: 'none' }}>Guide d'Achat</Link>
            <span>/</span>
            <Link to="/comparateur" style={{ color: '#94a3b8', textDecoration: 'none' }}>Comparateur</Link>
            <span>/</span>
            <span style={{ color: '#d4a017' }}>{v1.model_name} vs {v2.model_name}</span>
          </nav>

          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '5px 12px', background: 'rgba(212, 160, 23, 0.15)', border: '1px solid rgba(212, 160, 23, 0.4)', borderRadius: '30px', color: '#d4a017', fontSize: '0.8rem', fontWeight: 600, marginBottom: '16px' }}>
            <Award size={15} /> Comparatif Officiel Neuf • Données certifiées {data.updated_at.slice(0, 4)}
          </div>

          <h1 style={{ fontSize: 'clamp(1.8rem, 3.5vw, 2.8rem)', color: '#ffffff', fontWeight: 800, lineHeight: 1.2, marginBottom: '20px' }}>
            {v1.brand_name} {v1.model_name} vs {v2.brand_name} {v2.model_name} : Le Duel Automobile au Maroc
          </h1>

          {/* GEO Self-Contained Answer */}
          <div style={{ background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: '14px', padding: '20px', color: '#e2e8f0', fontSize: '1.05rem', lineHeight: 1.7 }}>
            <p style={{ margin: 0 }}>
              <strong>Verdict synthétique :</strong> {data.self_contained_answer}
            </p>
          </div>
        </div>
      </section>

      {/* Main Dual Cards Section */}
      <main style={{ maxWidth: '1140px', margin: '40px auto 0', padding: '0 20px' }}>
        
        {/* Face à Face Cartes */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px', marginBottom: '40px' }}>
          
          {/* Véhicule 1 */}
          <div style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '18px', border: '1px solid var(--border-subtle)', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ position: 'relative', height: '220px', background: '#0a1118' }}>
              <img
                src={v1.image_url || resolveVehicleImage(v1.brand_name, v1.model_name)}
                alt={v1.full_name}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src = CATALOGUE_IMAGE_FALLBACK;
                }}
              />
              <div style={{ position: 'absolute', top: '12px', left: '12px', padding: '4px 10px', background: 'rgba(0,0,0,0.7)', borderRadius: '20px', color: '#fff', fontSize: '0.75rem', fontWeight: 600 }}>
                {v1.brand_name}
              </div>
            </div>
            <div style={{ padding: '24px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <h2 style={{ fontSize: '1.4rem', color: '#fff', margin: '0 0 6px' }}>{v1.brand_name} {v1.model_name}</h2>
                <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Finition : {v1.trim_name}</span>
                
                <div style={{ margin: '16px 0', padding: '14px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Prix Clé en Main estimé</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#d4a017' }}>{v1.clef_en_main_mad.toLocaleString('fr-FR')} MAD</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
                    Catalogue : {v1.price_new_mad.toLocaleString('fr-FR')} MAD • Vignette : {v1.vignette_dgi_mad} MAD/an
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
                <Link
                  to={`/neuf/${v1.model_slug}`}
                  style={{ flex: 1, padding: '10px', background: '#d4a017', color: '#0f172a', fontWeight: 700, borderRadius: '8px', textAlign: 'center', textDecoration: 'none', fontSize: '0.9rem' }}
                >
                  Fiche Complète
                </Link>
                <Link
                  to={`/marque/${v1.brand_slug}`}
                  style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.08)', color: '#e2e8f0', borderRadius: '8px', textDecoration: 'none', fontSize: '0.85rem' }}
                >
                  Gamme {v1.brand_name}
                </Link>
              </div>
            </div>
          </div>

          {/* Véhicule 2 */}
          <div style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '18px', border: '1px solid var(--border-subtle)', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            <div style={{ position: 'relative', height: '220px', background: '#0a1118' }}>
              <img
                src={v2.image_url || resolveVehicleImage(v2.brand_name, v2.model_name)}
                alt={v2.full_name}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                onError={(e) => {
                  (e.currentTarget as HTMLImageElement).src = CATALOGUE_IMAGE_FALLBACK;
                }}
              />
              <div style={{ position: 'absolute', top: '12px', left: '12px', padding: '4px 10px', background: 'rgba(0,0,0,0.7)', borderRadius: '20px', color: '#fff', fontSize: '0.75rem', fontWeight: 600 }}>
                {v2.brand_name}
              </div>
            </div>
            <div style={{ padding: '24px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <h2 style={{ fontSize: '1.4rem', color: '#fff', margin: '0 0 6px' }}>{v2.brand_name} {v2.model_name}</h2>
                <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Finition : {v2.trim_name}</span>
                
                <div style={{ margin: '16px 0', padding: '14px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Prix Clé en Main estimé</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#d4a017' }}>{v2.clef_en_main_mad.toLocaleString('fr-FR')} MAD</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
                    Catalogue : {v2.price_new_mad.toLocaleString('fr-FR')} MAD • Vignette : {v2.vignette_dgi_mad} MAD/an
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
                <Link
                  to={`/neuf/${v2.model_slug}`}
                  style={{ flex: 1, padding: '10px', background: '#d4a017', color: '#0f172a', fontWeight: 700, borderRadius: '8px', textAlign: 'center', textDecoration: 'none', fontSize: '0.9rem' }}
                >
                  Fiche Complète
                </Link>
                <Link
                  to={`/marque/${v2.brand_slug}`}
                  style={{ padding: '10px 14px', background: 'rgba(255,255,255,0.08)', color: '#e2e8f0', borderRadius: '8px', textDecoration: 'none', fontSize: '0.85rem' }}
                >
                  Gamme {v2.brand_name}
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Tableau Comparatif des Spécifications */}
        <section style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '18px', border: '1px solid var(--border-subtle)', padding: '28px', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '1.5rem', color: '#fff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Scale color="#d4a017" /> Fiche Technique &amp; Données Chiffrées Réelles
          </h2>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', minWidth: '550px' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid rgba(255,255,255,0.1)' }}>
                  <th style={{ padding: '14px', color: '#94a3b8', fontWeight: 600, width: '35%' }}>Critère</th>
                  <th style={{ padding: '14px', color: '#60a5fa', fontWeight: 700, width: '32.5%' }}>{v1.brand_name} {v1.model_name}</th>
                  <th style={{ padding: '14px', color: '#34d399', fontWeight: 700, width: '32.5%' }}>{v2.brand_name} {v2.model_name}</th>
                </tr>
              </thead>
              <tbody style={{ color: '#e2e8f0', fontSize: '0.95rem' }}>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '14px', color: '#94a3b8' }}>Prix Clé en Main</td>
                  <td style={{ padding: '14px', fontWeight: 700, color: v1.clef_en_main_mad <= v2.clef_en_main_mad ? '#10b981' : '#fff' }}>
                    {v1.clef_en_main_mad.toLocaleString('fr-FR')} MAD
                  </td>
                  <td style={{ padding: '14px', fontWeight: 700, color: v2.clef_en_main_mad <= v1.clef_en_main_mad ? '#10b981' : '#fff' }}>
                    {v2.clef_en_main_mad.toLocaleString('fr-FR')} MAD
                  </td>
                </tr>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '14px', color: '#94a3b8' }}>Vignette DGI annuelle</td>
                  <td style={{ padding: '14px' }}>{v1.vignette_dgi_mad} MAD/an ({v1.specs.fiscal_power_cv})</td>
                  <td style={{ padding: '14px' }}>{v2.vignette_dgi_mad} MAD/an ({v2.specs.fiscal_power_cv})</td>
                </tr>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '14px', color: '#94a3b8' }}>Carburant &amp; Boîte</td>
                  <td style={{ padding: '14px' }}>{v1.specs.fuel_type} • {v1.specs.transmission}</td>
                  <td style={{ padding: '14px' }}>{v2.specs.fuel_type} • {v2.specs.transmission}</td>
                </tr>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '14px', color: '#94a3b8' }}>Puissance DIN</td>
                  <td style={{ padding: '14px' }}>{v1.specs.engine_power_hp} ch</td>
                  <td style={{ padding: '14px' }}>{v2.specs.engine_power_hp} ch</td>
                </tr>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '14px', color: '#94a3b8' }}>Consommation Mixte</td>
                  <td style={{ padding: '14px' }}>{v1.specs.consumption_l_100} L/100km</td>
                  <td style={{ padding: '14px' }}>{v2.specs.consumption_l_100} L/100km</td>
                </tr>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '14px', color: '#94a3b8' }}>Volume de Coffre</td>
                  <td style={{ padding: '14px' }}>{v1.specs.trunk_capacity_l} Litres</td>
                  <td style={{ padding: '14px' }}>{v2.specs.trunk_capacity_l} Litres</td>
                </tr>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '14px', color: '#94a3b8' }}>Sécurité EuroNCAP</td>
                  <td style={{ padding: '14px' }}>{'★'.repeat(v1.specs.euro_ncap_stars)}{'☆'.repeat(5 - v1.specs.euro_ncap_stars)}</td>
                  <td style={{ padding: '14px' }}>{'★'.repeat(v2.specs.euro_ncap_stars)}{'☆'.repeat(5 - v2.specs.euro_ncap_stars)}</td>
                </tr>
                <tr>
                  <td style={{ padding: '14px', color: '#94a3b8' }}>Garantie Constructeur</td>
                  <td style={{ padding: '14px' }}>{v1.warranty}</td>
                  <td style={{ padding: '14px' }}>{v2.warranty}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Radar Scores Heuristiques */}
        <section style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '18px', border: '1px solid var(--border-subtle)', padding: '28px', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '1.5rem', color: '#fff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Zap color="#d4a017" /> Indice de Performance &amp; Polyvalence (Radar 5D)
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            {[
              { label: 'Économie / Budget', k: 'economie' },
              { label: 'Puissance Moteur', k: 'puissance' },
              { label: 'Espace & Coffre', k: 'espace' },
              { label: 'Sécurité Crash Test', k: 'securite' },
              { label: 'Sobriété Écologique', k: 'ecologie' },
            ].map((metric) => {
              const s1 = v1.radar_scores[metric.k as keyof typeof v1.radar_scores];
              const s2 = v2.radar_scores[metric.k as keyof typeof v2.radar_scores];
              return (
                <div key={metric.k} style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '8px', fontWeight: 600 }}>{metric.label}</div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem', marginBottom: '4px' }}>
                    <span style={{ color: '#60a5fa' }}>{v1.model_name}: <strong>{s1}/100</strong></span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                    <span style={{ color: '#34d399' }}>{v2.model_name}: <strong>{s2}/100</strong></span>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Maillage Sémantique Recommandé */}
        <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '40px' }}>
          <div style={{ background: 'rgba(212, 160, 23, 0.08)', border: '1px solid rgba(212, 160, 23, 0.3)', borderRadius: '16px', padding: '24px' }}>
            <h3 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '10px' }}>Besoin d'un financement ?</h3>
            <p style={{ color: '#cbd5e1', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '16px' }}>
              Calculez vos mensualités en crédit classique ou Mourabaha pour {v1.model_name} ou {v2.model_name}.
            </p>
            <Link to="/financement-auto-maroc" style={{ color: '#d4a017', fontWeight: 700, textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              Simuler le financement auto au Maroc →
            </Link>
          </div>

          <div style={{ background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '16px', padding: '24px' }}>
            <h3 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '10px' }}>Consulter le Guide d'Achat</h3>
            <p style={{ color: '#cbd5e1', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '16px' }}>
              Tout savoir sur les démarches d'immatriculation, la vignette DGI et le choix des options au Maroc.
            </p>
            <Link to="/guide-achat-voiture-maroc" style={{ color: '#60a5fa', fontWeight: 700, textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
              Lire le guide d'achat complet →
            </Link>
          </div>
        </section>

        {/* FAQs */}
        <section style={{ marginBottom: '60px' }}>
          <h2 style={{ fontSize: '1.5rem', color: '#fff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <HelpCircle color="#d4a017" /> Questions Fréquentes sur ce Comparatif
          </h2>
          <div style={{ display: 'grid', gap: '12px' }}>
            {data.faqs.map((faq, idx) => {
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

      </main>
    </div>
  );
};

export default ComparatifPage;
