import { useState, useEffect, useCallback, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ChevronDown, ChevronRight, ArrowRight } from 'lucide-react';
import { AuthContext } from '../../context/AuthContext';
import type { RecommendationResponse } from '../../services/recommendationService';
import SearchBar from './SearchBar';
import styles from './hero.module.css';
import './Hero.css';

// Utilisation des données Wakala
const slides = [
  {
    id: 'dacialogan',
    image: '/assets/dacia-logan.jpg',
    bgPosition: '50% center',
    alt: 'Dacia Logan en vitrine WAKALA',
    titleTop: 'Recherche',
    titleBottom: 'Intuitive',
    description: 'Trouvez le véhicule idéal en quelques clics grâce à notre intelligence artificielle qui comprend vos besoins.',
  },
  {
    id: 'clio5',
    image: '/assets/clio5.jpg',
    bgPosition: '50% center',
    alt: 'Renault Clio en vitrine WAKALA',
    titleTop: 'Confiance',
    titleBottom: 'Absolue',
    description: 'Chaque véhicule sur Wakala est rigoureusement inspecté et certifié pour vous garantir un achat sans surprise.',
  },
  {
    id: 'mercedescla',
    image: '/assets/mercedes-cla.jpg',
    bgPosition: '50% center',
    alt: 'Mercedes CLA en vitrine WAKALA',
    titleTop: 'Transparence',
    titleBottom: 'Garantie',
    description: 'Accédez à un historique complet et transparent. Achetez votre véhicule au juste prix du marché.',
  },
  {
    id: 'jeepgrandcherokee',
    image: '/assets/jeep-grand-cherokee.jpg',
    bgPosition: '50% center',
    alt: 'Jeep Grand Cherokee WAKALA',
    titleTop: 'Achat',
    titleBottom: 'Simplifié',
    description: 'De la sélection à la livraison, profitez d\'un accompagnement personnalisé et 100% sécurisé.',
  }
];

