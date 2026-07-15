import React from 'react';
import { 
  Pressable, 
  Text, 
  StyleSheet, 
  Platform, 
  ViewStyle, 
  TextStyle 
} from 'react-native';
import { useTheme } from '../../theme/ThemeProvider';
import { typography } from '../../theme/Typography';

interface ButtonProps {
  title: string;
  onPress: () => void;
  style?: ViewStyle;
  textStyle?: TextStyle;
  variant?: 'primary' | 'outline' | 'text';
}

export const Button: React.FC<ButtonProps> = ({
  title,
  onPress,
  style,
  textStyle,
  variant = 'primary',
}) => {
  const theme = useTheme();

  const getContainerStyle = (pressed: boolean): ViewStyle => {
    let baseStyle: ViewStyle = { ...styles.baseContainer, borderRadius: theme.borderRadius.md };
    
    if (variant === 'primary') {
      baseStyle = {
        ...baseStyle,
        backgroundColor: theme.colors.accent,
      };
    } else if (variant === 'outline') {
      baseStyle = {
        ...baseStyle,
        backgroundColor: 'transparent',
        borderWidth: 1,
        borderColor: theme.colors.accent,
      };
    } else if (variant === 'text') {
      baseStyle = {
        ...baseStyle,
        backgroundColor: 'transparent',
      };
    }

    // iOS activeOpacity simulation
    if (pressed && Platform.OS === 'ios') {
      baseStyle.opacity = 0.7;
    }

    return { ...baseStyle, ...style };
  };

  const getTextStyle = (): TextStyle => {
    let baseStyle: TextStyle = { ...typography.buttonText };

    if (variant === 'primary') {
      baseStyle.color = theme.colors.primary; // Navy text on Gold button
    } else {
      baseStyle.color = theme.colors.accent; // Gold text for outline/text
    }

    return { ...baseStyle, ...textStyle };
  };

  return (
    <Pressable
      onPress={onPress}
      style={({ pressed }) => getContainerStyle(pressed)}
      android_ripple={{ color: theme.colors.muted, borderless: false }}
    >
      <Text style={getTextStyle()}>{title}</Text>
    </Pressable>
  );
};

const styles = StyleSheet.create({
  baseContainer: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
  },
});
