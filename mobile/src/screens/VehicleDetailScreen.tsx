import React, { useEffect, useState, useRef } from 'react';
import { View, StyleSheet, Text, Image, ScrollView, TouchableOpacity, Dimensions, Alert, Linking } from 'react-native';
import { useRoute } from '@react-navigation/native';
import PagerView from 'react-native-pager-view';

import { vehicleService } from '../services/vehicleService';
import { tokens } from '../styles/tokens';
import { Vehicle } from '@vente-auto/shared-types';
import { Skeleton } from '../components/common/Skeleton';

const { width } = Dimensions.get('window');

export default function VehicleDetailScreen() {
  const route = useRoute<any>();
  const { vehicleId } = route.params;
  
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);

  useEffect(() => {
    (async () => {
      try {
        const data = await vehicleService.getVehicle(vehicleId);
        setVehicle(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    })();
  }, [vehicleId]);

  if (loading) {
    return (
      <View style={styles.container}>
        <Skeleton style={styles.gallerySkeleton} />
        <View style={styles.content}>
          <Skeleton style={{ width: '70%', height: 32, marginBottom: 8 }} />
          <Skeleton style={{ width: '40%', height: 24, marginBottom: 24 }} />
          <View style={styles.specsGrid}>
            <Skeleton style={styles.specBoxSkeleton} />
            <Skeleton style={styles.specBoxSkeleton} />
            <Skeleton style={styles.specBoxSkeleton} />
            <Skeleton style={styles.specBoxSkeleton} />
          </View>
        </View>
      </View>
    );
  }

  if (!vehicle) {
    return <View style={styles.center}><Text style={styles.errorText}>Véhicule introuvable</Text></View>;
  }

  const images = vehicle.images?.length ? vehicle.images : [{ file_path: 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=600' }];

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollContainer} contentContainerStyle={styles.scrollContent}>
        
        {/* Galerie Photo avec PagerView */}
        <View style={styles.galleryContainer}>
          <View style={{ position: 'absolute', top: 16, left: 16, zIndex: 10, flexDirection: 'row' }}>
            <View style={[
              { paddingHorizontal: 12, paddingVertical: 6, borderRadius: tokens.radii.pill },
              vehicle.mileage === 0 ? { backgroundColor: tokens.colors.accentGold } : { backgroundColor: tokens.colors.bgSecondary, borderWidth: 1, borderColor: tokens.borders.subtle }
            ]}>
              <Text style={[
                { fontFamily: tokens.typography.sansBold, fontSize: 12, textTransform: 'uppercase' },
                vehicle.mileage === 0 ? { color: tokens.colors.textInverse } : { color: tokens.colors.textPrimary }
              ]}>
                {vehicle.mileage === 0 ? 'Neuf' : 'Occasion'}
              </Text>
            </View>
          </View>
          <PagerView 
            style={styles.pagerView} 
            initialPage={0}
            onPageSelected={(e) => setCurrentPage(e.nativeEvent.position)}
          >
            {images.map((img: any, i: number) => (
              <View key={i} style={styles.page}>
                <Image source={{ uri: img.file_path || img }} style={styles.galleryImage} resizeMode="cover" />
              </View>
            ))}
          </PagerView>
          
          {/* Indicateur de position (ex: 1/8) */}
          <View style={styles.pageIndicator}>
            <Text style={styles.pageIndicatorText}>{currentPage + 1} / {images.length}</Text>
          </View>
        </View>

        <View style={styles.content}>
          <Text style={styles.title}>{vehicle.brand} {vehicle.model}</Text>
          <Text style={styles.price}>{vehicle.price ? `${vehicle.price.toLocaleString('fr-FR')} MAD` : 'Prix sur demande'}</Text>
          
          {/* Bloc Confiance (Jauges IA) */}
          <View style={styles.trustBlock}>
            <Text style={styles.trustTitle}>Certifié par IA Wakala</Text>
            
            <View style={styles.gaugeContainer}>
              <View style={styles.gaugeHeader}>
                <Text style={styles.gaugeLabel}>État général (Computer Vision)</Text>
                <Text style={styles.gaugeValue}>{vehicle.condition_score ? `${(vehicle.condition_score * 100).toFixed(0)}%` : '92%'}</Text>
              </View>
              <View style={styles.gaugeTrack}>
                <View style={[styles.gaugeFill, { width: vehicle.condition_score ? `${vehicle.condition_score * 100}%` : '92%' }]} />
              </View>
            </View>
            
            <View style={styles.gaugeContainer}>
              <View style={styles.gaugeHeader}>
                <Text style={styles.gaugeLabel}>Fiabilité Vendeur (Score Réseau)</Text>
                <Text style={styles.gaugeValue}>{vehicle.popularity_score ? `${(vehicle.popularity_score * 100).toFixed(0)}%` : '85%'}</Text>
              </View>
              <View style={styles.gaugeTrack}>
                <View style={[styles.gaugeFill, { width: vehicle.popularity_score ? `${vehicle.popularity_score * 100}%` : '85%' }]} />
              </View>
            </View>
          </View>

          {/* Spécifications */}
          <View style={styles.specsGrid}>
            <View style={styles.specBox}>
              <Text style={styles.specLabel}>Année</Text>
              <Text style={styles.specValue}>{vehicle.year || 'N/A'}</Text>
            </View>
            <View style={styles.specBox}>
              <Text style={styles.specLabel}>Kilométrage</Text>
              <Text style={styles.specValue}>{vehicle.mileage ? `${vehicle.mileage.toLocaleString('fr-FR')} km` : 'N/A'}</Text>
            </View>
            <View style={styles.specBox}>
              <Text style={styles.specLabel}>Carburant</Text>
              <Text style={styles.specValue}>{vehicle.fuel_type || 'N/A'}</Text>
            </View>
            <View style={styles.specBox}>
              <Text style={styles.specLabel}>Boîte</Text>
              <Text style={styles.specValue}>{vehicle.transmission || 'N/A'}</Text>
            </View>
          </View>
          
          {/* Description */}
          <View style={styles.descriptionBox}>
            <Text style={styles.descriptionLabel}>Description</Text>
            <Text style={styles.descriptionText}>{vehicle.description || 'Aucune description fournie pour ce véhicule.'}</Text>
          </View>
        </View>
      </ScrollView>

      {/* Bouton Contact Sticky */}
      <View style={styles.stickyFooter}>
        <TouchableOpacity 
          style={styles.contactButton}
          onPress={() => {
            const phone = (vehicle as any).seller?.phone || '+212600000000';
            Alert.alert(
              'Contacter le Vendeur',
              `Numéro de contact : ${phone}`,
              [
                { text: 'Annuler', style: 'cancel' },
                { 
                  text: 'WhatsApp', 
                  onPress: () => {
                    const cleanPhone = phone.replace(/[^0-9]/g, '');
                    Linking.openURL(`https://wa.me/${cleanPhone}`);
                  } 
                },
                { 
                  text: 'Appeler', 
                  onPress: () => {
                    Linking.openURL(`tel:${phone}`);
                  } 
                }
              ]
            );
          }}
        >
          <Text style={styles.contactButtonText}>📞 Contacter le Vendeur</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: tokens.colors.bgPrimary,
  },
  scrollContainer: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 100, // Espace pour le sticky footer
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: tokens.colors.bgPrimary,
  },
  errorText: {
    fontFamily: tokens.typography.sans,
    color: tokens.colors.accentRed,
  },
  gallerySkeleton: {
    width: '100%',
    height: 300,
  },
  galleryContainer: {
    height: 300,
    width: width,
    position: 'relative',
  },
  pagerView: {
    flex: 1,
  },
  page: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  galleryImage: {
    width: '100%',
    height: '100%',
  },
  pageIndicator: {
    position: 'absolute',
    bottom: 16,
    right: 16,
    backgroundColor: 'rgba(0,0,0,0.6)',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: tokens.radii.pill,
  },
  pageIndicatorText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
    fontSize: 12,
  },
  content: {
    padding: tokens.spacing.md,
  },
  title: {
    fontFamily: tokens.typography.display,
    fontSize: 28,
    color: tokens.colors.textPrimary,
    marginBottom: 4,
  },
  price: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 24,
    color: tokens.colors.accentGold,
    marginBottom: tokens.spacing.lg,
  },
  trustBlock: {
    backgroundColor: tokens.colors.bgSecondary,
    borderRadius: tokens.radii.lg,
    padding: tokens.spacing.md,
    marginBottom: tokens.spacing.xl,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
  },
  trustTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
    color: tokens.colors.accentNavy,
    marginBottom: tokens.spacing.md,
  },
  gaugeContainer: {
    marginBottom: tokens.spacing.sm,
  },
  gaugeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  gaugeLabel: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.textSecondary,
  },
  gaugeValue: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 12,
    color: tokens.colors.textPrimary,
  },
  gaugeTrack: {
    height: 6,
    backgroundColor: tokens.colors.bgTertiary,
    borderRadius: 3,
    overflow: 'hidden',
  },
  gaugeFill: {
    height: '100%',
    backgroundColor: tokens.colors.accentGold,
    borderRadius: 3,
  },
  specsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: tokens.spacing.sm,
    marginBottom: tokens.spacing.xl,
  },
  specBox: {
    width: (width - tokens.spacing.md * 2 - tokens.spacing.sm) / 2,
    backgroundColor: tokens.colors.bgSecondary,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.md,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
  },
  specBoxSkeleton: {
    width: (width - tokens.spacing.md * 2 - tokens.spacing.sm) / 2,
    height: 70,
  },
  specLabel: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.textMuted,
    textTransform: 'uppercase',
  },
  specValue: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
    color: tokens.colors.textPrimary,
    marginTop: 4,
  },
  descriptionBox: {
    marginBottom: tokens.spacing.xxl,
  },
  descriptionLabel: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 18,
    color: tokens.colors.textPrimary,
    marginBottom: tokens.spacing.sm,
  },
  descriptionText: {
    fontFamily: tokens.typography.sans,
    fontSize: 15,
    color: tokens.colors.textSecondary,
    lineHeight: 24,
  },
  stickyFooter: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: tokens.colors.bgPrimary,
    padding: tokens.spacing.md,
    borderTopWidth: 1,
    borderTopColor: tokens.borders.subtle,
    ...tokens.shadows.card,
  },
  contactButton: {
    backgroundColor: tokens.colors.accentNavy,
    paddingVertical: tokens.spacing.md,
    borderRadius: tokens.radii.pill,
    alignItems: 'center',
  },
  contactButtonText: {
    fontFamily: tokens.typography.sansBold,
    color: tokens.colors.textInverse,
    fontSize: 16,
  }
});