export default function HeroCar() {
  const navigate = useNavigate();
  const authContext = useContext(AuthContext);
  const user = authContext?.user;
  const [currentSlide, setCurrentSlide] = useState(0);
  const [animatingTo, setAnimatingTo] = useState(0);
  const [transitionState, setTransitionState] = useState('isEntering');
  const [isScrolled, setIsScrolled] = useState(false);
  const [isInteractingWithSearch, setIsInteractingWithSearch] = useState(false);
  
  const autoPlayDelay = 5000;

  // Auto-play (paused while user is searching/interacting)
  useEffect(() => {
    if (isInteractingWithSearch) return;
    const timer = setInterval(() => {
      goToSlide((currentSlide + 1) % slides.length);
    }, autoPlayDelay);
    return () => clearInterval(timer);
  }, [currentSlide, isInteractingWithSearch]);

  // Transition state management
  useEffect(() => {
    if (currentSlide === animatingTo) return;
    setTransitionState('isExiting');
    const timer = setTimeout(() => {
      setCurrentSlide(animatingTo);
      setTransitionState('isEntering');
    }, 250); // Le temps de l'animation de sortie
    return () => clearTimeout(timer);
  }, [animatingTo, currentSlide]);

  // Scroll hint
  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 30);
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const goToSlide = (index: number) => {
    setAnimatingTo(index);
  };

  const handleWhyUsClick = () => {
    console.log("Pourquoi nous");
  };

  const handleResults = useCallback((query: string, recommendations?: RecommendationResponse | null) => {
    navigate(`/catalogue?q=${encodeURIComponent(query)}`, { state: recommendations ? { recommendations } : undefined });
  }, [navigate]);

  const activeSlideData = slides[animatingTo]; // Les données du slide en cours de transition
  const activeSlideVisual = slides[currentSlide]; // L'image qui s'affiche (pour les transitions fluides)

  return (
    <section className={styles.heroSlider}>
      {/* Effets ambiants */}
      <div className={styles.grain} aria-hidden="true" />
      <div className={styles.ambientGlow} aria-hidden="true" />

      {/* Track d'images en fond */}
      <div className={styles.track} aria-live="polite">
        {slides.map((slide, index) => {
          const isActive = index === currentSlide;
          return (
            <article
              key={slide.id}
              className={`${styles.slide} ${isActive ? styles.isActive : ''}`}
              aria-hidden={!isActive}
              style={{
                '--hero-image': `url(${slide.image})`,
                '--hero-image-position': slide.bgPosition
              } as React.CSSProperties}
            >
              <img
                src={slide.image}
                alt={slide.alt}
                className={styles.slideImage}
                style={{ objectPosition: slide.bgPosition }}
                loading={isActive ? "eager" : "lazy"}
              />
              <div className={styles.slideOverlay} />
            </article>
          );
        })}
      </div>

      {/* Contenu textuel, recherche et actions */}
      <div className={styles.contentWrap}>
        <div className={styles.content}>
          <div className={`${styles.slideTextWrap} ${styles[transitionState]}`}>
            <span className={styles.titleLine} aria-hidden="true" />
            <span className={styles.eyebrow}>WAKALA AUTOMOBILE</span>
            
            <div className={`${styles.titleWrap} ${activeSlideData.id === 'mercedescla' || activeSlideData.id === 'jeepgrandcherokee' ? styles.titleWrapLong : ''}`}>
              <h1 className={styles.title}>
                <span className={styles.titleTop}>{activeSlideData.titleTop}</span>
                <br />
                <span className={styles.titleBottom}>{activeSlideData.titleBottom}</span>
              </h1>
            </div>
            
            <p className={styles.description}>{activeSlideData.description}</p>
          </div>
          
          {/* Barre de Recherche IA du Repo */}
          <div
            className={styles.searchWrapper}
            onMouseEnter={() => setIsInteractingWithSearch(true)}
            onMouseLeave={() => setIsInteractingWithSearch(false)}
          >
            <SearchBar
              userId={user?.id}
              onResults={handleResults}
              onActiveChange={setIsInteractingWithSearch}
            />
          </div>

          <div className={styles.actions}>
            <Link to="/catalogue" className={styles.ctaBtn}>
              Explorer les véhicules
              <span className={styles.ctaArrow}><ArrowRight size={18} /></span>
            </Link>
            <button type="button" className={styles.ghostBtn} onClick={handleWhyUsClick}>
              Pourquoi nous
            </button>
          </div>
        </div>
      </div>

      {/* Navigation (flèches + progression) */}
      <div className={styles.nav} aria-label="Navigation du hero slider">
        <button
          type="button"
          className={styles.arrow}
          onClick={() => goToSlide((currentSlide - 1 + slides.length) % slides.length)}
          aria-label="Slide précédente"
        >
          <ChevronRight size={18} style={{ transform: 'rotate(180deg)' }} />
        </button>

        <div className={styles.progress} role="tablist" aria-label="Sélectionner un slide">
          <div className={styles.progressTrack}>
            <div 
              key={activeSlideVisual.id} // Force le re-render de l'animation
              className={styles.progressFill} 
              style={{ '--hero-autoplay-duration': `${autoPlayDelay}ms` } as React.CSSProperties} 
            />
          </div>
          <div className={styles.progressDots}>
            {slides.map((slide, index) => (
              <button
                key={slide.id}
                type="button"
                className={`${styles.dot} ${index === currentSlide ? styles.isActive : ''}`}
                onClick={() => goToSlide(index)}
                aria-label={`Aller au slide ${index + 1}`}
                aria-selected={index === currentSlide}
                role="tab"
              />
            ))}
          </div>
        </div>

        <button
          type="button"
          className={styles.arrow}
          onClick={() => goToSlide((currentSlide + 1) % slides.length)}
          aria-label="Slide suivante"
        >
          <ChevronRight size={18} />
        </button>
      </div>

      {/* Scroll hint */}
      {!isScrolled && (
        <button
          type="button"
          className={styles.scrollHint}
          aria-label="Défiler vers le bas"
          onClick={() => window.scrollTo({ top: window.innerHeight * 0.9, behavior: 'smooth' })}
        >
          <ChevronDown size={24} />
        </button>
      )}


    </section>
  );
}
