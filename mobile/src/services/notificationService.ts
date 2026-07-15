import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import api from './api';

// Configuration locale du comportement des notifications
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

export const notificationService = {
  /**
   * Demande la permission et enregistre le token sur le backend.
   * À appeler APRÈS une action engageante (ex: première recherche sauvegardée).
   */
  async registerForPushNotificationsAsync(): Promise<string | null> {
    let token;

    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'default',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#AE8C4E',
      });
    }

    const { status: existingStatus } = await Notifications.getPermissionsAsync();
    let finalStatus = existingStatus;
    
    if (existingStatus !== 'granted') {
      const { status } = await Notifications.requestPermissionsAsync();
      finalStatus = status;
    }
    
    if (finalStatus !== 'granted') {
      console.log('Permission de notification refusée.');
      return null;
    }

    try {
      token = (await Notifications.getExpoPushTokenAsync()).data;
      console.log('Push token:', token);
      
      // Envoi du token au backend pour le lier au profil utilisateur
      // Même si l'endpoint est nouveau, on respecte la consigne (POST /api/users/push-token)
      await api.post('/users/push-token', { token });
      
    } catch (e) {
      console.warn('Erreur récupération token push:', e);
    }

    return token || null;
  }
};
