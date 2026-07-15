import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';


interface LoginFormProps {
  onSwitchToRegister: () => void;
  onRequireOTP: (email: string) => void;
}

export default function LoginForm({ onSwitchToRegister, onRequireOTP }: LoginFormProps) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ email, password });
      // If login succeeds, the context will redirect to / (Home)
    } catch (err: any) {
      if (err.response?.status === 403 && err.response?.data?.detail?.includes('vérifier')) {
        // User not verified, switch to OTP
        onRequireOTP(email);
      } else {
        setError(err.response?.data?.detail || 'Email ou mot de passe incorrect.');
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

        <button type="submit" className="auth-btn" disabled={loading}>
          {loading ? 'Connexion en cours...' : 'Se connecter'}
        </button>
      </form>

      <div className="auth-footer">
        Nouveau sur Wakala ? 
        <button onClick={onSwitchToRegister} type="button">Créer un compte</button>
      </div>
    </>
  );
}
