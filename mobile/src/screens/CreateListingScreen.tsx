import React, { useState, useEffect } from 'react';
import { 
  View, StyleSheet, Text, TextInput, TouchableOpacity, 
  ScrollView, Image, Alert, ActivityIndicator, Modal 
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { tokens } from '../styles/tokens';
import { vehicleService } from '../services/vehicleService';
import VehiclePhotoCapture from '../components/camera/VehiclePhotoCapture';

export default function CreateListingScreen() {
  const navigation = useNavigation<any>();

  const [brand, setBrand] = useState('');
  const [model, setModel] = useState('');
  const [year, setYear] = useState('');
  const [price, setPrice] = useState('');
  const [city, setCity] = useState('');
  const [description, setDescription] = useState('');
  
  const [photos, setPhotos] = useState<{uri: string, score?: number}[]>([]);
  const [isCameraVisible, setIsCameraVisible] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const [predictedPrice, setPredictedPrice] = useState<number | null>(null);

  // Appel au PriceEstimator dès que la marque, modèle et année sont remplis
  useEffect(() => {
    if (brand.length > 2 && model.length > 1 && year.length === 4) {
      const fetchPrice = async () => {
        try {
          const result = await vehicleService.predictPrice({
            brand,
            model,
            year: parseInt(year),
            mileage: 50000, // On suppose un kilométrage moyen si non renseigné
          });
          setPredictedPrice(result.predicted_price);
        } catch (e) {
          console.log("Prediction non disponible");
        }
      };
      fetchPrice();
    }
  }, [brand, model, year]);

  const handleGenerateDescription = async () => {
    if (!brand || !model || !year) {
      Alert.alert('Erreur', 'Veuillez remplir au moins la marque, le modèle et l\'année.');
      return;
    }
    
    setIsGenerating(true);
    try {
      const res = await vehicleService.generateDescription({
        brand, model, year: parseInt(year), city
      });
      setDescription(res.description || res.generated_text || "Description générée non trouvée.");
    } catch (e) {
      Alert.alert('Erreur', 'Impossible de générer la description.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCaptureSuccess = (data: {uri: string, score?: number}) => {
    setPhotos(prev => [...prev, data]);
    setIsCameraVisible(false);
  };

  const handleRemovePhoto = (index: number) => {
    setPhotos(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (photos.length < 3) {
      Alert.alert('Attention', 'Vous devez ajouter au minimum 3 photos pour publier l\'annonce.');
      return;
    }
    if (!brand || !model || !year || !price || !city) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs obligatoires.');
      return;
    }

    setIsSubmitting(true);
    try {
      // Simuler l'envoi des infos + photos 
      // (Dans une vraie app, on upload d'abord sur S3/Cloud Storage ou on envoie en multipart)
      await vehicleService.createListing({
        brand,
        model,
        year: parseInt(year),
        price: parseFloat(price),
        city,
        description,
        images: photos.map(p => p.uri)
      });
      
      Alert.alert('Succès', 'Votre annonce a été publiée avec succès !', [
        { text: 'OK', onPress: () => navigation.navigate('Home') }
      ]);
    } catch (e) {
      console.error(e);
      Alert.alert('Erreur', 'Une erreur est survenue lors de la publication.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isCameraVisible) {
    return (
      <VehiclePhotoCapture 
        onCaptureSuccess={handleCaptureSuccess}
        onCancel={() => setIsCameraVisible(false)}
      />
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.title}>Vendre mon véhicule</Text>
      
      {/* ─── PHOTOS ─── */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Photos ({photos.length}/3 min)</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.photoScroll}>
          {photos.map((photo, index) => (
            <View key={index} style={styles.photoThumbnail}>
              <Image source={{ uri: photo.uri }} style={styles.photoImage} />
              {photo.score && (
                <View style={styles.scoreBadge}>
                  <Text style={styles.scoreText}>IA {(photo.score * 100).toFixed(0)}%</Text>
                </View>
              )}
              <TouchableOpacity style={styles.removePhoto} onPress={() => handleRemovePhoto(index)}>
                <Text style={styles.removePhotoText}>X</Text>
              </TouchableOpacity>
            </View>
          ))}
          
          <TouchableOpacity style={styles.addPhotoButton} onPress={() => setIsCameraVisible(true)}>
            <Text style={styles.addPhotoIcon}>📷</Text>
            <Text style={styles.addPhotoText}>Ajouter</Text>
          </TouchableOpacity>
        </ScrollView>
        {photos.length < 3 && (
          <Text style={styles.warningText}>* Encore {3 - photos.length} photo(s) requise(s)</Text>
        )}
      </View>

      {/* ─── INFOS ─── */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Informations</Text>
        
        <Text style={styles.label}>Marque</Text>
        <TextInput style={styles.input} value={brand} onChangeText={setBrand} placeholder="ex: Renault" />
        
        <Text style={styles.label}>Modèle</Text>
        <TextInput style={styles.input} value={model} onChangeText={setModel} placeholder="ex: Clio 4" />
        
        <View style={styles.row}>
          <View style={{ flex: 1, marginRight: tokens.spacing.sm }}>
            <Text style={styles.label}>Année</Text>
            <TextInput style={styles.input} value={year} onChangeText={setYear} keyboardType="numeric" placeholder="2020" maxLength={4} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.label}>Ville</Text>
            <TextInput style={styles.input} value={city} onChangeText={setCity} placeholder="ex: Casablanca" />
          </View>
        </View>
        
        <Text style={styles.label}>Prix (MAD)</Text>
        <TextInput style={styles.input} value={price} onChangeText={setPrice} keyboardType="numeric" placeholder="120000" />
        
        {predictedPrice && (
          <View style={styles.predictionBox}>
            <Text style={styles.predictionTitle}>Estimation IA Wakala</Text>
            <Text style={styles.predictionPrice}>{predictedPrice.toLocaleString('fr-FR')} MAD</Text>
          </View>
        )}
      </View>

      {/* ─── DESCRIPTION ─── */}
      <View style={styles.section}>
        <View style={styles.descriptionHeader}>
          <Text style={styles.sectionTitle}>Description</Text>
          <TouchableOpacity onPress={handleGenerateDescription} disabled={isGenerating}>
            {isGenerating ? (
              <ActivityIndicator size="small" color={tokens.colors.accentGold} />
            ) : (
              <Text style={styles.generateText}>✨ Générer avec l'IA</Text>
            )}
          </TouchableOpacity>
        </View>
        <TextInput 
          style={styles.textArea} 
          value={description} 
          onChangeText={setDescription} 
          multiline 
          numberOfLines={6}
          placeholder="Décrivez votre véhicule..."
          textAlignVertical="top"
        />
      </View>

      <TouchableOpacity 
        style={[styles.submitButton, photos.length < 3 && styles.submitButtonDisabled]} 
        onPress={handleSubmit}
        disabled={isSubmitting || photos.length < 3}
      >
        {isSubmitting ? (
          <ActivityIndicator color={tokens.colors.textInverse} />
        ) : (
          <Text style={styles.submitButtonText}>Publier l'annonce</Text>
        )}
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: tokens.colors.bgPrimary,
  },
  content: {
    padding: tokens.spacing.lg,
    paddingBottom: tokens.spacing.xxl,
  },
  title: {
    fontFamily: tokens.typography.display,
    fontSize: 28,
    color: tokens.colors.accentNavy,
    marginBottom: tokens.spacing.lg,
  },
  section: {
    marginBottom: tokens.spacing.xl,
  },
  sectionTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 18,
    color: tokens.colors.textPrimary,
    marginBottom: tokens.spacing.md,
  },
  photoScroll: {
    flexDirection: 'row',
  },
  photoThumbnail: {
    width: 100,
    height: 100,
    borderRadius: tokens.radii.md,
    marginRight: tokens.spacing.md,
    position: 'relative',
    backgroundColor: tokens.colors.bgSecondary,
  },
  photoImage: {
    width: '100%',
    height: '100%',
    borderRadius: tokens.radii.md,
  },
  scoreBadge: {
    position: 'absolute',
    bottom: 4,
    left: 4,
    backgroundColor: tokens.colors.accentNavy,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  scoreText: {
    color: tokens.colors.accentGold,
    fontSize: 10,
    fontFamily: tokens.typography.sansBold,
  },
  removePhoto: {
    position: 'absolute',
    top: -8,
    right: -8,
    backgroundColor: tokens.colors.accentRed,
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  removePhotoText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  addPhotoButton: {
    width: 100,
    height: 100,
    borderRadius: tokens.radii.md,
    borderWidth: 2,
    borderColor: tokens.borders.subtle,
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
  },
  addPhotoIcon: {
    fontSize: 24,
    marginBottom: 4,
  },
  addPhotoText: {
    fontFamily: tokens.typography.sansMedium,
    color: tokens.colors.textSecondary,
    fontSize: 12,
  },
  warningText: {
    color: tokens.colors.accentGold,
    fontFamily: tokens.typography.sans,
    fontSize: 12,
    marginTop: tokens.spacing.sm,
  },
  label: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 14,
    color: tokens.colors.textSecondary,
    marginBottom: 4,
  },
  input: {
    backgroundColor: tokens.colors.bgSecondary,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
    borderRadius: tokens.radii.md,
    padding: tokens.spacing.md,
    marginBottom: tokens.spacing.md,
    fontFamily: tokens.typography.sans,
    color: tokens.colors.textPrimary,
  },
  row: {
    flexDirection: 'row',
  },
  predictionBox: {
    backgroundColor: tokens.colors.bgElevated,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.md,
    marginTop: tokens.spacing.sm,
    borderWidth: 1,
    borderColor: tokens.colors.accentGold,
    alignItems: 'center',
  },
  predictionTitle: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.textSecondary,
  },
  predictionPrice: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 20,
    color: tokens.colors.accentGold,
  },
  descriptionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: tokens.spacing.md,
  },
  generateText: {
    color: tokens.colors.accentGold,
    fontFamily: tokens.typography.sansBold,
    fontSize: 14,
  },
  textArea: {
    backgroundColor: tokens.colors.bgSecondary,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
    borderRadius: tokens.radii.md,
    padding: tokens.spacing.md,
    fontFamily: tokens.typography.sans,
    color: tokens.colors.textPrimary,
    minHeight: 120,
  },
  submitButton: {
    backgroundColor: tokens.colors.accentNavy,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.lg,
    alignItems: 'center',
    marginTop: tokens.spacing.md,
  },
  submitButtonDisabled: {
    backgroundColor: tokens.colors.bgTertiary,
  },
  submitButtonText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
  }
});
