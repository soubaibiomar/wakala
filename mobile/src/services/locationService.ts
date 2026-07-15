import * as Location from 'expo-location';

export const locationService = {
  /**
   * Demande la permission UNIQUEMENT au moment pertinent.
   * Retourne la ville la plus proche si la permission est accordée.
   */
  async getNearestCity(): Promise<string | null> {
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      
      if (status !== 'granted') {
        console.log('Permission de localisation refusée par l\'utilisateur.');
        return null;
      }

      const location = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      
      // Reverse geocoding pour trouver la ville (fonctionnalité native d'expo-location)
      const geocode = await Location.reverseGeocodeAsync({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude
      });

      if (geocode && geocode.length > 0) {
        return geocode[0].city || geocode[0].region || null;
      }
      
      return null;
    } catch (e) {
      console.warn("Erreur lors de la récupération de la position:", e);
      return null;
    }
  }
};
