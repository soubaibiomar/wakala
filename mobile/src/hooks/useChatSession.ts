import { useState, useCallback, useRef } from 'react';
import { chatService, ChatMessage } from '../services/chatService';
import { useAuth } from '../context/AuthContext';

export function useChatSession() {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([{
    id: 'welcome',
    role: 'assistant',
    content: 'Bonjour ! Je suis Wakala, votre conseiller automobile IA. Quel type de véhicule recherchez-vous aujourd\'hui ? (ex: SUV hybride à Casablanca, budget 200 000 MAD)',
    timestamp: new Date().toISOString()
  }]);
  const [isTyping, setIsTyping] = useState(false);
  
  // Unique session ID
  const sessionIdRef = useRef(`mobile_session_${Math.random().toString(36).substr(2, 9)}`);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: `usr_${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const assistantMessage = await chatService.sendMessage(
        sessionIdRef.current, 
        content,
        user?.id
      );

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Erreur Chat:', error);
      
      const errorMessage: ChatMessage = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: 'Désolé, je rencontre des difficultés pour joindre le serveur. Veuillez vérifier votre connexion et réessayer.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, [user]);

  return {
    messages,
    isTyping,
    sendMessage
  };
}
