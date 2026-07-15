import React from 'react';
import { View, StyleSheet, Text, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
import { MainTabParamList } from '../navigation/AppNavigator';

import HeroCar from '../components/hero/HeroCar';
import SearchBar from '../components/hero/SearchBar';
import { useHeroSequence } from '../components/hero/useHeroSequence';
import { tokens } from '../styles/tokens';
import Animated, { useAnimatedStyle } from 'react-native-reanimated';

type HomeScreenNavigationProp = NativeStackNavigationProp<MainTabParamList, 'Home'>;

export default function HomeScreen() {
  const sequence = useHeroSequence();

  // On peut animer d'autres éléments (titres) en fonction de la séquence
  // Mais la recherche et la voiture sont les pièces maîtresses.
  const titleAnimatedStyle = useAnimatedStyle(() => ({
    opacity: sequence.carOpacity.value, 
    transform: [{ translateY: 20 * (1 - sequence.carOpacity.value) }]
  }));

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
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
});
