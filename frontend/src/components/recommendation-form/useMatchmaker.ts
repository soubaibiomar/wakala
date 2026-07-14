import { useCallback, useState } from 'react';
import {
  recommendationService,
  type RecommendationRequest,
  type RecommendationResponse,
} from '../../services/recommendationService';

export function useMatchmaker() {
  const [result, setResult] = useState<RecommendationResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const recommend = useCallback(async (request: RecommendationRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await recommendationService.search({ page_size: 12, ...request });
      setResult(response);
      return response;
    } catch {
      setError('Les recommandations sont momentanément indisponibles.');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { result, isLoading, error, recommend };
}
