import api from './api';
import { Vehicle } from '../types/vehicle';

export interface CompareResponse {
  vehicles: Vehicle[];
  ai_verdict: string;
}

export const compareService = {
  async getComparison(vehicleIds: string[]): Promise<CompareResponse> {
    const params = new URLSearchParams();
    vehicleIds.forEach(id => params.append('vehicle_ids', id));
    
    const { data } = await api.get<CompareResponse>(`/vehicles/compare?${params.toString()}`);
    return data;
  }
};
