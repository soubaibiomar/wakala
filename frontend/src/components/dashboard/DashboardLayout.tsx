import { Link, Outlet, useLocation, Navigate } from 'react-router-dom';
import { Home, List, Heart, TrendingUp, Menu, LogOut, ChevronLeft, BookOpen, MessageSquare, Sparkles, User } from 'lucide-react';
import { useState } from 'react';
import styles from './DashboardLayout.module.css';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/authService';
import ChatbotWidget from '../chatbot-widget/ChatbotWidget';
import Navbar from '../layout/Navbar';

export default function DashboardLayout() {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();
  const { user, isAuthenticated, loading, logout, updateUser } = useAuth();

  // ─── Route Guard ────────────────────────────────────────────
  // Pendant le chargement initial, ne rien montrer (évite le flash)
  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', background: 'var(--color-bg, #0d1117)' }}>
        <div style={{ color: 'var(--color-text-muted, #8b949e)', fontSize: '1rem' }}>Chargement...</div>
      </div>
    );
  }
  // Si pas authentifié, redirection immédiate vers /login
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  const NAV_ITEMS = [
    { label: 'Accueil', icon: Home, path: '/dashboard' },
    { label: "Carnet d'Entretien", icon: BookOpen, path: '/dashboard/maintenance' },
    { label: 'Mes Annonces', icon: List, path: '/dashboard/listings' },
    { label: 'Messagerie', icon: MessageSquare, path: '/dashboard/messages' },
    { label: 'Négociations', icon: MessageSquare, path: '/dashboard/offers' },
    { label: 'Favoris', icon: Heart, path: '/dashboard/favorites' },
    { label: 'Pour Vous', icon: Sparkles, path: '/dashboard/recommendations' },
    { label: 'Argus', icon: TrendingUp, path: '/dashboard/argus' },
    { label: 'Mon Profil', icon: User, path: '/dashboard/profile' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Navbar />
      <div className={styles.layout}>
        {/* Sidebar Desktop */}
        <aside className={`${styles.sidebar} ${isSidebarOpen ? styles.open : styles.closed}`}>
        <div className={styles.sidebarHeader}>
          {isSidebarOpen && (
            <Link to="/" className={styles.brand}>
              <img src="/assets/wakala-logo.png" alt="Wakala" className={styles.logo} />
            </Link>
          )}
          <button className={styles.toggleBtn} onClick={() => setSidebarOpen(!isSidebarOpen)}>
            {isSidebarOpen ? <ChevronLeft size={20} /> : <Menu size={20} />}
          </button>
        </div>

        <nav className={styles.nav}>
          {NAV_ITEMS.filter(item => {
            if (item.path === '/dashboard/listings' && user?.role !== 'seller' && user?.role !== 'admin') return false;
            return true;
          }).map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`${styles.navItem} ${isActive(item.path) ? styles.active : ''}`}
            >
              <item.icon size={24} className={styles.navIcon} />
              {isSidebarOpen && <span className={styles.navLabel}>{item.label}</span>}
            </Link>
          ))}
          
          {user?.role === 'admin' && (
            <Link to="/dashboard/admin" className={`${styles.navItem} ${isActive('/dashboard/admin') ? styles.active : ''}`}>
              <span className={styles.navIcon}>👑</span>
              {isSidebarOpen && <span className={styles.navLabel}>Admin</span>}
            </Link>
          )}

          {user?.role === 'buyer' && isSidebarOpen && (
            <div style={{
              margin: '16px 12px 8px 12px',
              padding: '12px',
              background: 'linear-gradient(135deg, rgba(174, 140, 78, 0.15) 0%, rgba(26, 35, 50, 0.5) 100%)',
              border: '1px solid rgba(174, 140, 78, 0.3)',
              borderRadius: '10px',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#d4af37', marginBottom: '4px' }}>
                Vendez votre voiture
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--color-text-secondary, #8b949e)', margin: '0 0 10px 0', lineHeight: 1.3 }}>
                Passez au statut vendeur en 1 clic
              </p>
              <button
                onClick={async () => {
                  try {
                    const updatedUser = await authService.becomeSeller();
                    updateUser(updatedUser);
                  } catch (e) {
                    console.error(e);
                  }
                }}
                style={{
                  width: '100%',
                  background: 'linear-gradient(135deg, #ae8c4e 0%, #d4af37 100%)',
                  color: '#fff',
                  border: 'none',
                  padding: '7px 10px',
                  borderRadius: '6px',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  boxShadow: '0 2px 8px rgba(174, 140, 78, 0.3)'
                }}
              >
                ✨ Devenir Vendeur
              </button>
            </div>
          )}
        </nav>

        <div className={styles.sidebarFooter}>
          {user && (
            <div style={{ padding: '15px 20px', color: 'var(--color-text-primary)', borderTop: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', gap: '12px', fontSize: '14px', fontWeight: '500' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--color-brand-primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                {user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
              </div>
              {isSidebarOpen && <span>{user.full_name}</span>}
            </div>
          )}
          <button className={styles.navItem} onClick={logout}>
            <LogOut size={24} className={styles.navIcon} />
            {isSidebarOpen && <span className={styles.navLabel}>Déconnexion</span>}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className={styles.mainContent}>
        <header className={styles.mobileHeader}>
          <Link to="/" className={styles.brand}>
            <img src="/assets/wakala-logo.png" alt="Wakala" className={styles.logo} />
          </Link>
          <div className={styles.userInfo}>
            {user?.full_name}
          </div>
        </header>
        
        <div className={styles.contentContainer}>
          <Outlet />
        </div>
      </main>

      {/* Bottom Nav Mobile */}
      <nav className={styles.bottomNav}>
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`${styles.bottomNavItem} ${isActive(item.path) ? styles.active : ''}`}
          >
            <item.icon size={20} />
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* Persistent Chatbot in Dashboard */}
      <ChatbotWidget />
      </div>
    </div>
  );
}
