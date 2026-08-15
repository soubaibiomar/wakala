/**
 * pages/Home.tsx — Page d'accueil.
 *
 * Sections :
 *   1. Hero (composant existant, connecté à la recherche réelle)
 *   2. Véhicules populaires (vehicleService.getVehicles sort=recent)
 *   3. Points forts IA (6 modules)
 */

import { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, Cpu, ShieldCheck, MessageSquare, LineChart, Network } from 'lucide-react';
import { vehicleService } from '../services/vehicleService';
import type { Vehicle } from '../types/vehicle';
import VehicleCard from '../components/vehicle-card/VehicleCard';
import { POPULAR_BRANDS } from '../constants/brands';

import HeroCar from '../components/hero/HeroCar';
import HeroIntro from '../components/hero/HeroIntro';
import './Home.css';



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
    condition?: 'neuf';  // PIVOT: occasion removed
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
        setVehicles(res.items.slice(0, 6)); // Show top 6
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
    {
      icon: <Search size={22} />,
      title: 'Trouvez en un mot',
      desc: 'Dites simplement ce que vous cherchez — « SUV familial diesel » — et on s\'occupe du reste.',
      accent: 'var(--color-accent-gold)',
    },
    {
      icon: <Cpu size={22} />,
      title: 'Des suggestions sur mesure',
      desc: 'Plus vous cherchez, mieux on vous connaît. Nos recommandations s\'adaptent à vos goûts et votre budget.',
      accent: '#6366f1',
    },
    {
      icon: <ShieldCheck size={22} />,
      title: 'Annonces vérifiées',
      desc: 'Chaque annonce est passée au crible : photos, prix, historique du vendeur. Fini les mauvaises surprises.',
      accent: '#10b981',
    },
    {
      icon: <MessageSquare size={22} />,
      title: 'Un expert à vos côtés',
      desc: 'Notre assistant connaît tout le catalogue. Posez-lui vos questions, il vous guide comme un ami.',
      accent: '#f59e0b',
    },
    {
      icon: <LineChart size={22} />,
      title: 'Le juste prix, garanti',
      desc: 'Notre IA analyse le marché en temps réel pour vous dire si le prix affiché est bon — ou pas.',
      accent: '#ec4899',
    },
    {
      icon: <Network size={22} />,
      title: 'Comparez facilement',
      desc: 'On identifie automatiquement les voitures similaires pour que vous puissiez comparer en un coup d\'œil.',
      accent: '#8b5cf6',
    },
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
          <span className="home-features__tag">Pourquoi nous choisir</span>
          <h2 className="home-features__title">
            Acheter une voiture, <span className="text-gradient">simplifié</span>.
          </h2>
          <p className="home-features__subtitle">
            Tout ce qu'il faut pour trouver la bonne voiture, au bon prix, en toute confiance.
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
              style={{ '--feature-accent': f.accent } as React.CSSProperties}
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
              <Link to={`/marque/${encodeURIComponent(brandObj.name)}`} className="home-brands__card">
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
  const [introDone, setIntroDone] = useState(() => {
    return sessionStorage.getItem('wakala_intro_seen') === 'true';
  });
  const handleIntroComplete = useCallback(() => {
    sessionStorage.setItem('wakala_intro_seen', 'true');
    setIntroDone(true);
  }, []);

  return (
    <>
      {!introDone && <HeroIntro onComplete={handleIntroComplete} />}
      {introDone && (
        <>
          <HeroCar />

          <BrandsSection />
          {/* PIVOT: Replaced "Véhicules d'Occasion" with "Véhicules Neufs" */}
          <CarSection
            id="new-vehicles"
            tag="Neufs"
            title="Véhicules Neufs"
            subtitle="Derniers modèles neufs ajoutés, analysés par notre IA."
            fetchParams={{ page_size: 15, sort_by: 'created_at', sort_order: 'desc' }}
            emptyMessage="Aucun véhicule neuf disponible."
          />
          <FeaturesSection />
        </>
      )}
    </>
  );
}
