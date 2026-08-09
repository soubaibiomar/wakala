import React from 'react';
import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { tokens } from '../../styles/tokens';

interface MatchScoreBadgeProps {
  score: number;
  style?: ViewStyle;
}

export function MatchScoreBadge({ score, style }: MatchScoreBadgeProps) {
  let badgeColor = '#10b981'; 
  let bgColor = '#d1fae5';
  
  if (score < 50) {
    badgeColor = '#ef4444'; 
    bgColor = '#fee2e2';
  } else if (score < 80) {
    badgeColor = '#f59e0b'; 
    bgColor = '#fef3c7';
  }

  return (
    <View style={[styles.container, { backgroundColor: bgColor }, style]}>
      <Text style={styles.icon}>✨</Text>
      <Text style={[styles.text, { color: badgeColor }]}>
        Match IA {Math.round(score)}%
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: tokens.radii.pill,
  },
  icon: {
    marginRight: 4,
    fontSize: 12,
  },
  text: {
    fontSize: 12,
    fontFamily: tokens.typography.sansBold,
  },
});
