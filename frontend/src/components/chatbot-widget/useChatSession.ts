import { useCallback, useRef, useState, useEffect } from 'react';
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
  let sid = localStorage.getItem(key);
  if (!sid) {
    sid = 'chat-' + generateId();
    localStorage.setItem(key, sid);
  }
  return sid;
}

const HISTORY_KEY = 'wakala_chat_history';

export function useChatSession() {
  const [messages, setMessages] = useState<Message[]>(() => {
    const saved = localStorage.getItem(HISTORY_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error("Failed to parse chat history", e);
        return [];
      }
    }
    return [];
  });
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionIdRef = useRef<string>(getOrCreateSessionId());
  const abortControllerRef = useRef<AbortController | null>(null);

  // Load history from DB on mount
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const history = await chatbotService.getChatHistory();
        if (history && history.length > 0) {
          // Take the most recent session's messages
          const latestSession = history[0];
          sessionIdRef.current = latestSession.session_id;
          
          const mappedMessages: Message[] = latestSession.messages.map((m: any) => ({
            id: m.id,
            role: m.role,
            content: m.content,
            timestamp: new Date(m.timestamp).getTime()
          }));
          
          setMessages(mappedMessages);
        }
      } catch (err) {
        console.error("Failed to load chat history", err);
      }
    };
    loadHistory();
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(messages));
  }, [messages]);

  const cancelGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsTyping(false);
    }
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;

    // Cancel any in-flight request
    cancelGeneration();

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

    // Create abort controller for this request
    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      // Build history for backend (excluding the current user message just added)
      // Actually, we can just pass the previous messages
      const history = messages.map(m => ({ role: m.role, content: m.content }));
      
      await chatbotService.streamMessage(
        trimmed,
        history,
        (chunk: string) => {
          setMessages((prev) => {
            return prev.map(msg => {
              if (msg.id === assistantId) {
                return { ...msg, content: msg.content + chunk };
              }
              return msg;
            });
          });
        },
        sessionIdRef.current,
        controller.signal
      );
      
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
      abortControllerRef.current = null;
      setIsTyping(false);
    }
  }, [messages, cancelGeneration]);

  const initConversation = useCallback((welcomeText: string) => {
    cancelGeneration();
    const assistantMsg: Message = {
      id: 'welcome-' + generateId(),
      role: 'assistant',
      content: welcomeText,
      timestamp: Date.now(),
    };
    setMessages([assistantMsg]);
    setError(null);
  }, [cancelGeneration]);

  const clearHistory = useCallback(() => {
    cancelGeneration();
    setMessages([]);
    setError(null);
    localStorage.removeItem(HISTORY_KEY);
    const newSid = 'chat-' + generateId();
    sessionIdRef.current = newSid;
    localStorage.setItem('wakala_chat_session', newSid);
  }, [cancelGeneration]);

  return {
    messages,
    isTyping,
    error,
    sendMessage,
    cancelGeneration,
    clearHistory,
    initConversation,
    sessionId: sessionIdRef.current,
  };
}
