/**
 * context/AuthContext.tsx — État d'authentification global.
 *
 * Fournit :
 *   useAuth() → { user, token, isAuthenticated, login, register, logout, loading }
 *
 * Le token JWT est conservé uniquement en mémoire pour éviter son exposition
 * aux scripts injectés dans le navigateur.
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
import { setSessionToken, clearSessionToken } from '../services/api';

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

export const AuthContext = createContext<AuthState | undefined>(undefined);

// ─── Provider ─────────────────────────────────────────────────

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(false);
  }, []);

  const login = async (payload: LoginPayload): Promise<User> => {
    const response: TokenResponse = await authService.login(payload);
    setToken(response.access_token);
    setSessionToken(response.access_token);
    setUser(response.user);
    return response.user;
  };

  const googleLogin = async (tokenStr: string, rememberMe?: boolean): Promise<User> => {
    const response: TokenResponse = await authService.googleLogin(tokenStr, rememberMe);
    setToken(response.access_token);
    setSessionToken(response.access_token);
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
    setSessionToken(response.access_token);
    setUser(response.user);
    return newUser;
  };

  const logout = () => {
    setToken(null);
    clearSessionToken();
    setUser(null);
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
