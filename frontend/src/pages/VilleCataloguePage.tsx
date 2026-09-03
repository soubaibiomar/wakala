import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  MapPin,
  Building2,
  Phone,
  Car,
  ShieldCheck,
  HelpCircle,
  ArrowRight,
  Sparkles,
  Award,
  CreditCard,
  Navigation
} from 'lucide-react';
import PageMeta from '../components/seo/PageMeta';
import FAQStructuredData from '../components/seo/FAQStructuredData';
import BreadcrumbStructuredData from '../components/seo/BreadcrumbStructuredData';
import seoService, { CitySeoData } from '../services/seoService';
import { CATALOGUE_IMAGE_FALLBACK, resolveVehicleImage } from '../utils/vehicleImageResolver';
import './Catalogue.css';

export const VilleCataloguePage: React.FC = () => {
  const { ville } = useParams<{ ville: string }>();
  const [data, setData] = useState<CitySeoData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  useEffect(() => {
    if (!ville) return;
    setLoading(true);
    setError(null);
    seoService.getCityData(ville)
      .then((res) => {
        setData(res);
      })
      .catch((err) => {
        console.error('Erreur chargement ville SEO:', err);
        setError("Impossible de charger les données pour cette ville.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [ville]);

  if (loading) {
    return (
      <div style={{ maxWidth: '1100px', margin: '80px auto', textAlign: 'center', padding: '0 20px' }}>
        <div className="spinner" style={{ margin: '0 auto 20px' }}></div>
        <p style={{ color: 'var(--text-secondary, #94a3b8)' }}>Chargement des concessions officielles de la ville...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div style={{ maxWidth: '800px', margin: '80px auto', textAlign: 'center', padding: '40px 20px', background: 'var(--bg-surface, #141f2d)', borderRadius: '16px', border: '1px solid var(--border-subtle)' }}>
        <MapPin size={48} color="#d4a017" style={{ marginBottom: '16px' }} />
        <h1 style={{ color: '#fff', fontSize: '1.6rem', marginBottom: '12px' }}>Ville introuvable</h1>
        <p style={{ color: '#94a3b8', marginBottom: '24px' }}>{error || "Nous n'avons pas pu charger cette ville."}</p>
        <Link to="/catalogue" className="btn btn--primary" style={{ padding: '10px 20px', borderRadius: '24px', textDecoration: 'none', background: '#d4a017', color: '#0f172a', fontWeight: 600 }}>
          Voir tout le catalogue national
        </Link>
      </div>
    );
  }

  return (
    <div className="ville-seo-page" style={{ paddingBottom: '80px' }}>
      <PageMeta
        title={data.title}
        description={data.meta_description}
        canonicalUrl={`https://wakala.ma/voitures-neuves/${data.city_slug}`}
        ogType="website"
      />
      <BreadcrumbStructuredData items={data.breadcrumbs} />
      <FAQStructuredData faqs={data.faqs} />

      {/* Hero Ville */}
      <section style={{ background: 'linear-gradient(135deg, #09111b 0%, #101e30 60%, #182e4a 100%)', padding: '50px 20px 40px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ maxWidth: '1140px', margin: '0 auto' }}>
          
          <nav style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '20px' }}>
            <Link to="/" style={{ color: '#94a3b8', textDecoration: 'none' }}>Accueil</Link>
            <span>/</span>
            <Link to="/guide-achat-voiture-maroc" style={{ color: '#94a3b8', textDecoration: 'none' }}>Guide d'Achat</Link>
            <span>/</span>
            <Link to="/catalogue" style={{ color: '#94a3b8', textDecoration: 'none' }}>Villes</Link>
            <span>/</span>
            <span style={{ color: '#d4a017' }}>{data.city_name}</span>
          </nav>

          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '5px 12px', background: 'rgba(212, 160, 23, 0.15)', border: '1px solid rgba(212, 160, 23, 0.4)', borderRadius: '30px', color: '#d4a017', fontSize: '0.8rem', fontWeight: 600, marginBottom: '16px' }}>
            <MapPin size={15} /> Réseau Concessionnaires Agréés • {data.city_name} (Maroc)
          </div>

          <h1 style={{ fontSize: 'clamp(1.8rem, 3.5vw, 2.8rem)', color: '#ffffff', fontWeight: 800, lineHeight: 1.2, marginBottom: '20px' }}>
            Voitures Neuves à {data.city_name} (2026) : Prix Clé en Main &amp; Concessions Agréées
          </h1>

          {/* GEO Self-Contained Answer */}
          <div style={{ background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: '14px', padding: '20px', color: '#e2e8f0', fontSize: '1.05rem', lineHeight: 1.7 }}>
            <p style={{ margin: 0 }}>
              <strong>Synthèse locale :</strong> {data.self_contained_answer}
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main style={{ maxWidth: '1140px', margin: '40px auto 0', padding: '0 20px' }}>

        {/* Section 1 : Concessionnaires et Showrooms Partenaires */}
        {data.showrooms && data.showrooms.length > 0 && (
          <section style={{ marginBottom: '50px' }}>
            <h2 style={{ fontSize: '1.6rem', color: '#fff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Building2 color="#d4a017" /> Concessionnaires &amp; Showrooms Officiels à {data.city_name}
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '18px' }}>
              {data.showrooms.map((sh) => (
                <div key={sh.id} style={{ background: 'var(--bg-surface, #141f2d)', padding: '22px', borderRadius: '14px', border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#d4a017', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{sh.dealership_name}</span>
                    <h3 style={{ fontSize: '1.15rem', color: '#fff', margin: '6px 0 10px' }}>{sh.name}</h3>
                    <p style={{ fontSize: '0.9rem', color: '#94a3b8', display: 'flex', alignItems: 'flex-start', gap: '8px', margin: '0 0 12px' }}>
                      <Navigation size={16} color="#64748b" style={{ flexShrink: 0, marginTop: '3px' }} />
                      <span>{sh.address}</span>
                    </p>
                    {sh.brand_affiliations && sh.brand_affiliations.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '14px' }}>
                        {sh.brand_affiliations.map((b, idx) => (
                          <span key={idx} style={{ padding: '3px 8px', background: 'rgba(255,255,255,0.06)', borderRadius: '12px', fontSize: '0.75rem', color: '#cbd5e1' }}>
                            {b}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div style={{ paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.85rem', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <ShieldCheck size={16} /> Agréé Wakala
                    </span>
                    <Link to="/chat" style={{ color: '#d4a017', fontSize: '0.85rem', fontWeight: 600, textDecoration: 'none' }}>
                      Réserver un essai →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Section 2 : Modèles Disponibles */}
        <section style={{ marginBottom: '50px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
            <h2 style={{ fontSize: '1.6rem', color: '#fff', margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Car color="#60a5fa" /> Modèles Neufs Recommandés à {data.city_name}
            </h2>
            <Link to="/catalogue" style={{ color: '#d4a017', textDecoration: 'none', fontWeight: 600, fontSize: '0.9rem' }}>
              Voir tout le catalogue ({data.models.length}+ modèles) →
            </Link>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px' }}>
            {data.models.map((m) => (
              <Link
                key={m.id}
                to={`/neuf/${m.slug}`}
                style={{
                  textDecoration: 'none',
                  background: 'var(--bg-surface, #141f2d)',
                  borderRadius: '14px',
                  overflow: 'hidden',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.2s ease'
                }}
              >
                <div style={{ height: '170px', background: '#0a1118', overflow: 'hidden' }}>
                  <img
                    src={resolveVehicleImage(m.brand_name, m.name)}
                    alt={`${m.brand_name} ${m.name}`}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    onError={(e) => {
                      (e.currentTarget as HTMLImageElement).src = CATALOGUE_IMAGE_FALLBACK;
                    }}
                  />
                </div>
                <div style={{ padding: '18px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>{m.brand_name}</span>
                    <h3 style={{ fontSize: '1.15rem', color: '#ffffff', margin: '4px 0 10px' }}>{m.name}</h3>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '10px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                    <div>
                      {m.starting_price_mad > 0 && <>
                        <span style={{ fontSize: '0.7rem', color: '#94a3b8', display: 'block' }}>À partir de</span>
                        <strong style={{ color: '#d4a017', fontSize: '1.05rem' }}>{m.starting_price_mad.toLocaleString('fr-FR')} MAD</strong>
                      </>}
                    </div>
                    <span style={{ padding: '5px 10px', background: 'rgba(212,160,23,0.1)', color: '#d4a017', borderRadius: '16px', fontSize: '0.75rem', fontWeight: 600 }}>
                      Détails →
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Section 3 : Maillage Villes Proches */}
        <section style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '16px', border: '1px solid var(--border-subtle)', padding: '24px', marginBottom: '50px' }}>
          <h3 style={{ color: '#fff', fontSize: '1.2rem', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Navigation size={18} color="#d4a017" /> Explorer d'autres villes au Maroc
          </h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
            {data.other_cities.map((oc) => (
              <Link
                key={oc.slug}
                to={`/voitures-neuves/${oc.slug}`}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 14px',
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '20px',
                  color: '#e2e8f0',
                  textDecoration: 'none',
                  fontSize: '0.85rem'
                }}
              >
                <MapPin size={13} color="#d4a017" />
                {oc.name}
              </Link>
            ))}
          </div>
        </section>

        {/* Section 4 : FAQ Ville */}
        <section style={{ marginBottom: '60px' }}>
          <h2 style={{ fontSize: '1.5rem', color: '#fff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <HelpCircle color="#d4a017" /> Questions Fréquentes sur l'Achat Auto à {data.city_name}
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

export default VilleCataloguePage;
