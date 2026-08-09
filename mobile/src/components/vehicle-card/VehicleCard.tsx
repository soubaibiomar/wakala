import React from 'react';
import { View, StyleSheet, Text, Image, TouchableOpacity, ViewStyle } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Vehicle } from '@vente-auto/shared-types';
import { tokens } from '../../styles/tokens';
import { Skeleton } from '../common/Skeleton';
import { MatchScoreBadge } from './MatchScoreBadge';

interface VehicleCardProps {
  vehicle: Vehicle;
  style?: ViewStyle;
  matchScore?: number;
  keyFacts?: string[];
  budgetMargin?: number | null;
  bestVersionName?: string | null;
  isGrouped?: boolean;
}

export function VehicleCard({ vehicle, style, matchScore, keyFacts, budgetMargin, bestVersionName, isGrouped }: VehicleCardProps) {
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
        
        {/* Badge Match IA en bas de l'image */}
        {matchScore !== undefined && (
          <View style={styles.matchScoreWrapper}>
            <MatchScoreBadge score={matchScore} />
          </View>
        )}
      </View>
      
      <View style={styles.cardContent}>
        <Text style={styles.cardTitle} numberOfLines={1}>{vehicle.brand} {vehicle.model}</Text>
        {bestVersionName && (
          <Text style={styles.versionName} numberOfLines={1}>{bestVersionName}</Text>
        )}
        <Text style={styles.cardPrice}>
          {vehicle.price ? `${vehicle.price.toLocaleString('fr-FR')} MAD` : 'Prix sur demande'}
        </Text>
        {budgetMargin !== undefined && budgetMargin !== null && (
          <Text style={styles.budgetMargin}>
            {budgetMargin > 0 ? `+${budgetMargin.toLocaleString('fr-FR')} MAD` : `${budgetMargin.toLocaleString('fr-FR')} MAD`}
          </Text>
        )}
        
        <View style={styles.cardSpecs}>
          <Text style={styles.specText}>{vehicle.year}</Text>
          <Text style={styles.specDot}>•</Text>
          <Text style={styles.specText}>{vehicle.fuel_type}</Text>
          <Text style={styles.specDot}>•</Text>
          <Text style={styles.specText}>{vehicle.mileage ? `${vehicle.mileage} km` : 'N/A'}</Text>
        </View>

        {keyFacts && keyFacts.length > 0 && (
          <View style={styles.keyFactsContainer}>
            {keyFacts.slice(0, 2).map((fact, index) => (
              <View key={index} style={styles.keyFactRow}>
                <Text style={styles.keyFactBullet}>•</Text>
                <Text style={styles.keyFactText} numberOfLines={1}>{fact}</Text>
              </View>
            ))}
          </View>
        )}

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
  matchScoreWrapper: {
    position: 'absolute',
    bottom: 12,
    left: 12,
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
  versionName: {
    fontFamily: tokens.typography.sans,
    fontSize: 14,
    color: tokens.colors.textSecondary,
    marginBottom: 4,
  },
  cardPrice: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
    color: tokens.colors.accentGold,
    marginBottom: 2,
  },
  budgetMargin: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.textMuted,
    marginBottom: 8,
  },
  cardSpecs: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 10,
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
  keyFactsContainer: {
    marginTop: 4,
    marginBottom: 10,
    backgroundColor: tokens.colors.bgSecondary,
    padding: 8,
    borderRadius: tokens.radii.md,
  },
  keyFactRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 2,
  },
  keyFactBullet: {
    color: tokens.colors.accentGold,
    marginRight: 6,
    fontSize: 14,
    lineHeight: 18,
  },
  keyFactText: {
    fontFamily: tokens.typography.sans,
    fontSize: 12,
    color: tokens.colors.textPrimary,
    flex: 1,
    lineHeight: 18,
  },
  cardCity: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.textMuted,
  }
});
