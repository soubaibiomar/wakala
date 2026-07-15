import api from './api';

export interface TransactionResponse {
  id: string;
  listing_id: string;
  amount: number;
  status: string;
  payment_intent_id: string | null;
}

export const transactionService = {
  async initiateTransaction(listingId: string): Promise<TransactionResponse> {
    const { data } = await api.post<TransactionResponse>('/v1/transactions/initiate', {
      listing_id: listingId
    });
    return data;
  },

  async simulateWebhookPayment(txId: string): Promise<{ status: string; message: string }> {
    const { data } = await api.post(`/v1/transactions/${txId}/webhook-pay`);
    return data;
  },

  async uploadDocument(txId: string, file: File): Promise<{ status: string; message: string }> {
    const formData = new FormData();
    formData.append('file', file);
    
    const { data } = await api.post(`/v1/transactions/${txId}/upload-document`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  }
};
