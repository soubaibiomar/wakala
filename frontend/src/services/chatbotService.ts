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
  /** Envoyer un message au chatbot RAG */
  sendMessage: (message: string, sessionId: string) =>
    api.post<ChatResponse>('/chat/', { message, session_id: sessionId }),
};
