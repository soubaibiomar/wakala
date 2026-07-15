import { useState, useCallback, useRef } from 'react';
import { chatService, ChatMessage } from '../services/chatService';

export function useChatSession() {
  const [messages, setMessages] = useState<ChatMessage[]>([{
    id: 'welcome',
    role: 'assistant',
    content: 'Bonjour ! Je suis Wakala, votre assistant IA. Comment puis-je vous aider à trouver votre prochain véhicule ?',
    timestamp: new Date().toISOString()
  }]);
  const [isTyping, setIsTyping] = useState(false);
  
  // Générer un ID de session unique pour l'app
  const sessionIdRef = useRef(`session_${Math.random().toString(36).substr(2, 9)}`);

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
      const response = await chatService.sendMessage(sessionIdRef.current, content);
      
      const assistantMessage: ChatMessage = {
        id: response.id || `ast_${Date.now()}`,
        role: 'assistant',
        content: response.content || (response as any).response || 'Voici les informations demandées.',
        timestamp: response.timestamp || new Date().toISOString(),
        suggested_vehicles: response.suggested_vehicles || (response as any).vehicles || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Erreur Chat:', error);
      
      const errorMessage: ChatMessage = {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: 'Désolé, je rencontre des difficultés techniques. Veuillez réessayer.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  }, []);

  return {
    messages,
    isTyping,
    sendMessage
  };
}
