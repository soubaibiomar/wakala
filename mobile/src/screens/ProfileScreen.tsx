import React from 'react';
import { View, StyleSheet, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { tokens } from '../styles/tokens';
import { useAuth } from '../context/AuthContext';

export default function ProfileScreen() {
  const { user, logout, isAuthenticated, isLoading } = useAuth();
  const navigation = useNavigation<any>();

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
        <Text style={styles.infoText}>Vous n'êtes pas connecté.</Text>
        <TouchableOpacity 
          style={styles.button}
          onPress={() => navigation.navigate('Login')}
        >
          <Text style={styles.buttonText}>Se connecter</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Mon Profil</Text>
      </View>
      
      <View style={styles.card}>
        <Text style={styles.label}>Nom complet</Text>
        <Text style={styles.value}>{user.name}</Text>
        
        <Text style={styles.label}>Email</Text>
        <Text style={styles.value}>{user.email}</Text>
        
        <Text style={styles.label}>Téléphone</Text>
        <Text style={styles.value}>{user.phone || 'Non renseigné'}</Text>
        
        <Text style={styles.label}>Rôle</Text>
        <Text style={styles.valueBadge}>{user.role === 'seller' ? 'Vendeur' : 'Acheteur'}</Text>
        
        {user.role === 'seller' && (
          <TouchableOpacity 
            style={styles.dashboardButton} 
            onPress={() => navigation.navigate('SellerDashboard')}
          >
            <Text style={styles.dashboardButtonText}>Accéder à mon Dashboard</Text>
          </TouchableOpacity>
        )}
      </View>

      <TouchableOpacity style={styles.logoutButton} onPress={logout}>
        <Text style={styles.logoutText}>Se déconnecter</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: tokens.colors.bgSecondary,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: tokens.colors.bgSecondary,
    padding: tokens.spacing.lg,
  },
  header: {
    padding: tokens.spacing.md,
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
  valueBadge: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 14,
    color: tokens.colors.accentNavy,
    backgroundColor: tokens.colors.bgElevated,
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: tokens.radii.pill,
    marginBottom: tokens.spacing.md,
  },
  infoText: {
    fontFamily: tokens.typography.sans,
    fontSize: 16,
    color: tokens.colors.textSecondary,
    marginBottom: tokens.spacing.lg,
    textAlign: 'center',
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
    fontSize: 16,
  },
  logoutButton: {
    marginHorizontal: tokens.spacing.md,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.md,
    borderWidth: 1,
    borderColor: tokens.colors.accentRed,
    alignItems: 'center',
  },
  logoutText: {
    color: tokens.colors.accentRed,
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
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
