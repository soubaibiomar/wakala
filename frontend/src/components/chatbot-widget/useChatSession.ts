import { useCallback, useRef, useState } from 'react';
import { chatbotService } from '../../services/chatbotService';

export interface SourceRef {
  vehicle_id: string;
  vehicle_title: string;
  relevance_score: number;
  source_type: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceRef[];
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

    try {
      const { data } = await chatbotService.sendMessage(trimmed, sessionIdRef.current);

      const assistantMsg: Message = {
        id: generateId(),
        role: 'assistant',
        content: data.reply,
        sources: data.sources?.filter((s) => s.relevance_score > 0) || [],
        timestamp: Date.now(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch {
      const fallback: Message = {
        id: generateId(),
        role: 'assistant',
        content: 'Desole, je rencontre une difficulte technique. Veuillez reessayer.',
        timestamp: Date.now(),
      };
      setMessages((prev) => [...prev, fallback]);
      setError('Erreur de communication avec le serveur.');
    } finally {
      setIsTyping(false);
    }
  }, []);

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
