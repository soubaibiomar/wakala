/**
 * services/listingService.ts — Appels API annonces (listings).
 */

import api from './api';
import type { Listing, ListingCreatePayload, ListingStatus } from '../types/listing';

export const listingService = {
  /**
   * Liste des annonces (filtrées par statut).
   */
  async getListings(
    status: ListingStatus = 'active',
    limit = 20,
    offset = 0
  ): Promise<Listing[]> {
    const { data } = await api.get<Listing[]>('/listings/', {
      params: { status, limit, offset },
    });
    return data;
  },

  /**
   * Liste des annonces de l'utilisateur connecté (vendeur).
   */
  async getMyListings(
    limit = 50,
    offset = 0
  ): Promise<Listing[]> {
    const { data } = await api.get<Listing[]>('/listings/me', {
      params: { limit, offset },
    });
    return data;
  },

  /**
   * Détail d'une annonce par ID.
   */
  async getListingById(id: string): Promise<Listing> {
    const { data } = await api.get<Listing>(`/listings/${id}`);
    return data;
  },

  /**
   * Créer une annonce liée à un véhicule.
   */
  async createListing(payload: ListingCreatePayload): Promise<Listing> {
    const { data } = await api.post<Listing>('/listings/', payload);
    return data;
  },

  /**
   * Mettre à jour une annonce (statut, images, etc.).
   */
  async updateListing(id: string, payload: Partial<Listing>): Promise<Listing> {
    const { data } = await api.patch<Listing>(`/listings/${id}`, payload);
    return data;
  },
};
