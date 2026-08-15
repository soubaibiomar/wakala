import React, { useState, useEffect } from 'react';
import { View, StyleSheet, Text, ScrollView, TouchableOpacity, Image } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { MainTabParamList } from '../navigation/AppNavigator';

import HeroCar from '../components/hero/HeroCar';
import SearchBar from '../components/hero/SearchBar';
import { useHeroSequence } from '../components/hero/useHeroSequence';
import { tokens } from '../styles/tokens';
import Animated, { useAnimatedStyle } from 'react-native-reanimated';
import { useAuth } from '../context/AuthContext';
import { vehicleService } from '../services/vehicleService';
import { Vehicle } from '@vente-auto/shared-types';

type HomeScreenNavigationProp = NativeStackNavigationProp<MainTabParamList, 'Home'>;

const CATEGORIES = [
  { id: 'neuf', name: 'Neuf', icon: '✨', query: 'Neuf' },
  // PIVOT: removed { id: 'occasion', name: 'Occasion', ... }
  { id: 'hybride', name: 'Hybride', icon: '⚡', query: 'Hybride' },
  { id: 'electrique', name: 'Électrique', icon: '🔋', query: 'Électrique' },
  { id: 'suv', name: 'SUV & 4x4', icon: '🚙', query: 'SUV' },
];

