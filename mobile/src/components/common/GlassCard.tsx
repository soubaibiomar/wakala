import React, { ReactNode } from 'react';
import { StyleSheet, ViewStyle, Platform, View } from 'react-native';
import { BlurView } from 'expo-blur';
import { useTheme } from '../../theme/ThemeProvider';

interface GlassCardProps {
  children: ReactNode;
  style?: ViewStyle;
  intensity?: number;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  style,
  intensity = 20,
}) => {
  const theme = useTheme();

  return (
    <View style={[styles.shadowContainer, style]}>
      <BlurView
        intensity={intensity}
        tint="light" // Or 'dark' based on specific needs, though we use Navy background mostly
        style={[
          styles.blurContainer,
          {
            borderRadius: theme.borderRadius.lg,
            backgroundColor: 'rgba(255, 255, 255, 0.05)', // Subtle white overlay for glass effect on dark bg
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
          },
        ]}
      >
        {children}
      </BlurView>
    </View>
  );
};

const styles = StyleSheet.create({
  shadowContainer: {
    // Android Shadow
    elevation: 10,
    // iOS Shadow
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 20,
    overflow: Platform.OS === 'android' ? 'hidden' : 'visible',
  },
  blurContainer: {
    overflow: 'hidden',
    padding: 16,
  },
});
