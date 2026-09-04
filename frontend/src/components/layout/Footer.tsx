import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer" id="footer">
      <div className="footer__container">
        
        {/* ─── Grille Principale ──────────────────────────────────────── */}
        <div className="footer__main-grid">
          
          {/* Colonne 1 : Marque & Présentation */}
          <div className="footer__col footer__col--brand">
            <Link to="/" className="footer__logo-link">
              <img 
                src="/assets/wakala-logo-light.png" 
                alt="Wakala" 
                className="footer__logo-img"
              />
            </Link>
            <p className="footer__brand-desc">
              Votre partenaire de confiance pour l’achat automobile au Maroc.
              Consultez les fiches techniques certifiées, comparez les finitions 
              et découvrez les prix réels en concession en toute transparence.
            </p>
            <div className="footer__contact-info">
              <span>Casablanca, Maroc</span>
              <a href="mailto:contact@wakala.ma">contact@wakala.ma</a>
            </div>

          </div>

          {/* Colonne 2 : Véhicules & Outils */}
          <div className="footer__col">
            <h4 className="footer__col-title">Véhicules & Outils</h4>
            <ul className="footer__nav-list">
              <li>
                <Link to="/catalogue" className="footer__nav-link">
                  Catalogue Voitures Neuves
                </Link>
              </li>
              <li>
                <Link to="/marque" className="footer__nav-link">
                  Toutes les marques
                </Link>
              </li>
              <li>
                <Link to="/comparateur" className="footer__nav-link">
                  Comparateur de modèles
                </Link>
              </li>
              <li>
                <Link to="/dedouanement" className="footer__nav-link">
                  Simulateur de dédouanement
                </Link>
              </li>
            </ul>
          </div>

          {/* Colonne 3 : Wakala & Confiance */}
          <div className="footer__col">
            <h4 className="footer__col-title">Wakala</h4>
            <ul className="footer__nav-list">
              <li>
                <Link to="/a-propos" className="footer__nav-link">
                  À propos de Wakala
                </Link>
              </li>
              <li>
                <Link to="/contact" className="footer__nav-link">
                  Nous contacter
                </Link>
              </li>
              <li>
                <Link to="/mentions-legales" className="footer__nav-link">
                  Mentions Légales & CGU
                </Link>
              </li>
              <li>
                <Link to="/mentions-legales" className="footer__nav-link">
                  Protection des données (CNDP)
                </Link>
              </li>
            </ul>
          </div>

        </div>

        {/* ─── Barre Inférieure ───────────────────────────────────────── */}
        <div className="footer__bottom-bar">
          <div className="footer__copyright">
            © {currentYear} <span className="footer__copyright-brand">Wakala</span>. Tous droits réservés. L’automobile en toute confiance au Maroc.
          </div>
          <div className="footer__bottom-links">
            <Link to="/mentions-legales" className="footer__bottom-link">Confidentialité</Link>
            <span className="footer__bottom-sep">•</span>
            <Link to="/mentions-legales" className="footer__bottom-link">CNDP</Link>
            <span className="footer__bottom-sep">•</span>
            <span className="footer__location-badge">Casablanca, Maroc 🇲🇦</span>
          </div>
        </div>

      </div>
    </footer>
  );
}
