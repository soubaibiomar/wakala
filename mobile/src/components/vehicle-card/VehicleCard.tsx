import React from 'react';
import { View, StyleSheet, Text, Image, TouchableOpacity, ViewStyle } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Vehicle } from '@vente-auto/shared-types';
import { tokens } from '../../styles/tokens';
import { Skeleton } from '../common/Skeleton';

interface VehicleCardProps {
  vehicle: Vehicle;
  style?: ViewStyle;
}

export function VehicleCard({ vehicle, style }: VehicleCardProps) {
  const navigation = useNavigation<any>();
  const imageUri = vehicle.images?.[0]?.file_path || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=600';

  const isNew = vehicle.mileage === 0;

  return (
    <TouchableOpacity 
      style={[styles.card, style]}
      onPress={() => navigation.navigate('VehicleDetail', { vehicleId: vehicle.id })}
      activeOpacity={0.9}
    >
      <View style={styles.imageContainer}>
        <Image source={{ uri: imageUri }} style={styles.cardImage} />
        {/* Badges sur l'image */}
        <View style={styles.badgeContainer}>
          <View style={[styles.badge, isNew ? styles.badgeNew : styles.badgeUsed]}>
            <Text style={[styles.badgeText, isNew ? styles.badgeTextNew : styles.badgeTextUsed]}>
              {isNew ? 'Neuf' : 'Occasion'}
            </Text>
          </View>
        </View>
      </View>
      
      <View style={styles.cardContent}>
        <Text style={styles.cardTitle} numberOfLines={1}>{vehicle.brand} {vehicle.model}</Text>
        <Text style={styles.cardPrice}>
          {vehicle.price ? `${vehicle.price.toLocaleString('fr-FR')} MAD` : 'Prix sur demande'}
        </Text>
        
        <View style={styles.cardSpecs}>
          <Text style={styles.specText}>{vehicle.year}</Text>
          <Text style={styles.specDot}>•</Text>
          <Text style={styles.specText}>{vehicle.fuel_type}</Text>
          <Text style={styles.specDot}>•</Text>
          <Text style={styles.specText}>{vehicle.mileage ? `${vehicle.mileage} km` : 'N/A'}</Text>
        </View>
        <Text style={styles.cardCity}>{vehicle.city}</Text>
      </View>
    </TouchableOpacity>
  );
}

export function VehicleCardSkeleton({ style }: { style?: ViewStyle }) {
  return (
    <View style={[styles.card, style]}>
      <Skeleton style={styles.cardImage} />
      <View style={styles.cardContent}>
        <Skeleton style={{ width: '60%', height: 20, marginBottom: 8 }} />
        <Skeleton style={{ width: '40%', height: 18, marginBottom: 12 }} />
        <Skeleton style={{ width: '80%', height: 14, marginBottom: 8 }} />
        <Skeleton style={{ width: '30%', height: 14 }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: tokens.colors.bgCard,
    borderRadius: tokens.radii.lg,
    marginBottom: tokens.spacing.lg,
    overflow: 'hidden',
    ...tokens.shadows.card,
  },
  imageContainer: {
    position: 'relative',
    width: '100%',
    height: 180,
  },
  cardImage: {
    width: '100%',
    height: '100%',
    backgroundColor: tokens.colors.bgTertiary,
  },
  badgeContainer: {
    position: 'absolute',
    top: 12,
    left: 12,
    flexDirection: 'row',
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: tokens.radii.pill,
  },
  badgeNew: {
    backgroundColor: tokens.colors.accentGold,
  },
  badgeUsed: {
    backgroundColor: tokens.colors.bgSecondary,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
  },
  badgeText: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 10,
    textTransform: 'uppercase',
  },
  badgeTextNew: {
    color: tokens.colors.textInverse,
  },
  badgeTextUsed: {
    color: tokens.colors.textPrimary,
  },
  cardContent: {
    padding: tokens.spacing.md,
  },
  cardTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 18,
    color: tokens.colors.textPrimary,
    marginBottom: 4,
  },
  cardPrice: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
    color: tokens.colors.accentGold,
    marginBottom: 8,
  },
  cardSpecs: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  specText: {
    fontFamily: tokens.typography.sans,
    fontSize: 13,
    color: tokens.colors.textSecondary,
  },
  specDot: {
    marginHorizontal: 6,
    color: tokens.colors.textMuted,
  },
  cardCity: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.textMuted,
  }
});
