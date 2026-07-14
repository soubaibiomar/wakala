import api from './api';

export interface PricePredictionInput {
  brand: string;
  model: string;
  year: number;
  mileage: number;
  fuel_type: string;
  body_type: string;
  transmission?: string;
  engine_power_hp?: number | null;
  doors?: number;
  seats?: number;
  city: string;
}

export interface ConfidenceInterval {
  low: number;
  high: number;
}

export interface PricePredictionResult {
  predicted_price: number;
  confidence_interval: ConfidenceInterval;
  method: string;
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
      '/vehicles/predict-price',
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
