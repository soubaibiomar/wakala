/**
 * pages/TechnologyPage.tsx — Page "IA & Big Data" / technologie de Wakala.
 */

import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  Brain,
  Database,
  ShieldCheck,
  Zap,
  MessageSquare,
  BarChart3,
  Network,
  Search,
} from 'lucide-react';
import './StaticPages.css';

const modules = [
  {
    icon: <Search size={28} />,
    title: 'NLP Search Engine',
    desc: "Notre moteur de recherche en langage naturel comprend des requêtes comme \"SUV familial diesel\" et les traduit en filtres techniques précis grâce à un pipeline NLP avancé.",
    tags: ['NLP', 'LLM', 'Extraction sémantique'],
    accent: 'var(--color-accent-gold)',
  },
  {
    icon: <Brain size={28} />,
    title: 'Recommandation hybride',
    desc: "Un système de recommandation combinant filtrage collaboratif et content-based filtering. Il apprend de vos recherches pour proposer des véhicules pertinents.",
    tags: ['ML', 'Content-based', 'Collaboratif'],
    accent: '#6366f1',
  },
  {
    icon: <ShieldCheck size={28} />,
    title: 'Score de confiance',
    desc: "Chaque annonce est évaluée sur 8 critères pondérés : cohérence du prix, qualité photos, historique vendeur, complétude des informations, etc.",
    tags: ['Scoring', 'Détection anomalies', 'Pondération'],
    accent: '#10b981',
  },
  {
    icon: <BarChart3 size={28} />,
    title: 'Argus intelligent',
    desc: "Notre moteur d'estimation de prix analyse le marché en temps réel pour déterminer si un prix est bon, correct ou surévalué par rapport aux véhicules similaires.",
    tags: ['Régression', 'Analyse marché', 'Prix dynamique'],
    accent: '#ec4899',
  },
  {
    icon: <MessageSquare size={28} />,
    title: 'Chatbot expert',
    desc: "Un assistant conversationnel connecté à l'intégralité du catalogue. Il comprend le contexte, pose des questions de clarification et propose des résultats pertinents.",
    tags: ['Chatbot', 'RAG', 'Conversation'],
    accent: '#f59e0b',
  },
  {
    icon: <Network size={28} />,
    title: 'Véhicules similaires',
    desc: "Un algorithme de similarité multi-dimensionnelle identifie automatiquement les véhicules comparables en se basant sur les spécifications techniques, le prix et le segment.",
    tags: ['Similarité', 'KNN', 'Feature engineering'],
    accent: '#8b5cf6',
  },
];

const techStack = [
  { name: 'Python / FastAPI', desc: 'Backend haute performance' },
  { name: 'React / TypeScript', desc: 'Interface utilisateur réactive' },
  { name: 'PostgreSQL', desc: 'Base de données relationnelle' },
  { name: 'Scikit-learn', desc: 'Machine Learning' },
  { name: 'Framer Motion', desc: 'Animations fluides' },
  { name: 'LLM Pipeline', desc: 'Extraction d\'entités NLP' },
];

export default function TechnologyPage() {
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
          <span className="static-page__tag">Technologie</span>
          <h1 className="static-page__hero-title">
            IA & <span className="text-gradient">Big Data</span>
          </h1>
          <p className="static-page__hero-subtitle">
            Découvrez les technologies qui propulsent Wakala — du machine
            learning au traitement du langage naturel, chaque module est conçu
            pour vous offrir la meilleure expérience d'achat automobile.
          </p>
        </motion.div>
      </section>

      {/* Modules IA */}
      <section className="static-page__section">
        <div className="static-page__content">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="static-page__section-title">Nos modules d'intelligence artificielle</h2>
          </motion.div>
          <div className="tech-modules__grid">
            {modules.map((m, i) => (
              <motion.div
                key={m.title}
                className="tech-modules__card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
                style={{ '--module-accent': m.accent } as React.CSSProperties}
              >
                <div className="tech-modules__card-icon">{m.icon}</div>
                <h3>{m.title}</h3>
                <p>{m.desc}</p>
                <div className="tech-modules__tags">
                  {m.tags.map((t) => (
                    <span key={t} className="tech-modules__tag">{t}</span>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="static-page__section static-page__section--alt">
        <div className="static-page__content">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="static-page__section-title">Stack technique</h2>
          </motion.div>
          <div className="tech-stack__grid">
            {techStack.map((t, i) => (
              <motion.div
                key={t.name}
                className="tech-stack__item"
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.06 }}
              >
                <Database size={20} style={{ color: 'var(--color-accent-gold)', flexShrink: 0 }} />
                <div>
                  <strong>{t.name}</strong>
                  <span>{t.desc}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="static-page__section">
        <div className="static-page__content" style={{ textAlign: 'center' }}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="static-page__section-title">Explorez l'API</h2>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem', maxWidth: 500, margin: '0 auto 2rem' }}>
              Développeur ? Consultez notre documentation API interactive pour intégrer Wakala dans vos projets.
            </p>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="btn btn--primary btn--lg"
            >
              Voir la documentation API →
            </a>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
