import React, { useEffect, useState, useCallback } from 'react';
import { View, StyleSheet, Text, FlatList, TouchableOpacity, RefreshControl, ScrollView } from 'react-native';
import { useNavigation, useRoute } from '@react-navigation/native';

import { vehicleService } from '../services/vehicleService';
import { tokens } from '../styles/tokens';
import { Vehicle } from '@vente-auto/shared-types';
import { VehicleCard, VehicleCardSkeleton } from '../components/vehicle-card/VehicleCard';
import { locationService } from '../services/locationService';
import { notificationService } from '../services/notificationService';
import { offlineCache } from '../services/offlineCache';

const CATEGORIES = ['Tous', 'Neuf', 'Occasion', 'Hybride', 'Électrique', 'SUV'];

export default function CatalogueScreen() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  
  const [activeCategory, setActiveCategory] = useState('Tous');
  const [locationStr, setLocationStr] = useState<string | null>(null);
  
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const initialQuery = route.params?.query || '';

  const [isOffline, setIsOffline] = useState(false);

  const fetchVehicles = async (pageToFetch: number = 1, isRefresh: boolean = false) => {
    try {
      const params: any = { page: pageToFetch, page_size: 10 };
      if (initialQuery) {
        params.q = initialQuery;
      }
      
      if (activeCategory === 'Neuf') params.mileage_max = 0;
      if (activeCategory === 'Hybride') params.fuel_type = 'hybride';
      if (activeCategory === 'Électrique') params.fuel_type = 'electrique';
      if (activeCategory === 'SUV') params.body_type = 'suv';

      const data = await vehicleService.getVehicles(params);
      
      const newVehicles = Array.isArray(data) ? data : (data as any).items || [];
      
      // Si la première item a _isOffline, on sait qu'on est hors-ligne
      if (newVehicles.length > 0 && newVehicles[0]._isOffline) {
        setIsOffline(true);
      } else {
        setIsOffline(false);
        // Sauvegarder en cache pour le hors-ligne si c'est la page 1
        if (pageToFetch === 1) {
          await offlineCache.saveCatalogue(newVehicles);
        }
      }

      if (isRefresh) {
        setVehicles(newVehicles);
      } else {
        setVehicles(prev => {
          // Filtrer les doublons potentiels du cache
          const existingIds = new Set(prev.map((v: any) => v.id));
          const uniqueNew = newVehicles.filter((v: any) => !existingIds.has(v.id));
          return [...prev, ...uniqueNew];
        });
      }
      
      setHasMore(newVehicles.length === 10 && !isOffline); // Pas de load more si hors-ligne
    } catch (error: any) {
      console.error("Error fetching catalogue:", error);
      
      // Fallback sur le cache uniquement pour les erreurs réseau (pas de réponse)
      const isNetworkError = !error.response;
      
      if (isNetworkError && pageToFetch === 1) {
        setIsOffline(true);
        const cached = await offlineCache.getCatalogue();
        if (cached) {
          setVehicles(cached);
        }
      } else if (!isNetworkError) {
        // C'est une erreur serveur (500, 400, etc.), propager l'erreur
        // On pourrait afficher un toast ou une alerte ici
        console.error("API Error: ", error.response?.status, error.response?.data);
      }
      setLoading(false);
      setRefreshing(false);
      setLoadingMore(false);
    }
  };

  const handleSaveSearch = async () => {
    const queryToSave = initialQuery || activeCategory;
    await offlineCache.saveRecentSearch(queryToSave);
    
    // Demander les permissions de notification APRÈS la première action engageante
    await notificationService.registerForPushNotificationsAsync();
    
    alert('Recherche sauvegardée ! Vous recevrez des notifications.');
  };

  useEffect(() => {
    (async () => {
      // 1. Localisation : seulement au moment d'afficher le catalogue
      const city = await locationService.getNearestCity();
      if (city) {
        setLocationStr(`Proche de ${city}`);
      }
      
      // 2. Chargement des données (avec cache hors-ligne)
      setLoading(true);
      fetchVehicles(1, true);
    })();
  }, [initialQuery, activeCategory]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    setPage(1);
    fetchVehicles(1, true);
  }, [initialQuery, activeCategory]);

  const onLoadMore = () => {
    if (!loadingMore && hasMore && !loading) {
      setLoadingMore(true);
      const nextPage = page + 1;
      setPage(nextPage);
      fetchVehicles(nextPage, false);
    }
  };

  const renderFilterPills = () => (
    <View style={styles.filtersWrapper}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filtersContainer}>
        {CATEGORIES.map(cat => (
          <TouchableOpacity 
            key={cat} 
            style={[styles.pill, activeCategory === cat && styles.pillActive]}
            onPress={() => setActiveCategory(cat)}
          >
            <Text style={[styles.pillText, activeCategory === cat && styles.pillTextActive]}>{cat}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );

  const renderFooter = () => {
    if (!loadingMore) return null;
    return <VehicleCardSkeleton style={{ marginBottom: tokens.spacing.lg }} />;
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <Text style={styles.headerTitle}>Catalogue</Text>
          <TouchableOpacity onPress={handleSaveSearch} style={styles.saveSearchButton}>
            <Text style={styles.saveSearchText}>🔔 Alerte</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.headerBottom}>
          {locationStr && <Text style={styles.locationText}>📍 {locationStr}</Text>}
          {isOffline && <Text style={styles.offlineText}>⚠️ Mode hors-ligne</Text>}
        </View>
      </View>
      
      {renderFilterPills()}

      {loading ? (
        <ScrollView style={styles.listContent}>
          <VehicleCardSkeleton />
          <VehicleCardSkeleton />
          <VehicleCardSkeleton />
        </ScrollView>
      ) : (
        <FlatList
          data={vehicles}
          keyExtractor={(item, index) => `${item.id}-${index}`}
          renderItem={({ item }) => <VehicleCard vehicle={item} />}
          contentContainerStyle={styles.listContent}
          showsVerticalScrollIndicator={false}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={tokens.colors.accentGold} />
          }
          onEndReached={onLoadMore}
          onEndReachedThreshold={0.5}
          ListFooterComponent={renderFooter}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyText}>Aucun véhicule trouvé.</Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: tokens.colors.bgSecondary,
  },
  header: {
    padding: tokens.spacing.md,
    backgroundColor: tokens.colors.bgPrimary,
    borderBottomWidth: 1,
    borderBottomColor: tokens.borders.subtle,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerBottom: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 4,
  },
  headerTitle: {
    fontFamily: tokens.typography.display,
    fontSize: 28,
    color: tokens.colors.textPrimary,
  },
  saveSearchButton: {
    backgroundColor: tokens.colors.bgSecondary,
    paddingHorizontal: tokens.spacing.sm,
    paddingVertical: tokens.spacing.xs,
    borderRadius: tokens.radii.pill,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
  },
  saveSearchText: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.textPrimary,
  },
  locationText: {
    fontFamily: tokens.typography.sans,
    fontSize: 12,
    color: tokens.colors.textSecondary,
  },
  offlineText: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.accentRed,
  },
  filtersWrapper: {
    backgroundColor: tokens.colors.bgPrimary,
    borderBottomWidth: 1,
    borderBottomColor: tokens.borders.subtle,
  },
  filtersContainer: {
    paddingHorizontal: tokens.spacing.md,
    paddingVertical: tokens.spacing.sm,
    gap: tokens.spacing.sm,
  },
  pill: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: tokens.radii.pill,
    backgroundColor: tokens.colors.bgSecondary,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
    marginRight: 8,
  },
  pillActive: {
    backgroundColor: tokens.colors.accentNavy,
    borderColor: tokens.colors.accentNavy,
  },
  pillText: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 13,
    color: tokens.colors.textSecondary,
  },
  pillTextActive: {
    color: tokens.colors.textInverse,
  },
  listContent: {
    padding: tokens.spacing.md,
  },
  emptyContainer: {
    padding: tokens.spacing.xl,
    alignItems: 'center',
  },
  emptyText: {
    fontFamily: tokens.typography.sans,
    fontSize: 15,
    color: tokens.colors.textMuted,
  }
});
