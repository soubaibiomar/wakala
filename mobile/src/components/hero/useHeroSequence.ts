import { useEffect } from 'react';
import { 
  useSharedValue, 
  withTiming, 
  withDelay, 
  Easing 
} from 'react-native-reanimated';

export function useHeroSequence() {
  // 1. Voiture apparaît
  const carOpacity = useSharedValue(0);
  const carScale = useSharedValue(0.9);
  
  // 2. Phares s'allument
  const headlightsOpacity = useSharedValue(0);
  
  // 3. La plaque devient la barre de recherche
  const plateOpacity = useSharedValue(0);
  const plateScale = useSharedValue(0.5);
  const searchBarOpacity = useSharedValue(0);
  const searchBarTranslateY = useSharedValue(20);

  useEffect(() => {
    // Étape 1 : Voiture (0 - 600ms)
    carOpacity.value = withTiming(1, { duration: 600 });
    carScale.value = withTiming(1, { duration: 600, easing: Easing.out(Easing.exp) });

    // Étape 2 : Phares (600 - 1000ms)
    headlightsOpacity.value = withDelay(
      600,
      withTiming(1, { duration: 400 })
    );

    // Étape 3 : Plaque d'immatriculation (1000ms)
    plateOpacity.value = withDelay(
      800,
      withTiming(1, { duration: 300 })
    );
    plateScale.value = withDelay(
      800,
      withTiming(1, { duration: 400, easing: Easing.elastic(1) })
    );

    // Étape 4 : Barre de recherche apparaît juste en dessous ou remplace la plaque (1200ms)
    searchBarOpacity.value = withDelay(
      1200,
      withTiming(1, { duration: 400 })
    );
    searchBarTranslateY.value = withDelay(
      1200,
      withTiming(0, { duration: 400, easing: Easing.out(Easing.back(1.5)) })
    );
  }, []);

  return {
    carOpacity,
    carScale,
    headlightsOpacity,
    plateOpacity,
    plateScale,
    searchBarOpacity,
    searchBarTranslateY,
  };
}
