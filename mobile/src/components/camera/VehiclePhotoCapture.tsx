import React, { useState, useRef } from 'react';
import { View, StyleSheet, Text, TouchableOpacity, Image, ActivityIndicator } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { vehicleService } from '../../services/vehicleService';
import { tokens } from '../../styles/tokens';

export default function VehiclePhotoCapture({ 
  onCaptureSuccess, 
  onCancel 
}: { 
  onCaptureSuccess: (data: { uri: string, base64?: string, score?: number }) => void,
  onCancel: () => void 
}) {
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);
  
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [analyzedPhoto, setAnalyzedPhoto] = useState<string | null>(null);
  const [conditionScore, setConditionScore] = useState<number | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!permission) {
    return <View style={styles.container}><ActivityIndicator /></View>;
  }

  if (!permission.granted) {
    return (
      <View style={styles.permissionContainer}>
        <Text style={styles.permissionTitle}>Caméra requise</Text>
        <Text style={styles.permissionText}>Nous avons besoin de l'accès à votre caméra pour prendre en photo votre véhicule et l'analyser via l'IA.</Text>
        <TouchableOpacity style={styles.primaryButton} onPress={requestPermission}>
          <Text style={styles.primaryButtonText}>Autoriser la caméra</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.cancelButton} onPress={onCancel}>
          <Text style={styles.cancelButtonText}>Annuler</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const takePicture = async () => {
    if (cameraRef.current) {
      const photoData = await cameraRef.current.takePictureAsync({ base64: true });
      if (photoData) {
        setPhotoUri(photoData.uri);
        analyzePhoto(photoData.uri);
      }
    }
  };

  const analyzePhoto = async (uri: string) => {
    setIsAnalyzing(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('file', {
        uri: uri,
        name: 'photo.jpg',
        type: 'image/jpeg',
      } as any);

      // Appel de l'API /api/v1/vision/analyze
      const result = await vehicleService.analyzeImage('temp', formData);
      
      // result contient image_base64 et condition_score
      setAnalyzedPhoto(result.image_base64 || uri);
      setConditionScore(result.condition_score);
    } catch (err) {
      console.error(err);
      setError('Erreur lors de l\'analyse. Vous pouvez réessayer.');
      // En cas d'erreur, on permet quand même d'utiliser la photo brute si on veut, 
      // ou on force à recommencer. Ici on force à recommencer pour respecter le flux IA.
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleValidate = () => {
    if (analyzedPhoto) {
      onCaptureSuccess({ uri: analyzedPhoto, score: conditionScore || undefined });
    }
  };

  const handleRetake = () => {
    setPhotoUri(null);
    setAnalyzedPhoto(null);
    setConditionScore(null);
    setError(null);
  };

  // ─── Vue Validation de l'image analysée ───────────────────────────────────
  if (photoUri && !isAnalyzing) {
    return (
      <View style={styles.container}>
        <Image source={{ uri: analyzedPhoto || photoUri }} style={styles.camera} resizeMode="contain" />
        
        {/* Résultat de l'analyse */}
        <View style={styles.analysisOverlay}>
          {error ? (
            <Text style={styles.errorText}>{error}</Text>
          ) : (
            <View style={styles.scoreContainer}>
              <Text style={styles.scoreLabel}>État détecté par IA :</Text>
              <Text style={styles.scoreValue}>{conditionScore ? `${(conditionScore * 100).toFixed(0)}%` : 'N/A'}</Text>
              <Text style={styles.infoText}>La plaque a été automatiquement floutée.</Text>
            </View>
          )}
        </View>

        {/* Boutons d'action */}
        <View style={styles.actionRow}>
          <TouchableOpacity style={styles.retakeButton} onPress={handleRetake}>
            <Text style={styles.retakeText}>Reprendre</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.validateButton, error ? styles.disabledButton : null]} 
            onPress={handleValidate}
            disabled={!!error}
          >
            <Text style={styles.validateText}>Valider cette photo</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  // ─── Vue Chargement / Analyse ──────────────────────────────────────────────
  if (photoUri && isAnalyzing) {
    return (
      <View style={styles.container}>
        <Image source={{ uri: photoUri }} style={styles.camera} resizeMode="contain" />
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color={tokens.colors.accentGold} />
          <Text style={styles.loadingText}>Analyse IA en cours...</Text>
          <Text style={styles.loadingSubtext}>Détection d'état et floutage de la plaque</Text>
        </View>
      </View>
    );
  }

  // ─── Vue Prise de photo (Caméra) ───────────────────────────────────────────
  return (
    <View style={styles.container}>
      <CameraView style={styles.camera} ref={cameraRef} facing="back">
        <TouchableOpacity style={styles.closeButton} onPress={onCancel}>
          <Text style={styles.closeButtonText}>X</Text>
        </TouchableOpacity>
        <View style={styles.buttonContainer}>
          <TouchableOpacity style={styles.captureButton} onPress={takePicture}>
            <View style={styles.captureInner} />
          </TouchableOpacity>
        </View>
      </CameraView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
  },
  permissionContainer: {
    flex: 1,
    backgroundColor: tokens.colors.bgPrimary,
    justifyContent: 'center',
    padding: tokens.spacing.xl,
  },
  permissionTitle: {
    fontFamily: tokens.typography.display,
    fontSize: 24,
    color: tokens.colors.textPrimary,
    marginBottom: tokens.spacing.md,
    textAlign: 'center',
  },
  permissionText: {
    fontFamily: tokens.typography.sans,
    fontSize: 16,
    color: tokens.colors.textSecondary,
    textAlign: 'center',
    marginBottom: tokens.spacing.xxl,
  },
  primaryButton: {
    backgroundColor: tokens.colors.accentNavy,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.pill,
    alignItems: 'center',
    marginBottom: tokens.spacing.md,
  },
  primaryButtonText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
  },
  cancelButton: {
    padding: tokens.spacing.md,
    alignItems: 'center',
  },
  cancelButtonText: {
    color: tokens.colors.textSecondary,
    fontFamily: tokens.typography.sansMedium,
    fontSize: 16,
  },
  camera: {
    flex: 1,
  },
  closeButton: {
    position: 'absolute',
    top: 40,
    left: 20,
    backgroundColor: 'rgba(0,0,0,0.5)',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  buttonContainer: {
    flex: 1,
    backgroundColor: 'transparent',
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'flex-end',
    marginBottom: 40,
  },
  captureButton: {
    width: 70,
    height: 70,
    borderRadius: 35,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  captureInner: {
    width: 54,
    height: 54,
    borderRadius: 27,
    backgroundColor: '#fff',
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: 'rgba(18, 33, 53, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
    fontSize: 20,
    marginTop: tokens.spacing.lg,
  },
  loadingSubtext: {
    color: tokens.colors.textMuted,
    fontFamily: tokens.typography.sans,
    fontSize: 14,
    marginTop: tokens.spacing.sm,
  },
  analysisOverlay: {
    position: 'absolute',
    top: 60,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(18, 33, 53, 0.85)',
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.lg,
  },
  scoreContainer: {
    alignItems: 'center',
  },
  scoreLabel: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansMedium,
    fontSize: 14,
  },
  scoreValue: {
    color: tokens.colors.accentGold,
    fontFamily: tokens.typography.display,
    fontSize: 36,
    marginVertical: tokens.spacing.xs,
  },
  infoText: {
    color: '#10B981', // green
    fontFamily: tokens.typography.sansBold,
    fontSize: 12,
  },
  errorText: {
    color: tokens.colors.accentRed,
    fontFamily: tokens.typography.sansBold,
    textAlign: 'center',
  },
  actionRow: {
    position: 'absolute',
    bottom: 40,
    left: 20,
    right: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  retakeButton: {
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingVertical: tokens.spacing.md,
    paddingHorizontal: tokens.spacing.lg,
    borderRadius: tokens.radii.pill,
  },
  retakeText: {
    color: '#fff',
    fontFamily: tokens.typography.sansBold,
  },
  validateButton: {
    backgroundColor: tokens.colors.accentGold,
    paddingVertical: tokens.spacing.md,
    paddingHorizontal: tokens.spacing.lg,
    borderRadius: tokens.radii.pill,
  },
  disabledButton: {
    backgroundColor: tokens.colors.bgTertiary,
  },
  validateText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
  }
});
