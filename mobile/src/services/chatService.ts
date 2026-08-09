import api from './api';

export interface ChatSourceVehicle {
  vehicle_id?: string;
  id?: string;
  vehicle_title?: string;
  title?: string;
  brand?: string;
  model?: string;
  price?: string | number;
  relevance_score?: number;
  image_url?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  suggested_vehicles?: ChatSourceVehicle[];
}

export const chatService = {
  async sendMessage(sessionId: string, message: string, userId?: string): Promise<ChatMessage> {
    const payload: any = {
      session_id: sessionId,
      message: message,
    };
    if (userId) payload.user_id = userId;

    const response = await api.post('/chat', payload);
    const data = response.data;
    
    // Format backend response (ChatResponse has `reply` and `sources`)
    const sources = (data.sources || []).map((s: any) => ({
      id: s.vehicle_id || s.id,
      vehicle_id: s.vehicle_id || s.id,
      title: s.vehicle_title || `${s.brand || ''} ${s.model || ''}`.trim() || 'Véhicule',
      brand: s.brand || (s.vehicle_title ? s.vehicle_title.split(' ')[0] : ''),
      model: s.model || (s.vehicle_title ? s.vehicle_title.split(' ').slice(1).join(' ') : ''),
      price: s.price,
      image_url: s.image_url,
      relevance_score: s.relevance_score,
    }));

    return {
      id: `ast_${Date.now()}`,
      role: 'assistant',
      content: data.reply || data.content || data.message || 'Voici les informations demandées.',
      timestamp: new Date().toISOString(),
      suggested_vehicles: sources,
    };
  }
};
