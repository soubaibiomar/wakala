import api from './api';
import type { VehicleFilters } from '../types/vehicle';

export interface ScoreBreakdown {
  content: number;
  collaborative: number;
}

export interface WakalaCriteriaScores {
  espace_coffre?: number | null;
  economie_usage?: number | null;
  performance?: number | null;
  securite?: number | null;
  confort?: number | null;
  technologie?: number | null;
  robustesse?: number | null;
  fiabilite?: number | null;
  design?: number | null;
}

export interface RecommendationResult {
  vehicle_id: string;
  match_score: number;
  score_breakdown: ScoreBreakdown;
  key_facts?: string[];
  budget_margin?: number | null;
  best_version_name?: string | null;
  relaxed_filter?: string | null;
  wakala_score_breakdown?: WakalaCriteriaScores;
}

export interface Top3VehicleItem {
  vehicle_id: string;
  brand: string;
  model: string;
  version_name?: string;
  price: number;
  year: number;
  match_score: number;
  score_breakdown: {
    qualite: number;
    budget: number;
    pratique: number;
    criteria: WakalaCriteriaScores;
  };
  key_facts: string[];
  budget_margin?: number | null;
  body_type?: string;
  fuel_type?: string;
  transmission?: string;
  mileage?: number;
  image_url?: string;
}

export interface Top3Response {
  items: Top3VehicleItem[];
  relaxed_filter?: string | null;
  message?: string | null;
}

export interface RecommendationResponse {
  items: RecommendationResult[];
  total: number;
  page: number;
  page_size: number;
  method: 'content-based' | 'hybrid' | 'cold-start';
}

export interface RecommendationRequest {
  query?: string;
  filters?: VehicleFilters;
  user_id?: string | null;
  page?: number;
  page_size?: number;
}

export const recommendationService = {
  async search(params: RecommendationRequest): Promise<RecommendationResponse> {
    const { data } = await api.post<RecommendationResponse>(
      '/recommendation/',
      params
    );
    return data;
  },

  async getTop3(params: {
    query: string;
    quiz_answers?: Record<string, any>;
    user_id?: string | null;
  }): Promise<Top3Response> {
    const { data } = await api.post<Top3Response>(
      '/recommendation/top3',
      params
    );
    return data;
  },
};

