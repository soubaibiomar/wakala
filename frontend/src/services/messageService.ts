import api from './api';
import type { Message, ConversationContact, MessageCreate } from '../types/message';

export const messageService = {
  async getConversations(): Promise<ConversationContact[]> {
    const { data } = await api.get<ConversationContact[]>('/messages/user/conversations');
    return data;
  },

  async getMessages(contactId: string, listingId?: string, limit = 50, offset = 0): Promise<Message[]> {
    const params: any = { limit, offset };
    if (listingId) {
      params.listing_id = listingId;
    }
    const { data } = await api.get<Message[]>(`/messages/${contactId}`, { params });
    return data;
  },

  async sendMessage(message: MessageCreate): Promise<Message> {
    const { data } = await api.post<Message>('/messages/', message);
    return data;
  }
};
