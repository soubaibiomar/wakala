import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import type { UserRole } from '../types/user';
import fr from '../i18n/fr';

const PHONE_RE = /^(\+212|0)[5-7]\d{8}$/;
const CIN_RE = /^[A-Za-z]{2}\d{5,6}$/;

export default function Register() {
  const navigate = useNavigate();
  const { register, isAuthenticated } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [cin, setCin] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<UserRole>('buyer');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [cinError, setCinError] = useState('');

  if (isAuthenticated) {
    navigate('/', { replace: true });
    return null;
  }

  const validatePhone = (v: string) => {
    if (v && !PHONE_RE.test(v)) setPhoneError(fr.auth.phoneError);
    else setPhoneError('');
  };

  const validateCin = (v: string) => {
    if (v && !CIN_RE.test(v)) setCinError(fr.auth.cinError);
    else setCinError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (phoneError || cinError) return;
    setError('');
    setLoading(true);
    try {
      await register({ name, email, password, role, phone: phone || undefined });
      navigate('/');
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') setError(detail);
      else if (Array.isArray(detail)) setError(detail.map((d: any) => d.msg).join('. '));
      else setError(fr.error.generic);
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
            {fr.auth.registerTitle}
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Créez votre compte Wakala
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
            }} htmlFor="register-name">
              {fr.auth.name}
            </label>
            <input
              id="register-name"
              required minLength={2} autoComplete="name"
              value={name} onChange={(e) => setName(e.target.value)}
              placeholder="Jean Dupont"
              style={{
                width: '100%', padding: '12px 16px',
                background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-card)', color: 'var(--text-primary)',
                fontSize: '0.9rem', outline: 'none',
              }}
            />
          </div>

          <div style={{ marginBottom: 'var(--space-md)' }}>
            <label style={{
              display: 'block', fontSize: '0.8rem', fontWeight: 600,
              color: 'var(--text-secondary)', marginBottom: 'var(--space-xs)',
            }} htmlFor="register-email">
              {fr.auth.email}
            </label>
            <input
              id="register-email"
              type="email" required autoComplete="email"
              value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="exemple@email.ma"
              style={{
                width: '100%', padding: '12px 16px',
                background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-card)', color: 'var(--text-primary)',
                fontSize: '0.9rem', outline: 'none',
              }}
            />
          </div>

          <div style={{ marginBottom: 'var(--space-md)' }}>
            <label style={{
              display: 'block', fontSize: '0.8rem', fontWeight: 600,
              color: 'var(--text-secondary)', marginBottom: 'var(--space-xs)',
            }} htmlFor="register-phone">
              {fr.auth.phone}
            </label>
            <input
              id="register-phone"
              type="tel" autoComplete="tel"
              value={phone}
              onChange={(e) => { setPhone(e.target.value); validatePhone(e.target.value); }}
              placeholder={fr.auth.phonePlaceholder}
              style={{
                width: '100%', padding: '12px 16px',
                background: 'var(--bg-elevated)',
                border: `1px solid ${phoneError ? 'var(--accent-red)' : 'var(--border-subtle)'}`,
                borderRadius: 'var(--radius-card)', color: 'var(--text-primary)',
                fontSize: '0.9rem', outline: 'none',
              }}
            />
            {phoneError && (
              <p style={{ fontSize: '0.72rem', color: 'var(--accent-red)', marginTop: 4 }}>{phoneError}</p>
            )}
          </div>

          <div style={{ marginBottom: 'var(--space-md)' }}>
            <label style={{
              display: 'block', fontSize: '0.8rem', fontWeight: 600,
              color: 'var(--text-secondary)', marginBottom: 'var(--space-xs)',
            }} htmlFor="register-cin">
              {fr.auth.cin}
            </label>
            <input
              id="register-cin"
              value={cin}
              onChange={(e) => { setCin(e.target.value.toUpperCase()); validateCin(e.target.value.toUpperCase()); }}
              placeholder={fr.auth.cinPlaceholder}
              style={{
                width: '100%', padding: '12px 16px',
                background: 'var(--bg-elevated)',
                border: `1px solid ${cinError ? 'var(--accent-red)' : 'var(--border-subtle)'}`,
                borderRadius: 'var(--radius-card)', color: 'var(--text-primary)',
                fontSize: '0.9rem', outline: 'none',
              }}
            />
            {cinError && (
              <p style={{ fontSize: '0.72rem', color: 'var(--accent-red)', marginTop: 4 }}>{cinError}</p>
            )}
          </div>

          <div style={{ marginBottom: 'var(--space-md)' }}>
            <label style={{
              display: 'block', fontSize: '0.8rem', fontWeight: 600,
              color: 'var(--text-secondary)', marginBottom: 'var(--space-xs)',
            }} htmlFor="register-password">
              {fr.auth.password}
            </label>
            <input
              id="register-password"
              type="password" required minLength={8} autoComplete="new-password"
              value={password} onChange={(e) => setPassword(e.target.value)}
              placeholder="Min. 8 car., 1 majuscule, 1 chiffre"
              style={{
                width: '100%', padding: '12px 16px',
                background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-card)', color: 'var(--text-primary)',
                fontSize: '0.9rem', outline: 'none',
              }}
            />
            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 4 }}>
              {fr.auth.passwordRules}
            </p>
          </div>

          <div style={{ marginBottom: 'var(--space-lg)' }}>
            <label style={{
              display: 'block', fontSize: '0.8rem', fontWeight: 600,
              color: 'var(--text-secondary)', marginBottom: 'var(--space-xs)',
            }}>
              Profil
            </label>
            <div style={{ display: 'flex', gap: 8 }}>
              <button
                type="button"
                style={{
                  flex: 1, padding: '10px', border: 'none', borderRadius: 'var(--radius-pill)',
                  fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer',
                  background: role === 'buyer' ? 'var(--accent-gold)' : 'var(--bg-elevated)',
                  color: role === 'buyer' ? '#0f1a2b' : 'var(--text-secondary)',
                }}
                onClick={() => setRole('buyer')}
              >
                🛒 {fr.auth.roleBuyer}
              </button>
              <button
                type="button"
                style={{
                  flex: 1, padding: '10px', border: 'none', borderRadius: 'var(--radius-pill)',
                  fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer',
                  background: role === 'seller' ? 'var(--accent-gold)' : 'var(--bg-elevated)',
                  color: role === 'seller' ? '#0f1a2b' : 'var(--text-secondary)',
                }}
                onClick={() => setRole('seller')}
              >
                🏷️ {fr.auth.roleSeller}
              </button>
            </div>
          </div>

          <button
            id="register-submit"
            type="submit"
            disabled={loading || !!phoneError || !!cinError}
            style={{
              width: '100%', padding: '14px 24px',
              background: 'var(--accent-gold)', color: '#0f1a2b',
              border: 'none', borderRadius: 'var(--radius-pill)',
              fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer',
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? fr.general.loading : fr.auth.submitRegister}
          </button>
        </form>

        <p style={{
          textAlign: 'center', marginTop: 'var(--space-lg)',
          fontSize: '0.85rem', color: 'var(--text-muted)',
        }}>
          {fr.auth.haveAccount}{' '}
          <Link to="/login" style={{ color: 'var(--accent-gold)', fontWeight: 600, textDecoration: 'none' }}>
            {fr.auth.loginLink}
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
