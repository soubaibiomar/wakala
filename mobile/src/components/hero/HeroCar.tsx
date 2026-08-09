import React from 'react';
import { View, StyleSheet, useWindowDimensions } from 'react-native';
import Svg, { Path, Defs, LinearGradient, Stop, Ellipse, Rect } from 'react-native-svg';
import Animated, { useAnimatedStyle } from 'react-native-reanimated';

export default function HeroCar({ sequence }: { sequence: any }) {
  const { width } = useWindowDimensions();
  const CAR_WIDTH = Math.min(width * 0.85, 400); // Max width to avoid huge SVG on tablets
  const CAR_HEIGHT = CAR_WIDTH * 0.45;

  const { carOpacity, carScale, headlightsOpacity, plateOpacity, plateScale } = sequence;

  const carAnimatedStyle = useAnimatedStyle(() => ({
    opacity: carOpacity.value,
    transform: [{ scale: carScale.value }],
  }));

  const headlightAnimatedStyle = useAnimatedStyle(() => ({
    opacity: headlightsOpacity.value,
  }));

  const plateAnimatedStyle = useAnimatedStyle(() => ({
    opacity: plateOpacity.value,
    transform: [{ scale: plateScale.value }],
  }));

  return (
    <Animated.View style={[styles.container, { width: CAR_WIDTH, height: CAR_HEIGHT }, carAnimatedStyle]}>
      {/* SVG Silhouette Voiture minimaliste premium */}
      <Svg width={CAR_WIDTH} height={CAR_HEIGHT} viewBox="0 0 400 180" fill="none">
        <Defs>
          <LinearGradient id="carGrad" x1="0" y1="0" x2="0" y2="1">
            <Stop offset="0%" stopColor="#1A3A5C" />
            <Stop offset="100%" stopColor="#0B1524" />
          </LinearGradient>
          <LinearGradient id="windshieldGrad" x1="0" y1="0" x2="0" y2="1">
            <Stop offset="0%" stopColor="#0A1220" />
            <Stop offset="100%" stopColor="#122135" />
          </LinearGradient>
        </Defs>

        {/* Corps principal */}
        <Path 
          d="M 50 100 Q 100 20 200 20 Q 300 20 350 100 L 380 150 Q 385 160 380 170 L 20 170 Q 15 160 20 150 Z" 
          fill="url(#carGrad)" 
        />
        
        {/* Pare-brise */}
        <Path 
          d="M 90 95 Q 150 35 200 35 Q 250 35 310 95 Z" 
          fill="url(#windshieldGrad)" 
        />
        
        {/* Calandre / Grille frontale */}
        <Path 
          d="M 120 120 L 280 120 L 290 150 L 110 150 Z" 
          fill="#050A12" 
        />
      </Svg>

      {/* Phares avec lueur - Gérés par Reanimated View plutôt que SVG pour les ombres portées native */}
      <Animated.View style={[styles.headlight, styles.headlightLeft, headlightAnimatedStyle]} />
      <Animated.View style={[styles.headlight, styles.headlightRight, headlightAnimatedStyle]} />

      {/* Plaque d'immatriculation */}
      <Animated.View style={[styles.plateContainer, plateAnimatedStyle]}>
        <View style={styles.plate}>
          <View style={styles.plateStripe} />
          <Animated.Text style={styles.plateText}>IA AUTO</Animated.Text>
        </View>
      </Animated.View>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    marginVertical: 20,
  },
  headlight: {
    position: 'absolute',
    width: 45,
    height: 12,
    borderRadius: 6,
    backgroundColor: '#FFFFFF',
    shadowColor: '#60A5FA',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 1,
    shadowRadius: 20,
    elevation: 15,
  },
  headlightLeft: {
    left: '12%',
    top: '65%',
    transform: [{ rotate: '-8deg' }],
  },
  headlightRight: {
    right: '12%',
    top: '65%',
    transform: [{ rotate: '8deg' }],
  },
  plateContainer: {
    position: 'absolute',
    bottom: -5,
    alignSelf: 'center',
  },
  plate: {
    width: 90,
    height: 24,
    backgroundColor: '#FFFFFF',
    borderRadius: 3,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    flexDirection: 'row',
    alignItems: 'center',
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 3,
  },
  plateStripe: {
    width: 10,
    height: '100%',
    backgroundColor: '#1D4ED8', // Bleu plaque
  },
  plateText: {
    flex: 1,
    textAlign: 'center',
    fontFamily: 'Inter_700Bold', // tokens.typography.sansBold
    fontSize: 12,
    color: '#111827',
    letterSpacing: 1,
  }
});
