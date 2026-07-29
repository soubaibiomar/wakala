export interface UserBasic {
  id: string;
  full_name: string;
  avatar_url?: string | null;
}

export interface ListingBasic {
  id: string;
  vehicle_id: string;
}

export interface Message {
  id: string;
  sender_id: string;
  recipient_id: string;
  listing_id?: string | null;
  content: string;
  is_read: boolean;
  created_at: string;
}

export interface ConversationContact {
  contact: UserBasic;
  listing: ListingBasic | null;
  last_message: Message;
  unread_count: number;
}

export interface MessageCreate {
  recipient_id: string;
  listing_id?: string;
  content: string;
}
