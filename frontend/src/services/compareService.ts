import api from './api';
import { Vehicle } from '../types/vehicle';

export interface CompareResponse {
  vehicles: Vehicle[];
  ai_verdict?: string;
}

export const compareService = {
  async getComparison(vehicleIds: string[]): Promise<CompareResponse> {
    // Load the selected records directly and in parallel. The old aggregate
    // endpoint performed an AI synthesis before returning otherwise simple data.
    const vehicles = await Promise.all(
      vehicleIds.map(async (id) => {
        const { data } = await api.get<Vehicle>(`/vehicles/${id}`);
        return data;
      }),
    );
    return { vehicles, ai_verdict: '' };
  }
};
