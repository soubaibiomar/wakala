import { useEffect, useRef, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Message } from './useChatSession';
import ChatMessage from './ChatMessage';
import PreferenceBar from './PreferenceBar';
import { useVoiceInput } from '../../hooks/useVoiceInput';
import styles from './chatbot.module.css';

interface ChatWindowProps {
  messages: Message[];
  isTyping: boolean;
  error: string | null;
  currentLanguage?: string;
  onSend: (text: string) => void;
  onCancel: () => void;
  onClear: () => void;
  onInitLanguage?: (welcomeText: string, langCode?: string) => void;
  onClose: () => void;
}

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

export default function ChatWindow({
  messages,
  isTyping,
  error,
  currentLanguage,
  onSend,
  onCancel,
  onClear,
  onInitLanguage,
  onClose,
}: ChatWindowProps) {
  const [input, setInput] = useState('');
  const [selectedVoiceLang, setSelectedVoiceLang] = useState('fr-FR');
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const voice = useVoiceInput({
    defaultLang: selectedVoiceLang,
    onTranscript: (transcript: string) => {
      setInput((prev) => {
        const base = prev.trim();
        return base ? `${base} ${transcript}` : transcript;
      });
    },
  });

  // Détection du dernier message de l'assistant pour alimenter la barre contextuelle de préférences
  const lastAssistantMsg = [...messages].reverse().find((m) => m.role === 'assistant')?.content;

  const scrollToBottom = useCallback((behavior: ScrollBehavior = 'smooth') => {
    endRef.current?.scrollIntoView({ behavior });
  }, []);

  useEffect(() => {
    scrollToBottom('smooth');
  }, [messages, isTyping, scrollToBottom]);

  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    const distanceToBottom = scrollHeight - scrollTop - clientHeight;
    setShowScrollBottom(distanceToBottom > 120);
  };

  useEffect(() => {
    if (!isTyping && messages.length > 0) {
      inputRef.current?.focus();
    }
  }, [isTyping, messages.length]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isTyping) return;
    onSend(trimmed);
    setInput('');
    if (inputRef.current) {
      inputRef.current.style.height = '24px';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSelectLanguage = (lang: LanguageOption) => {
    setSelectedVoiceLang(lang.voiceLang);
    if (onInitLanguage) {
      onInitLanguage(lang.welcomeMessage, lang.code);
    }
  };

  const navigate = useNavigate();
  const handleOpenCatalogue = useCallback(() => {
    const lastUser = [...messages].reverse().find((m) => m.role === 'user');
    if (lastUser) {
      sessionStorage.setItem('wakala_pending_intent', JSON.stringify({
        message: lastUser.content,
        language: currentLanguage || 'fr',
      }));
    }
    navigate('/catalogue');
  }, [messages, currentLanguage, navigate]);

  return (
    <div className={styles.window}>
      {/* Header Premium */}
      <div className={styles.windowHeader}>
        <div className={styles.windowHeaderLeft}>
          <div className={styles.headerLogoWrap}>
            <img
              src="/assets/chatlogo.png"
              alt="Wakala"
              className={styles.headerLogoImg}
            />
          </div>
          <div className={styles.windowTitle}>
            <span className={styles.windowTitleMain}>Assistant Wakala</span>
            <span className={styles.windowTitleSub}>Conseiller Automobile Intelligent</span>
          </div>
        </div>

        <div className={styles.windowHeaderRight}>
          {messages.length > 0 && (
            <button
              className={styles.headerActionBtn}
              onClick={handleOpenCatalogue}
              title="Continuer dans le catalogue de véhicules"
            >
              Catalogue ↗
            </button>
          )}
          <button
            className={styles.headerActionBtn}
            onClick={onClear}
            title="Changer de langue / Nouvelle conversation"
          >
            Nouveau
          </button>
          <button
            className={styles.headerCloseBtn}
            onClick={onClose}
            title="Fermer"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className={styles.windowMessages} ref={scrollContainerRef} onScroll={handleScroll}>
        {messages.length === 0 && (
          <div className={styles.windowEmpty}>
            <div className={styles.emptyHeroCard}>
              <div className={styles.emptyHeroLogoWrap}>
                <img src="/assets/chatlogo.png" alt="Wakala" className={styles.emptyHeroLogo} />
              </div>
              <h2 className={styles.emptyHeroTitle}>Bienvenue sur Wakala</h2>
              <p className={styles.emptyHeroSubtitle}>
                Choisissez votre langue pour débuter :
              </p>
            </div>

            <div className={styles.langGrid}>
              {LANGUAGES.map((lang) => (
                <button
                  key={lang.code}
                  type="button"
                  className={styles.langCard}
                  onClick={() => handleSelectLanguage(lang)}
                  style={{ '--lang-accent': lang.accent } as React.CSSProperties}
                >
                  <span className={styles.langTag} style={{ backgroundColor: lang.accent }}>
                    {lang.tag}
                  </span>
                  <div className={styles.langInfo}>
                    <span className={styles.langNative}>{lang.nativeName}</span>
                    <span className={styles.langSub}>{lang.sub}</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, index) => {
          const isLast = index === messages.length - 1;
          const isStreaming = isLast && msg.role === 'assistant' && isTyping;

          return <ChatMessage key={msg.id} message={msg} isStreaming={isStreaming} />;
        })}

        {/* Indicateur de frappe */}
        {isTyping && messages.length > 0 && messages[messages.length - 1].role === 'user' && (
          <div className={styles.typing}>
            <div className={styles.typingDots}>
              <span className={styles.typingDot} />
              <span className={styles.typingDot} />
              <span className={styles.typingDot} />
            </div>
            <span className={styles.typingLabel}>Wakala formule votre réponse...</span>
          </div>
        )}

        {error && <div className={styles.windowError}>{error}</div>}

        <div ref={endRef} />
      </div>

      {/* Bouton pour redescendre rapidement */}
      {showScrollBottom && (
        <button
          onClick={() => scrollToBottom('smooth')}
          className={styles.scrollBottomBtn}
          title="Faire défiler vers le bas"
        >
          ↓ Bas
        </button>
      )}

      {/* Barre de critères contextuels */}
      <PreferenceBar
        lastAssistantMessage={lastAssistantMsg}
        currentLanguage={currentLanguage}
        onSelectOption={(optionText: string) => {
          onSend(optionText);
        }}
        disabled={isTyping}
      />

      {/* Input bar */}
      <div className={styles.windowInput}>
        <div className={styles.inputBar}>
          <div className={styles.inputLicenseFlag}>
            <span>M</span>
            <span>A</span>
          </div>
          <textarea
            ref={inputRef}
            className={styles.inputField}
            placeholder={
              messages.length === 0
                ? 'Choisissez une langue ou écrivez...'
                : voice.status === 'listening'
                ? 'Parlez maintenant...'
                : 'Posez votre question...'
            }
            value={voice.interimTranscript ? input + (input ? ' ' : '') + voice.interimTranscript : input}
            rows={1}
            style={{ resize: 'none', overflow: 'hidden', height: '24px', maxHeight: '100px' }}
            onChange={(e) => {
              setInput(e.target.value);
              e.target.style.height = '24px';
              e.target.style.height = `${Math.min(e.target.scrollHeight, 100)}px`;
            }}
            onKeyDown={handleKeyDown}
            disabled={isTyping}
            readOnly={voice.status === 'listening'}
          />

          {/* Bouton micro */}
          {voice.isSupported && (
            <button
              className={`${styles.micBtn} ${voice.status === 'listening' ? styles.micBtnListening : ''}`}
              onClick={voice.toggleListening}
              title={voice.status === 'listening' ? "Arrêter l'écoute" : 'Saisie vocale'}
              type="button"
            >
              {voice.status === 'listening' ? 'Stop' : 'Vocal'}
            </button>
          )}

          {/* Bouton Envoi / Arrêt */}
          {isTyping ? (
            <button
              className={styles.cancelBtn}
              onClick={onCancel}
              title="Arrêter la génération"
            >
              Arrêter
            </button>
          ) : (
            <button
              className={styles.inputBtn}
              onClick={handleSubmit}
              disabled={!input.trim()}
            >
              Envoyer
            </button>
          )}
        </div>

        {voice.errorMessage && (
          <div className={styles.voiceError} role="alert">
            {voice.errorMessage}
          </div>
        )}
      </div>
    </div>
  );
}
