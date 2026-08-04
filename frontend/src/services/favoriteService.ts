import api from './api';
import { Vehicle } from '../types/vehicle';

export const favoriteService = {
  /**
   * Ajoute un véhicule aux favoris
   */
  addFavorite: async (vehicleId: string): Promise<{ message: string }> => {
    const response = await api.post(`/favorites/${vehicleId}`);
    return response.data;
  },

  /**
   * Retire un véhicule des favoris
   */
  removeFavorite: async (vehicleId: string): Promise<void> => {
    await api.delete(`/favorites/${vehicleId}`);
  },

  /**
   * Récupère la liste des véhicules favoris de l'utilisateur
   */
  getFavorites: async (): Promise<Vehicle[]> => {
    const response = await api.get('/favorites/');
    return response.data;
  }
};
