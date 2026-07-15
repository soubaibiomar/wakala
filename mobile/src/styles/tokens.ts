export const tokens = {
  colors: {
    // Palette principale — Thème clair
    bgPrimary: '#FFFFFF',
    bgSecondary: '#F8F7F4',
    bgTertiary: '#F1EFE9',
    bgCard: '#FFFFFF',
    bgCardHover: '#FAFAF8',
    bgElevated: '#EDE9E0',

    // Surfaces semi-transparentes
    glass: 'rgba(255, 255, 255, 0.88)',
    glassBorder: 'rgba(18, 33, 53, 0.08)',

    // Texte
    textPrimary: '#122135',
    textSecondary: '#4A5568',
    textMuted: '#8492A6',
    textInverse: '#FFFFFF',

    // Accents
    accentGold: '#AE8C4E',
    accentNavy: '#122135',
    accentBlue: '#1A3A5C',
    accentPurple: '#6B4C8A',
    accentGreen: '#2D8659',
    accentRed: '#C0392B',
    accentCyan: '#3B7A9E',
  },
  
  gradients: {
    // Note: React Native requires specific libraries like expo-linear-gradient for gradients.
    // We define arrays of colors here to be used with LinearGradient component.
    hero: ['#122135', '#1A3A5C'],
    card: ['#FFFFFF', '#F8F7F4'],
    cta: ['#AE8C4E', '#C9A24B'],
    gold: ['#AE8C4E', '#957639'],
    navy: ['#122135', '#1A3A5C'],
  },

  borders: {
    subtle: 'rgba(18, 33, 53, 0.08)',
    accent: 'rgba(174, 140, 78, 0.3)',
  },

  shadows: {
    sm: {
      shadowColor: '#122135',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.04,
      shadowRadius: 2,
      elevation: 2,
    },
    md: {
      shadowColor: '#122135',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.06,
      shadowRadius: 8,
      elevation: 4,
    },
    lg: {
      shadowColor: '#122135',
      shadowOffset: { width: 0, height: 4 },
      shadowOpacity: 0.08,
      shadowRadius: 16,
      elevation: 8,
    },
    card: {
      shadowColor: '#122135',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.05,
      shadowRadius: 3,
      elevation: 3,
    },
  },

  typography: {
    display: 'CormorantGaramond_700Bold', // Assuming fonts loaded via Expo
    sans: 'Inter_400Regular',
    sansMedium: 'Inter_500Medium',
    sansSemiBold: 'Inter_600SemiBold',
    sansBold: 'Inter_700Bold',
  },

  radii: {
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    pill: 9999,
  },

  spacing: {
    xs: 8,
    sm: 16,
    md: 24,
    lg: 32,
    xl: 48,
    xxl: 64, // 2xl
    xxxl: 80, // 3xl
  }
};
