import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { tokens } from '../styles/tokens';
import { useAuth } from '../context/AuthContext';
import { vehicleService } from '../services/vehicleService';

// Types simulés basés sur ce qui serait renvoyé par les endpoints web
interface DashboardMetrics {
  totalViews: number;
  averageTrustScore: number;
  activeListingsCount: number;
  soldListingsCount: number;
}

export default function SellerDashboardScreen() {
  const { user } = useAuth();
  const navigation = useNavigation<any>();
  
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [listings, setListings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulation du fetch des endpoints utilisés par seller_dashboard.py
    const fetchDashboardData = async () => {
      try {
        // En vrai : fetch('/api/users/me/metrics') ou similaire
        // Ici on mock les métriques en l'absence de l'endpoint exact connu, 
        // ou on assume que les endpoints existent et on les mock localement pour l'UI.
        
        // Mock data to represent what seller_dashboard.py gets
        const mockMetrics = {
          totalViews: 1432,
          averageTrustScore: 94.5,
          activeListingsCount: 3,
          soldListingsCount: 12
        };
        
        const mockListings = [
          { id: '1', title: 'Renault Clio 4', price: 120000, status: 'active', views: 342, fraud_score: 5 },
          { id: '2', title: 'Peugeot 3008', price: 250000, status: 'active', views: 89, fraud_score: 12 },
          { id: '3', title: 'Dacia Duster', price: 150000, status: 'sold', views: 1001, fraud_score: 2 },
        ];

        // Simulate network delay
        await new Promise(r => setTimeout(r, 800));

        setMetrics(mockMetrics);
        setListings(mockListings);
      } catch (error) {
        console.error("Erreur chargement dashboard", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={tokens.colors.accentGold} />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Tableau de bord</Text>
        <Text style={styles.subtitle}>Bonjour, {user?.name}</Text>
      </View>

      {/* ─── METRIQUES ─── */}
      <View style={styles.metricsContainer}>
        <View style={styles.metricCard}>
          <Text style={styles.metricValue}>{metrics?.activeListingsCount}</Text>
          <Text style={styles.metricLabel}>Annonces Actives</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricValue}>{metrics?.soldListingsCount}</Text>
          <Text style={styles.metricLabel}>Véhicules Vendus</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricValue}>{metrics?.totalViews}</Text>
          <Text style={styles.metricLabel}>Vues Totales</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={[styles.metricValue, { color: tokens.colors.accentGold }]}>
            {metrics?.averageTrustScore}%
          </Text>
          <Text style={styles.metricLabel}>Score de Confiance</Text>
        </View>
      </View>

      {/* ─── BOUTON ACTION RAPIDE ─── */}
      <View style={styles.actionContainer}>
        <TouchableOpacity 
          style={styles.primaryButton}
          onPress={() => navigation.navigate('Create')} // Navigue vers le tab CreateListingScreen
        >
          <Text style={styles.primaryButtonText}>+ Créer une annonce</Text>
        </TouchableOpacity>
      </View>

      {/* ─── LISTE DES ANNONCES ─── */}
      <View style={styles.listContainer}>
        <Text style={styles.sectionTitle}>Mes Annonces Récentes</Text>
        
        {listings.map(listing => (
          <View key={listing.id} style={styles.listingCard}>
            <View style={styles.listingInfo}>
              <Text style={styles.listingTitle}>{listing.title}</Text>
              <Text style={styles.listingPrice}>{listing.price.toLocaleString('fr-FR')} MAD</Text>
              <Text style={styles.listingViews}>👁 {listing.views} vues</Text>
            </View>
            <View style={styles.listingStatusContainer}>
              <View style={[
                styles.statusBadge, 
                listing.status === 'active' ? styles.statusActive : styles.statusSold
              ]}>
                <Text style={styles.statusText}>
                  {listing.status === 'active' ? 'En ligne' : 'Vendu'}
                </Text>
              </View>
              {listing.fraud_score > 0 && (
                <Text style={styles.fraudText}>Risque: {listing.fraud_score}%</Text>
              )}
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
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
  },
  header: {
    padding: tokens.spacing.lg,
    backgroundColor: tokens.colors.bgPrimary,
    borderBottomWidth: 1,
    borderBottomColor: tokens.borders.subtle,
  },
  title: {
    fontFamily: tokens.typography.display,
    fontSize: 28,
    color: tokens.colors.accentNavy,
  },
  subtitle: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 16,
    color: tokens.colors.textSecondary,
    marginTop: 4,
  },
  metricsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: tokens.spacing.md,
    gap: tokens.spacing.md,
  },
  metricCard: {
    width: '47%',
    backgroundColor: tokens.colors.bgPrimary,
    padding: tokens.spacing.lg,
    borderRadius: tokens.radii.lg,
    alignItems: 'center',
    ...tokens.shadows.card,
  },
  metricValue: {
    fontFamily: tokens.typography.display,
    fontSize: 28,
    color: tokens.colors.textPrimary,
    marginBottom: 4,
  },
  metricLabel: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.textMuted,
    textAlign: 'center',
  },
  actionContainer: {
    paddingHorizontal: tokens.spacing.md,
    marginBottom: tokens.spacing.xl,
  },
  primaryButton: {
    backgroundColor: tokens.colors.accentGold,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.pill,
    alignItems: 'center',
  },
  primaryButtonText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
  },
  listContainer: {
    paddingHorizontal: tokens.spacing.md,
    paddingBottom: tokens.spacing.xxl,
  },
  sectionTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 18,
    color: tokens.colors.textPrimary,
    marginBottom: tokens.spacing.md,
  },
  listingCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: tokens.colors.bgPrimary,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.md,
    marginBottom: tokens.spacing.sm,
    ...tokens.shadows.card,
  },
  listingInfo: {
    flex: 1,
  },
  listingTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
    color: tokens.colors.textPrimary,
  },
  listingPrice: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 14,
    color: tokens.colors.textSecondary,
    marginTop: 2,
  },
  listingViews: {
    fontFamily: tokens.typography.sans,
    fontSize: 12,
    color: tokens.colors.textMuted,
    marginTop: 8,
  },
  listingStatusContainer: {
    alignItems: 'flex-end',
    justifyContent: 'center',
  },
  statusBadge: {
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: tokens.radii.pill,
    marginBottom: 4,
  },
  statusActive: {
    backgroundColor: 'rgba(16, 185, 129, 0.1)', // Green
  },
  statusSold: {
    backgroundColor: tokens.colors.bgSecondary,
  },
  statusText: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 12,
    color: tokens.colors.textPrimary,
  },
  fraudText: {
    fontFamily: tokens.typography.sans,
    fontSize: 10,
    color: tokens.colors.accentRed,
  }
});
