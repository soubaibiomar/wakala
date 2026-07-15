import { useCallback, useRef, useState } from 'react';
import { chatbotService } from '../../services/chatbotService';

export interface SourceRef {
  vehicle_id: string;
  vehicle_title: string;
  relevance_score: number;
  source_type: string;
  image_url?: string;
  price?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceRef[];
  style_profile?: { formality: string; verbosity: string; technicality: string };
  timestamp: number;
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

function getOrCreateSessionId(): string {
  const key = 'wakala_chat_session';
  let sid = sessionStorage.getItem(key);
  if (!sid) {
    sid = 'chat-' + generateId();
    sessionStorage.setItem(key, sid);
  }
  return sid;
}

export function useChatSession() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionIdRef = useRef<string>(getOrCreateSessionId());

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    const userMsg: Message = {
      id: generateId(),
      role: 'user',
      content: trimmed,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);
    setError(null);

    // Prepare assistant message stub
    const assistantId = generateId();
    const assistantMsg: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    };
    
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      // Build history for backend (excluding the current user message just added)
      // Actually, we can just pass the previous messages
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      
      await chatbotService.streamMessage(trimmed, history, (chunk: string) => {
        setMessages((prev) => {
          return prev.map(msg => {
            if (msg.id === assistantId) {
              return { ...msg, content: msg.content + chunk };
            }
            return msg;
          });
        });
        // Scroll bottom effect can be triggered if needed, but handled by useEffect usually
      });
      
    } catch {
      setMessages((prev) => {
        return prev.map(msg => {
          if (msg.id === assistantId && !msg.content) {
            return { ...msg, content: 'Désolé, je rencontre une difficulté technique. Veuillez réessayer.' };
          }
          return msg;
        });
      });
      setError('Erreur de communication avec le serveur.');
    } finally {
      setIsTyping(false);
    }
  }, [messages]);

  const clearHistory = useCallback(() => {
    setMessages([]);
    setError(null);
    const newSid = 'chat-' + generateId();
    sessionIdRef.current = newSid;
    sessionStorage.setItem('wakala_chat_session', newSid);
  }, []);

  return {
    messages,
    isTyping,
    error,
    sendMessage,
    clearHistory,
    sessionId: sessionIdRef.current,
  };
}
