import api from './api';
import type { VehicleFilters } from '../types/vehicle';

export interface ScoreBreakdown {
  content: number;
  collaborative: number;
}

export interface RecommendationResult {
  vehicle_id: string;
  match_score: number;
  score_breakdown: ScoreBreakdown;
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
};
