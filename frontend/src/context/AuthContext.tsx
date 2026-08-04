/**
 * context/AuthContext.tsx — État d'authentification global.
 *
 * Fournit :
 *   useAuth() → { user, token, isAuthenticated, login, register, logout, loading }
 *
 * Le token JWT est stocké en mémoire (state) ET dans localStorage
 * pour survivre aux rechargements de page.
 */

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import type { User, LoginPayload, RegisterPayload, TokenResponse } from '../types/user';
import { authService } from '../services/authService';

// ─── Interface du contexte ────────────────────────────────────

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (payload: LoginPayload) => Promise<User>;
  googleLogin: (token: string, rememberMe?: boolean) => Promise<User>;
  register: (payload: RegisterPayload) => Promise<User>;
  logout: () => void;
  updateUser: (user: User) => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

// ─── Provider ─────────────────────────────────────────────────

const TOKEN_KEY = 'wakala_token';
const USER_KEY = 'wakala_user';

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Restaurer la session depuis localStorage au montage
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY);
    const storedUser = localStorage.getItem(USER_KEY);

    if (storedToken && storedUser) {
      try {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      }
    }
    setLoading(false);
  }, []);

  // Persister le token à chaque changement
  useEffect(() => {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  }, [token]);

  useEffect(() => {
    if (user) {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(USER_KEY);
    }
  }, [user]);

  const login = async (payload: LoginPayload): Promise<User> => {
    const response: TokenResponse = await authService.login(payload);
    setToken(response.access_token);
    setUser(response.user);
    return response.user;
  };

  const googleLogin = async (tokenStr: string, rememberMe?: boolean): Promise<User> => {
    const response: TokenResponse = await authService.googleLogin(tokenStr, rememberMe);
    setToken(response.access_token);
    setUser(response.user);
    return response.user;
  };

  const register = async (payload: RegisterPayload): Promise<User> => {
    const newUser = await authService.register(payload);
    // Auto-login après inscription
    const response = await authService.login({
      email: payload.email,
      password: payload.password,
    });
    setToken(response.access_token);
    setUser(response.user);
    return newUser;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  };

  const value = useMemo<AuthState>(
    () => ({
      user,
      token,
      isAuthenticated: !!token && !!user,
      loading,
      login,
      googleLogin,
      register,
      logout,
      updateUser: setUser,
    }),
    [user, token, loading]
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// ─── Hook ─────────────────────────────────────────────────────

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth() doit être utilisé dans un <AuthProvider>');
  }
  return context;
}
