import api from './api';

export interface VisionAnalysisResponse {
  condition_score: number;
  fraud_detected: boolean;
  blur_variance: number;
  anomalies_count: number;
  image_base64: string;
}

export const visionService = {
  async analyzeImage(file: File): Promise<VisionAnalysisResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await api.post<VisionAnalysisResponse>(
      '/v1/vision/analyze',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return data;
  },
};
