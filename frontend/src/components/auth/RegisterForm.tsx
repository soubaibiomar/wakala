import { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import api from '../../services/api';

interface RegisterFormProps {
  onSwitchToLogin: () => void;
  onRegisterSuccess: (email: string) => void;
}

export default function RegisterForm({ onSwitchToLogin, onRegisterSuccess }: RegisterFormProps) {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [role, setRole] = useState<'buyer' | 'seller'>('buyer');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas.');
      return;
    }

    setLoading(true);

    try {
      await api.post('/auth/register', {
        full_name: fullName,
        email,
        phone: phone || null,
        password,
        role,
      });
      onRegisterSuccess(email);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Une erreur s'est produite lors de l'inscription.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <h2 className="auth-form-title">Créer un compte</h2>
      <p className="auth-form-subtitle">Rejoignez Wakala pour acheter ou vendre votre prochain véhicule.</p>
      
      {error && <div className="auth-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="auth-form-group" style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
            <input 
              type="radio" 
              name="role" 
              value="buyer" 
              checked={role === 'buyer'} 
              onChange={() => setRole('buyer')} 
            />
            Acheteur
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
            <input 
              type="radio" 
              name="role" 
              value="seller" 
              checked={role === 'seller'} 
              onChange={() => setRole('seller')} 
            />
            Vendeur
          </label>
        </div>

        <div className="auth-form-group">
          <label className="auth-label" htmlFor="fullName">Nom complet</label>
          <input 
            type="text" 
            id="fullName" 
            className="auth-input" 
            placeholder="Jean Dupont"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
            minLength={2}
          />
        </div>

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
          <label className="auth-label" htmlFor="phone">Téléphone</label>
          <input 
            type="tel" 
            id="phone" 
            className="auth-input" 
            placeholder="+2126..."
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
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
              placeholder="Au moins 8 caractères, 1 majuscule, 1 chiffre"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
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

        <div className="auth-form-group">
          <label className="auth-label" htmlFor="confirmPassword">Confirmer le mot de passe</label>
          <div className="password-input-wrapper">
            <input 
              type={showConfirmPassword ? "text" : "password"}
              id="confirmPassword" 
              className="auth-input" 
              placeholder="Confirmez votre mot de passe"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={8}
            />
            <button
              type="button"
              className="password-toggle-btn"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              aria-label={showConfirmPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"}
            >
              {showConfirmPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>
        </div>

        <button type="submit" className="auth-btn" disabled={loading}>
          {loading ? 'Création en cours...' : 'S\'inscrire'}
        </button>
      </form>

      <div className="auth-footer">
        Vous avez déjà un compte ? 
        <button onClick={onSwitchToLogin} type="button">Se connecter</button>
      </div>
    </>
  );
}