export default function HomeScreen() {
  const sequence = useHeroSequence();
  const navigation = useNavigation<any>();
  const { user, becomeSeller } = useAuth();
  const [featuredVehicles, setFeaturedVehicles] = useState<Vehicle[]>([]);

  useEffect(() => {
    (async () => {
      try {
        const list = await vehicleService.getVehicles({ page_size: 4 });
        const items = Array.isArray(list) ? list : (list as any)?.items || [];
        setFeaturedVehicles(items.slice(0, 4));
      } catch (err) {
        console.warn('Featured vehicles load error:', err);
      }
    })();
  }, []);

  const titleAnimatedStyle = useAnimatedStyle(() => ({
    opacity: sequence.carOpacity.value, 
    transform: [{ translateY: 20 * (1 - sequence.carOpacity.value) }]
  }));

  const handleCategoryPress = (category: string) => {
    navigation.navigate('Catalogue', { query: category });
  };

  const handleSellPress = () => {
    if (!user) {
      navigation.navigate('Login');
    } else if (user.role === 'seller') {
      navigation.navigate('Create');
    } else {
      navigation.navigate('Profile');
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <View style={styles.heroSection}>
        <Animated.View style={titleAnimatedStyle}>
          <Text style={styles.title}>Trouvez votre véhicule avec l'IA.</Text>
          <Text style={styles.subtitle}>Marketplace automobile propulsée par l'intelligence artificielle</Text>
        </Animated.View>
        
        {/* Composant Voiture SVG (Voiture -> Phares -> Plaque) */}
        <HeroCar sequence={sequence} />
        
        {/* Barre de recherche (apparaît après la plaque) */}
        <SearchBar sequence={sequence} />
      </View>

      {/* ─── RACCOURCIS CATÉGORIES ─── */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Explorer par univers</Text>
        <View style={styles.categoriesGrid}>
          {CATEGORIES.map(cat => (
            <TouchableOpacity 
              key={cat.id} 
              style={styles.categoryCard} 
              onPress={() => handleCategoryPress(cat.name)}
              activeOpacity={0.8}
            >
              <Text style={styles.categoryIcon}>{cat.icon}</Text>
              <Text style={styles.categoryName}>{cat.name}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* ─── BANNIÈRE VENDEUR / CTA IA ─── */}
      <View style={styles.bannerSection}>
        <TouchableOpacity style={styles.sellerBanner} onPress={handleSellPress} activeOpacity={0.85}>
          <View style={styles.bannerContent}>
            <Text style={styles.bannerBadge}>Estimation IA instantanée</Text>
            <Text style={styles.bannerTitle}>
              {user?.role === 'buyer' 
                ? 'Devenez vendeur et publiez en 3 photos' 
                : 'Vendez votre véhicule au meilleur prix'}
            </Text>
            <Text style={styles.bannerDesc}>
              Notre vision IA scanne votre carrosserie, prédit la cote Argus et rédige votre annonce automatiquement.
            </Text>
            <View style={styles.bannerButton}>
              <Text style={styles.bannerButtonText}>
                {user?.role === 'seller' ? '✨ Créer une annonce' : '🚀 Activer mon compte vendeur'}
              </Text>
            </View>
          </View>
        </TouchableOpacity>
      </View>

      {/* ─── SÉLECTION DU MOMENT ─── */}
      {featuredVehicles.length > 0 && (
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Véhicules recommandés</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Catalogue')}>
              <Text style={styles.seeAllText}>Voir tout →</Text>
            </TouchableOpacity>
          </View>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.featuredScroll}>
            {featuredVehicles.map(v => (
              <TouchableOpacity 
                key={v.id} 
                style={styles.featuredCard}
                onPress={() => navigation.navigate('VehicleDetail', { vehicleId: v.id })}
                activeOpacity={0.85}
              >
                <Image 
                  source={{ uri: (v as any).images?.[0]?.file_path || (v as any).image_url || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=600' }} 
                  style={styles.featuredImage}
                />
                <View style={styles.featuredInfo}>
                  <Text style={styles.featuredTitle} numberOfLines={1}>{v.brand} {v.model}</Text>
                  <Text style={styles.featuredYear}>{v.year} • {v.fuel_type || 'Diesel'} • {v.city || 'Maroc'}</Text>
                  <Text style={styles.featuredPrice}>
                    {v.price ? `${v.price.toLocaleString('fr-FR')} MAD` : 'Prix n/d'}
                  </Text>
                </View>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: tokens.colors.bgPrimary,
  },
  content: {
    paddingBottom: tokens.spacing.xxl,
  },
  heroSection: {
    paddingTop: tokens.spacing.xl,
    alignItems: 'center',
    width: '100%',
  },
  title: {
    fontFamily: tokens.typography.display,
    fontSize: 32,
    color: tokens.colors.accentNavy,
    textAlign: 'center',
    marginBottom: tokens.spacing.sm,
    paddingHorizontal: tokens.spacing.md,
  },
  subtitle: {
    fontFamily: tokens.typography.sans,
    fontSize: 15,
    color: tokens.colors.textSecondary,
    textAlign: 'center',
    marginBottom: tokens.spacing.md,
    paddingHorizontal: tokens.spacing.lg,
  },
  section: {
    marginTop: tokens.spacing.xl,
    paddingHorizontal: tokens.spacing.lg,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: tokens.spacing.md,
  },
  sectionTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 18,
    color: tokens.colors.textPrimary,
    marginBottom: tokens.spacing.md,
  },
  seeAllText: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 14,
    color: tokens.colors.accentGold,
  },
  categoriesGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: tokens.spacing.sm,
  },
  categoryCard: {
    flex: 1,
    backgroundColor: tokens.colors.bgSecondary,
    borderRadius: tokens.radii.md,
    paddingVertical: tokens.spacing.md,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
  },
  categoryIcon: {
    fontSize: 22,
    marginBottom: 4,
  },
  categoryName: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.textPrimary,
  },
  bannerSection: {
    marginTop: tokens.spacing.xl,
    paddingHorizontal: tokens.spacing.lg,
  },
  sellerBanner: {
    backgroundColor: tokens.colors.accentNavy,
    borderRadius: tokens.radii.lg,
    padding: tokens.spacing.lg,
    ...tokens.shadows.card,
  },
  bannerContent: {
    alignItems: 'flex-start',
  },
  bannerBadge: {
    backgroundColor: 'rgba(212, 175, 55, 0.2)',
    color: tokens.colors.accentGold,
    fontFamily: tokens.typography.sansBold,
    fontSize: 11,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: tokens.radii.pill,
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  bannerTitle: {
    fontFamily: tokens.typography.display,
    fontSize: 20,
    color: tokens.colors.textInverse,
    marginBottom: 6,
  },
  bannerDesc: {
    fontFamily: tokens.typography.sans,
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: 18,
    marginBottom: tokens.spacing.md,
  },
  bannerButton: {
    backgroundColor: tokens.colors.accentGold,
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: tokens.radii.pill,
  },
  bannerButtonText: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 13,
    color: tokens.colors.textInverse,
  },
  featuredScroll: {
    flexDirection: 'row',
  },
  featuredCard: {
    width: 220,
    backgroundColor: tokens.colors.bgSecondary,
    borderRadius: tokens.radii.md,
    marginRight: tokens.spacing.md,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
    overflow: 'hidden',
  },
  featuredImage: {
    width: '100%',
    height: 120,
  },
  featuredInfo: {
    padding: tokens.spacing.sm,
  },
  featuredTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 14,
    color: tokens.colors.textPrimary,
  },
  featuredYear: {
    fontFamily: tokens.typography.sans,
    fontSize: 11,
    color: tokens.colors.textMuted,
    marginTop: 2,
  },
  featuredPrice: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 14,
    color: tokens.colors.accentGold,
    marginTop: 4,
  }
});
