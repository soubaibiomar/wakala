import React, { useState, useEffect, useCallback } from 'react';
import { View, StyleSheet, Text, ScrollView, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { tokens } from '../styles/tokens';
import { useAuth } from '../context/AuthContext';
import { vehicleService } from '../services/vehicleService';

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
  const [refreshing, setRefreshing] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const data = await vehicleService.getMyListings();
      const myListings = Array.isArray(data) ? data : [];
      setListings(myListings);

      // Compute metrics from actual data
      let views = 0;
      let active = 0;
      let sold = 0;
      let trustSum = 0;
      let trustCount = 0;

      myListings.forEach((item: any) => {
        views += (item.views || 0);
        if (item.status === 'active') active++;
        if (item.status === 'sold') sold++;
        
        const fraud = item.fraud_score ?? 5;
        const trust = Math.max(0, 100 - fraud);
        trustSum += trust;
        trustCount++;
      });

      setMetrics({
        totalViews: views,
        activeListingsCount: active,
        soldListingsCount: sold,
        averageTrustScore: trustCount > 0 ? Math.round(trustSum / trustCount) : 95,
      });
    } catch (error) {
      console.warn("Could not fetch seller listings, using local summary:", error);
      // Default fallback state if server has no listings yet
      setMetrics({
        totalViews: 0,
        activeListingsCount: 0,
        soldListingsCount: 0,
        averageTrustScore: 95,
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={tokens.colors.accentGold} />
      </View>
    );
  }

  const displayName = user?.full_name || user?.name || 'Vendeur';

  return (
    <ScrollView 
      style={styles.container}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={tokens.colors.accentGold} />}
    >
      <View style={styles.header}>
        <Text style={styles.title}>Tableau de bord Vendeur</Text>
        <Text style={styles.subtitle}>Bonjour, {displayName}</Text>
      </View>

      {/* ─── METRIQUES ─── */}
      <View style={styles.metricsContainer}>
        <View style={styles.metricCard}>
          <Text style={styles.metricValue}>{metrics?.activeListingsCount ?? 0}</Text>
          <Text style={styles.metricLabel}>Annonces Actives</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricValue}>{metrics?.soldListingsCount ?? 0}</Text>
          <Text style={styles.metricLabel}>Véhicules Vendus</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={styles.metricValue}>{metrics?.totalViews ?? 0}</Text>
          <Text style={styles.metricLabel}>Vues Totales</Text>
        </View>
        <View style={styles.metricCard}>
          <Text style={[styles.metricValue, { color: tokens.colors.accentGold }]}>
            {metrics?.averageTrustScore ?? 95}%
          </Text>
          <Text style={styles.metricLabel}>Score de Confiance IA</Text>
        </View>
      </View>

      {/* ─── BOUTON ACTION RAPIDE ─── */}
      <View style={styles.actionContainer}>
        <TouchableOpacity 
          style={styles.primaryButton}
          onPress={() => navigation.navigate('MainTabs', { screen: 'Create' })}
        >
          <Text style={styles.primaryButtonText}>✨ + Créer une annonce</Text>
        </TouchableOpacity>
      </View>

      {/* ─── LISTE DES ANNONCES ─── */}
      <View style={styles.listContainer}>
        <Text style={styles.sectionTitle}>Mes Annonces ({listings.length})</Text>
        
        {listings.length === 0 ? (
          <View style={styles.emptyCard}>
            <Text style={styles.emptyTitle}>Vous n'avez pas encore d'annonce en ligne</Text>
            <Text style={styles.emptySubtitle}>
              Prenez 3 photos de votre véhicule pour obtenir une estimation IA et publier en quelques secondes.
            </Text>
          </View>
        ) : (
          listings.map((listing: any) => (
            <TouchableOpacity 
              key={listing.id} 
              style={styles.listingCard}
              onPress={() => {
                const vId = listing.vehicle_id || listing.vehicle?.id;
                if (vId) navigation.navigate('VehicleDetail', { vehicleId: vId });
              }}
            >
              <View style={styles.listingInfo}>
                <Text style={styles.listingTitle}>
                  {listing.title || `${listing.vehicle?.brand || ''} ${listing.vehicle?.model || ''}`}
                </Text>
                <Text style={styles.listingPrice}>
                  {listing.price ? `${Number(listing.price).toLocaleString('fr-FR')} MAD` : 'Prix sur demande'}
                </Text>
                <Text style={styles.listingViews}>👁 {listing.views || 0} vues</Text>
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
                {listing.fraud_score !== undefined && listing.fraud_score > 0 && (
                  <Text style={styles.fraudText}>Risque: {Math.round(listing.fraud_score)}%</Text>
                )}
              </View>
            </TouchableOpacity>
          ))
        )}
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
  emptyCard: {
    backgroundColor: tokens.colors.bgPrimary,
    padding: tokens.spacing.xl,
    borderRadius: tokens.radii.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
  },
  emptyTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 15,
    color: tokens.colors.textPrimary,
    marginBottom: 8,
    textAlign: 'center',
  },
  emptySubtitle: {
    fontFamily: tokens.typography.sans,
    fontSize: 13,
    color: tokens.colors.textSecondary,
    textAlign: 'center',
    lineHeight: 20,
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
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
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
