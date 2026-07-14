import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import fr from '../i18n/fr';

export default function Login() {
  const navigate = useNavigate();
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (isAuthenticated) {
    navigate('/', { replace: true });
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login({ email, password });
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || fr.auth.loginError);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      background: 'var(--bg-primary)', minHeight: '100vh',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: 'var(--space-xl)', paddingTop: 'calc(var(--nav-height) + var(--space-xl))',
    }}>
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{
          maxWidth: 420, width: '100%', padding: 'var(--space-2xl)',
          background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
          border: '1px solid var(--border-subtle)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-xl)' }}>
          <h1 style={{
            fontSize: '1.5rem', fontFamily: 'var(--font-display)',
            fontWeight: 800, marginBottom: 8, color: 'var(--accent-gold)',
          }}>
            {fr.auth.loginTitle}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Connectez-vous à votre compte Wakala
          </p>
        </div>

        {error && (
          <div style={{
            padding: '10px 14px', marginBottom: 'var(--space-md)',
            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
            borderRadius: 'var(--radius-card)', color: 'var(--accent-red)',
            fontSize: '0.85rem',
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 'var(--space-md)' }}>
            <label style={{
              display: 'block', fontSize: '0.8rem', fontWeight: 600,
              color: 'var(--text-secondary)', marginBottom: 'var(--space-xs)',
            }} htmlFor="login-email">
              {fr.auth.email}
            </label>
            <input
              id="login-email"
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="exemple@email.ma"
              style={{
                width: '100%', padding: '12px 16px',
                background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-card)', color: 'var(--text-primary)',
                fontSize: '0.9rem', outline: 'none',
              }}
            />
          </div>

          <div style={{ marginBottom: 'var(--space-lg)' }}>
            <label style={{
              display: 'block', fontSize: '0.8rem', fontWeight: 600,
              color: 'var(--text-secondary)', marginBottom: 'var(--space-xs)',
            }} htmlFor="login-password">
              {fr.auth.password}
            </label>
            <input
              id="login-password"
              type="password"
              required
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              style={{
                width: '100%', padding: '12px 16px',
                background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-card)', color: 'var(--text-primary)',
                fontSize: '0.9rem', outline: 'none',
              }}
            />
          </div>

          <button
            id="login-submit"
            type="submit"
            disabled={loading}
            style={{
              width: '100%', padding: '14px 24px',
              background: 'var(--accent-gold)', color: '#0f1a2b',
              border: 'none', borderRadius: 'var(--radius-pill)',
              fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer',
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? fr.general.loading : fr.auth.submitLogin}
          </button>
        </form>

        <p style={{
          textAlign: 'center', marginTop: 'var(--space-lg)',
          fontSize: '0.85rem', color: 'var(--text-muted)',
        }}>
          {fr.auth.noAccount}{' '}
          <Link to="/register" style={{ color: 'var(--accent-gold)', fontWeight: 600, textDecoration: 'none' }}>
            {fr.auth.registerLink}
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
