import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  CreditCard,
  CheckCircle2,
  HelpCircle,
  Calculator,
  ShieldCheck,
  Building,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Car,
  FileCheck,
  BadgePercent
} from 'lucide-react';
import PageMeta from '../components/seo/PageMeta';
import FAQStructuredData from '../components/seo/FAQStructuredData';
import BreadcrumbStructuredData from '../components/seo/BreadcrumbStructuredData';
import seoService, { SeoHubData } from '../services/seoService';
import './StaticPages.css';

export const FinancementPage: React.FC = () => {
  const [hubData, setHubData] = useState<SeoHubData | null>(null);
  const [activeFaq, setActiveFaq] = useState<number | null>(null);

  // Mini simulateur interactif
  const [vehiclePrice, setVehiclePrice] = useState<number>(200000);
  const [downPaymentPercent, setDownPaymentPercent] = useState<number>(20);
  const [durationMonths, setDurationMonths] = useState<number>(48);

  useEffect(() => {
    seoService.getHubData().then(setHubData).catch(console.warn);
  }, []);

  const downPaymentMad = (vehiclePrice * downPaymentPercent) / 100;
  const loanAmountMad = vehiclePrice - downPaymentMad;
  const monthlyRate = 0.055 / 12; // 5.5% TEG annuel indicatif
  const monthlyPaymentMad = Math.round(
    (loanAmountMad * monthlyRate) / (1 - Math.pow(1 + monthlyRate, -durationMonths))
  );

  const breadcrumbs = [
    { name: 'Accueil', item: 'https://wakala.ma/' },
    { name: "Guide d'Achat", item: 'https://wakala.ma/guide-achat-voiture-maroc' },
    { name: "Financement Auto Maroc (Crédit & Mourabaha)", item: 'https://wakala.ma/financement-auto-maroc' },
  ];

  const faqs = [
    {
      question: "Quelle est la différence entre le crédit auto classique et la Mourabaha au Maroc ?",
      answer: "Le crédit auto classique est un prêt bancaire avec intérêts calculés selon un taux effectif global (TEG). La Mourabaha est un contrat de vente participatif (banque islamique agréée Bank Al-Maghrib) où la banque achète le véhicule et le revend au client avec une marge bénéficiaire fixe et convenue à l'avance, sans pénalités de retard usuraires."
    },
    {
      question: "Quel est l'apport personnel recommandé pour acheter une voiture neuve au Maroc ?",
      answer: "Un apport personnel de 15% à 20% du prix clé en main est généralement recommandé pour obtenir un accord bancaire rapide et réduire les mensualités. Certains concessionnaires et organismes proposent toutefois des formules sans apport (0% d'apport) sous réserve de solvabilité."
    },
    {
      question: "Quelles sont les pièces justificatives exigées pour un financement auto ?",
      answer: "Pour les salariés : copie CIN, 3 derniers bulletins de paie, 3 derniers relevés bancaires, attestation de travail récente et quittance d'électricité/eau. Pour les professions libérales et commerçants : registre de commerce, modèle J, bilans fiscaux et relevés bancaires professionnels sur 6 à 12 mois."
    },
    {
      question: "Quelle est la durée maximale d'un crédit automobile au Maroc ?",
      answer: "La durée de remboursement s'étale généralement de 12 à 84 mois (7 ans). Une durée de 48 à 60 mois constitue le point d'équilibre optimal entre mensualités modérées et coût global du financement."
    }
  ];

  return (
    <div className="static-page financement-page" style={{ paddingBottom: '80px' }}>
      <PageMeta
        title="Financement Auto Maroc 2026 : Simulateur Crédit, Mourabaha & LOA | Wakala"
        description="Guide et simulateur officiel du financement automobile neuf au Maroc. Comparez le crédit auto classique, la Mourabaha participative et la LOA avec calcul des mensualités en MAD."
        canonicalUrl="https://wakala.ma/financement-auto-maroc"
        ogType="article"
      />
      <BreadcrumbStructuredData items={breadcrumbs} />
      <FAQStructuredData faqs={faqs} />

      {/* Hero Financement */}
      <section style={{ background: 'linear-gradient(135deg, #0a1118 0%, #0e1e32 60%, #152d4c 100%)', padding: '60px 20px', borderBottom: '1px solid var(--border-subtle)' }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
          
          <nav style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '20px' }}>
            <Link to="/" style={{ color: '#94a3b8', textDecoration: 'none' }}>Accueil</Link>
            <span>/</span>
            <Link to="/guide-achat-voiture-maroc" style={{ color: '#94a3b8', textDecoration: 'none' }}>Guide d'Achat</Link>
            <span>/</span>
            <span style={{ color: '#d4a017' }}>Financement Auto</span>
          </nav>

          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '6px 14px', background: 'rgba(212, 160, 23, 0.15)', border: '1px solid rgba(212, 160, 23, 0.4)', borderRadius: '30px', color: '#d4a017', fontSize: '0.85rem', fontWeight: 600, marginBottom: '20px' }}>
            <BadgePercent size={16} /> Guide Pratique &amp; Simulateur • 2026
          </div>

          <h1 style={{ fontSize: 'clamp(2rem, 4vw, 3.2rem)', color: '#ffffff', fontWeight: 800, lineHeight: 1.2, marginBottom: '20px' }}>
            Financer sa Voiture Neuve au Maroc : Crédit, Mourabaha &amp; LOA
          </h1>

          {/* GEO Self-Contained Answer */}
          <div style={{ background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255, 255, 255, 0.12)', borderRadius: '14px', padding: '24px', color: '#e2e8f0', fontSize: '1.05rem', lineHeight: 1.7 }}>
            <p style={{ margin: 0 }}>
              <strong>L'essentiel du financement au Maroc :</strong> Les acheteurs de véhicules neufs ont le choix entre le <em>crédit auto conventionnel</em> (taux fixe ~5.5% TEG), la <em>Mourabaha islamique</em> (banques participatives, marge fixe sans intérêts usuraires) et la <em>LOA/LLD</em>. Pour un véhicule à 200 000 MAD avec 20% d'apport sur 48 mois, la mensualité moyenne s'établit à environ 3 720 MAD/mois.
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main style={{ maxWidth: '1100px', margin: '40px auto 0', padding: '0 20px' }}>

        {/* Simulateur Rapide Interactif */}
        <section style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '20px', border: '1px solid var(--border-subtle)', padding: '32px', marginBottom: '50px' }}>
          <h2 style={{ fontSize: '1.5rem', color: '#fff', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Calculator color="#d4a017" /> Simulateur Indicatif de Mensualités
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px' }}>
            {/* Contrôles */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              <div>
                <label style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.9rem', marginBottom: '8px' }}>
                  <span>Prix du véhicule neuf</span>
                  <strong style={{ color: '#fff' }}>{vehiclePrice.toLocaleString('fr-FR')} MAD</strong>
                </label>
                <input
                  type="range"
                  min={120000}
                  max={600000}
                  step={10000}
                  value={vehiclePrice}
                  onChange={(e) => setVehiclePrice(Number(e.target.value))}
                  style={{ width: '100%', accentColor: '#d4a017' }}
                />
              </div>

              <div>
                <label style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.9rem', marginBottom: '8px' }}>
                  <span>Apport personnel ({downPaymentPercent}%)</span>
                  <strong style={{ color: '#fff' }}>{downPaymentMad.toLocaleString('fr-FR')} MAD</strong>
                </label>
                <input
                  type="range"
                  min={0}
                  max={50}
                  step={5}
                  value={downPaymentPercent}
                  onChange={(e) => setDownPaymentPercent(Number(e.target.value))}
                  style={{ width: '100%', accentColor: '#d4a017' }}
                />
              </div>

              <div>
                <label style={{ display: 'flex', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.9rem', marginBottom: '8px' }}>
                  <span>Durée de remboursement</span>
                  <strong style={{ color: '#fff' }}>{durationMonths} mois ({durationMonths / 12} ans)</strong>
                </label>
                <input
                  type="range"
                  min={24}
                  max={84}
                  step={12}
                  value={durationMonths}
                  onChange={(e) => setDurationMonths(Number(e.target.value))}
                  style={{ width: '100%', accentColor: '#d4a017' }}
                />
              </div>
            </div>

            {/* Résultat Calculé */}
            <div style={{ background: 'rgba(212, 160, 23, 0.08)', border: '1px solid rgba(212, 160, 23, 0.3)', borderRadius: '16px', padding: '24px', display: 'flex', flexDirection: 'column', justifyContent: 'center', textAlign: 'center' }}>
              <span style={{ fontSize: '0.9rem', color: '#94a3b8' }}>Mensualité estimée (Crédit / Mourabaha)</span>
              <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#d4a017', margin: '10px 0' }}>
                ~{monthlyPaymentMad.toLocaleString('fr-FR')} <span style={{ fontSize: '1.2rem' }}>MAD/mois</span>
              </div>
              <p style={{ fontSize: '0.8rem', color: '#64748b', margin: '0 0 16px' }}>
                Montant financé : {loanAmountMad.toLocaleString('fr-FR')} MAD • Base TEG indicatif 5.5%
              </p>
              <Link to="/catalogue" style={{ padding: '10px 20px', background: '#d4a017', color: '#0f172a', fontWeight: 700, borderRadius: '24px', textDecoration: 'none', fontSize: '0.9rem' }}>
                Trouver un véhicule dans ce budget →
              </Link>
            </div>
          </div>
        </section>

        {/* Section Comparatif des Modes de Financement */}
        <section style={{ marginBottom: '50px' }}>
          <h2 style={{ fontSize: '1.6rem', color: '#fff', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <CreditCard color="#60a5fa" /> Les 3 Formules de Financement au Maroc
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
            {/* Crédit classique */}
            <div style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '16px', border: '1px solid var(--border-subtle)', padding: '24px' }}>
              <h3 style={{ color: '#60a5fa', fontSize: '1.2rem', marginBottom: '10px' }}>1. Crédit Auto Bancaire Classique</h3>
              <p style={{ color: '#94a3b8', fontSize: '0.95rem', lineHeight: 1.6 }}>
                Formule la plus répandue au Maroc (Wafasalaf, Eqdom, Salafin, Sofac, RCI Finance). Vous êtes propriétaire immédiat du véhicule avec gage au profit de l'organisme prêteur.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, margin: '16px 0 0', display: 'grid', gap: '8px', fontSize: '0.85rem', color: '#cbd5e1' }}>
                <li>✔ Durée : 12 à 84 mois</li>
                <li>✔ Remboursement par prélèvement bancaire</li>
                <li>✔ Possibilité de remboursement anticipé</li>
              </ul>
            </div>

            {/* Mourabaha */}
            <div style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '16px', border: '1px solid var(--border-subtle)', padding: '24px' }}>
              <h3 style={{ color: '#34d399', fontSize: '1.2rem', marginBottom: '10px' }}>2. Financement Mourabaha (Banques Islamiques)</h3>
              <p style={{ color: '#94a3b8', fontSize: '0.95rem', lineHeight: 1.6 }}>
                Proposé par les banques participatives (Umnia Bank, Bank Assafa, BTI Bank, Al Yousr). Achat du véhicule par la banque puis revente avec marge bénéficiaire fixe et transparente.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, margin: '16px 0 0', display: 'grid', gap: '8px', fontSize: '0.85rem', color: '#cbd5e1' }}>
                <li>✔ 100% conforme Sharia (Conseil Supérieur des Oulémas)</li>
                <li>✔ Prix total et marge connus dès la signature</li>
                <li>✔ Pas de pénalités de retard d'intérêts</li>
              </ul>
            </div>

            {/* LOA / LLD */}
            <div style={{ background: 'var(--bg-surface, #141f2d)', borderRadius: '16px', border: '1px solid var(--border-subtle)', padding: '24px' }}>
              <h3 style={{ color: '#fbbf24', fontSize: '1.2rem', marginBottom: '10px' }}>3. LOA &amp; LLD (Location avec Option d'Achat)</h3>
              <p style={{ color: '#94a3b8', fontSize: '0.95rem', lineHeight: 1.6 }}>
                Location pendant 3 à 5 ans avec entretien et assurance inclus. En fin de contrat, vous pouvez lever l'option d'achat pour devenir propriétaire ou changer pour un modèle neuf.
              </p>
              <ul style={{ listStyle: 'none', padding: 0, margin: '16px 0 0', display: 'grid', gap: '8px', fontSize: '0.85rem', color: '#cbd5e1' }}>
                <li>✔ Entretien, assurance tous risques et assistance intégrés</li>
                <li>✔ Mensualités souvent plus faibles qu'un crédit sec</li>
                <li>✔ Très prisé par les professions libérales et PME</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Section Grille des Budgets types & Liens Véhicules Réels */}
        <section style={{ marginBottom: '50px' }}>
          <h2 style={{ fontSize: '1.6rem', color: '#fff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <TrendingUp color="#d4a017" /> Exemples de Budgets &amp; Modèles Neufs Recommandés
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '18px' }}>
            
            <div style={{ background: 'var(--bg-surface, #141f2d)', padding: '22px', borderRadius: '14px', border: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '0.8rem', color: '#10b981', fontWeight: 700 }}>BUDGET ÉCONOMIQUE</span>
              <h3 style={{ fontSize: '1.2rem', color: '#fff', margin: '6px 0' }}>~ 150 000 MAD</h3>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Mensualité indicative (sur 48 mois avec 20% d'apport) : <strong>~2 750 MAD/mois</strong></p>
              <div style={{ marginTop: '14px' }}>
                <Link to="/marque/dacia" style={{ color: '#d4a017', fontSize: '0.85rem', fontWeight: 600, textDecoration: 'none' }}>
                  Voir Dacia Sandero, Renault Clio →
                </Link>
              </div>
            </div>

            <div style={{ background: 'var(--bg-surface, #141f2d)', padding: '22px', borderRadius: '14px', border: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '0.8rem', color: '#3b82f6', fontWeight: 700 }}>BUDGET FAMILIAL &amp; SUV</span>
              <h3 style={{ fontSize: '1.2rem', color: '#fff', margin: '6px 0' }}>~ 250 000 MAD</h3>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Mensualité indicative (sur 48 mois avec 20% d'apport) : <strong>~4 600 MAD/mois</strong></p>
              <div style={{ marginTop: '14px' }}>
                <Link to="/comparer/dacia-duster-vs-renault-captur" style={{ color: '#d4a017', fontSize: '0.85rem', fontWeight: 600, textDecoration: 'none' }}>
                  Voir Duster vs Captur, Peugeot 2008 →
                </Link>
              </div>
            </div>

            <div style={{ background: 'var(--bg-surface, #141f2d)', padding: '22px', borderRadius: '14px', border: '1px solid var(--border-subtle)' }}>
              <span style={{ fontSize: '0.8rem', color: '#a855f7', fontWeight: 700 }}>BUDGET PREMIUM &amp; HYBRIDE</span>
              <h3 style={{ fontSize: '1.2rem', color: '#fff', margin: '6px 0' }}>~ 400 000 MAD</h3>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Mensualité indicative (sur 48 mois avec 20% d'apport) : <strong>~7 400 MAD/mois</strong></p>
              <div style={{ marginTop: '14px' }}>
                <Link to="/comparer/hyundai-tucson-vs-kia-sportage" style={{ color: '#d4a017', fontSize: '0.85rem', fontWeight: 600, textDecoration: 'none' }}>
                  Voir Tucson vs Sportage, VW Tiguan →
                </Link>
              </div>
            </div>

          </div>
        </section>

        {/* Section FAQ Financement */}
        <section style={{ marginBottom: '60px' }}>
          <h2 style={{ fontSize: '1.5rem', color: '#fff', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <HelpCircle color="#d4a017" /> Questions Fréquentes sur le Financement Automobile au Maroc
          </h2>
          <div style={{ display: 'grid', gap: '12px' }}>
            {faqs.map((faq, idx) => {
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

export default FinancementPage;
