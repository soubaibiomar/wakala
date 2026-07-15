import AsyncStorage from '@react-native-async-storage/async-storage';

const CACHE_KEYS = {
  SEARCHES: '@cache_recent_searches',
  FAVORITES: '@cache_favorites',
  CATALOGUE: '@cache_catalogue',
};

export const offlineCache = {
  // --- Catalogue ---
  async saveCatalogue(vehicles: any[]) {
    try {
      await AsyncStorage.setItem(CACHE_KEYS.CATALOGUE, JSON.stringify(vehicles));
    } catch (e) {
      console.warn('Error saving catalogue to cache', e);
    }
  },
  async getCatalogue(): Promise<any[] | null> {
    try {
      const data = await AsyncStorage.getItem(CACHE_KEYS.CATALOGUE);
      return data ? JSON.parse(data) : null;
    } catch (e) {
      console.warn('Error reading catalogue from cache', e);
      return null;
    }
  },

  // --- Recherches Récentes ---
  async saveRecentSearch(query: string) {
    try {
      const existingStr = await AsyncStorage.getItem(CACHE_KEYS.SEARCHES);
      let searches: string[] = existingStr ? JSON.parse(existingStr) : [];
      
      // Add to top, remove duplicates
      searches = [query, ...searches.filter(s => s !== query)].slice(0, 5); // Keep last 5
      
      await AsyncStorage.setItem(CACHE_KEYS.SEARCHES, JSON.stringify(searches));
    } catch (e) {
      console.warn('Error saving recent search', e);
    }
  },
  async getRecentSearches(): Promise<string[]> {
    try {
      const data = await AsyncStorage.getItem(CACHE_KEYS.SEARCHES);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.warn('Error reading recent searches', e);
      return [];
    }
  },

  // --- Favoris (si besoin hors-ligne) ---
  async saveFavorites(vehicleIds: string[]) {
    try {
      await AsyncStorage.setItem(CACHE_KEYS.FAVORITES, JSON.stringify(vehicleIds));
    } catch (e) {
      console.warn('Error saving favorites', e);
    }
  },
  async getFavorites(): Promise<string[]> {
    try {
      const data = await AsyncStorage.getItem(CACHE_KEYS.FAVORITES);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.warn('Error reading favorites', e);
      return [];
    }
  }
};
