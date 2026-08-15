import api from './api';

export interface PricePredictionInput {
  brand: string;
  model: string;
  year: number;
  // PIVOT: mileage removed (new vehicles only)
  fuel_type: string;
  body_type: string;
  transmission?: string;
  engine_power_hp?: number | null;
  doors?: number;
  seats?: number;
  city: string;
  // PIVOT: condition_score removed (new vehicles only)
  month?: number;
}

export interface ConfidenceInterval {
  low: number;
  high: number;
}

export interface PricePredictionResult {
  estimated_price: number;  // PIVOT: renamed from predicted_price
  confidence_interval: ConfidenceInterval;
  method: string;
  market_trend?: string;
  features_importance: Record<string, number>;
}

export interface BatchPredictionItem {
  input: PricePredictionInput;
  prediction: PricePredictionResult;
}

export interface BatchPredictionResponse {
  items: BatchPredictionItem[];
  total: number;
}

export interface ModelInfo {
  trained: boolean;
  n_features: number;
  features: string[];
}

export const pricingService = {
  async predict(input: PricePredictionInput): Promise<PricePredictionResult> {
    const { data } = await api.post<PricePredictionResult>(
      '/vehicles/estimate',
      input
    );
    return data;
  },

  async predictBatch(inputs: PricePredictionInput[]): Promise<BatchPredictionResponse> {
    const { data } = await api.post<BatchPredictionResponse>(
      '/vehicles/predict-price/batch',
      { vehicles: inputs }
    );
    return data;
  },

  async getModelInfo(): Promise<ModelInfo> {
    const { data } = await api.get<ModelInfo>('/vehicles/predict-price/model-info');
    return data;
  },
};
