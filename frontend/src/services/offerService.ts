import api from './api';
import { Vehicle } from '../types/vehicle';

export interface Offer {
  id: string;
  buyer_id: string;
  vehicle_id: string;
  amount: number;
  status: 'pending' | 'accepted' | 'rejected' | 'countered';
  message: string | null;
  created_at: string;
  updated_at: string;
  vehicle?: Vehicle;
}

export interface OfferCreate {
  vehicle_id: string;
  amount: number;
  message?: string;
}

export const offerService = {
  createOffer: async (data: OfferCreate): Promise<Offer> => {
    const response = await api.post<Offer>('/offers/', data);
    return response.data;
  },

  getSentOffers: async (): Promise<Offer[]> => {
    const response = await api.get<Offer[]>('/offers/sent');
    return response.data;
  },

  getReceivedOffers: async (): Promise<Offer[]> => {
    const response = await api.get<Offer[]>('/offers/received');
    return response.data;
  },

  updateOfferStatus: async (offerId: string, status: 'accepted' | 'rejected' | 'countered'): Promise<Offer> => {
    const response = await api.patch<Offer>(`/offers/${offerId}/status`, { status });
    return response.data;
  }
};
