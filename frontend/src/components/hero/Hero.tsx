import { useCallback } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import type { RecommendationResponse } from '../../services/recommendationService';
import SearchBar from './SearchBar';
import './Hero.css';

export default function Hero() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const handleResults = useCallback((query: string, recommendations: RecommendationResponse) => {
    navigate(`/catalogue?q=${encodeURIComponent(query)}`, { state: { recommendations } });
  }, [navigate]);

  return (
    <section className="hero" id="hero-section">
      <div className="hero-bg"><div className="bg-grid" /><div className="bg-glow bg-glow--1" /><div className="bg-glow bg-glow--2" /></div>
      <motion.div className="car-container" initial={{ opacity: 0, scale: 0.92 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.8 }}>
        <img src="/assets/hero-car.png" alt="Véhicule premium — AutoMind" className="car-image" />
        <motion.div className="headlight headlight--left" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.8, duration: 0.6 }} />
        <motion.div className="headlight headlight--right" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.9, duration: 0.6 }} />
      </motion.div>
      <motion.div className="hero-content" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.2, duration: 0.6 }}>
        <p className="hero-tagline"><span className="tagline-dot" />Marketplace automobile propulsée par l'intelligence artificielle</p>
        <h1 className="hero-title">Trouvez votre véhicule <br /><span className="title-gradient">avec l'IA.</span></h1>
      </motion.div>
      <motion.div className="search-wrapper" initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.6, duration: 0.6 }}>
        <SearchBar userId={user?.id} onResults={handleResults} />
        <div className="ai-badge"><span className="ai-badge-pulse" /><span>Propulsé par IA</span><span className="ai-badge-sep">·</span><span>Recommandation hybride personnalisée</span></div>
      </motion.div>
    </section>
  );
}
