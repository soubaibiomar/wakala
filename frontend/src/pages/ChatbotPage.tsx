import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User, CarFront } from 'lucide-react';
import './ChatbotPage.css';
import { chatbotService } from '../services/chatbotService';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

const SUGGESTIONS = [
  "Je cherche un SUV diesel avec un grand coffre",
  "Quelles sont les voitures les plus fiables en ville ?",
  "Je veux une voiture économique pour 150000 MAD"
];

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Salam ! Je suis Wakala Bot, votre expert automobile. Que recherchez-vous aujourd\'hui ?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Use a fixed session ID for demo purposes, normally generated per user session
  const sessionId = "session-12345";

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    const assistantId = (Date.now() + 1).toString();
    const assistantMsg: Message = {
      id: assistantId,
      role: 'assistant',
      content: ''
    };
    setMessages(prev => [...prev, assistantMsg]);

    try {
      const history = messages
        .filter(m => m.id !== '1') // Optional: skip welcome msg in history
        .map(m => ({ role: m.role, content: m.content }));

      await chatbotService.streamMessage(
        text,
        history,
        (chunk) => {
          setMessages(prev => prev.map(m => 
            m.id === assistantId ? { ...m, content: m.content + chunk } : m
          ));
        },
        sessionId
      );
    } catch (error) {
      setMessages(prev => prev.map(m => 
        m.id === assistantId ? { ...m, content: "Désolé, je suis temporairement indisponible. Veuillez réessayer plus tard." } : m
      ));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <Bot size={28} />
        <div>
          <h1>Wakala AI</h1>
          <p>Trouvez la voiture parfaite avec notre assistant intelligent</p>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message-wrapper ${msg.role}`}>
            <div className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.role === 'assistant' ? (
                  <ReactMarkdown
                    components={{
                      code({ node, inline, className, children, ...props }: any) {
                        const match = /language-(\w+)/.exec(className || '');
                        if (!inline && match && match[1] === 'json') {
                          try {
                            const data = JSON.parse(String(children).replace(/\n$/, ''));
                            if (data.type === 'CAR_RECOMMENDATION') {
                              return (
                                <div style={{ border: '1px solid var(--border-subtle)', borderRadius: 8, padding: 16, marginTop: 12, marginBottom: 12, display: 'flex', gap: 16, alignItems: 'center', background: 'var(--bg-elevated)' }}>
                                  <CarFront size={32} style={{ color: 'var(--accent-gold)', flexShrink: 0 }} />
                                  <div style={{ flex: 1, minWidth: 0 }}>
                                    <h4 style={{ margin: '0 0 4px 0', color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{data.brand} {data.model} {data.year && `(${data.year})`}</h4>
                                    <p style={{ margin: 0, fontWeight: 'bold', color: 'var(--accent-gold)' }}>{data.price} MAD</p>
                                  </div>
                                  <a href={`/catalog/${data.id}`} target="_blank" rel="noreferrer" style={{ padding: '8px 16px', background: 'var(--accent-gold)', color: '#0f1a2b', textDecoration: 'none', borderRadius: 4, fontWeight: 'bold', flexShrink: 0 }}>Voir</a>
                                </div>
                              );
                            }
                          } catch (e) {
                            // ignore json parse error
                          }
                        }
                        return <code className={className} {...props}>{children}</code>;
                      }
                    }}
                  >{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message-wrapper assistant">
            <div className="typing-indicator">
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
              <div className="typing-dot"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {messages.length === 1 && (
        <div className="suggestion-chips">
          {SUGGESTIONS.map((sug, i) => (
            <div key={i} className="chip" onClick={() => handleSend(sug)}>
              {sug}
            </div>
          ))}
        </div>
      )}

      <div className="chat-input-container">
        <form 
          className="chat-input-form"
          onSubmit={(e) => {
            e.preventDefault();
            handleSend(input);
          }}
        >
          <input
            type="text"
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Posez votre question (ex: Je cherche un SUV Diesel...)"
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="chat-send-btn"
            disabled={!input.trim() || isLoading}
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
