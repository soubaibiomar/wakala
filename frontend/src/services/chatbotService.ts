/**
 * chatbotService.ts — Service pour le chatbot RAG.
 */
import api from './api';

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
    onChunk: (chunk: string) => void
  ) => {
    // Determine the base URL from the Axios instance or env
    const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
    
    try {
      const response = await fetch(`${baseURL}/v1/ai/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Optional: Add Auth header if required
          // 'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          message,
          history
        })
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
      console.error("Streaming error:", error);
      throw error;
    }
  }
};
