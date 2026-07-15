import React, { useState } from 'react';
import { View, StyleSheet, Text, TextInput, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { tokens } from '../styles/tokens';
import { authService } from '../services/authService';
import { useAuth } from '../context/AuthContext';

export default function LoginScreen() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const navigation = useNavigation<any>();
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs.');
      return;
    }

    setIsLoading(true);
    try {
      const response = await authService.login(email, password);
      await login(response.access_token);
      navigation.navigate('MainTabs', { screen: 'Home' });
    } catch (e: any) {
      console.error(e);
      Alert.alert('Erreur', 'Email ou mot de passe incorrect.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Bienvenue sur Wakala</Text>
      
      <View style={styles.form}>
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
        
        <TouchableOpacity style={styles.button} onPress={handleLogin} disabled={isLoading}>
          {isLoading ? (
            <ActivityIndicator color={tokens.colors.textInverse} />
          ) : (
            <Text style={styles.buttonText}>Se connecter</Text>
          )}
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.linkButton} 
          onPress={() => navigation.navigate('Register')}
        >
          <Text style={styles.linkText}>Pas encore de compte ? S'inscrire</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
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
