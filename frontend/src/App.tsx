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

import { BrowserRouter, Routes, Route, Link, useLocation, Outlet, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Home as HomeIcon, Search, Calculator, User, LogOut } from 'lucide-react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CompareProvider } from './context/CompareContext';
import Home from './pages/Home';
import Catalogue from './pages/Catalogue';
import { NewCarDetailPage } from './pages/NewCarDetailPage';
import { ComparatorPage } from './pages/ComparatorPage';
import VehicleDetail from './pages/VehicleDetail';
import AuthPage from './pages/Auth/AuthPage';
import BrandPage from './pages/BrandPage/BrandPage';
import MarquesPage from './pages/MarquesPage';
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
import GuideAchatPage from './pages/GuideAchatPage';
import ComparatifPage from './pages/ComparatifPage';
import VilleCataloguePage from './pages/VilleCataloguePage';
import FinancementPage from './pages/FinancementPage';
import OrganizationStructuredData from './components/seo/OrganizationStructuredData';
import RecommendationExperience from './components/recommendation-experience/RecommendationExperience';
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
            Votre partenaire de confiance pour l’achat automobile au Maroc.
            Comparez les véhicules neufs, consultez des fiches techniques fiables,
            estimez les frais d’importation et trouvez le modèle adapté à vos besoins.
          </p>
        </div>
        <div>
          <div className="footer__title">Nos services</div>
          <ul className="footer__list">
            <li><Link to="/guide-achat-voiture-maroc">Guide d’achat automobile</Link></li>
            <li><Link to="/catalogue">Catalogue de voitures neuves</Link></li>
            <li><Link to="/financement-auto-maroc">Financement et Mourabaha</Link></li>
            <li><Link to="/comparateur">Comparateur de véhicules</Link></li>
            <li><Link to="/dedouanement">Simulateur de dédouanement</Link></li>
            <li><Link to="/chat">Assistant automobile multilingue</Link></li>
          </ul>
        </div>
        <div>
          <div className="footer__title">Villes et réseau</div>
          <ul className="footer__list">
            <li><Link to="/voitures-neuves/casablanca">Casablanca</Link></li>
            <li><Link to="/voitures-neuves/rabat">Rabat</Link></li>
            <li><Link to="/voitures-neuves/marrakech">Marrakech</Link></li>
            <li><Link to="/voitures-neuves/tanger">Tanger</Link></li>
            <li><Link to="/voitures-neuves/agadir">Agadir</Link></li>
            <li><Link to="/marque">Toutes les marques</Link></li>
          </ul>
        </div>
        <div>
          <div className="footer__title">Wakala</div>
          <ul className="footer__list">
            <li><Link to="/score-de-confiance">Score de confiance Wakala</Link></li>
            <li><Link to="/technologie">Technologie et données</Link></li>
            <li><Link to="/a-propos">À propos de Wakala</Link></li>
            <li><Link to="/contact">Nous contacter</Link></li>
            <li><Link to="/mentions-legales">Mentions légales</Link></li>
          </ul>
        </div>
      </div>
      <div className="footer__bottom">
        © {new Date().getFullYear()} Wakala — L’automobile en toute confiance au Maroc
      </div>
    </footer>
  );
}

// ─── Layouts ──────────────────────────────────────────────────

function MainLayout() {
  return (
    <>
      <OrganizationStructuredData />
      <Navbar />
      <main className="page">
        <Outlet />
      </main>
      <Footer />
      <RecommendationExperience />
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
        
        {/* SEO & GEO Semantic Silos */}
        <Route path="/guide-achat-voiture-maroc" element={<GuideAchatPage />} />
        <Route path="/comparer/:slug" element={<ComparatifPage />} />
        <Route path="/voitures-neuves/:ville" element={<VilleCataloguePage />} />
        <Route path="/financement-auto-maroc" element={<FinancementPage />} />
        
        <Route path="/neuf/:slug" element={<NewCarDetailPage />} />
        <Route path="/neuf/:brand/:slug" element={<NewCarDetailPage />} />
        <Route path="/comparateur" element={<ComparatorPage />} />
        <Route path="/vehicule/:id" element={<VehicleDetail />} />
        <Route path="/marque" element={<MarquesPage />} />
        <Route path="/marques" element={<MarquesPage />} />
        <Route path="/marque/:brandName" element={<BrandPage />} />
        <Route path="/marque/:brandName/:modelName" element={<ModelPage />} />
        <Route path="/marque/:brandName/:modelName/:versionSlug" element={<VehicleDetail />} />
        <Route path="/auth" element={<AuthPage />} />
        <Route path="/chat" element={<ChatbotPage />} />
        <Route path="/conseiller-ia" element={<ChatbotPage />} />
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
        {/* Master Admin Cockpit Route & Catalogue Management */}
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/cockpit" element={<AdminDashboard />} />
        <Route path="/admin/catalogue" element={<Catalogue />} />
      </Route>
      
      {/* Redirect old dashboard to Admin Cockpit */}
      <Route path="/dashboard" element={<Navigate to="/admin" replace />} />
      <Route path="/dashboard/*" element={<Navigate to="/admin" replace />} />
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
