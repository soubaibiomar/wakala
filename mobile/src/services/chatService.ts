import api from './api';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  suggested_vehicles?: any[];
}

export const chatService = {
  async sendMessage(sessionId: string, message: string): Promise<ChatMessage> {
    const response = await api.post('/chat', {
      session_id: sessionId,
      message: message,
    });
    return response.data; // { id, role, content, timestamp, suggested_vehicles }
  }
};
