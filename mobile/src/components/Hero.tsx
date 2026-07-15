import React, { useEffect } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withDelay,
  Easing,
} from 'react-native-reanimated';
import { useTheme } from '../theme/ThemeProvider';
import { typography } from '../theme/Typography';

export const Hero = () => {
  const theme = useTheme();

  // Headlight animation values
  const leftHeadlightOpacity = useSharedValue(0);
  const rightHeadlightOpacity = useSharedValue(0);
  const textOpacity = useSharedValue(0);

  useEffect(() => {
    // Left headlight turns on
    leftHeadlightOpacity.value = withTiming(1, {
      duration: 500,
      easing: Easing.inOut(Easing.ease),
    });

    // Right headlight turns on slightly after
    rightHeadlightOpacity.value = withDelay(
      200,
      withTiming(1, {
        duration: 500,
        easing: Easing.inOut(Easing.ease),
      })
    );

    // Text fades in
    textOpacity.value = withDelay(
      800,
      withTiming(1, {
        duration: 1000,
      })
    );
  }, []);

  const leftLightStyle = useAnimatedStyle(() => {
    return {
      opacity: leftHeadlightOpacity.value,
      shadowOpacity: leftHeadlightOpacity.value * 0.8,
    };
  });

  const rightLightStyle = useAnimatedStyle(() => {
    return {
      opacity: rightHeadlightOpacity.value,
      shadowOpacity: rightHeadlightOpacity.value * 0.8,
    };
  });

  const textStyle = useAnimatedStyle(() => {
    return {
      opacity: textOpacity.value,
    };
  });

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.primary }]}>
      <Animated.View style={textStyle}>
        <Text style={[typography.h1, { color: theme.colors.textLight, textAlign: 'center' }]}>
          Wakala
        </Text>
        <Text style={[typography.bodyLarge, { color: theme.colors.accent, textAlign: 'center', marginTop: 8 }]}>
          L'excellence automobile
        </Text>
      </Animated.View>

      <View style={styles.carContainer}>
        <View style={styles.carSilhouette}>
          {/* Left Headlight */}
          <Animated.View
            style={[
              styles.headlight,
              { backgroundColor: theme.colors.accent, shadowColor: theme.colors.accent },
              leftLightStyle,
            ]}
          />
          {/* Right Headlight */}
          <Animated.View
            style={[
              styles.headlight,
              { backgroundColor: theme.colors.accent, shadowColor: theme.colors.accent },
              rightLightStyle,
            ]}
          />
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    height: 400,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    overflow: 'hidden',
  },
  carContainer: {
    marginTop: 60,
    width: 200,
    height: 60,
    position: 'relative',
  },
  carSilhouette: {
    flex: 1,
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    backgroundColor: 'rgba(255, 255, 255, 0.05)',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  headlight: {
    width: 20,
    height: 10,
    borderRadius: 5,
    shadowOffset: { width: 0, height: 10 },
    shadowRadius: 20,
    elevation: 15,
  },
});
