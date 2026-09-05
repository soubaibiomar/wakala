import { Link, useLocation } from 'react-router-dom';
import { User, LogOut } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function Navbar() {
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

            {isAuthenticated && user ? (
              <>
                <li>
                  <Link to="/admin" className={isActive('/admin')}>
                    Cockpit Admin ({user.full_name})
                  </Link>
                </li>
                <li>
                  <button
                    className="navbar__link"
                    style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer', fontFamily: 'inherit' }}
                    onClick={() => logout()}
                    id="nav-logout"
                  >
                    Déconnexion
                  </button>
                </li>
              </>
            ) : (
              <li>
                <Link to="/login" className="btn btn--primary btn--sm" id="nav-login">
                  Se connecter
                </Link>
              </li>
            )}
          </ul>
        </div>
      </nav>

      {/* Mobile Tab Bar */}
      <nav className="mobile-tab-bar" id="mobile-tab-bar">
        <Link to="/" className={isMobileActive('/')}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          <span>Accueil</span>
        </Link>
        <Link to="/catalogue" className={isMobileActive('/catalogue')}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <span>Catalogue</span>
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
