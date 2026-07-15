import React, { useEffect } from 'react';
import { StyleSheet, ViewStyle } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withRepeat,
  withTiming,
  Easing,
  interpolateColor,
} from 'react-native-reanimated';
import { tokens } from '../../styles/tokens';

interface SkeletonProps {
  style?: ViewStyle;
}

export function Skeleton({ style }: SkeletonProps) {
  const animatedValue = useSharedValue(0);

  useEffect(() => {
    animatedValue.value = withRepeat(
      withTiming(1, { duration: 1200, easing: Easing.inOut(Easing.ease) }),
      -1,
      true
    );
  }, []);

  const animatedStyle = useAnimatedStyle(() => {
    const backgroundColor = interpolateColor(
      animatedValue.value,
      [0, 1],
      ['#F8F7F4', '#EDE9E0']
    );

    return {
      backgroundColor: backgroundColor as any,
    };
  });

  return <Animated.View style={[styles.skeleton, style, animatedStyle]} />;
}

const styles = StyleSheet.create({
  skeleton: {
    borderRadius: tokens.radii.sm,
    backgroundColor: tokens.colors.bgSecondary,
  },
});
