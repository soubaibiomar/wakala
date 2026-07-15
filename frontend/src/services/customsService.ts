import api from './api';

export interface CustomsRequest {
  brand: string;
  model: string;
  year: number;
  fuel_type: string;
  fiscal_power: number;
  origin_eu: boolean;
  purchase_price_origin: number;
}

export interface CustomsResponse {
  financial_breakdown: {
    purchase_price: number;
    import_duty: number;
    parafiscal_tax: number;
    vat: number;
    additional_tax: number;
    total_customs_fees: number;
    total_cost: number;
    breakdown: Array<{label: string, amount: number, color: string}>;
  };
  local_market_price: number;
  ai_verdict: string;
}

export const customsService = {
  async calculate(data: CustomsRequest): Promise<CustomsResponse> {
    const response = await api.post<CustomsResponse>('/v1/customs/calculate', data);
    return response.data;
  }
};
