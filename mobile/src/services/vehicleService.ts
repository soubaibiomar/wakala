import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Vehicle } from '@vente-auto/shared-types';

export const vehicleService = {
  async getVehicles(params?: any): Promise<Vehicle[]> {
    try {
      const response = await api.get('/vehicles', { params });
      
      // Cache results for offline use
      if (response.data && response.data.length > 0) {
        await AsyncStorage.setItem('cached_vehicles', JSON.stringify(response.data));
      }
      return response.data;
    } catch (error) {
      console.warn('API error, falling back to cache:', error);
      const cached = await AsyncStorage.getItem('cached_vehicles');
      if (cached) {
        // We might want to add a flag indicating this is offline data
        const parsed = JSON.parse(cached);
        return parsed.map((v: any) => ({ ...v, _isOffline: true }));
      }
      throw error;
    }
  },

  async getVehicle(id: string): Promise<Vehicle> {
    const response = await api.get(`/vehicles/${id}`);
    return response.data;
  },
  
  async analyzeImage(id: string, formData: FormData): Promise<any> {
    // Si pas d'ID, on utilise le nouveau endpoint global /v1/vision/analyze 
    // ou on garde le /vehicles/${id}/analyze-images selon le backend actuel
    const url = id && id !== 'temp' ? `/vehicles/${id}/analyze-images` : '/v1/vision/analyze';
    const response = await api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async predictPrice(data: any): Promise<any> {
    // routes_pricing.py est monté sur /api dans main.py, avec le path /predict-price
    const response = await api.post('/predict-price', data);
    return response.data;
  },

  async createListing(data: any): Promise<any> {
    const response = await api.post('/listings', data);
    return response.data;
  },

  async generateDescription(data: any): Promise<any> {
    const response = await api.post('/listings/generate', data);
    return response.data;
  }
};
