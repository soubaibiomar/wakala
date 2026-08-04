/**
 * types/user.ts — Interfaces utilisateur (miroir du schema Pydantic backend).
 */

export type UserRole = 'buyer' | 'seller' | 'admin';

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone?: string;
  role: UserRole;
  is_verified: boolean;
  preferences: Record<string, unknown>;
  avatar_url?: string;
  created_at: string;
}

/** Version allégée pour l'imbrication dans véhicules/reviews */
export interface UserBrief {
  id: string;
  name?: string;
  full_name?: string;
  role: UserRole;
  is_verified: boolean;
}

export interface LoginPayload {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  role: UserRole;
  phone?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}
