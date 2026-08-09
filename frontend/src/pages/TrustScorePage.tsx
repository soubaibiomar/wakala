/**
 * pages/TrustScorePage.tsx — Page explicative du score de confiance.
 */

import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  Camera,
  DollarSign,
  FileText,
  User,
  Clock,
  MapPin,
  Award,
  BarChart3,
} from 'lucide-react';
import './StaticPages.css';

const criteria = [
  {
    icon: <DollarSign size={24} />,
    title: 'Cohérence du prix',
    desc: "Le prix est-il aligné avec le marché pour ce modèle, cette année et ce kilométrage ? Notre IA compare avec des milliers d'annonces.",
    weight: 25,
  },
  {
    icon: <Camera size={24} />,
    title: 'Qualité des photos',
    desc: "Nombre de photos, résolution, diversité des angles. Plus il y a de photos de qualité, plus l'annonce est fiable.",
    weight: 15,
  },
  {
    icon: <FileText size={24} />,
    title: 'Complétude de l\'annonce',
    desc: "Description détaillée, spécifications techniques renseignées, équipements listés. Une annonce complète inspire confiance.",
    weight: 15,
  },
  {
    icon: <User size={24} />,
    title: 'Profil vendeur',
    desc: "Ancienneté du compte, nombre d'annonces, taux de réponse et historique de transactions réussies.",
    weight: 15,
  },
  {
    icon: <Clock size={24} />,
    title: 'Fraîcheur de l\'annonce',
    desc: "Les annonces récentes et régulièrement mises à jour sont mieux notées que les annonces dormantes.",
    weight: 10,
  },
  {
    icon: <MapPin size={24} />,
    title: 'Localisation vérifiée',
    desc: "La localisation du véhicule est-elle cohérente ? Les annonces avec une ville précise sont mieux notées.",
    weight: 5,
  },
  {
    icon: <BarChart3 size={24} />,
    title: 'Kilométrage vs. Âge',
    desc: "Le kilométrage annoncé est-il réaliste par rapport à l'année du véhicule ? Les incohérences font baisser le score.",
    weight: 10,
  },
  {
    icon: <Award size={24} />,
    title: 'Détection d\'anomalies',
    desc: "Notre IA détecte les signaux d'alerte : prix trop bas, descriptions copiées, photos réutilisées.",
    weight: 5,
  },
];

export default function TrustScorePage() {
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
          <span className="static-page__tag">Transparence</span>
          <h1 className="static-page__hero-title">
            Score de <span className="text-gradient">confiance</span>
          </h1>
          <p className="static-page__hero-subtitle">
            Chaque annonce sur Wakala reçoit un score de confiance de 0 à 100,
            calculé automatiquement par notre IA. Voici comment ça fonctionne.
          </p>
        </motion.div>
      </section>

      {/* How it works */}
      <section className="static-page__section">
        <div className="static-page__content">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="static-page__section-title">8 critères, 1 score transparent</h2>
            <p style={{ color: 'var(--color-text-secondary)', maxWidth: 600, marginBottom: '2.5rem' }}>
              Notre algorithme évalue chaque annonce sur 8 critères pondérés.
              Le score final est une moyenne pondérée, affichée directement sur chaque fiche véhicule.
            </p>
          </motion.div>

          <div className="trust-score__grid">
            {criteria.map((c, i) => (
              <motion.div
                key={c.title}
                className="trust-score__card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.07 }}
              >
                <div className="trust-score__card-header">
                  <div className="trust-score__card-icon">{c.icon}</div>
                  <span className="trust-score__card-weight">{c.weight}%</span>
                </div>
                <h3>{c.title}</h3>
                <p>{c.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Score ranges */}
      <section className="static-page__section static-page__section--alt">
        <div className="static-page__content">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="static-page__section-title">Interprétation du score</h2>
          </motion.div>
          <div className="trust-score__ranges">
            {[
              { range: '80 – 100', label: 'Excellent', color: '#10b981', desc: 'Annonce très fiable, vendeur vérifié, prix cohérent.' },
              { range: '60 – 79', label: 'Bon', color: '#3b82f6', desc: 'Annonce correcte avec quelques éléments à vérifier.' },
              { range: '40 – 59', label: 'Moyen', color: '#f59e0b', desc: 'Des points d\'attention — vérifiez les détails avant de contacter.' },
              { range: '0 – 39', label: 'Attention', color: '#ef4444', desc: 'Plusieurs signaux d\'alerte détectés — prudence recommandée.' },
            ].map((r, i) => (
              <motion.div
                key={r.range}
                className="trust-score__range"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
              >
                <div className="trust-score__range-bar" style={{ background: r.color }} />
                <div className="trust-score__range-info">
                  <div className="trust-score__range-header">
                    <strong>{r.range}</strong>
                    <span style={{ color: r.color, fontWeight: 600 }}>{r.label}</span>
                  </div>
                  <p>{r.desc}</p>
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
            <h2 className="static-page__section-title">Voyez-le en action</h2>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem', maxWidth: 500, margin: '0 auto 2rem' }}>
              Parcourez le catalogue et consultez le score de confiance sur chaque annonce.
            </p>
            <Link to="/catalogue" className="btn btn--primary btn--lg">
              Explorer le catalogue →
            </Link>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
