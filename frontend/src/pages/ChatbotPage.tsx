import { useState, useRef, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { chatbotService } from '../services/chatbotService';
import { useVoiceInput } from '../hooks/useVoiceInput';
import ChatMessage from '../components/chatbot-widget/ChatMessage';
import PreferenceBar from '../components/chatbot-widget/PreferenceBar';
import type { Message } from '../components/chatbot-widget/useChatSession';
import './ChatbotPage.css';

interface LanguageOption {
  code: string;
  tag: string;
  nativeName: string;
  sub: string;
  welcomeMessage: string;
  voiceLang: string;
  accent: string;
}

const LANGUAGES: LanguageOption[] = [
  {
    code: 'fr',
    tag: 'FR',
    nativeName: 'Français',
    sub: 'Conseil en français',
    welcomeMessage:
      'Bonjour et bienvenue sur Wakala ! Je suis votre conseiller automobile dédié au marché marocain.\n\nComment puis-je vous aider aujourd’hui ?',
    voiceLang: 'fr-FR',
    accent: '#1e3a5f',
  },
  {
    code: 'darija',
    tag: 'MA',
    nativeName: 'الدارجة',
    sub: 'هضر معايا بالدارجة',
    welcomeMessage:
      'مرحباً بك في وكالة (Wakala) ! أنا المستشار ديالك الخاص بالسيارات في المغرب.\n\nكيفاش نقدر نعاونك اليوم ؟',
    voiceLang: 'ar-MA',
    accent: '#10b981',
  },
  {
    code: 'ar',
    tag: 'AR',
    nativeName: 'العربية',
    sub: 'الفصحى',
    welcomeMessage:
      'أهلاً وسهلاً بك في وكالة ! أنا مستشارك الذكي لاختيار وشراء السيارات في المغرب.\n\nكيف يمكنني مساعدتك اليوم ؟',
    voiceLang: 'ar-SA',
    accent: '#b89a44',
  },
  {
    code: 'en',
    tag: 'EN',
    nativeName: 'English',
    sub: 'Advisor in English',
    welcomeMessage:
      'Welcome to Wakala! I am your intelligent automotive advisor for the Moroccan market.\n\nHow can I help you today?',
    voiceLang: 'en-US',
    accent: '#6366f1',
  },
];

export default function ChatbotPage() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const query = searchParams.get('q');
  const budget = searchParams.get('budget');

  // Extraction des priorités dynamiques
  const dynamicPriorities: { name: string; value: string }[] = [];
  searchParams.forEach((value, key) => {
    if (key.startsWith('prio_')) {
      const name = key.replace('prio_', '');
      dynamicPriorities.push({ name, value });
    }
  });

  const hasPreferences = dynamicPriorities.length > 0 || !!query || !!budget;

  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedVoiceLang, setSelectedVoiceLang] = useState('ar-MA');
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const sessionId = 'session-' + Date.now();

  const voice = useVoiceInput({
    defaultLang: selectedVoiceLang,
    onTranscript: (text) => {
      setInput((prev) => {
        const sep = prev.trim() ? ' ' : '';
        return prev + sep + text;
      });
    },
  });

  const handleScroll = useCallback(() => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
    setShowScrollBottom(!isNearBottom);
  }, []);

  const scrollToBottom = (behavior: ScrollBehavior = 'smooth') => {
    messagesEndRef.current?.scrollIntoView({ behavior });
  };

  useEffect(() => {
    if (!showScrollBottom) {
      scrollToBottom('smooth');
    }
  }, [messages, isLoading, showScrollBottom]);

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsLoading(false);
    }
  };

  const handleSend = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: Date.now(),
    };

    const assistantId = (Date.now() + 1).toString();
    const placeholderAssistant: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage, placeholderAssistant]);
    setInput('');
    setIsLoading(true);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const history = messages
        .filter((m) => m.content.trim() !== '')
        .map((m) => ({ role: m.role, content: m.content }));

      await chatbotService.streamMessage(
        text,
        history,
        (chunk) => {
          setMessages((prev) =>
            prev.map((m) => (m.id === assistantId ? { ...m, content: m.content + chunk } : m))
          );
        },
        sessionId,
        controller.signal
      );
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId && !m.content
            ? { ...m, content: 'Désolé, je suis temporairement indisponible. Veuillez réessayer.' }
            : m
        )
      );
    } finally {
      abortControllerRef.current = null;
      setIsLoading(false);
    }
  };

  // Initialisation si URL params présents
  useEffect(() => {
    if (hasPreferences && messages.length === 0) {
      const prioStr = dynamicPriorities
        .map((p) => `- **${p.name.charAt(0).toUpperCase() + p.name.slice(1)}**: ${p.value}%`)
        .join('\n');
      let promptText = `Bonjour ! Voici mes critères de recherche :\n`;
      if (prioStr) promptText += `${prioStr}\n`;
      if (budget) promptText += `- **Budget**: ${budget} MAD\n`;
      if (query) promptText += `- **Recherche**: "${query}"\n`;
      promptText += `\nQuelles voitures du catalogue me recommandez-vous ?`;
      
      handleSend(promptText);
    }
  }, [hasPreferences]);

  const handleClear = () => {
    handleCancel();
    setMessages([]);
  };

  const handleSelectLanguage = (lang: LanguageOption) => {
    setSelectedVoiceLang(lang.voiceLang);
    const welcomeMsg: Message = {
      id: 'welcome-' + Date.now(),
      role: 'assistant',
      content: lang.welcomeMessage,
      timestamp: Date.now(),
    };
    setMessages([welcomeMsg]);
  };

  const lastAssistantMsg = [...messages].reverse().find((m) => m.role === 'assistant')?.content;

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <div
            style={{
              width: 44,
              height: 44,
              borderRadius: 12,
              background: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 4px 14px rgba(18,33,53,0.15)',
              overflow: 'hidden',
              padding: 3,
            }}
          >
            <img
              src="/assets/chatlogo.png"
              alt="Wakala"
              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
            />
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)' }}>
              Wakala AI • Conseiller Automobile
            </h1>
            <p style={{ margin: 0, fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Conseil Automobile Intelligent • Marché Marocain
            </p>
          </div>
        </div>

        <button
          onClick={handleClear}
          style={{
            background: 'var(--bg-elevated)',
            border: '1px solid var(--border-subtle)',
            color: 'var(--text-secondary)',
            padding: '6px 14px',
            borderRadius: 8,
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
          }}
          title="Changer de langue / Réinitialiser la conversation"
        >
          Nouveau
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="chat-messages" ref={scrollContainerRef} onScroll={handleScroll}>
        {messages.length === 0 && (
          <div className="chat-lang-select-screen">
            <div className="chat-lang-hero">
              <span className="chat-lang-badge">Wakala IA</span>
              <h2 className="chat-lang-title">Choisissez votre langue / اختر لغتك</h2>
              <p className="chat-lang-subtitle">
                Sélectionnez votre langue de préférence pour démarrer la consultation personnalisée :
              </p>
            </div>

            <div className="chat-lang-grid">
              {LANGUAGES.map((lang) => (
                <button
                  key={lang.code}
                  type="button"
                  className="chat-lang-card"
                  onClick={() => handleSelectLanguage(lang)}
                  style={{ '--lang-accent': lang.accent } as React.CSSProperties}
                >
                  <div className="chat-lang-tag" style={{ backgroundColor: lang.accent }}>
                    {lang.tag}
                  </div>
                  <div className="chat-lang-info">
                    <div className="chat-lang-name">{lang.nativeName}</div>
                    <div className="chat-lang-sub">{lang.sub}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, index) => {
          const isLast = index === messages.length - 1;
          const isStreaming = isLast && msg.role === 'assistant' && isLoading;

          return <ChatMessage key={msg.id} message={msg} isStreaming={isStreaming} />;
        })}

        {/* Indicateur d'attente initiale */}
        {isLoading && messages.length > 0 && messages[messages.length - 1].role === 'user' && (
          <div className="message-wrapper assistant">
            <div className="typing-indicator">
              <div className="typing-dot" />
              <div className="typing-dot" />
              <div className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Bouton de scroll vers le bas */}
      {showScrollBottom && (
        <button
          onClick={() => scrollToBottom('smooth')}
          style={{
            position: 'absolute',
            bottom: '180px',
            right: '32px',
            background: 'rgba(15, 23, 42, 0.9)',
            backdropFilter: 'blur(8px)',
            color: '#FFFFFF',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            padding: '6px 12px',
            borderRadius: '20px',
            fontSize: '0.75rem',
            fontWeight: 700,
            cursor: 'pointer',
            boxShadow: '0 6px 16px rgba(0, 0, 0, 0.3)',
            zIndex: 30,
          }}
          title="Faire défiler vers le bas"
        >
          ↓ Bas
        </button>
      )}

      {/* Barre de critères contextuels */}
      <PreferenceBar
        lastAssistantMessage={lastAssistantMsg}
        onSelectOption={(optionText) => {
          handleSend(optionText);
        }}
        disabled={isLoading}
      />

      {/* Input area */}
      <div className="chat-input-wrapper">
        <div className="chat-input-bar">
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              width: '24px',
              height: '32px',
              background: '#122135',
              color: 'white',
              borderRadius: '4px',
              fontSize: '0.65rem',
              fontWeight: 800,
              flexShrink: 0,
              lineHeight: 1,
            }}
          >
            <span>M</span>
            <span>A</span>
          </div>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend(input);
              }
            }}
            placeholder={
              messages.length === 0
                ? 'Choisissez une langue ou posez votre question...'
                : voice.status === 'listening'
                ? 'Parlez maintenant...'
                : 'Posez votre question...'
            }
            rows={1}
            disabled={isLoading}
            className="chat-textarea"
          />

          {voice.isSupported && (
            <button
              onClick={voice.toggleListening}
              type="button"
              className={`action-btn ${voice.status === 'listening' ? 'listening' : ''}`}
              title={voice.status === 'listening' ? 'Arrêter écoute' : 'Saisie vocale'}
            >
              {voice.status === 'listening' ? 'Stop' : 'Vocal'}
            </button>
          )}

          {isLoading ? (
            <button onClick={handleCancel} className="cancel-btn" title="Arrêter">
              Arrêter
            </button>
          ) : (
            <button
              onClick={() => handleSend(input)}
              disabled={!input.trim()}
              className="send-btn"
            >
              Envoyer
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
