import React, { useState } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, ActivityIndicator, Alert, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { tokens } from '../styles/tokens';
import { useAuth } from '../context/AuthContext';

export default function ProfileScreen() {
  const { user, logout, becomeSeller, isAuthenticated, isLoading } = useAuth();
  const navigation = useNavigation<any>();
  const [upgrading, setUpgrading] = useState(false);

  if (isLoading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={tokens.colors.accentGold} />
      </View>
    );
  }

  if (!isAuthenticated || !user) {
    return (
      <View style={styles.center}>
        <Text style={styles.infoTitle}>Espace Personnel</Text>
        <Text style={styles.infoText}>Connectez-vous pour accéder à vos favoris, messages et publier des annonces.</Text>
        <TouchableOpacity 
          style={styles.button}
          onPress={() => navigation.navigate('Login')}
        >
          <Text style={styles.buttonText}>Se connecter / S'inscrire</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const handleBecomeSeller = async () => {
    Alert.alert(
      'Devenir Vendeur',
      'Souhaitez-vous activer votre espace vendeur pour publier des annonces et estimer vos véhicules ?',
      [
        { text: 'Annuler', style: 'cancel' },
        {
          text: 'Confirmer',
          onPress: async () => {
            setUpgrading(true);
            try {
              await becomeSeller();
              Alert.alert('Félicitations !', 'Votre compte est maintenant un compte Vendeur. Vous pouvez publier vos annonces.');
            } catch (err: any) {
              console.error(err);
              Alert.alert('Erreur', 'Impossible de mettre à jour votre statut. Veuillez réessayer.');
            } finally {
              setUpgrading(false);
            }
          }
        }
      ]
    );
  };

  const displayName = user.full_name || user.name || 'Utilisateur';

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Mon Profil</Text>
      </View>
      
      <View style={styles.card}>
        <Text style={styles.label}>Nom complet</Text>
        <Text style={styles.value}>{displayName}</Text>
        
        <Text style={styles.label}>Email</Text>
        <Text style={styles.value}>{user.email}</Text>
        
        <Text style={styles.label}>Téléphone</Text>
        <Text style={styles.value}>{user.phone || 'Non renseigné'}</Text>
        
        <Text style={styles.label}>Statut du Compte</Text>
        <View style={styles.roleRow}>
          <Text style={[styles.valueBadge, user.role === 'seller' ? styles.badgeSeller : styles.badgeBuyer]}>
            {user.role === 'seller' ? '👑 Vendeur Certifié' : '🚗 Acheteur'}
          </Text>
        </View>
        
        {user.role === 'buyer' && (
          <View style={styles.becomeSellerCard}>
            <Text style={styles.becomeSellerTitle}>Vendez votre véhicule sur Wakala</Text>
            <Text style={styles.becomeSellerSubtitle}>
              Passez au statut vendeur en 1 clic pour publier des annonces avec estimation IA et photos certifiées.
            </Text>
            <TouchableOpacity 
              style={styles.becomeSellerButton} 
              onPress={handleBecomeSeller}
              disabled={upgrading}
            >
              {upgrading ? (
                <ActivityIndicator color={tokens.colors.textInverse} size="small" />
              ) : (
                <Text style={styles.becomeSellerButtonText}>✨ Devenir Vendeur</Text>
              )}
            </TouchableOpacity>
          </View>
        )}

        {user.role === 'seller' && (
          <TouchableOpacity 
            style={styles.dashboardButton} 
            onPress={() => navigation.navigate('SellerDashboard')}
          >
            <Text style={styles.dashboardButtonText}>📊 Accéder au Tableau de Bord Vendeur</Text>
          </TouchableOpacity>
        )}
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={logout}>
        <Text style={styles.logoutText}>Se déconnecter</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: tokens.colors.bgSecondary,
  },
  content: {
    paddingBottom: tokens.spacing.xxl,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: tokens.colors.bgSecondary,
    padding: tokens.spacing.lg,
  },
  header: {
    padding: tokens.spacing.lg,
    backgroundColor: tokens.colors.bgPrimary,
    borderBottomWidth: 1,
    borderBottomColor: tokens.borders.subtle,
  },
  headerTitle: {
    fontFamily: tokens.typography.display,
    fontSize: 28,
    color: tokens.colors.textPrimary,
  },
  card: {
    margin: tokens.spacing.md,
    backgroundColor: tokens.colors.bgPrimary,
    borderRadius: tokens.radii.lg,
    padding: tokens.spacing.lg,
    ...tokens.shadows.card,
  },
  label: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.textMuted,
    textTransform: 'uppercase',
    marginBottom: 4,
  },
  value: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
    color: tokens.colors.textPrimary,
    marginBottom: tokens.spacing.md,
  },
  roleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: tokens.spacing.md,
  },
  valueBadge: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 13,
    paddingHorizontal: 12,
    paddingVertical: 5,
    borderRadius: tokens.radii.pill,
    overflow: 'hidden',
  },
  badgeSeller: {
    color: '#d4af37',
    backgroundColor: 'rgba(212, 175, 55, 0.15)',
  },
  badgeBuyer: {
    color: tokens.colors.accentNavy,
    backgroundColor: tokens.colors.bgElevated,
  },
  becomeSellerCard: {
    marginTop: tokens.spacing.sm,
    marginBottom: tokens.spacing.md,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.md,
    backgroundColor: 'rgba(174, 140, 78, 0.1)',
    borderWidth: 1,
    borderColor: 'rgba(174, 140, 78, 0.3)',
  },
  becomeSellerTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 14,
    color: tokens.colors.accentGold,
    marginBottom: 4,
  },
  becomeSellerSubtitle: {
    fontFamily: tokens.typography.sans,
    fontSize: 12,
    color: tokens.colors.textSecondary,
    marginBottom: tokens.spacing.md,
    lineHeight: 18,
  },
  becomeSellerButton: {
    backgroundColor: tokens.colors.accentGold,
    paddingVertical: 10,
    borderRadius: tokens.radii.md,
    alignItems: 'center',
  },
  becomeSellerButtonText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
    fontSize: 14,
  },
  infoTitle: {
    fontFamily: tokens.typography.display,
    fontSize: 24,
    color: tokens.colors.accentNavy,
    marginBottom: 8,
  },
  infoText: {
    fontFamily: tokens.typography.sans,
    fontSize: 14,
    color: tokens.colors.textSecondary,
    marginBottom: tokens.spacing.lg,
    textAlign: 'center',
    lineHeight: 20,
  },
  button: {
    backgroundColor: tokens.colors.accentGold,
    paddingHorizontal: tokens.spacing.xl,
    paddingVertical: tokens.spacing.sm,
    borderRadius: tokens.radii.md,
  },
  buttonText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
    fontSize: 15,
  },
  logoutButton: {
    marginHorizontal: tokens.spacing.md,
    marginTop: tokens.spacing.sm,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.md,
    borderWidth: 1,
    borderColor: tokens.colors.accentRed,
    alignItems: 'center',
  },
  logoutText: {
    color: tokens.colors.accentRed,
    fontFamily: tokens.typography.sansBold,
    fontSize: 15,
  },
  dashboardButton: {
    backgroundColor: tokens.colors.accentNavy,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.pill,
    alignItems: 'center',
    marginTop: tokens.spacing.md,
  },
  dashboardButtonText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
    fontSize: 14,
  }
});
