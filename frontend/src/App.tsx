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
import ModelPage from './pages/ModelPage/ModelPage';
import AdminDashboard from './pages/AdminDashboard';
import MaintenanceBook from './pages/Dashboard/MaintenanceBook';
import CustomsPage from './pages/CustomsPage';
import TransactionPage from './pages/TransactionPage';
import ChatbotPage from './pages/ChatbotPage';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import LegalPage from './pages/LegalPage';
import HowItWorksPage from './pages/HowItWorksPage';
import TechnologyPage from './pages/TechnologyPage';
import TrustScorePage from './pages/TrustScorePage';
import ChatbotWidget from './components/chatbot-widget/ChatbotWidget';
import CompareDrawer from './components/compare/CompareDrawer';
import DashboardLayout from './components/dashboard/DashboardLayout';
import DashboardIndex from './pages/Dashboard';
import SellerListings from './pages/Dashboard/SellerListings';
import NewListing from './pages/Dashboard/NewListing';
import Messages from './pages/Dashboard/Messages';
import Favorites from './pages/Dashboard/Favorites';
import Recommendations from './pages/Dashboard/Recommendations';
import Offers from './pages/Dashboard/Offers';
import Profile from './pages/Dashboard/Profile';
import './styles/globals.css';

// ─── React Query Client ───────────────────────────────────────
const queryClient = new QueryClient();

// ─── Navbar ───────────────────────────────────────────────────

import Navbar from './components/layout/Navbar';

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
            <li><Link to="/comment-ca-marche">Comment ça marche</Link></li>
          </ul>
        </div>
        <div>
          <div className="footer__title">Technologie</div>
          <ul className="footer__list">
            <li><Link to="/technologie">IA &amp; Big Data</Link></li>
            <li><Link to="/score-de-confiance">Score de confiance</Link></li>
            <li><a href="http://localhost:8000/docs" target="_blank" rel="noreferrer">API Docs</a></li>
          </ul>
        </div>
        <div>
          <div className="footer__title">Entreprise</div>
          <ul className="footer__list">
            <li><Link to="/a-propos">À propos</Link></li>
            <li><Link to="/contact">Contact</Link></li>
            <li><Link to="/mentions-legales">Mentions légales</Link></li>
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
        <Route path="/vehicule/:id" element={<VehicleDetail />} />
        <Route path="/marque/:brandName" element={<BrandPage />} />
        <Route path="/marque/:brandName/:modelName" element={<ModelPage />} />
        <Route path="/marque/:brandName/:modelName/:versionSlug" element={<VehicleDetail />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/chat" element={<ChatbotPage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/register" element={<AuthPage />} />
        <Route path="/dedouanement" element={<CustomsPage />} />
        <Route path="/transaction/:id" element={<TransactionPage />} />
        <Route path="/a-propos" element={<AboutPage />} />
        <Route path="/contact" element={<ContactPage />} />
        <Route path="/mentions-legales" element={<LegalPage />} />
        <Route path="/comment-ca-marche" element={<HowItWorksPage />} />
        <Route path="/technologie" element={<TechnologyPage />} />
        <Route path="/score-de-confiance" element={<TrustScorePage />} />
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
        <Route path="offers" element={<Offers />} />
        <Route path="favorites" element={<Favorites />} />
        <Route path="recommendations" element={<Recommendations />} />
        <Route path="profile" element={<Profile />} />
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
