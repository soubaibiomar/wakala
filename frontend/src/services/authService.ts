/**
 * services/authService.ts — Appels API d'authentification.
 */

import api from './api';
import type { User, LoginPayload, RegisterPayload, TokenResponse } from '../types/user';

export const authService = {
  /**
   * Inscription d'un nouvel utilisateur.
   */
  async register(payload: RegisterPayload): Promise<User> {
    const { data } = await api.post<User>('/auth/register', payload);
    return data;
  },

  /**
   * Connexion — retourne un JWT + les infos utilisateur.
   */
  async login(payload: LoginPayload): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>('/auth/login', payload);
    return data;
  },

  /**
   * Connexion avec Google OAuth
   */
  async googleLogin(token: string, remember_me: boolean = false): Promise<TokenResponse> {
    const { data } = await api.post<TokenResponse>('/auth/google-login', { token, remember_me });
    return data;
  },

  /**
   * Récupère le profil de l'utilisateur connecté.
   */
  async getMe(): Promise<User> {
    const { data } = await api.get<User>('/users/me');
    return data;
  },

  /**
   * Met à jour le profil de l'utilisateur connecté.
   */
  async updateMe(payload: Partial<User>): Promise<User> {
    const { data } = await api.put<User>('/users/me', payload);
    return data;
  },

  /**
   * Passer au statut vendeur.
   */
  async becomeSeller(): Promise<User> {
    const { data } = await api.post<User>('/users/me/become-seller');
    return data;
  },
};
