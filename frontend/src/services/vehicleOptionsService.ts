/**
 * services/vehicleOptionsService.ts — Appels API pour les options & configurateur de véhicules.
 */

import api from './api';

export interface VehicleOptionItem {
  id: string;
  vehicle_id: string;
  category: 'accessoire' | 'couleur' | 'jante' | 'sellerie' | 'pack' | string;
  name: string;
  price_delta: number;
  is_default: boolean;
  image_reference?: string | null;
}

export interface VehicleColorItem {
  id: string;
  vehicle_id: string;
  color_name: string;
  hex_code: string;
  price_delta: number;
  is_default: boolean;
}

export interface VehicleWakalaScoreData {
  space_score?: number | null;
  safety_score?: number | null;
  real_cost_score?: number | null;
  access_price_score?: number | null;
  city_practicality_score?: number | null;
  performance_score?: number | null;
  ecology_score?: number | null;
  offroad_score?: number | null;
  overall_score?: number | null;
  data_reliability?: string | null;
  observations?: string | null;
  source_note?: string | null;
}

export interface VehicleConfiguratorData {
  vehicle_id: string;
  brand: string;
  model: string;
  version?: string | null;
  base_price: number;
  colors: VehicleColorItem[];
  options: VehicleOptionItem[];
  options_by_category: Record<string, VehicleOptionItem[]>;
  wakala_scores?: VehicleWakalaScoreData | null;
}

export const vehicleOptionsService = {
  /**
   * Récupère les options, couleurs et notes Wakala pour un véhicule donné.
   */
  async getVehicleOptions(vehicleId: string): Promise<VehicleConfiguratorData> {
    const { data } = await api.get<VehicleConfiguratorData>(`/vehicles/${vehicleId}/options`);
    return data;
  },
};
