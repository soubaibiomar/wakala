import React, { useRef, useMemo, useCallback } from 'react';
import { StyleSheet, View, Text, Pressable } from 'react-native';
import BottomSheet, { BottomSheetView } from '@gorhom/bottom-sheet';
import { useTheme } from '../theme/ThemeProvider';
import { typography } from '../theme/Typography';
import { GlassCard } from './common/GlassCard';

export const ChatbotWidget = () => {
  const theme = useTheme();
  
  // Ref for the bottom sheet
  const bottomSheetRef = useRef<BottomSheet>(null);

  // Define snap points
  const snapPoints = useMemo(() => ['25%', '50%', '90%'], []);

  // Callbacks
  const handleOpenPress = useCallback(() => {
    bottomSheetRef.current?.snapToIndex(1);
  }, []);

  return (
    <>
      {/* Floating Action Button */}
      <Pressable 
        style={[styles.fab, { backgroundColor: theme.colors.accent }]}
        onPress={handleOpenPress}
        android_ripple={{ color: theme.colors.muted, borderless: true }}
      >
        <Text style={[typography.h2, { color: theme.colors.primary }]}>W</Text>
      </Pressable>

      {/* Bottom Sheet */}
      <BottomSheet
        ref={bottomSheetRef}
        index={-1} // Closed by default
        snapPoints={snapPoints}
        enablePanDownToClose={true}
        backgroundStyle={{ backgroundColor: theme.colors.primary }}
        handleIndicatorStyle={{ backgroundColor: theme.colors.muted }}
      >
        <BottomSheetView style={styles.sheetContentContainer}>
          <Text style={[typography.h3, { color: theme.colors.accent, marginBottom: 20 }]}>
            Assistant Wakala IA
          </Text>
          
          <GlassCard style={styles.messageCard}>
            <Text style={[typography.bodyMedium, { color: theme.colors.textLight }]}>
              Bonjour ! Je suis l'IA de Wakala. 
              Posez-moi vos questions sur un véhicule, 
              les taxes douanières ou la fiabilité d'un modèle.
            </Text>
          </GlassCard>
        </BottomSheetView>
      </BottomSheet>
    </>
  );
};

const styles = StyleSheet.create({
  fab: {
    position: 'absolute',
    bottom: 30,
    right: 20,
    width: 60,
    height: 60,
    borderRadius: 30,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    zIndex: 100, // Ensure it sits above other content
  },
  sheetContentContainer: {
    flex: 1,
    padding: 24,
    alignItems: 'center',
  },
  messageCard: {
    width: '100%',
  }
});
