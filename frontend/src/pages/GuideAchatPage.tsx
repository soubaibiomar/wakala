import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ShieldCheck,
  Calculator,
  Compass,
  CheckCircle2,
  HelpCircle,
  Car,
  MapPin,
  Sparkles,
  ArrowRight,
  TrendingUp,
  CreditCard,
  FileText,
  Clock,
  Award
} from 'lucide-react';
import PageMeta from '../components/seo/PageMeta';
import FAQStructuredData from '../components/seo/FAQStructuredData';
import BreadcrumbStructuredData from '../components/seo/BreadcrumbStructuredData';
import seoService, { SeoHubData } from '../services/seoService';
import { resolveVehicleImage } from '../utils/vehicleImageResolver';
import './StaticPages.css';

export const GuideAchatPage: React.FC = () => {
  const [hubData, setHubData] = useState<SeoHubData | null>(null);
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  useEffect(() => {
    seoService.getHubData().then(setHubData).catch((err) => {
      console.warn("Could not load SEO hub data for GuideAchatPage", err);
    });
  }, []);

  const breadcrumbs = [
    { name: 'Accueil', item: 'https://wakala.ma/' },
    { name: "Guide d'Achat Voiture Neuve Maroc", item: 'https://wakala.ma/guide-achat-voiture-maroc' },
  ];

  const faqs = [
    {
      question: "Comment calculer le prix clé en main d'une voiture neuve au Maroc ?",
      answer: "Le prix clé en main comprend le prix catalogue du véhicule neuf, auquel s'ajoutent les frais de carte grise / immatriculation, la vignette DGI annuelle (de 350 à 20 000+ MAD selon la puissance fiscale CV et le carburant), les frais de dossier et plaques, ainsi que l'éventuelle taxe de luxe pour les véhicules de plus de 400 000 MAD HT (les hybrides et électriques en sont totalement exonérés)."
    },
    {
      question: "Vaut-il mieux acheter un moteur Diesel, Essence ou Hybride au Maroc en 2026 ?",
      answer: "Si vous roulez plus de 20 000 km/an, le Diesel reste très rentable. Pour un usage urbain inférieur à 15 000 km/an, l'Essence moderne offre un coût d'acquisition plus bas. L'Hybride (HEV) est désormais le meilleur compromis économique et fiscal au Maroc : consommation sous les 4.5 L/100km, vignette réduite et exonération de taxe de luxe."
    },
    {
      question: "Quelles sont les garanties officielles des constructeurs au Maroc ?",
      answer: "Au Maroc, la garantie légale et constructeur varie généralement de 3 ans / 100 000 km (Dacia, Renault, Peugeot) à 5 ans ou 7 ans / 150 000 km (Kia, MG, Hyundai selon modèles). Cette garantie couvre pièces et main-d'œuvre dans l'ensemble des concessions agréées du Royaume."
    },
    {
      question: "Quel est le délai de livraison d'un véhicule neuf au Maroc ?",
      answer: "Pour les véhicules produits localement (Dacia Sandero à Somaca Casablanca ou Tanger) ou en stock concessionnaire, la livraison intervient en 5 à 10 jours ouvrés avec immatriculation WW provisoire. Pour les commandes d'usines spécifiques ou modèles importés rares, les délais varient de 4 à 12 semaines."
    },
    {
      question: "Comment financer sa voiture neuve au Maroc (Crédit classique vs Mourabaha) ?",
      answer: "Vous pouvez opter pour un crédit auto bancaire classique (avec un apport conseillé de 20% et un taux effectif global entre 5% et 7%), ou pour un financement participatif Mourabaha (sans intérêts usuraires, avec marge bénéficiaire convenue d'avance et conforme aux avis du Conseil Supérieur des Oulémas)."
    }
  ];

  return (
    <div className="static-page guide-achat-page">
      <PageMeta
        title="Guide d'Achat Voiture Neuve Maroc 2026 : Prix, Taxes & Démarches"
        description="Le guide de référence officiel pour acheter une voiture neuve au Maroc en 2026. Calcul du prix clé en main, vignette DGI, comparatifs, garanties et financement."
        canonicalUrl="https://wakala.ma/guide-achat-voiture-maroc"
        ogType="article"
      />
      <BreadcrumbStructuredData items={breadcrumbs} />
      <FAQStructuredData faqs={faqs} />

      {/* Hero Pilier */}
      <section className="static-hero" style={{ background: 'linear-gradient(135deg, #0a1118 0%, #0f1d2e 60%, #172d47 100%)', padding: '60px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 14px', background: 'rgba(212, 160, 23, 0.15)', border: '1px solid rgba(212, 160, 23, 0.4)', borderRadius: '30px', color: 'var(--accent-gold, #d4a017)', fontSize: '0.85rem', fontWeight: 600, marginBottom: '20px' }}>
            <Award size={16} /> Guide Officiel de Référence • Mis à jour : Août 2026
          </div>
          <h1 style={{ fontSize: 'clamp(2rem, 4vw, 3.2rem)', fontFamily: 'var(--font-display, inherit)', fontWeight: 800, color: '#ffffff', lineHeight: 1.2, marginBottom: '20px' }}>
            Guide Complet de l'Achat Automobile Neuf au Maroc (2026)
          </h1>
          
          {/* GEO Self-Contained Answer */}
          <div style={{ background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: '16px', padding: '24px', color: '#e2e8f0', fontSize: '1.05rem', lineHeight: 1.7, marginTop: '20px' }}>
            <p style={{ margin: 0 }}>
              <strong>L'essentiel en 2026 :</strong> L'achat d'un véhicule neuf au Maroc nécessite d'anticiper le <em>prix clé en main</em> (prix catalogue + vignette DGI de 350 à plus de 20 000 MAD + frais d'immatriculation). Les modèles hybrides bénéficient d'une totale exonération de taxe de luxe et d'une fiscalité allégée. Wakala certifie 100% des fiches techniques des concessionnaires officiels du Royaume et vous accompagne du choix de la motorisation jusqu'à la livraison en concession.
            </p>
          </div>
        </div>
      </section>

      {/* Sommaire Sémantique & Liens Rapides */}
      <section style={{ maxWidth: '1100px', margin: '40px auto 0', padding: '0 20px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          <a href="#budget-clef-en-main" style={{ textDecoration: 'none', background: 'var(--bg-surface, #141f2d)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-subtle)', color: 'var(--text-primary, #fff)', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Calculator color="#d4a017" size={24} />
            <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>1. Budget Clé en Main</span>
          </a>
          <a href="#choix-motorisation" style={{ textDecoration: 'none', background: 'var(--bg-surface, #141f2d)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-subtle)', color: 'var(--text-primary, #fff)', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Compass color="#3b82f6" size={24} />
            <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>2. Motorisations</span>
          </a>
          <a href="#garanties-reseau" style={{ textDecoration: 'none', background: 'var(--bg-surface, #141f2d)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-subtle)', color: 'var(--text-primary, #fff)', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <ShieldCheck color="#10b981" size={24} />
            <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>3. Réseau & Garanties</span>
          </a>
          <Link to="/financement-auto-maroc" style={{ textDecoration: 'none', background: 'var(--bg-surface, #141f2d)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-subtle)', color: 'var(--text-primary, #fff)', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <CreditCard color="#a855f7" size={24} />
            <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>4. Guide Financement →</span>
          </Link>
        </div>
      </section>

      {/* Contenu Rédactionnel Long Format */}
      <main style={{ maxWidth: '1100px', margin: '40px auto', padding: '0 20px', color: 'var(--text-secondary, #94a3b8)', lineHeight: 1.8 }}>
        
        {/* Section 1 : Budget & Taxes Clé en Main */}
        <section id="budget-clef-en-main" style={{ marginBottom: '60px' }}>
          <h2 style={{ fontSize: '1.8rem', color: 'var(--text-primary, #ffffff)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Calculator color="#d4a017" /> 1. Le Budget Réel : Comprendre le Prix Clé en Main au Maroc
          </h2>
          <p>
            Lors de l'achat d'un véhicule neuf au Maroc, le prix affiché en vitrine ou dans les publicités constructeurs est le <strong>prix catalogue de base</strong>. Pour obtenir le coût d'acquisition effectif (débours réel), vous devez intégrer l'ensemble des frais obligatoires légaux :
          </p>
          <div style={{ background: 'var(--bg-surface, #141f2d)', padding: '24px', borderRadius: '16px', border: '1px solid var(--border-subtle)', margin: '24px 0' }}>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'grid', gap: '14px' }}>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <CheckCircle2 size={20} color="#10b981" style={{ flexShrink: 0, marginTop: '4px' }} />
                <div>
                  <strong style={{ color: '#fff' }}>Vignette DGI annuelle :</strong> Fixée selon la puissance fiscale (CV) et le type de carburant. Les moteurs essence de moins de 8 CV payent 350 MAD/an, contre 700 MAD pour le Diesel. Au-delà de 15 CV, la vignette atteint 8 000 à 20 000 MAD/an.
                </div>
              </li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <CheckCircle2 size={20} color="#10b981" style={{ flexShrink: 0, marginTop: '4px' }} />
                <div>
                  <strong style={{ color: '#fff' }}>Frais d'immatriculation et Carte Grise :</strong> Proportionnels à la puissance fiscale et perçus par l'Agence Nationale de la Sécurité Routière (NARSA).
                </div>
              </li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <CheckCircle2 size={20} color="#10b981" style={{ flexShrink: 0, marginTop: '4px' }} />
                <div>
                  <strong style={{ color: '#fff' }}>Taxe de Luxe (TIC additionnelle) :</strong> S'applique aux véhicules dont la valeur excède 400 000 MAD HT (5% à 30%). <em>Bon à savoir :</em> Les motorisations hybrides et électriques en sont 100% exonérées.
                </div>
              </li>
              <li style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <CheckCircle2 size={20} color="#10b981" style={{ flexShrink: 0, marginTop: '4px' }} />
                <div>
                  <strong style={{ color: '#fff' }}>Frais de dossier et plaques d'immatriculation :</strong> Frais administratifs et pose des plaques définitives, généralement compris entre 1 500 et 3 000 MAD.
                </div>
              </li>
            </ul>
          </div>
          <p>
            Sur Wakala, chaque fiche véhicule calcule automatiquement le détail fiscal exact grâce à notre simulateur certifié, évitant toute surprise chez le concessionnaire.
          </p>
        </section>

        {/* Section 2 : Motorisations */}
        <section id="choix-motorisation" style={{ marginBottom: '60px' }}>
          <h2 style={{ fontSize: '1.8rem', color: 'var(--text-primary, #ffffff)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Compass color="#3b82f6" /> 2. Quelle Motorisation Choisir au Maroc en 2026 ?
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', margin: '24px 0' }}>
            <div style={{ background: 'var(--bg-surface, #141f2d)', padding: '24px', borderRadius: '16px', border: '1px solid var(--border-subtle)' }}>
              <h3 style={{ color: '#60a5fa', fontSize: '1.2rem', marginBottom: '8px' }}>⛽ Essence Turbo (TCe, PureTech, TSI)</h3>
              <p style={{ fontSize: '0.95rem' }}>
                Idéal pour les trajets urbains et moins de 15 000 km/an. Prix d'achat inférieur de 15 000 à 30 000 MAD par rapport au Diesel. Vignette économique (350 à 650 MAD).
              </p>
            </div>
            <div style={{ background: 'var(--bg-surface, #141f2d)', padding: '24px', borderRadius: '16px', border: '1px solid var(--border-subtle)' }}>
              <h3 style={{ color: '#34d399', fontSize: '1.2rem', marginBottom: '8px' }}>🛢️ Diesel (dCi, BlueHDi, CRDi)</h3>
              <p style={{ fontSize: '0.95rem' }}>
                Le roi des longs trajets interurbains au Maroc. Consommation minimale (3.8 à 5.0 L/100km). Rentable pour les conducteurs effectuant plus de 20 000 km annuels.
              </p>
            </div>
            <div style={{ background: 'var(--bg-surface, #141f2d)', padding: '24px', borderRadius: '16px', border: '1px solid var(--border-subtle)' }}>
              <h3 style={{ color: '#fbbf24', fontSize: '1.2rem', marginBottom: '8px' }}>⚡ Hybride &amp; Électrique</h3>
              <p style={{ fontSize: '0.95rem' }}>
                Le segment à plus forte croissance. Exonération totale de taxe de luxe, vignette réduite, silence de fonctionnement et conso record sous 4.5 L/100km en ville.
              </p>
            </div>
          </div>
        </section>

        {/* Section 3 : Comparatifs Phares du Marché */}
        <section style={{ marginBottom: '60px' }}>
          <h2 style={{ fontSize: '1.8rem', color: 'var(--text-primary, #ffffff)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <TrendingUp color="#a855f7" /> 3. Comparatifs Directs les Plus Consultés
          </h2>
          <p>
            Comparez côte à côte les prix clés en main, les motorisations réelles et les volumes de coffre des modèles les plus vendus au Maroc :
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', margin: '24px 0' }}>
            {(hubData?.popular_comparisons || [
              { slug: "dacia-duster-vs-renault-captur", title: "Dacia Duster vs Renault Captur" },
              { slug: "dacia-sandero-streetway-vs-renault-clio", title: "Dacia Sandero vs Renault Clio" },
              { slug: "hyundai-tucson-vs-kia-sportage", title: "Hyundai Tucson vs Kia Sportage" },
              { slug: "peugeot-208-vs-renault-clio", title: "Peugeot 208 vs Renault Clio" },
            ]).map((comp) => (
              <Link
                key={comp.slug}
                to={`/comparer/${comp.slug}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  background: 'var(--bg-surface, #141f2d)',
                  padding: '18px 20px',
                  borderRadius: '12px',
                  border: '1px solid var(--border-subtle)',
                  color: '#ffffff',
                  textDecoration: 'none',
                  fontWeight: 600,
                  transition: 'all 0.2s ease'
                }}
              >
                <span>{comp.title}</span>
                <ArrowRight size={18} color="#d4a017" />
              </Link>
            ))}
          </div>
        </section>

        {/* Section 4 : Réseau & Garanties par Ville */}
        <section id="garanties-reseau" style={{ marginBottom: '60px' }}>
          <h2 style={{ fontSize: '1.8rem', color: 'var(--text-primary, #ffffff)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <MapPin color="#ef4444" /> 4. Réseau des Concessionnaires Agréés par Ville
          </h2>
          <p>
            Wakala centralise les stocks neufs des importateurs officiels (Renault Commerce Maroc, Auto Hall, CAC, SMEIA, Sopriam...). Découvrez les showrooms certifiés par ville :
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', margin: '20px 0' }}>
            {[
              { slug: 'casablanca', name: 'Casablanca' },
              { slug: 'rabat', name: 'Rabat' },
              { slug: 'marrakech', name: 'Marrakech' },
              { slug: 'tanger', name: 'Tanger' },
              { slug: 'agadir', name: 'Agadir' },
              { slug: 'fes', name: 'Fès' },
              { slug: 'meknes', name: 'Meknès' },
              { slug: 'kenitra', name: 'Kénitra' },
              { slug: 'tetouan', name: 'Tétouan' },
              { slug: 'oujda', name: 'Oujda' },
            ].map((city) => (
              <Link
                key={city.slug}
                to={`/voitures-neuves/${city.slug}`}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 16px',
                  background: 'rgba(255, 255, 255, 0.06)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '20px',
                  color: '#e2e8f0',
                  textDecoration: 'none',
                  fontSize: '0.9rem'
                }}
              >
                <MapPin size={14} color="#d4a017" />
                {city.name}
              </Link>
            ))}
          </div>
        </section>

        {/* Section 5 : Modèles Neufs Réels en Vedette */}
        {hubData?.featured_models && hubData.featured_models.length > 0 && (
          <section style={{ marginBottom: '60px' }}>
            <h2 style={{ fontSize: '1.8rem', color: 'var(--text-primary, #ffffff)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Car color="#d4a017" /> 5. Fiches Modèles Populaires Disponibles Immédiatement
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', margin: '24px 0' }}>
              {hubData.featured_models.slice(0, 4).map((m) => (
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
                    transition: 'transform 0.2s ease'
                  }}
                >
                  <div style={{ height: '180px', background: '#0a1118', overflow: 'hidden' }}>
                    <img
                      src={m.hero_image_url || resolveVehicleImage(m.brand_name, m.name)}
                      alt={`${m.brand_name} ${m.name}`}
                      style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      onError={(e) => {
                        (e.currentTarget as HTMLImageElement).src = resolveVehicleImage(m.brand_name, m.name);
                      }}
                    />
                  </div>
                  <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div>
                      <span style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{m.brand_name}</span>
                      <h3 style={{ fontSize: '1.2rem', color: '#ffffff', margin: '4px 0 12px' }}>{m.name}</h3>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                      <div>
                        <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block' }}>À partir de</span>
                        <strong style={{ color: '#d4a017', fontSize: '1.1rem' }}>{m.starting_price_mad.toLocaleString('fr-FR')} MAD</strong>
                      </div>
                      <span style={{ padding: '6px 12px', background: 'rgba(212, 160, 23, 0.1)', color: '#d4a017', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 600 }}>
                        Fiche technique →
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Section 6 : Conseiller IA */}
        <section style={{ background: 'linear-gradient(135deg, rgba(212, 160, 23, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)', border: '1px solid rgba(212, 160, 23, 0.3)', borderRadius: '20px', padding: '32px', marginBottom: '60px' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '20px', flexWrap: 'wrap' }}>
            <div style={{ background: '#d4a017', color: '#000', padding: '16px', borderRadius: '16px' }}>
              <Sparkles size={32} />
            </div>
            <div style={{ flex: 1, minWidth: '260px' }}>
              <h3 style={{ fontSize: '1.4rem', color: '#ffffff', marginBottom: '8px' }}>Besoin d'un Conseil Personnalisé ?</h3>
              <p style={{ margin: 0, color: '#cbd5e1', fontSize: '1rem' }}>
                Posez vos questions à notre <strong>Conseiller IA Consultatif</strong> (en français ou Darija) : <em>« Quelle citadine automatique choisir pour 180 000 MAD à Casablanca ? »</em>, <em>« Quel SUV hybride consomme le moins ? »</em>. Réponses neutres et factuelles basées sur le catalogue officiel.
              </p>
              <div style={{ marginTop: '20px' }}>
                <Link to="/chat" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '12px 24px', background: '#d4a017', color: '#0f172a', fontWeight: 700, borderRadius: '30px', textDecoration: 'none' }}>
                  Poser ma question au Conseiller IA →
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* Section 7 : FAQ Structurée Interactive */}
        <section style={{ marginBottom: '60px' }}>
          <h2 style={{ fontSize: '1.8rem', color: 'var(--text-primary, #ffffff)', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <HelpCircle color="#d4a017" /> Questions Fréquentes (FAQ Achat Automobile Maroc)
          </h2>
          <div style={{ display: 'grid', gap: '14px' }}>
            {faqs.map((faq, idx) => {
              const isOpen = activeFaq === idx;
              return (
                <div
                  key={idx}
                  style={{
                    background: 'var(--bg-surface, #141f2d)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '12px',
                    overflow: 'hidden',
                    transition: 'border-color 0.2s ease'
                  }}
                >
                  <button
                    onClick={() => setActiveFaq(isOpen ? null : idx)}
                    style={{
                      width: '100%',
                      padding: '18px 20px',
                      background: 'none',
                      border: 'none',
                      color: '#ffffff',
                      fontSize: '1.05rem',
                      fontWeight: 600,
                      textAlign: 'left',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      cursor: 'pointer'
                    }}
                  >
                    <span>{faq.question}</span>
                    <span style={{ color: '#d4a017', fontSize: '1.2rem', marginLeft: '12px' }}>{isOpen ? '−' : '+'}</span>
                  </button>
                  {isOpen && (
                    <div style={{ padding: '0 20px 20px', color: '#cbd5e1', fontSize: '0.95rem', lineHeight: 1.7, borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '12px' }}>
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

export default GuideAchatPage;
