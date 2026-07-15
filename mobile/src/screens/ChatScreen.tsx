import React, { useState, useRef, useEffect } from 'react';
import { 
  View, StyleSheet, Text, TextInput, TouchableOpacity, 
  FlatList, KeyboardAvoidingView, Platform, Keyboard, ScrollView
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { tokens } from '../styles/tokens';
import { useChatSession } from '../hooks/useChatSession';
import { ChatMessage } from '../services/chatService';

// Un composant miniature pour afficher la source (véhicule) citée
const SourceVehicleCard = ({ vehicle, onPress }: { vehicle: any, onPress: () => void }) => {
  const imageUri = vehicle.images?.[0]?.file_path || vehicle.image_url || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?q=80&w=600';
  
  return (
    <TouchableOpacity style={styles.sourceCard} onPress={onPress} activeOpacity={0.8}>
      {/* On simule une petite vue avec image et texte */}
      <View style={styles.sourceImagePlaceholder}>
        <Text style={styles.sourceImageText}>🚗</Text>
      </View>
      <View style={styles.sourceInfo}>
        <Text style={styles.sourceTitle} numberOfLines={1}>{vehicle.brand} {vehicle.model}</Text>
        <Text style={styles.sourcePrice}>{vehicle.price ? `${vehicle.price.toLocaleString('fr-FR')} MAD` : 'Prix n/d'}</Text>
      </View>
    </TouchableOpacity>
  );
};

export default function ChatScreen() {
  const { messages, isTyping, sendMessage } = useChatSession();
  const [inputText, setInputText] = useState('');
  const flatListRef = useRef<FlatList>(null);
  const navigation = useNavigation<any>();

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    setTimeout(() => {
      flatListRef.current?.scrollToEnd({ animated: true });
    }, 200);
  }, [messages, isTyping]);

  const handleSend = () => {
    if (!inputText.trim()) return;
    sendMessage(inputText);
    setInputText('');
    Keyboard.dismiss();
  };

  const navigateToVehicle = (vehicleId: string) => {
    navigation.navigate('VehicleDetail', { vehicleId });
  };

  const renderMessage = ({ item }: { item: ChatMessage }) => {
    const isUser = item.role === 'user';

    return (
      <View style={[styles.messageWrapper, isUser ? styles.messageWrapperUser : styles.messageWrapperAssistant]}>
        <View style={[styles.messageBubble, isUser ? styles.messageBubbleUser : styles.messageBubbleAssistant]}>
          <Text style={[styles.messageText, isUser ? styles.messageTextUser : styles.messageTextAssistant]}>
            {item.content}
          </Text>
          
          {/* Si des véhicules sont suggérés, on affiche les "sources" */}
          {!isUser && item.suggested_vehicles && item.suggested_vehicles.length > 0 && (
            <View style={styles.sourcesContainer}>
              <Text style={styles.sourcesTitle}>Véhicules suggérés :</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.sourcesScroll}>
                {item.suggested_vehicles.map((v, i) => (
                  <SourceVehicleCard 
                    key={v.id || i} 
                    vehicle={v} 
                    onPress={() => navigateToVehicle(v.id)} 
                  />
                ))}
              </ScrollView>
            </View>
          )}
        </View>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Assistant IA</Text>
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={item => item.id}
        renderItem={renderMessage}
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
        ListFooterComponent={
          isTyping ? (
            <View style={styles.typingContainer}>
              <Text style={styles.typingText}>Wakala réfléchit...</Text>
            </View>
          ) : null
        }
      />

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          value={inputText}
          onChangeText={setInputText}
          placeholder="Posez votre question..."
          placeholderTextColor={tokens.colors.textMuted}
          multiline
          maxLength={500}
        />
        <TouchableOpacity 
          style={[styles.sendButton, !inputText.trim() && styles.sendButtonDisabled]} 
          onPress={handleSend}
          disabled={!inputText.trim() || isTyping}
        >
          <Text style={styles.sendButtonText}>Envoyer</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: tokens.colors.bgSecondary,
  },
  header: {
    padding: tokens.spacing.md,
    backgroundColor: tokens.colors.bgPrimary,
    borderBottomWidth: 1,
    borderBottomColor: tokens.borders.subtle,
    alignItems: 'center',
  },
  headerTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 18,
    color: tokens.colors.textPrimary,
  },
  listContent: {
    padding: tokens.spacing.md,
    paddingBottom: tokens.spacing.xl,
  },
  messageWrapper: {
    marginBottom: tokens.spacing.md,
    flexDirection: 'row',
  },
  messageWrapperUser: {
    justifyContent: 'flex-end',
  },
  messageWrapperAssistant: {
    justifyContent: 'flex-start',
  },
  messageBubble: {
    maxWidth: '85%',
    padding: tokens.spacing.md,
    borderRadius: tokens.radii.lg,
  },
  messageBubbleUser: {
    backgroundColor: tokens.colors.accentNavy,
    borderBottomRightRadius: 4,
  },
  messageBubbleAssistant: {
    backgroundColor: tokens.colors.bgPrimary,
    borderBottomLeftRadius: 4,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
  },
  messageText: {
    fontFamily: tokens.typography.sans,
    fontSize: 15,
    lineHeight: 22,
  },
  messageTextUser: {
    color: tokens.colors.textInverse,
  },
  messageTextAssistant: {
    color: tokens.colors.textPrimary,
  },
  typingContainer: {
    padding: tokens.spacing.md,
    alignItems: 'flex-start',
  },
  typingText: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 13,
    color: tokens.colors.textMuted,
    fontStyle: 'italic',
  },
  sourcesContainer: {
    marginTop: tokens.spacing.md,
    borderTopWidth: 1,
    borderTopColor: tokens.borders.subtle,
    paddingTop: tokens.spacing.md,
  },
  sourcesTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 12,
    color: tokens.colors.textSecondary,
    marginBottom: tokens.spacing.sm,
  },
  sourcesScroll: {
    flexDirection: 'row',
  },
  sourceCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: tokens.colors.bgSecondary,
    borderRadius: tokens.radii.md,
    padding: tokens.spacing.sm,
    marginRight: tokens.spacing.sm,
    width: 200,
    borderWidth: 1,
    borderColor: tokens.borders.subtle,
  },
  sourceImagePlaceholder: {
    width: 40,
    height: 40,
    backgroundColor: tokens.colors.bgTertiary,
    borderRadius: tokens.radii.sm,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: tokens.spacing.sm,
  },
  sourceImageText: {
    fontSize: 20,
  },
  sourceInfo: {
    flex: 1,
  },
  sourceTitle: {
    fontFamily: tokens.typography.sansBold,
    fontSize: 13,
    color: tokens.colors.textPrimary,
  },
  sourcePrice: {
    fontFamily: tokens.typography.sansMedium,
    fontSize: 12,
    color: tokens.colors.accentGold,
  },
  inputContainer: {
    flexDirection: 'row',
    padding: tokens.spacing.md,
    backgroundColor: tokens.colors.bgPrimary,
    borderTopWidth: 1,
    borderTopColor: tokens.borders.subtle,
    alignItems: 'flex-end',
  },
  input: {
    flex: 1,
    backgroundColor: tokens.colors.bgSecondary,
    borderRadius: tokens.radii.lg,
    paddingHorizontal: tokens.spacing.md,
    paddingTop: 12,
    paddingBottom: 12,
    fontFamily: tokens.typography.sans,
    fontSize: 15,
    color: tokens.colors.textPrimary,
    maxHeight: 100,
  },
  sendButton: {
    marginLeft: tokens.spacing.sm,
    backgroundColor: tokens.colors.accentGold,
    paddingHorizontal: tokens.spacing.lg,
    paddingVertical: 12,
    borderRadius: tokens.radii.pill,
    justifyContent: 'center',
    alignItems: 'center',
    height: 44,
  },
  sendButtonDisabled: {
    backgroundColor: tokens.colors.bgTertiary,
  },
  sendButtonText: {
    fontFamily: tokens.typography.sansBold,
    color: tokens.colors.textInverse,
    fontSize: 14,
  }
});


