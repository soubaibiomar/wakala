/**
 * App.tsx — Racine de l'application Wakala.
 *
 * Structure :
 *   <AuthProvider>
 *     <BrowserRouter>
 *       <Navbar />
 *       <Routes />
 *       <Footer />
 *     </BrowserRouter>
 *   </AuthProvider>
 */

import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Home from './pages/Home';
import Catalogue from './pages/Catalogue';
import VehicleDetail from './pages/VehicleDetail';
import Login from './pages/Login';
import Register from './pages/Register';
import ChatbotWidget from './components/chatbot-widget/ChatbotWidget';
import './styles/globals.css';
import './styles/car-motifs.css';

// ─── Navbar ───────────────────────────────────────────────────

function Navbar() {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  const isActive = (path: string) =>
    location.pathname === path ? 'navbar__link navbar__link--active' : 'navbar__link';

  return (
    <nav className="navbar" id="navbar">
      <div className="navbar__inner">
        <Link to="/" className="navbar__brand">
          <img
            src="/assets/wakala-logo.png"
            alt="Wakala"
            className="navbar__brand-logo"
          />
        </Link>

        <ul className="navbar__links">
          <li>
            <Link to="/" className={isActive('/')}>Accueil</Link>
          </li>
          <li>
            <Link to="/catalogue" className={isActive('/catalogue')}>Catalogue</Link>
          </li>

          {isAuthenticated && user ? (
            <>
              <li>
                <span
                  className="navbar__link"
                  style={{ opacity: 0.7, fontSize: '0.82rem', cursor: 'default' }}
                >
                  👤 {user.name}
                  {user.role === 'seller' && (
                    <span className="badge badge--gold" style={{ marginLeft: 6, fontSize: '0.6rem' }}>
                      Vendeur
                    </span>
                  )}
                </span>
              </li>
              <li>
                <button
                  className="btn btn--ghost btn--sm"
                  onClick={logout}
                  id="nav-logout"
                >
                  Déconnexion
                </button>
              </li>
            </>
          ) : (
            <>
              <li>
                <Link to="/login" className={isActive('/login')}>Connexion</Link>
              </li>
              <li>
                <Link to="/register" className={isActive('/register')}>
                  S'inscrire
                </Link>
              </li>
            </>
          )}
        </ul>
      </div>
    </nav>
  );
}

// ─── Footer ───────────────────────────────────────────────────

function Footer() {
  return (
    <footer className="footer" id="footer">
      <div className="footer__inner">
        <div>
          <div className="footer__brand">Wakala</div>
          <p className="footer__desc">
            La marketplace automobile intelligente propulsée par l'IA.
            Recherche intuitive, recommandation hybride,
            score de confiance transparent.
          </p>
        </div>
        <div>
          <div className="footer__title">Plateforme</div>
          <ul className="footer__list">
            <li><Link to="/catalogue">Catalogue</Link></li>
            <li><Link to="/register">Vendre un véhicule</Link></li>
            <li><a href="#">Comment ça marche</a></li>
          </ul>
        </div>
        <div>
          <div className="footer__title">Technologie</div>
          <ul className="footer__list">
            <li><a href="#">IA &amp; Big Data</a></li>
            <li><a href="#">Score de confiance</a></li>
            <li><a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">API Docs</a></li>
          </ul>
        </div>
        <div>
          <div className="footer__title">Entreprise</div>
          <ul className="footer__list">
            <li><a href="#">À propos</a></li>
            <li><a href="#">Contact</a></li>
            <li><a href="#">Mentions légales</a></li>
          </ul>
        </div>
      </div>
      <div className="footer__bottom">
        © {new Date().getFullYear()} Wakala — Propulsé par l'intelligence artificielle
      </div>
    </footer>
  );
}

// ─── App (wrapped in AuthProvider) ────────────────────────────

function AppRoutes() {
  return (
    <>
      <Navbar />
      <main className="page">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/catalogue" element={<Catalogue />} />
          <Route path="/vehicule/:id" element={<VehicleDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </main>
      <Footer />
      <ChatbotWidget />
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
