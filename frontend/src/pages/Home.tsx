/**
 * pages/Home.tsx — Page d'accueil.
 *
 * Sections :
 *   1. Hero (composant existant, connecté à la recherche réelle)
 *   2. Statistiques plateforme
 *   3. Véhicules populaires (vehicleService.getVehicles sort=recent)
 *   4. Points forts IA (6 modules)
 */

import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Cpu, ShieldCheck, MessageSquare, LineChart, Network, BarChart3, Target, Zap, Star } from 'lucide-react';
import { vehicleService } from '../services/vehicleService';
import type { Vehicle } from '../types/vehicle';
import VehicleCard from '../components/vehicle-card/VehicleCard';
import { POPULAR_BRANDS } from '../constants/brands';

import HeroCar from '../components/hero/HeroCar';
import HeroIntro from '../components/hero/HeroIntro';
import './Home.css';

// ═══════════════════════════════════════════════════════════════
// Stats Section
// ═══════════════════════════════════════════════════════════════

function StatsSection() {
  const stats = [
    { value: '15 000+', label: 'Véhicules analysés', icon: <BarChart3 size={24} /> },
    { value: '98.5%', label: 'Précision IA', icon: <Target size={24} /> },
    { value: '< 2s', label: 'Temps de recommandation', icon: <Zap size={24} /> },
    { value: '4.8/5', label: 'Satisfaction utilisateur', icon: <Star size={24} /> },
  ];

  return (
    <section className="home-stats">
      <div className="home-stats__inner">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            className="home-stats__item"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
          >
            <span className="home-stats__icon">{s.icon}</span>
            <div className="home-stats__data">
              <span className="home-stats__value">{s.value}</span>
              <span className="home-stats__label">{s.label}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

// ═══════════════════════════════════════════════════════════════
// Featured Vehicles — appels API réels
// ═══════════════════════════════════════════════════════════════

interface CarSectionProps {
  id: string;
  tag: string;
  title: string;
  subtitle: string;
  fetchParams: {
    page_size: number;
    sort_by: string;
    sort_order: 'asc' | 'desc';
    condition?: 'neuf' | 'occasion';
  };
  emptyMessage: string;
}

function CarSection({ id, tag, title, subtitle, fetchParams, emptyMessage }: CarSectionProps) {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    vehicleService
      .getVehicles(fetchParams)
      .then((res) => {
        // If it's used cars (no mileage_max=0), we might get new cars. Let's filter locally if needed.
        let items = res.items;
        if (fetchParams.condition !== 'neuf') {
           const usedItems = items.filter(v => !v.description?.toLowerCase().includes('véhicule neuf officiel'));
           if (usedItems.length > 0) {
             items = usedItems;
           }
        }
        setVehicles(items.slice(0, 6)); // Ensure we only show 6
      })
      .catch((err) => {
        console.error('Erreur chargement véhicules:', err);
        setError('Impossible de charger les véhicules');
      })
      .finally(() => setLoading(false));
  }, [fetchParams]);

  return (
    <section className="home-featured" id={id}>
      <div className="home-featured__inner">
        
        <motion.div
          className="home-featured__header"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <div className="home-featured__header-left">
            <span className="home-featured__tag">{tag}</span>
            <h2 className="home-featured__title">{title}</h2>
            <p className="home-featured__subtitle">
              {subtitle}
            </p>
          </div>
          <Link to="/catalogue" className="home-featured__see-all">
            Voir tout →
          </Link>
        </motion.div>

        {loading ? (
          <div className="home-featured__grid">
            {[1, 2, 3].map((i) => (
              <div key={i} className="home-featured__skeleton" />
            ))}
          </div>
        ) : error ? (
          <div className="home-featured__empty-state">
            <p className="home-featured__empty-icon">⚠️</p>
            <p className="home-featured__empty-msg">{error}</p>
            <p className="home-featured__empty-hint">
              Assurez-vous que le backend est lancé.
            </p>
          </div>
        ) : vehicles.length > 0 ? (
          <div className="home-featured__grid">
            {vehicles.map((v, i) => (
              <motion.div
                key={v.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
              >
                <VehicleCard vehicle={v} animationDelay={i * 0.1} />
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="home-featured__empty-state">
            <p className="home-featured__empty-icon">🚗</p>
            <p className="home-featured__empty-msg">{emptyMessage}</p>
            <p className="home-featured__empty-hint">
              Revenez plus tard pour de nouvelles annonces.
            </p>
          </div>
        )}

        <div className="home-featured__cta-wrap">
          <Link to="/catalogue" className="btn btn--primary btn--lg">
            Voir tout le catalogue →
          </Link>
        </div>
      </div>
    </section>
  );
}

// ═══════════════════════════════════════════════════════════════
// Features Section — présentation des 6 modules IA
// ═══════════════════════════════════════════════════════════════

function FeaturesSection() {
  const features = [
    { icon: <Search size={24} />, title: 'Recherche intelligente', desc: 'Décrivez en langage naturel le véhicule de vos rêves. Notre NLP comprend votre besoin.' },
    { icon: <Cpu size={24} />, title: 'Recommandation IA hybride', desc: 'Algorithmes content-based + collaborative filtering pour des suggestions ultra-pertinentes.' },
    { icon: <ShieldCheck size={24} />, title: 'Score de confiance', desc: 'Chaque annonce est analysée par 5 modules IA : vision, fraude, prix, vendeur, qualité.' },
    { icon: <MessageSquare size={24} />, title: 'Chatbot RAG', desc: 'Un assistant qui connaît tout le catalogue. Posez vos questions en français.' },
    { icon: <LineChart size={24} />, title: 'Estimation de prix', desc: 'XGBoost prédit le juste prix avec intervalle de confiance. Plus de mauvaises surprises.' },
    { icon: <Network size={24} />, title: 'Graphe de similarité', desc: 'Neo4j + PageRank identifient les véhicules similaires et les tendances marché.' },
  ];

  return (
    <section className="home-features" id="features">
      <div className="home-features__inner">
        <motion.div
          className="home-features__header"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <span className="home-features__tag">Technologie</span>
          <h2 className="home-features__title">
            Pourquoi <span className="text-gradient">Wakala</span> ?
          </h2>
          <p className="home-features__subtitle">
            6 modules d'intelligence artificielle au service de votre recherche
          </p>
        </motion.div>

        <div className="home-features__grid">
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              className="home-features__card"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
            >
              <div className="home-features__card-icon">{f.icon}</div>
              <h3 className="home-features__card-title">{f.title}</h3>
              <p className="home-features__card-desc">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ═══════════════════════════════════════════════════════════════
// Section Marques (Fiches Techniques)
// ═══════════════════════════════════════════════════════════════


function BrandsSection() {
  return (
    <section className="home-brands" id="brands-section">
      <div className="home-brands__container">
        <div className="home-brands__header">
          <span className="home-brands__tag">Fiches Techniques & Neuf</span>
          <h2 className="home-brands__title">Catalogue par Marque</h2>
          <p className="home-brands__subtitle">
            Explorez les véhicules neufs et consultez les fiches techniques détaillées de toutes les marques disponibles au Maroc.
          </p>
        </div>
        
        <div className="home-brands__grid">
          {POPULAR_BRANDS.map((brandObj, i) => (
            <motion.div
              key={brandObj.name}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.4, delay: i * 0.05 }}
            >
              <Link to={`/marque/${encodeURIComponent(brandObj.name)}?tab=neuf`} className="home-brands__card">
                <div className="home-brands__card-content">
                  <img src={brandObj.logo} alt={brandObj.name} className="home-brands__card-logo" />
                  <span className="home-brands__card-name">{brandObj.name}</span>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ═══════════════════════════════════════════════════════════════
// Page Home
// ═══════════════════════════════════════════════════════════════

export default function Home() {
  const [introDone, setIntroDone] = useState(false);
  const handleIntroComplete = useCallback(() => setIntroDone(true), []);

  return (
    <>
      {!introDone && <HeroIntro onComplete={handleIntroComplete} />}
      {introDone && (
        <>
          <HeroCar />
          <StatsSection />
          <BrandsSection />
          <CarSection
            id="used-vehicles"
            tag="Occasions"
            title="Véhicules d'Occasion"
            subtitle="Dernières annonces d'occasion ajoutées, analysées par notre IA."
            fetchParams={{ page_size: 15, sort_by: 'created_at', sort_order: 'desc' }}
            emptyMessage="Aucun véhicule d'occasion disponible."
          />
          <FeaturesSection />
        </>
      )}
    </>
  );
}
