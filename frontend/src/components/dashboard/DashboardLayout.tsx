import { Link, Outlet, useLocation } from 'react-router-dom';
import { Home, List, Heart, TrendingUp, MessageSquare, Menu, LogOut, ChevronLeft } from 'lucide-react';
import { useState } from 'react';
import styles from './DashboardLayout.module.css';
import { useAuth } from '../../context/AuthContext';
import ChatbotWidget from '../chatbot-widget/ChatbotWidget';

export default function DashboardLayout() {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();
  const { user, logout } = useAuth();

  const NAV_ITEMS = [
    { label: 'Accueil', icon: Home, path: '/dashboard' },
    { label: 'Mes Annonces', icon: List, path: '/dashboard/listings' },
    { label: 'Favoris', icon: Heart, path: '/dashboard/favorites' },
    { label: 'Argus', icon: TrendingUp, path: '/dashboard/argus' },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
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
          {NAV_ITEMS.map((item) => (
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
        </nav>

        <div className={styles.sidebarFooter}>
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
            {user?.name}
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
            <item.icon size={22} />
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* Persistent Chatbot in Dashboard */}
      <ChatbotWidget />
    </div>
  );
}
