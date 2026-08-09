import api from './api';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { User, TokenResponse } from '@vente-auto/shared-types';

export const authService = {
  async login(email: string, password: string): Promise<TokenResponse> {
    // FastAPI /api/auth/login expects JSON body with email and password
    const response = await api.post<TokenResponse>('/auth/login', {
      email,
      password,
    });

    const { access_token } = response.data;
    if (access_token) {
      if (Platform.OS === 'web') {
        if (typeof window !== 'undefined') localStorage.setItem('token', access_token);
      } else {
        await SecureStore.setItemAsync('token', access_token);
      }
    }
    
    return response.data;
  },

  async register(data: {
    fullName?: string;
    full_name?: string;
    name?: string;
    email: string;
    password: string;
    phone?: string;
    role?: string;
  }): Promise<any> {
    const payload = {
      full_name: data.full_name || data.fullName || data.name || '',
      email: data.email,
      password: data.password,
      phone: data.phone || '+212600000000',
      role: data.role || 'buyer',
    };
    const response = await api.post('/auth/register', payload);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/users/me');
    return response.data;
  },

  async becomeSeller(): Promise<User> {
    const response = await api.post<User>('/users/me/become-seller');
    return response.data;
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.put<User>('/users/me', data);
    return response.data;
  },

  async logout(): Promise<void> {
    if (Platform.OS === 'web') {
      if (typeof window !== 'undefined') localStorage.removeItem('token');
    } else {
      await SecureStore.deleteItemAsync('token');
    }
  },
  
  async getToken(): Promise<string | null> {
    if (Platform.OS === 'web') {
      return typeof window !== 'undefined' ? localStorage.getItem('token') : null;
    }
    return await SecureStore.getItemAsync('token');
  }
};
