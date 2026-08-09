import { useEffect, useRef, useState } from 'react';
import { Mic, Square } from 'lucide-react';
import type { Message } from './useChatSession';
import ChatMessage from './ChatMessage';
import { useVoiceInput } from '../../hooks/useVoiceInput';
import styles from './chatbot.module.css';

interface ChatWindowProps {
  messages: Message[];
  isTyping: boolean;
  error: string | null;
  onSend: (text: string) => void;
  onCancel: () => void;
  onClear: () => void;
  onClose: () => void;
}

export default function ChatWindow({
  messages,
  isTyping,
  error,
  onSend,
  onCancel,
  onClear,
  onClose,
}: ChatWindowProps) {
  const [input, setInput] = useState('');
  const endRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // ─── Saisie vocale (Web Speech API) ───────────────────────
  const voice = useVoiceInput({
    defaultLang: 'ar-MA',
    onTranscript: (text) => {
      // Injecte le texte transcrit dans le même state que le clavier
      setInput((prev) => {
        const separator = prev.trim() ? ' ' : '';
        return prev + separator + text;
      });
    },
  });

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isTyping) return;
    onSend(trimmed);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className={styles.window}>
      <div className={styles.windowHeader}>
        <div className={styles.windowHeaderLeft}>
          <div className={styles.windowTitle}>
            <span className={styles.windowTitleMain}>Assistant Wakala</span>
            <span className={styles.windowTitleSub}>Propulsé par IA</span>
          </div>
        </div>

        <div className={styles.windowHeaderRight}>
          <button className={styles.windowBtn} onClick={onClear} title="Nouvelle conversation">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2" />
            </svg>
          </button>
          <button className={styles.windowBtn} onClick={onClose} title="Fermer">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div className={styles.windowMessages}>
        {messages.length === 0 && (
          <div className={styles.windowEmpty}>
            <div className={styles.windowEmptyIcon}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
                <rect x="3" y="3" width="18" height="14" rx="2" />
                <path d="M8 21h8M12 17v4" />
              </svg>
            </div>
            <p className={styles.windowEmptyTitle}>Bonjour !</p>
            <p className={styles.windowEmptyText}>
              Je suis l'assistant Wakala. Posez-moi des questions sur les véhicules disponibles&nbsp;!
            </p>
            <div className={styles.windowEmptySuggestions}>
              {[
                'SUV diesel à Casablanca',
                'Berline automatique moins de 300 000 MAD',
                'Citadine essence pas chère',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  className={styles.suggestionChip}
                  onClick={() => { onSend(suggestion); }}
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {isTyping && (
          <div className={styles.typing}>
            <div className={styles.typingDots}>
              <span className={styles.typingDot} />
              <span className={styles.typingDot} />
              <span className={styles.typingDot} />
            </div>
            <span className={styles.typingLabel}>Wakala réfléchit...</span>
          </div>
        )}

        {error && (
          <div className={styles.windowError}>
            {error}
          </div>
        )}

        <div ref={endRef} />
      </div>

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
              voice.status === 'listening'
                ? 'Parlez maintenant...'
                : 'Rechercher (ex: Dacia Duster Casablanca)'
            }
            value={voice.interimTranscript ? input + (input ? ' ' : '') + voice.interimTranscript : input}
            rows={1}
            style={{ resize: 'none', overflow: 'hidden', minHeight: '36px', maxHeight: '120px' }}
            onChange={(e) => {
              setInput(e.target.value);
              e.target.style.height = 'auto';
              e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
            }}
            onKeyDown={handleKeyDown}
            disabled={isTyping}
            readOnly={voice.status === 'listening'}
          />

          {/* ─── Bouton micro (masqué si non supporté) ──── */}
          {voice.isSupported && (
            <button
              className={`${styles.micBtn} ${voice.status === 'listening' ? styles.micBtnListening : ''}`}
              onClick={voice.toggleListening}
              title={voice.status === 'listening' ? "Arrêter l'écoute" : 'Saisie vocale'}
              type="button"
              aria-label={voice.status === 'listening' ? 'Arrêter la reconnaissance vocale' : 'Activer la reconnaissance vocale'}
            >
              {voice.status === 'listening' ? <Square size={14} fill="currentColor" /> : <Mic size={16} />}
            </button>
          )}

          {/* ─── Send or Cancel button ──── */}
          {isTyping ? (
            <button
              className={styles.cancelBtn}
              onClick={onCancel}
              title="Arrêter la génération"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <rect x="6" y="6" width="12" height="12" rx="2" />
              </svg>
            </button>
          ) : (
            <button
              className={styles.inputBtn}
              onClick={handleSubmit}
              disabled={!input.trim()}
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </button>
          )}
        </div>

        {/* ─── Erreur vocale ──────────────────────────────── */}
        {voice.errorMessage && (
          <div className={styles.voiceError} role="alert">
            ⚠️ {voice.errorMessage}
          </div>
        )}
      </div>
    </div>
  );
}
