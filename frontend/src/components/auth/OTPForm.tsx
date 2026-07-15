import { useState, useRef, KeyboardEvent, ChangeEvent } from 'react';

import api from '../../services/api';

interface OTPFormProps {
  email: string;
  onBackToLogin: () => void;
}

export default function OTPForm({ email, onBackToLogin }: OTPFormProps) {
  const [otp, setOtp] = useState<string[]>(Array(6).fill(''));
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const handleChange = (element: HTMLInputElement, index: number) => {
    if (isNaN(Number(element.value))) return;

    const newOtp = [...otp];
    newOtp[index] = element.value;
    setOtp(newOtp);

    // Focus next input
    if (element.value !== '' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>, index: number) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      // Focus previous input on backspace if current is empty
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const otpCode = otp.join('');
    
    if (otpCode.length !== 6) {
      setError('Veuillez saisir les 6 chiffres du code.');
      return;
    }

    setError('');
    setLoading(true);

    try {
      await api.post('/auth/verify-email', {
        email,
        otp_code: otpCode,
      });
      // Verification successful, redirect to login
      onBackToLogin();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Code OTP invalide ou expiré.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <h2 className="auth-form-title">Vérification</h2>
      <p className="auth-form-subtitle">
        Un code à 6 chiffres a été envoyé à <strong>{email}</strong>.
      </p>
      
      {error && <div className="auth-error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="otp-container">
          {otp.map((data, index) => (
            <input
              className="otp-input"
              type="text"
              name="otp"
              maxLength={1}
              key={index}
              value={data}
              onChange={(e: ChangeEvent<HTMLInputElement>) => handleChange(e.target, index)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              ref={(el) => (inputRefs.current[index] = el)}
              autoFocus={index === 0}
            />
          ))}
        </div>

        <button type="submit" className="auth-btn" disabled={loading}>
          {loading ? 'Vérification...' : 'Valider le code'}
        </button>
      </form>

      <div className="auth-footer">
        <button onClick={onBackToLogin} type="button">Retour à la connexion</button>
      </div>
    </>
  );
}
