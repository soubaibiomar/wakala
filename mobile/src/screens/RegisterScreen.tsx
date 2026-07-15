import React, { useState } from 'react';
import { View, StyleSheet, Text, TextInput, TouchableOpacity, Alert, ActivityIndicator, ScrollView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { tokens } from '../styles/tokens';
import { authService } from '../services/authService';

export default function RegisterScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('+212');
  const [phoneError, setPhoneError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const navigation = useNavigation<any>();

  const validatePhone = (text: string) => {
    // Force prefix +212
    if (!text.startsWith('+212')) {
      setPhone('+212');
      return;
    }
    
    setPhone(text);
    
    // Check if it matches +212 followed by 9 digits
    const phoneRegex = /^\+212[5-7]\d{8}$/;
    if (text.length > 4 && !phoneRegex.test(text)) {
      setPhoneError('Format invalide. Ex: +212600000000');
    } else {
      setPhoneError('');
    }
  };

  const handleRegister = async () => {
    if (!email || !password || !fullName || !phone) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs.');
      return;
    }

    if (phoneError) {
      Alert.alert('Erreur', 'Veuillez corriger le numéro de téléphone.');
      return;
    }

    setIsLoading(true);
    try {
      await authService.register({
        email,
        password,
        name: fullName,
        role: 'buyer', // par défaut
        phone: phone,
      });
      Alert.alert('Succès', 'Compte créé ! Vous pouvez vous connecter.');
      navigation.navigate('Login');
    } catch (e: any) {
      console.error(e);
      // Basic error handling based on status code
      if (e.response?.status === 400) {
        Alert.alert('Erreur', 'Cet email est probablement déjà utilisé.');
      } else {
        Alert.alert('Erreur', 'Une erreur est survenue lors de l\'inscription.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Rejoignez Wakala</Text>
      
      <View style={styles.form}>
        <Text style={styles.label}>Nom complet</Text>
        <TextInput 
          style={styles.input}
          value={fullName}
          onChangeText={setFullName}
          placeholder="Jean Dupont"
        />

        <Text style={styles.label}>Téléphone</Text>
        <TextInput 
          style={[styles.input, phoneError ? styles.inputError : null]}
          value={phone}
          onChangeText={validatePhone}
          keyboardType="phone-pad"
          maxLength={13}
        />
        {phoneError ? <Text style={styles.errorText}>{phoneError}</Text> : null}
        
        <Text style={styles.label}>Email</Text>
        <TextInput 
          style={styles.input}
          value={email}
          onChangeText={setEmail}
          placeholder="votre@email.com"
          keyboardType="email-address"
          autoCapitalize="none"
        />
        
        <Text style={styles.label}>Mot de passe</Text>
        <TextInput 
          style={styles.input}
          value={password}
          onChangeText={setPassword}
          placeholder="********"
          secureTextEntry
        />
        
        <TouchableOpacity style={styles.button} onPress={handleRegister} disabled={isLoading}>
          {isLoading ? (
            <ActivityIndicator color={tokens.colors.textInverse} />
          ) : (
            <Text style={styles.buttonText}>Créer mon compte</Text>
          )}
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.linkButton} 
          onPress={() => navigation.navigate('Login')}
        >
          <Text style={styles.linkText}>Déjà un compte ? Se connecter</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: tokens.colors.bgPrimary,
    justifyContent: 'center',
    padding: tokens.spacing.lg,
  },
  title: {
    fontFamily: tokens.typography.display,
    fontSize: 28,
    color: tokens.colors.accentNavy,
    textAlign: 'center',
    marginBottom: tokens.spacing.xxl,
  },
  form: {
    backgroundColor: tokens.colors.bgSecondary,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.lg,
    ...tokens.shadows.md,
  },
  label: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 14,
    color: tokens.colors.textSecondary,
    marginBottom: tokens.spacing.xs,
  },
  input: {
    backgroundColor: tokens.colors.bgPrimary,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
    borderRadius: tokens.radii.md,
    padding: tokens.spacing.sm,
    marginBottom: tokens.spacing.md,
    fontFamily: tokens.typography.sans,
  },
  inputError: {
    borderColor: tokens.colors.accentRed,
  },
  errorText: {
    color: tokens.colors.accentRed,
    fontSize: 12,
    marginTop: -tokens.spacing.sm,
    marginBottom: tokens.spacing.md,
  },
  button: {
    backgroundColor: tokens.colors.accentGold,
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.md,
    alignItems: 'center',
    marginTop: tokens.spacing.sm,
  },
  buttonText: {
    color: tokens.colors.textInverse,
    fontFamily: tokens.typography.sansBold,
    fontSize: 16,
  },
  linkButton: {
    marginTop: tokens.spacing.md,
    alignItems: 'center',
  },
  linkText: {
    fontFamily: tokens.typography.sansMedium,
    color: tokens.colors.accentGold,
    fontSize: 14,
  }
});
