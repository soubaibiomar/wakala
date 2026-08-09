/**
 * pages/HowItWorksPage.tsx — Page "Comment ça marche" de Wakala.
 */

import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Search, Cpu, ShieldCheck, MessageSquare, Calculator, TrendingUp } from 'lucide-react';
import './StaticPages.css';

const steps = [
  {
    number: '01',
    icon: <Search size={32} />,
    title: 'Recherchez naturellement',
    desc: 'Tapez ce que vous cherchez comme vous le diriez à un ami : "SUV familial diesel moins de 200 000 DH". Notre moteur NLP comprend votre demande et vous propose les meilleures correspondances.',
    accent: 'var(--color-accent-gold)',
  },
  {
    number: '02',
    icon: <ShieldCheck size={32} />,
    title: 'Consultez le score de confiance',
    desc: "Chaque annonce est analysée par notre IA : cohérence du prix, qualité des photos, historique du vendeur. Un score transparent de 0 à 100 vous aide à repérer les bonnes affaires.",
    accent: '#10b981',
  },
  {
    number: '03',
    icon: <Cpu size={32} />,
    title: 'Recevez des recommandations',
    desc: "Plus vous naviguez, mieux notre système vous connaît. Nous vous proposons des véhicules qui correspondent à votre style, votre budget et vos préférences réelles.",
    accent: '#6366f1',
  },
  {
    number: '04',
    icon: <MessageSquare size={32} />,
    title: 'Discutez avec notre assistant',
    desc: "Pas envie de chercher ? Notre chatbot expert connaît tout le catalogue. Posez-lui vos questions et il vous guide vers la voiture idéale.",
    accent: '#f59e0b',
  },
  {
    number: '05',
    icon: <Calculator size={32} />,
    title: 'Calculez les frais de douane',
    desc: "Vous importez ? Notre calculateur intégré estime instantanément les droits de douane, la TVA et les taxes pour n'importe quel véhicule.",
    accent: '#ec4899',
  },
  {
    number: '06',
    icon: <TrendingUp size={32} />,
    title: 'Comparez et décidez',
    desc: "Ajoutez jusqu'à 3 véhicules au comparateur pour analyser les spécifications, les prix et les scores côte à côte. Prenez votre décision en toute confiance.",
    accent: '#8b5cf6',
  },
];

export default function HowItWorksPage() {
  return (
    <div className="static-page">
      {/* Hero */}
      <section className="static-page__hero">
        <motion.div
          className="static-page__hero-inner"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <span className="static-page__tag">Guide</span>
          <h1 className="static-page__hero-title">
            Comment ça <span className="text-gradient">marche</span> ?
          </h1>
          <p className="static-page__hero-subtitle">
            De la recherche à la décision, Wakala vous accompagne à chaque étape
            grâce à l'intelligence artificielle.
          </p>
        </motion.div>
      </section>

      {/* Steps */}
      <section className="static-page__section">
        <div className="static-page__content">
          <div className="how-it-works__steps">
            {steps.map((step, i) => (
              <motion.div
                key={step.number}
                className="how-it-works__step"
                initial={{ opacity: 0, x: i % 2 === 0 ? -30 : 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div
                  className="how-it-works__step-number"
                  style={{ background: step.accent }}
                >
                  {step.number}
                </div>
                <div className="how-it-works__step-content">
                  <div className="how-it-works__step-icon" style={{ color: step.accent }}>
                    {step.icon}
                  </div>
                  <h3>{step.title}</h3>
                  <p>{step.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="static-page__section static-page__section--alt">
        <div className="static-page__content" style={{ textAlign: 'center' }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="static-page__section-title">Prêt à essayer ?</h2>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem', maxWidth: 500, margin: '0 auto 2rem' }}>
              Commencez votre recherche dès maintenant — c'est gratuit, rapide et intelligent.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Link to="/catalogue" className="btn btn--primary btn--lg">
                Explorer le catalogue →
              </Link>
              <Link to="/chat" className="btn btn--outline btn--lg">
                Parler à l'assistant
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
