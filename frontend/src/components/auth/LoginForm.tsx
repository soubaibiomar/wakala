import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { GoogleLogin } from '@react-oauth/google';


interface LoginFormProps {
  onSwitchToRegister: () => void;
  onRequireOTP: (email: string) => void;
}

export default function LoginForm({ onSwitchToRegister, onRequireOTP }: LoginFormProps) {
  const { login, googleLogin } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ email, password, remember_me: rememberMe });
      // If login succeeds, the context will redirect to / (Home)
    } catch (err: any) {
      if (err.response?.status === 403 && err.response?.data?.detail?.includes('vérifier')) {
        // User not verified, switch to OTP
        onRequireOTP(email);
      } else {
        const detail = err.response?.data?.detail;
        let errorMsg = 'Email ou mot de passe incorrect.';
        if (typeof detail === 'string') {
          errorMsg = detail;
        } else if (Array.isArray(detail)) {
          errorMsg = detail.map(d => d.msg || JSON.stringify(d)).join(', ');
        } else if (typeof detail === 'object' && detail !== null) {
          errorMsg = detail.msg || JSON.stringify(detail);
        }
        setError(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <h2 className="auth-form-title">Bon retour</h2>
      <p className="auth-form-subtitle">Connectez-vous pour accéder à votre espace Wakala.</p>
      
      {error && <div className="auth-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="auth-form-group">
          <label className="auth-label" htmlFor="email">Adresse E-mail</label>
          <input 
            type="email" 
            id="email" 
            className="auth-input" 
            placeholder="vous@exemple.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>

        <div className="auth-form-group">
          <label className="auth-label" htmlFor="password">Mot de passe</label>
          <div className="password-input-wrapper">
            <input 
              type={showPassword ? "text" : "password"}
              id="password" 
              className="auth-input" 
              placeholder="Votre mot de passe"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button
              type="button"
              className="password-toggle-btn"
              onClick={() => setShowPassword(!showPassword)}
              aria-label={showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>
        </div>

        <div className="auth-form-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '-0.5rem' }}>
          <input 
            type="checkbox" 
            id="rememberMe" 
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
          />
          <label htmlFor="rememberMe" style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
            Se souvenir de moi
          </label>
        </div>

        <button type="submit" className="auth-btn" disabled={loading}>
          {loading ? 'Connexion en cours...' : 'Se connecter'}
        </button>

        <div style={{ display: 'flex', alignItems: 'center', margin: '1.5rem 0' }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-glass-border)' }}></div>
          <span style={{ padding: '0 1rem', fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>Ou continuer avec</span>
          <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-glass-border)' }}></div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center' }}>
          <GoogleLogin
            onSuccess={async (credentialResponse: any) => {
              try {
                if (credentialResponse.credential) {
                  await googleLogin(credentialResponse.credential, rememberMe);
                }
              } catch (err) {
                setError("Erreur lors de la connexion Google");
              }
            }}
            onError={() => {
              setError("La connexion avec Google a échoué");
            }}
            theme="outline"
            size="large"
            shape="rectangular"
            text="signin_with"
            width="100%"
          />
        </div>
      </form>

      <div className="auth-footer">
        Nouveau sur Wakala ? 
        <button onClick={onSwitchToRegister} type="button">Créer un compte</button>
      </div>
    </>
  );
}
