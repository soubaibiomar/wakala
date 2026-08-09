import api from './api';

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

export interface RecommendationResponse {
  items: RecommendationResult[];
  total: number;
  page: number;
  page_size: number;
  method: 'content-based' | 'hybrid' | 'cold-start';
}

export interface RecommendationRequest {
  query?: string;
  filters?: any;
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
  }
};
