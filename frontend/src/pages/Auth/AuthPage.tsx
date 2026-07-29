import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import LoginForm from '../../components/auth/LoginForm';
import RegisterForm from '../../components/auth/RegisterForm';
import OTPForm from '../../components/auth/OTPForm';
import './AuthPage.css';

export type AuthMode = 'login' | 'register' | 'otp';

export default function AuthPage() {
  const location = useLocation();
  const navigate = useNavigate();
  // By default, if we navigate to /register, mode is register, else login.
  const [mode, setMode] = useState<AuthMode>(
    location.pathname === '/register' ? 'register' : 'login'
  );
  
  // Sync state when URL changes (e.g. clicking Navbar links)
  useEffect(() => {
    if (location.pathname === '/register' && mode !== 'otp') {
      setMode('register');
    } else if (location.pathname === '/login') {
      setMode('login');
    }
  }, [location.pathname]);

  // State passed to OTP form (email of the user trying to verify)
  const [emailForOTP, setEmailForOTP] = useState('');

  const handleSwitchToRegister = () => {
    navigate('/register');
  };

  const handleSwitchToLogin = () => {
    navigate('/login');
  };

  const renderForm = () => {
    switch (mode) {
      case 'login':
        return (
          <LoginForm 
            onSwitchToRegister={handleSwitchToRegister}
            onRequireOTP={(email: string) => {
              setEmailForOTP(email);
              setMode('otp');
            }}
          />
        );
      case 'register':
        return (
          <RegisterForm 
            onSwitchToLogin={handleSwitchToLogin}
            onRegisterSuccess={(email: string) => {
              setEmailForOTP(email);
              setMode('otp');
            }}
          />
        );
      case 'otp':
        return (
          <OTPForm 
            email={emailForOTP}
            onBackToLogin={() => setMode('login')}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-logo-container">
          <img src="/assets/wakala-logo.png" alt="Wakala Logo" className="auth-logo-img" />
        </div>
        <AnimatePresence mode="wait">
          <motion.div
            key={mode}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderForm()}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
