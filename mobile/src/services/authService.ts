import api from './api';
import * as SecureStore from 'expo-secure-store';
import { User } from '@vente-auto/shared-types';

export const authService = {
  async login(email: string, password: string):Promise<{ access_token: string; token_type: string }> {
    // Note: FastAPI OAuth2PasswordRequestForm requires form data
    const formData = new FormData();
    formData.append('username', email); // OAuth2 expects 'username'
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    const { access_token } = response.data;
    await SecureStore.setItemAsync('token', access_token);
    
    return response.data;
  },

  async register(data: any): Promise<any> {
    const response = await api.post('/auth/register', data);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/users/me');
    return response.data;
  },

  async logout(): Promise<void> {
    await SecureStore.deleteItemAsync('token');
  },
  
  async getToken(): Promise<string | null> {
    return await SecureStore.getItemAsync('token');
  }
};
