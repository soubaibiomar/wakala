import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Vehicle } from '@vente-auto/shared-types';

export const vehicleService = {
  async getVehicles(params?: any): Promise<Vehicle[]> {
    try {
      const response = await api.get('/vehicles/', { params });
      const data = response.data;
      const list = Array.isArray(data) ? data : (data?.items || []);
      
      // Cache results for offline use
      if (list && list.length > 0) {
        await AsyncStorage.setItem('cached_vehicles', JSON.stringify(list));
      }
      return list;
    } catch (error) {
      console.warn('API error, falling back to cache:', error);
      const cached = await AsyncStorage.getItem('cached_vehicles');
      if (cached) {
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

  async getMyVehicles(): Promise<Vehicle[]> {
    const response = await api.get('/vehicles/me');
    return response.data;
  },

  async getMyListings(): Promise<any[]> {
    const response = await api.get('/listings/me');
    return response.data;
  },
  
  async analyzeImage(id: string, formData: FormData): Promise<any> {
    const url = id && id !== 'temp' ? `/vehicles/${id}/analyze-images` : '/v1/vision/analyze';
    const response = await api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async predictPrice(data: {
    brand: string;
    model: string;
    year: number;
    mileage?: number;
    fuel_type?: string;
    transmission?: string;
    city?: string;
  }): Promise<any> {
    const response = await api.post('/predict-price', {
      brand: data.brand,
      model: data.model,
      year: data.year,
      mileage: data.mileage ?? 50000,
      fuel_type: data.fuel_type || 'Diesel',
      transmission: data.transmission || 'Manuelle',
      city: data.city || 'Casablanca'
    });
    return response.data;
  },

  async generateDescription(data: {
    brand: string;
    model: string;
    year: number;
    mileage?: number;
    city?: string;
    fuel_type?: string;
    transmission?: string;
  }): Promise<any> {
    const response = await api.post('/listings/generate', data);
    return response.data;
  },

  async createVehicle(data: any): Promise<Vehicle> {
    const response = await api.post('/vehicles', data);
    return response.data;
  },

  async createListing(data: {
    brand: string;
    model: string;
    year: number;
    price: number;
    city: string;
    mileage?: number;
    fuel_type?: string;
    transmission?: string;
    description?: string;
    images?: string[];
  }): Promise<any> {
    // 1. Créer le véhicule en base
    const vehiclePayload = {
      brand: data.brand,
      model: data.model,
      year: data.year,
      price: data.price,
      city: data.city,
      mileage: data.mileage ?? 0,
      fuel_type: data.fuel_type || 'Diesel',
      transmission: data.transmission || 'Manuelle',
      description: data.description || '',
    };
    
    const vehicleRes = await api.post('/vehicles', vehiclePayload);
    const createdVehicle = vehicleRes.data;

    // 2. Créer l'annonce attachée au véhicule
    const listingPayload = {
      vehicle_id: createdVehicle.id,
      title: `${data.brand} ${data.model} (${data.year})`,
      price: data.price,
      description: data.description || '',
      status: 'active',
    };

    const listingRes = await api.post('/listings', listingPayload);
    return {
      vehicle: createdVehicle,
      listing: listingRes.data,
    };
  }
};
