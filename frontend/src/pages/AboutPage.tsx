/**
 * pages/AboutPage.tsx — Page "À propos" de Wakala.
 */

import { motion } from 'framer-motion';
import { Cpu, ShieldCheck, Users, Target, Sparkles, Globe } from 'lucide-react';
import './StaticPages.css';

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, delay: i * 0.1 },
  }),
};

export default function AboutPage() {
  const values = [
    {
      icon: <ShieldCheck size={28} />,
      title: 'Transparence',
      desc: 'Chaque annonce est vérifiée, chaque score est expliqué. Pas de zones grises.',
    },
    {
      icon: <Cpu size={28} />,
      title: 'Innovation',
      desc: "L'intelligence artificielle au service d'une expérience d'achat moderne et fiable.",
    },
    {
      icon: <Users size={28} />,
      title: 'Communauté',
      desc: 'Acheteurs et vendeurs connectés dans un écosystème de confiance.',
    },
    {
      icon: <Target size={28} />,
      title: 'Précision',
      desc: 'Des recommandations personnalisées et des estimations de prix justes.',
    },
    {
      icon: <Sparkles size={28} />,
      title: 'Simplicité',
      desc: "Une interface intuitive qui rend l'achat automobile aussi simple qu'une recherche Google.",
    },
    {
      icon: <Globe size={28} />,
      title: 'Maroc d\'abord',
      desc: 'Conçu spécifiquement pour le marché automobile marocain et ses spécificités.',
    },
  ];

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
          <span className="static-page__tag">À propos</span>
          <h1 className="static-page__hero-title">
            L'automobile, <span className="text-gradient">réinventée</span>.
          </h1>
          <p className="static-page__hero-subtitle">
            Wakala est la première marketplace automobile au Maroc propulsée par
            l'intelligence artificielle. Notre mission : rendre l'achat et la
            vente de véhicules plus transparent, plus intelligent et plus
            accessible.
          </p>
        </motion.div>
      </section>

      {/* Story */}
      <section className="static-page__section">
        <div className="static-page__content">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="static-page__section-title">Notre histoire</h2>
            <div className="static-page__text-block">
              <p>
                Née de la frustration de chercher une voiture au Maroc — entre
                annonces douteuses, prix opaques et manque d'information —
                Wakala a été fondée avec une idée simple : et si l'IA pouvait
                résoudre tout ça ?
              </p>
              <p>
                Aujourd'hui, notre plateforme analyse des milliers d'annonces en
                temps réel, calcule des scores de confiance transparents et
                propose des recommandations personnalisées grâce à nos
                algorithmes de machine learning.
              </p>
              <p>
                Du calculateur de douane intégré au chatbot expert, chaque
                fonctionnalité est pensée pour le marché marocain et ses
                spécificités.
              </p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Values */}
      <section className="static-page__section static-page__section--alt">
        <div className="static-page__content">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="static-page__section-title">Nos valeurs</h2>
          </motion.div>
          <div className="static-page__grid">
            {values.map((v, i) => (
              <motion.div
                key={v.title}
                className="static-page__value-card"
                custom={i}
                variants={fadeUp}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true }}
              >
                <div className="static-page__value-icon">{v.icon}</div>
                <h3>{v.title}</h3>
                <p>{v.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="static-page__section">
        <div className="static-page__content">
          <motion.div
            className="static-page__stats"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            {[
              { value: '10 000+', label: 'Véhicules analysés' },
              { value: '98%', label: 'Précision IA' },
              { value: '24/7', label: 'Assistant disponible' },
              { value: '100%', label: 'Gratuit' },
            ].map((s) => (
              <div key={s.label} className="static-page__stat">
                <div className="static-page__stat-value">{s.value}</div>
                <div className="static-page__stat-label">{s.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>
    </div>
  );
}
