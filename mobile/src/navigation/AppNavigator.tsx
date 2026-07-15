import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { View, Text, StyleSheet } from 'react-native';

import { tokens } from '../styles/tokens';

import HomeScreen from '../screens/HomeScreen';
import CatalogueScreen from '../screens/CatalogueScreen';
import ChatScreen from '../screens/ChatScreen';
import VehicleDetailScreen from '../screens/VehicleDetailScreen';
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import ProfileScreen from '../screens/ProfileScreen';
import CreateListingScreen from '../screens/CreateListingScreen';
import SellerDashboardScreen from '../screens/SellerDashboardScreen';
import VehiclePhotoCapture from '../components/camera/VehiclePhotoCapture';

// Types for Navigation
export type RootStackParamList = {
  MainTabs: undefined;
  VehicleDetail: { vehicleId: string };
  Login: undefined;
  Register: undefined;
  SellerDashboard: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Catalogue: undefined;
  Create: undefined;
  Chat: undefined;
  Profile: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();
const Tab = createBottomTabNavigator<MainTabParamList>();

function MainTabs() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: tokens.colors.bgPrimary,
          borderTopColor: tokens.borders.subtle,
        },
        tabBarActiveTintColor: tokens.colors.accentGold,
        tabBarInactiveTintColor: tokens.colors.textMuted,
      }}
    >
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Catalogue" component={CatalogueScreen} />
      <Tab.Screen name="Create" component={CreateListingScreen} />
      <Tab.Screen name="Chat" component={ChatScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        screenOptions={{
          headerStyle: {
            backgroundColor: tokens.colors.bgPrimary,
          },
          headerTintColor: tokens.colors.textPrimary,
          headerShadowVisible: false,
        }}
      >
        <Stack.Screen 
          name="MainTabs" 
          component={MainTabs} 
          options={{ headerShown: false }}
        />
        <Stack.Screen 
          name="VehicleDetail" 
          component={VehicleDetailScreen} 
          options={{ title: 'Détails du véhicule' }}
        />
        <Stack.Screen 
          name="Login" 
          component={LoginScreen} 
          options={{ title: 'Connexion' }}
        />
        <Stack.Screen 
          name="Register" 
          component={RegisterScreen} 
          options={{ title: 'Inscription' }}
        />
        <Stack.Screen 
          name="SellerDashboard" 
          component={SellerDashboardScreen} 
          options={{ title: 'Tableau de bord' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: tokens.colors.bgSecondary,
  },
});
