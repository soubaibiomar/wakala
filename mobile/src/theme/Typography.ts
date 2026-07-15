import { StyleSheet, TextStyle } from 'react-native';

export const FONTS = {
  PlayfairDisplay: {
    Regular: 'PlayfairDisplay_400Regular',
    Bold: 'PlayfairDisplay_700Bold',
  },
  Inter: {
    Regular: 'Inter_400Regular',
    Medium: 'Inter_500Medium',
    Bold: 'Inter_700Bold',
  },
};

// Accessbility friendly sizes.
// 14 is the minimum recommended for body text on mobile devices.
export const FONT_SIZES = {
  xs: 12, // Use sparingly
  sm: 14,
  md: 16,
  lg: 20,
  xl: 24,
  xxl: 32,
};

export const typography = StyleSheet.create({
  h1: {
    fontFamily: FONTS.PlayfairDisplay.Bold,
    fontSize: FONT_SIZES.xxl,
    lineHeight: 40,
  },
  h2: {
    fontFamily: FONTS.PlayfairDisplay.Bold,
    fontSize: FONT_SIZES.xl,
    lineHeight: 32,
  },
  h3: {
    fontFamily: FONTS.PlayfairDisplay.Bold,
    fontSize: FONT_SIZES.lg,
    lineHeight: 28,
  },
  bodyLarge: {
    fontFamily: FONTS.Inter.Regular,
    fontSize: FONT_SIZES.md,
    lineHeight: 24,
  },
  bodyMedium: {
    fontFamily: FONTS.Inter.Regular,
    fontSize: FONT_SIZES.sm,
    lineHeight: 20,
  },
  buttonText: {
    fontFamily: FONTS.Inter.Medium,
    fontSize: FONT_SIZES.md,
  },
  label: {
    fontFamily: FONTS.Inter.Medium,
    fontSize: FONT_SIZES.sm,
  }
});
