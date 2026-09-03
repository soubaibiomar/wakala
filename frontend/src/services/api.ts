/**
 * services/api.ts — Instance Axios configurée.
 *
 * - baseURL pointant vers le backend FastAPI
 * - Injection automatique du JWT via intercepteur
 * - Gestion centralisée des erreurs 401 (token expiré)
 *
 * Tous les autres services importent cette instance.
 */

import axios from 'axios';

let sessionToken: string | null = null;
export const setSessionToken = (token: string | null) => { sessionToken = token; };
export const getSessionToken = () => sessionToken;
export const clearSessionToken = () => { sessionToken = null; };

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://originally-demonstrated-multi-pressed.trycloudflare.com/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Intercepteur requête : injecter le JWT ──────────────────
api.interceptors.request.use((config) => {
  const token = sessionToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ─── Intercepteur réponse : gérer les erreurs réseau ─────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expiré ou invalide — nettoyer et laisser le AuthContext gérer
      clearSessionToken();
    }
    return Promise.reject(error);
  }
);

export default api;
