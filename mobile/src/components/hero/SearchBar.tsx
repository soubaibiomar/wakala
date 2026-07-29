import React, { useState } from 'react';
import { View, StyleSheet, TextInput, TouchableOpacity, Text, ActivityIndicator } from 'react-native';
import { tokens } from '../../styles/tokens';
import Animated, { useAnimatedStyle } from 'react-native-reanimated';
import { useNavigation } from '@react-navigation/native';
import { vehicleService } from '../../services/vehicleService';
import { useVoiceInput } from '../../hooks/useVoiceInput';

const LANG_FLAGS: Record<string, string> = {
  'fr-FR': '🇫🇷',
  'ar-MA': '🇲🇦',
  'en-US': '🇬🇧',
};
const LANG_KEYS = Object.keys(LANG_FLAGS);

export default function SearchBar({ sequence }: { sequence: any }) {
  const { searchBarOpacity, searchBarTranslateY } = sequence;
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigation = useNavigation<any>();

  const voice = useVoiceInput({
    onTranscript: (text) => {
      setQuery((prev) => {
        const separator = prev.trim() ? ' ' : '';
        return prev + separator + text;
      });
    },
  });

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    try {
      // Pour l'instant, fallback simple: on passe la query au CatalogueScreen 
      // ou on utilise l'API directement pour pré-fetch
      // Note: Le backend hybride requiert recommendationService, mais
      // on peut envoyer la requête "brand" ou texte simple au Catalogue.
      
      // Simuler l'attente du service
      await new Promise(resolve => setTimeout(resolve, 600));
      
      navigation.navigate('Catalogue', { query });
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const animatedStyle = useAnimatedStyle(() => ({
    opacity: searchBarOpacity.value,
    transform: [{ translateY: searchBarTranslateY.value }],
  }));

  return (
    <Animated.View style={[styles.container, animatedStyle]}>
      <View style={styles.searchWrapper}>
        <TextInput 
          style={styles.input}
          placeholder={voice.status === 'listening' ? 'Parlez maintenant...' : 'Rechercher une marque, un modèle...'}
          placeholderTextColor={tokens.colors.textMuted}
          value={voice.interimTranscript ? query + (query ? ' ' : '') + voice.interimTranscript : query}
          onChangeText={setQuery}
          onSubmitEditing={handleSearch}
          returnKeyType="search"
          editable={voice.status !== 'listening'}
        />

        {voice.isSupported && (
          <View style={styles.voiceControls}>
            <TouchableOpacity 
              onPress={() => {
                const currentIndex = LANG_KEYS.indexOf(voice.lang);
                const nextIndex = (currentIndex + 1) % LANG_KEYS.length;
                voice.setLang(LANG_KEYS[nextIndex]);
              }}
              style={styles.langButton}
            >
              <Text style={styles.langEmoji}>{LANG_FLAGS[voice.lang] || '🇫🇷'}</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              onPress={voice.toggleListening}
              style={[styles.micButton, voice.status === 'listening' && styles.micButtonListening]}
            >
              <Text style={styles.micEmoji}>{voice.status === 'listening' ? '⏹️' : '🎙️'}</Text>
            </TouchableOpacity>
          </View>
        )}

        <TouchableOpacity style={styles.button} onPress={handleSearch} disabled={isLoading}>
          {isLoading ? (
            <ActivityIndicator size="small" color={tokens.colors.textInverse} />
          ) : (
            <Text style={styles.buttonText}>IA</Text>
          )}
        </TouchableOpacity>
      </View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: '100%',
    paddingHorizontal: tokens.spacing.md,
    marginTop: tokens.spacing.sm, // Appears right below the car/plate
  },
  searchWrapper: {
    flexDirection: 'row',
    backgroundColor: tokens.colors.bgPrimary,
    borderRadius: tokens.radii.pill,
    borderWidth: 1,
    borderColor: tokens.borders.accent,
    ...tokens.shadows.md,
    height: 56,
    alignItems: 'center',
    paddingHorizontal: tokens.spacing.sm,
  },
  input: {
    flex: 1,
    fontFamily: tokens.typography.sans,
    fontSize: 16,
    color: tokens.colors.textPrimary,
    paddingHorizontal: tokens.spacing.sm,
  },
  button: {
    backgroundColor: tokens.colors.accentGold,
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
    ...tokens.shadows.sm,
  },
  buttonText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
    fontSize: 14,
  },
  voiceControls: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: tokens.spacing.xs,
  },
  langButton: {
    paddingHorizontal: 4,
  },
  langEmoji: {
    fontSize: 18,
  },
  micButton: {
    padding: 6,
    borderRadius: 16,
  },
  micButtonListening: {
    backgroundColor: 'rgba(255, 0, 0, 0.1)',
  },
  micEmoji: {
    fontSize: 18,
  }
});
