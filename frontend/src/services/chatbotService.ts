/**
 * chatbotService.ts — Service pour le chatbot RAG.
 */
import api, { getSessionToken } from './api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatResponse {
  reply: string;
  session_id: string;
  sources: Array<{
    vehicle_id: string;
    vehicle_title: string;
    relevance_score: number;
    source_type: string;
  }>;
}

export const chatbotService = {
  /** Envoyer un message au chatbot RAG (Legacy) */
  sendMessage: (message: string, sessionId: string) =>
    api.post<ChatResponse>('/chat/', { message, session_id: sessionId }),
    
  /** Envoyer un message et lire la réponse en streaming (SSE) */
  streamMessage: async (
    message: string, 
    history: Array<{ role: string; content: string }>,
    onChunk: (chunk: string) => void,
    sessionId?: string,
    signal?: AbortSignal,
    language?: string
  ) => {
    // Determine the base URL from the Axios instance or env
    const baseURL = import.meta.env.VITE_API_URL || '/api';
    
    const timeoutController = signal ? null : new AbortController();
    const timeoutId = timeoutController ? window.setTimeout(() => timeoutController.abort(), 45_000) : null;
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      
      const token = getSessionToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${baseURL}/v1/ai/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          message,
          history,
          session_id: sessionId,
          language
        }),
        signal: signal || timeoutController?.signal
      });

      if (!response.ok) {
        throw new Error('Erreur de communication avec le serveur IA.');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder('utf-8');

      if (reader) {
        let done = false;
        while (!done) {
          const { value, done: doneReading } = await reader.read();
          done = doneReading;
          if (value) {
            const chunk = decoder.decode(value, { stream: true });
            onChunk(chunk);
          }
        }
      }
    } catch (error) {
      if (error instanceof DOMException && error.name === 'AbortError') {
        // User cancelled — not a real error
        return;
      }
      console.error("Streaming error:", error);
      throw error;
    } finally {
      if (timeoutId !== null) window.clearTimeout(timeoutId);
    }
  },
  
  /** Récupérer l'historique des sessions de chat de l'utilisateur */
  getChatHistory: async () => {
    const baseURL = import.meta.env.VITE_API_URL || '/api';
    const token = getSessionToken();
    if (!token) return [];
    
    const response = await fetch(`${baseURL}/v1/ai/chat/history`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) return [];
    return response.json();
  }
};
