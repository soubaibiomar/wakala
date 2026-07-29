/**
 * types/vehicle.ts — Interfaces véhicule (miroir du schema Pydantic backend).
 */

export type FuelType =
  | 'essence' | 'diesel' | 'hybride' | 'hybride_rechargeable'
  | 'electrique' | 'gpl' | 'hydrogene';

export type BodyType =
  | 'citadine' | 'berline' | 'suv' | 'break' | 'coupe'
  | 'cabriolet' | 'monospace' | 'utilitaire' | 'pick_up';

export type TransmissionType = 'manuelle' | 'automatique' | 'semi_auto';

export interface Vehicle {
  id: string;
  seller_id: string;
  brand: string;
  model: string;
  version?: string;
  year: number;
  mileage: number;
  fuel_type: FuelType;
  body_type: BodyType;
  transmission: TransmissionType;
  engine_power_hp?: number;
  color?: string;
  doors: number;
  seats: number;
  city: string;
  postal_code?: string;
  price: number;
  description?: string;
  status?: string;

  // Champs IA (nullable — remplis par les modules ML)
  predicted_price?: number;
  price_confidence?: number;
  condition_score?: number;   // ← Module vision
  popularity_score?: number;  // ← Neo4j PageRank
  images?: Array<{ file_path: string }>;

  created_at: string;
  updated_at: string;

  // Relations imbriquées (selon l'endpoint)
  seller?: import('./user').UserBrief;
  source_url?: string;
}

export interface VehicleListResponse {
  items: Vehicle[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface VehicleFilters {
  brand?: string;
  model?: string;
  city?: string;
  fuel_type?: FuelType | '';
  body_type?: BodyType | '';
  transmission?: TransmissionType | '';
  price_min?: number;
  price_max?: number;
  year_min?: number;
  year_max?: number;
  mileage_max?: number;
  condition?: 'neuf' | 'occasion';
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  page?: number;
  page_size?: number;
}

/** Labels affichables pour les types de carburant */
export const FUEL_LABELS: Record<FuelType, string> = {
  essence: 'Essence',
  diesel: 'Diesel',
  hybride: 'Hybride',
  hybride_rechargeable: 'PHEV',
  electrique: '⚡ Électrique',
  gpl: 'GPL',
  hydrogene: 'Hydrogène',
};

/** Labels affichables pour les types de carrosserie */
export const BODY_LABELS: Record<BodyType, string> = {
  citadine: 'Citadine',
  berline: 'Berline',
  suv: 'SUV',
  break: 'Break',
  coupe: 'Coupé',
  cabriolet: 'Cabriolet',
  monospace: 'Monospace',
  utilitaire: 'Utilitaire',
  pick_up: 'Pick-up',
};

export const TRANSMISSION_LABELS: Record<TransmissionType, string> = {
  manuelle: 'Manuelle',
  automatique: 'Automatique',
  semi_auto: 'Semi-auto',
};
