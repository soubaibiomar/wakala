/**
 * services/vehicleService.ts — Appels API véhicules + reviews.
 *
 * Point d'extension pour le moteur de recommandation :
 *   USE_RECOMMENDATION_ENGINE — Quand le module hybride sera prêt,
 *   basculer ce flag sur true pour router les recherches texte
 *   vers /api/recommendations au lieu de /api/vehicles.
 */

import api from './api';
import type { Vehicle, VehicleListResponse, VehicleFilters } from '../types/vehicle';
import type { Review } from '../types/listing';
import { recommendationService } from './recommendationService';
const USE_RECOMMENDATION_ENGINE = false;

export const vehicleService = {
  async getVehicles(filters: VehicleFilters = {}): Promise<VehicleListResponse> {
    if (USE_RECOMMENDATION_ENGINE) {
      // @ts-ignore - TODO: brancher avec le RecommendationService complet.
      return [];
    }

    const params = Object.fromEntries(
      Object.entries(filters).filter(([, v]) => v !== undefined && v !== '')
    );
    const { data } = await api.get<VehicleListResponse>('/vehicles/', { params });
    return data;
  },

  /**
   * Détail d'un véhicule par ID (inclut les infos vendeur).
   */
  async getVehicleById(id: string): Promise<Vehicle> {
    const { data } = await api.get<Vehicle>(`/vehicles/${id}`);
    return data;
  },

  /**
   * Détail d'un véhicule Neuf par slug.
   */
  async getVehicleBySlug(brand: string, model: string, slug: string): Promise<Vehicle> {
    const { data } = await api.get<Vehicle>(`/vehicles/by-slug/${brand}/${model}/${slug}`);
    return data;
  },

  /**
   * Créer un véhicule (seller authentifié).
   */
  async createVehicle(payload: Omit<Vehicle, 'id' | 'seller_id' | 'created_at' | 'updated_at'>): Promise<Vehicle> {
    const { data } = await api.post<Vehicle>('/vehicles/', payload);
    return data;
  },

  /**
   * Mettre à jour un véhicule.
   */
  async updateVehicle(id: string, payload: Partial<Vehicle>): Promise<Vehicle> {
    const { data } = await api.put<Vehicle>(`/vehicles/${id}`, payload);
    return data;
  },

  /**
   * Supprimer un véhicule.
   */
  async deleteVehicle(id: string): Promise<void> {
    await api.delete(`/vehicles/${id}`);
  },
};

// ─── Reviews ──────────────────────────────────────────────────

export const reviewService = {
  /**
   * Liste des avis (filtrés par véhicule ou vendeur).
   */
  async getReviews(params: {
    vehicle_id?: string;
    seller_id?: string;
    min_rating?: number;
    limit?: number;
    offset?: number;
  }): Promise<Review[]> {
    const { data } = await api.get<Review[]>('/reviews/', { params });
    return data;
  },

  /**
   * Publier un avis (utilisateur authentifié).
   */
  async createReview(payload: {
    target_type: 'vehicle' | 'seller';
    vehicle_id?: string;
    seller_id?: string;
    rating: number;
    title?: string;
    comment: string;
  }): Promise<Review> {
    const { data } = await api.post<Review>('/reviews/', payload);
    return data;
  },
};
