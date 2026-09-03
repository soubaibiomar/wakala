import axios from 'axios';
import { Platform } from 'react-native';
import * as SecureStore from 'expo-secure-store';

let webSessionToken: string | null = null;
export const setWebSessionToken = (token: string | null) => { webSessionToken = token; };
export const getWebSessionToken = () => webSessionToken;

const DEFAULT_API_URL = process.env.EXPO_PUBLIC_API_URL || 
  (Platform.OS === 'android' 
    ? 'http://10.0.2.2:8000/api' 
    : 'http://localhost:8000/api');

const api = axios.create({
  baseURL: DEFAULT_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

api.interceptors.request.use(async (config) => {
  try {
    let token: string | null = null;
    if (Platform.OS === 'web') {
      token = webSessionToken;
    } else {
      token = await SecureStore.getItemAsync('token');
    }
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  } catch (err) {
    console.warn('Could not read auth token', err);
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      try {
        if (Platform.OS === 'web') {
          webSessionToken = null;
        } else {
          await SecureStore.deleteItemAsync('token');
        }
      } catch (e) {
        // ignore
      }
    }
    return Promise.reject(error);
  }
);

export default api;
