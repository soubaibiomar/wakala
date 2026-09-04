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
import { CATALOGUE_IMAGE_FALLBACK, resolveVehicleImage } from '../utils/vehicleImageResolver';

import HeroCar from '../components/hero/HeroCar';
import './Home.css';



// ═══════════════════════════════════════════════════════════════
// Featured Vehicles — appels API réels
// ═══════════════════════════════════════════════════════════════

interface CarSectionProps {
  id: string;
  tag: string;
  title: string;
  subtitle?: string;
  fetchParams: {
    page_size: number;
    sort_by: string;
    sort_order: 'asc' | 'desc';
    condition?: 'neuf';  // PIVOT: occasion removed
  };
  emptyMessage: string;
}

const HOME_BUDGET_OPTIONS = [
  { label: 'Moins de 150 000 MAD', max: 150000, brand: 'Dacia', model: 'Sandero' },
  { label: 'Moins de 250 000 MAD', max: 250000, brand: 'Renault', model: 'Clio' },
  { label: 'Moins de 350 000 MAD', max: 350000, brand: 'Peugeot', model: '208' },
  { label: 'Moins de 500 000 MAD', max: 500000, brand: 'Toyota', model: 'Corolla' },
  { label: 'Moins de 750 000 MAD', max: 750000, brand: 'BMW', model: 'X3' },
  { label: 'Tous les budgets', max: null, brand: 'Aston Martin', model: 'DB12' },
];

function HomeBudgetBrowser() {
  return (
    <section className="home-budget-browser" aria-labelledby="home-budget-title">
      <div className="home-budget-browser__heading">
        <span>EXPLORER LE CATALOGUE</span>
        <h2 id="home-budget-title">Parcourir par budget</h2>
      </div>
      <div className="home-budget-browser__grid">
        {HOME_BUDGET_OPTIONS.map((option) => (
          <Link
            key={option.label}
            className="home-budget-browser__card"
            to={option.max ? `/catalogue?price_max=${option.max}` : '/catalogue'}
          >
            <span className="home-budget-browser__image">
              <img
                src={resolveVehicleImage(option.brand, option.model)}
                alt=""
                aria-hidden="true"
                onError={(event) => {
                  event.currentTarget.onerror = null;
                  event.currentTarget.src = CATALOGUE_IMAGE_FALLBACK;
                }}
              />
            </span>
            <span>{option.label}</span>
          </Link>
        ))}
      </div>
    </section>
  );
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
            {subtitle && (
              <p className="home-featured__subtitle">
                {subtitle}
              </p>
            )}
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
      <HomeBudgetBrowser />

      <BrandsSection />
      {/* PIVOT: Replaced "Véhicules d'Occasion" with "Véhicules Neufs" */}
      <CarSection
        id="new-vehicles"
        tag="Neufs"
        title="Véhicules Neufs"
        fetchParams={{ page_size: 15, sort_by: 'created_at', sort_order: 'desc' }}
        emptyMessage="Aucun véhicule neuf disponible."
      />
    </>
  );
}
