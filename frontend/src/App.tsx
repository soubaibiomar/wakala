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

import { BrowserRouter, Routes, Route, Link, useLocation, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Home as HomeIcon, Search, Calculator, User, LogOut } from 'lucide-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CompareProvider } from './context/CompareContext';
import Home from './pages/Home';
import Catalogue from './pages/Catalogue';
import VehicleDetail from './pages/VehicleDetail';
import AuthPage from './pages/Auth/AuthPage';
import BrandPage from './pages/BrandPage/BrandPage';
import AdminDashboard from './pages/AdminDashboard';
import MaintenanceBook from './pages/Dashboard/MaintenanceBook';
import CustomsPage from './pages/CustomsPage';
import TransactionPage from './pages/TransactionPage';
import ChatbotPage from './pages/ChatbotPage';
import ChatbotWidget from './components/chatbot-widget/ChatbotWidget';
import CompareDrawer from './components/compare/CompareDrawer';
import DashboardLayout from './components/dashboard/DashboardLayout';
import DashboardIndex from './pages/Dashboard';
import SellerListings from './pages/Dashboard/SellerListings';
import NewListing from './pages/Dashboard/NewListing';
import Messages from './pages/Dashboard/Messages';
import './styles/globals.css';

// ─── React Query Client ───────────────────────────────────────
const queryClient = new QueryClient();

// ─── Navbar ───────────────────────────────────────────────────

function Navbar() {
  const location = useLocation();
  const { user, isAuthenticated, logout } = useAuth();

  const isActive = (path: string) =>
    location.pathname === path ? 'navbar__link navbar__link--active' : 'navbar__link';

  const isMobileActive = (path: string) =>
    location.pathname === path ? 'mobile-tab-bar__item mobile-tab-bar__item--active' : 'mobile-tab-bar__item';

  return (
    <>
      {/* Desktop Navbar */}
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

            <li>
              <Link to="/dedouanement" className={isActive('/dedouanement')}>Dédouanement</Link>
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
                    onClick={() => logout()}
                    id="nav-logout"
                  >
                    Déconnexion
                  </button>
                </li>
                {user.role === 'admin' && (
                  <li>
                    <Link to="/admin" className="navbar__link">Admin</Link>
                  </li>
                )}
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

      {/* Mobile Bottom Tab Bar */}
      <nav className="mobile-tab-bar">
        <Link to="/" className={isMobileActive('/')}>
          <HomeIcon size={24} />
          <span>Accueil</span>
        </Link>
        <Link to="/catalogue" className={isMobileActive('/catalogue')}>
          <Search size={24} />
          <span>Catalogue</span>
        </Link>
        <Link to="/dedouanement" className={isMobileActive('/dedouanement')}>
          <Calculator size={24} />
          <span>Douane</span>
        </Link>
        {isAuthenticated ? (
          <button className="mobile-tab-bar__item" onClick={logout} style={{ background: 'none', border: 'none' }}>
            <LogOut size={24} />
            <span>Sortir</span>
          </button>
        ) : (
          <Link to="/login" className={isMobileActive('/login')}>
            <User size={24} />
            <span>Profil</span>
          </Link>
        )}
      </nav>
    </>
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
            <li><Link to="/dedouanement">Calculateur Douane</Link></li>
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

// ─── Layouts ──────────────────────────────────────────────────

function MainLayout() {
  return (
    <>
      <Navbar />
      <main className="page">
        <Outlet />
      </main>
      <Footer />
      <ChatbotWidget />
      <CompareDrawer />
    </>
  );
}

// ─── App (wrapped in AuthProvider) ────────────────────────────

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes with standard Navbar/Footer */}
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/catalogue" element={<Catalogue />} />
        <Route path="/vehicles/:id" element={<VehicleDetail />} />
        <Route path="/marque/:brandName" element={<BrandPage />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/chat" element={<ChatbotPage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/register" element={<AuthPage />} />
        <Route path="/dedouanement" element={<CustomsPage />} />
        <Route path="/transaction/:id" element={<TransactionPage />} />
        {/* L'ancien admin, en attendant d'être supprimé ou refactoré */}
        <Route path="/admin" element={<AdminDashboard />} />
      </Route>
      
      {/* Dashboard Routes with Sidebar/BottomNav */}
      <Route path="/dashboard" element={<DashboardLayout />}>
        <Route index element={<DashboardIndex />} />
        <Route path="maintenance" element={<MaintenanceBook />} />
        <Route path="listings" element={<SellerListings />} />
        <Route path="new-listing" element={<NewListing />} />
        <Route path="messages" element={<Messages />} />
        <Route path="favorites" element={<div>Favoris (À venir)</div>} />
        <Route path="argus" element={<div>Argus Complet (À venir)</div>} />
        {/* L'Admin Bento est géré par l'index qui check le role, ou on peut le forcer ici */}
        <Route path="admin" element={<DashboardIndex />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <CompareProvider>
          <BrowserRouter>
            <AppRoutes />
          </BrowserRouter>
        </CompareProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}
