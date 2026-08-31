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
// Features Section — Suite d'Outils Intelligents Wakala
// ═══════════════════════════════════════════════════════════════

function FeaturesSection() {
  const tools = [
    {
      tag: 'Taxes & Douane',
      title: 'Simulateur de Dédouanement',
      desc: 'Calculez instantanément les droits de douane, la TVA et la taxe de luxe selon le barème officiel marocain en vigueur.',
      badge: 'Barème 2026',
      link: '/dedouanement',
      linkText: 'Calculer mes frais',
      accent: '#10b981',
    },
    {
      tag: 'Conseil Intelligent',
      title: 'Conseiller IA & Recherche Vocale',
      desc: 'Exprimez vos critères en Darija ou Français. Notre IA diagnostique vos besoins et extrait les fiches certifiées du catalogue.',
      badge: 'Multilingue • Sans Hallucination',
      link: '/chat',
      linkText: 'Consulter l’IA',
      accent: '#f59e0b',
    },
    {
      tag: 'Outil Décisionnel',
      title: 'Comparateur Technique Multicritères',
      desc: 'Mettez en concurrence jusqu’à 4 véhicules côte à côte : consommation réelle, volume de coffre, puissance fiscale et équipements.',
      badge: '+30 Critères Comparés',
      link: '/comparateur',
      linkText: 'Lancer la comparaison',
      accent: '#6366f1',
    },
    {
      tag: 'Valorisation Marché',
      title: 'Argus & Cote Prédictive',
      desc: 'Évaluez la juste valeur marchande de chaque modèle grâce à notre algorithme basé sur l’historique des transactions réelles au Maroc.',
      badge: 'Modèle Machine Learning',
      link: '/catalogue',
      linkText: 'Explorer les cotes',
      accent: '#0ea5e9',
    },
    {
      tag: 'Sécurité & Prévention',
      title: 'Audit & Fiabilité Moteurs',
      desc: 'Identifiez en amont les motorisations et boîtes de vitesses à risque (PureTech, TCe, THP, DSG sèches) avant votre achat.',
      badge: 'Base Pannes Constructeurs',
      link: '/chat?q=Quels+moteurs+eviter+en+occasion',
      linkText: 'Vérifier un moteur',
      accent: '#ec4899',
    },
    {
      tag: 'Catalogue Officiel',
      title: 'Fiches Techniques Constructeurs',
      desc: 'Consultez les caractéristiques officielles, dimensions, finitions, motorisations et tarifs neufs de chaque marque au Maroc.',
      badge: 'Toutes Marques Maroc',
      link: '/marque',
      linkText: 'Consulter les fiches',
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
          <span className="home-features__tag">Suite d'Outils Intelligents</span>
          <h2 className="home-features__title">
            L'Automobile en toute <span className="text-gradient">clarté</span>.
          </h2>
          <p className="home-features__subtitle">
            Des outils interactifs exclusifs pour estimer, comparer, dédouaner et choisir votre véhicule en toute indépendance.
          </p>
        </motion.div>

        <div className="home-features__grid">
          {tools.map((tool, i) => (
            <motion.div
              key={tool.title}
              className="home-features__card"
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.45, delay: i * 0.07 }}
              style={{ '--feature-accent': tool.accent } as React.CSSProperties}
            >
              <div className="home-features__card-top">
                <span className="home-features__card-tag" style={{ color: tool.accent }}>
                  {tool.tag}
                </span>
                <span className="home-features__card-badge">{tool.badge}</span>
              </div>

              <h3 className="home-features__card-title">{tool.title}</h3>
              <p className="home-features__card-desc">{tool.desc}</p>

              <div className="home-features__card-footer">
                <Link to={tool.link} className="home-features__card-link" style={{ color: tool.accent }}>
                  <span>{tool.linkText}</span>
                  <span className="home-features__card-arrow">→</span>
                </Link>
              </div>
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
  return (
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
  );
}
