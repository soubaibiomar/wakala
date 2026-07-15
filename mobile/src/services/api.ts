import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

// We use 10.0.2.2 for Android emulator to access localhost, 
// or the local IP for physical devices.
const API_URL = 'http://10.0.2.2:8000/api'; 

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
