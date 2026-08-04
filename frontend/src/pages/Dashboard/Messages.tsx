import { useState, useEffect, useRef } from 'react';
import { useAuth } from "../../context/AuthContext";
import { messageService } from '../../services/messageService';
import type { ConversationContact, Message } from '../../types/message';
import { Send, User as UserIcon, MessageSquare } from 'lucide-react';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';

export default function Messages() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState<ConversationContact[]>([]);
  const [activeContactId, setActiveContactId] = useState<string | null>(null);
  const [activeListingId, setActiveListingId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversations();
    const interval = setInterval(loadConversations, 10000); // Poll every 10s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeContactId) {
      loadMessages();
      const interval = setInterval(loadMessages, 3000); // Poll messages every 3s
      return () => clearInterval(interval);
    }
  }, [activeContactId, activeListingId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadConversations = async () => {
    try {
      const data = await messageService.getConversations();
      setConversations(data);
    } catch (err) {
      console.error("Erreur de chargement des conversations", err);
    }
  };

  const loadMessages = async () => {
    if (!activeContactId) return;
    try {
      const data = await messageService.getMessages(activeContactId, activeListingId || undefined);
      setMessages(data);
    } catch (err) {
      console.error("Erreur de chargement des messages", err);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeContactId) return;

    try {
      const sent = await messageService.sendMessage({
        recipient_id: activeContactId,
        listing_id: activeListingId || undefined,
        content: newMessage
      });
      setMessages([...messages, sent]);
      setNewMessage('');
      loadConversations(); // Refresh list to update "last message"
    } catch (err) {
      console.error("Erreur d'envoi", err);
    }
  };

  const activeContact = conversations.find(c => c.contact.id === activeContactId && c.listing?.id === activeListingId);

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 120px)', background: 'var(--color-surface)', borderRadius: '16px', overflow: 'hidden', border: '1px solid var(--color-border)' }}>
      
      {/* Sidebar - Liste des conversations */}
      <div style={{ width: '320px', borderRight: '1px solid var(--color-border)', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '20px', borderBottom: '1px solid var(--color-border)', background: 'var(--color-bg)' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>Messagerie</h2>
        </div>
        
        <div style={{ flex: 1, overflowY: 'auto' }}>
          {conversations.length === 0 ? (
            <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
              Aucune conversation pour le moment.
            </div>
          ) : (
            conversations.map((conv) => {
              const isActive = conv.contact.id === activeContactId && conv.listing?.id === activeListingId;
              return (
                <div 
                  key={`${conv.contact.id}-${conv.listing?.id}`}
                  onClick={() => {
                    setActiveContactId(conv.contact.id);
                    setActiveListingId(conv.listing?.id || null);
                  }}
                  style={{
                    padding: '16px',
                    borderBottom: '1px solid var(--color-bg)',
                    cursor: 'pointer',
                    background: isActive ? 'var(--color-bg)' : 'transparent',
                    transition: 'background 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <UserIcon size={20} color="var(--color-text-muted)" />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {conv.contact.full_name}
                        </h4>
                        <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                          {format(new Date(conv.last_message.created_at), 'HH:mm')}
                        </span>
                      </div>
                      <p style={{ margin: 0, fontSize: '0.85rem', color: conv.unread_count > 0 ? 'var(--color-text)' : 'var(--color-text-secondary)', fontWeight: conv.unread_count > 0 ? 600 : 400, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {conv.last_message.content}
                      </p>
                    </div>
                    {conv.unread_count > 0 && (
                      <div style={{ background: 'var(--color-accent)', color: '#fff', fontSize: '0.75rem', fontWeight: 'bold', padding: '2px 8px', borderRadius: '12px' }}>
                        {conv.unread_count}
                      </div>
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: 'var(--color-bg)' }}>
        {activeContactId && activeContact ? (
          <>
            {/* Chat Header */}
            <div style={{ padding: '20px', borderBottom: '1px solid var(--color-border)', background: 'var(--color-surface)', display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ width: 48, height: 48, borderRadius: '50%', background: 'var(--color-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <UserIcon size={24} color="var(--color-text-muted)" />
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 'bold' }}>
                  {activeContact.contact.full_name}
                </h3>
                {activeContact.listing && (
                  <span style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                    À propos de l'annonce
                  </span>
                )}
              </div>
            </div>

            {/* Chat Messages */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {messages.map((msg) => {
                const isMe = msg.sender_id === user?.id;
                return (
                  <div key={msg.id} style={{ display: 'flex', justifyContent: isMe ? 'flex-end' : 'flex-start' }}>
                    <div style={{
                      maxWidth: '70%',
                      padding: '12px 16px',
                      borderRadius: '16px',
                      borderBottomRightRadius: isMe ? '4px' : '16px',
                      borderBottomLeftRadius: isMe ? '16px' : '4px',
                      background: isMe ? 'var(--color-accent)' : 'var(--color-surface)',
                      color: isMe ? '#fff' : 'var(--color-text)',
                      boxShadow: '0 2px 5px rgba(0,0,0,0.05)'
                    }}>
                      <p style={{ margin: 0, lineHeight: 1.4 }}>{msg.content}</p>
                      <div style={{ fontSize: '0.7rem', color: isMe ? 'rgba(255,255,255,0.7)' : 'var(--color-text-muted)', textAlign: 'right', marginTop: '4px' }}>
                        {format(new Date(msg.created_at), 'HH:mm', { locale: fr })}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Chat Input */}
            <div style={{ padding: '20px', background: 'var(--color-surface)', borderTop: '1px solid var(--color-border)' }}>
              <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '12px' }}>
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Écrivez votre message..."
                  style={{
                    flex: 1,
                    padding: '16px 20px',
                    borderRadius: '24px',
                    border: '1px solid var(--color-border)',
                    background: 'var(--color-bg)',
                    outline: 'none',
                    fontSize: '1rem'
                  }}
                />
                <button
                  type="submit"
                  disabled={!newMessage.trim()}
                  style={{
                    width: '54px',
                    height: '54px',
                    borderRadius: '50%',
                    background: 'var(--color-accent)',
                    color: '#fff',
                    border: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: newMessage.trim() ? 'pointer' : 'not-allowed',
                    opacity: newMessage.trim() ? 1 : 0.5
                  }}
                >
                  <Send size={20} style={{ marginLeft: '4px' }} />
                </button>
              </form>
            </div>
          </>
        ) : (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-muted)' }}>
            <MessageSquare size={64} style={{ marginBottom: '16px', opacity: 0.5 }} />
            <h3>Sélectionnez une conversation</h3>
            <p>Choisissez un contact dans la liste pour commencer à discuter.</p>
          </div>
        )}
      </div>
    </div>
  );
}
