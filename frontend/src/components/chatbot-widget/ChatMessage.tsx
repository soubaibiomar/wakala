import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import type { Message } from './useChatSession';
import CarRecommendation from './CarRecommendation';
import styles from './chatbot.module.css';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = message.content;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className={`${styles.message} ${isUser ? styles.messageUser : styles.messageAssistant}`}>
      <div className={styles.messageAvatar}>
        {isUser ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <circle cx="12" cy="8" r="4" />
            <path d="M20 21c0-4.4-3.6-8-8-8s-8 3.6-8 8" />
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <rect x="3" y="3" width="18" height="14" rx="2" />
            <path d="M8 21h8M12 17v4" />
          </svg>
        )}
      </div>

      <div className={styles.messageContent}>
        <div className={styles.messageText}>
          <ReactMarkdown
            components={{
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '');
                if (!inline && match && match[1] === 'json') {
                  try {
                    const rawJson = Array.isArray(children) ? children.join('') : String(children);
                    // Nettoyer les virgules traînantes courantes (trailing commas) générées par les LLM
                    const cleanJson = rawJson.replace(/,\s*([\]}])/g, '$1').trim();
                    const data = JSON.parse(cleanJson);
                    
                    if (data.type === 'CAR_RECOMMENDATION') {
                      return <CarRecommendation {...data} />;
                    }
                  } catch (e) {
                    const rawStr = Array.isArray(children) ? children.join('') : String(children);
                    if (rawStr.includes('CAR_RECOMMENDATION')) {
                       return (
                         <div style={{ padding: '16px', background: 'rgba(18,33,53,0.03)', borderRadius: '12px', border: '1px dashed rgba(18,33,53,0.15)', textAlign: 'center', margin: '12px 0' }}>
                           <p style={{ fontSize: '0.85rem', color: '#b89a44', margin: 0, fontWeight: 500 }}>
                             ⏳ Chargement de la fiche véhicule...
                           </p>
                         </div>
                       );
                    }
                    // fall back to default rendering if not valid JSON and not a car recommendation
                  }
                }
                return inline ? (
                  <code className={className} {...props}>
                    {children}
                  </code>
                ) : (
                  <pre style={{ background: '#f4f4f4', padding: '8px', borderRadius: '4px', overflowX: 'auto', fontSize: '0.8rem' }}>
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </pre>
                );
              }
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* ─── Copy button (shown on hover) ──── */}
        {message.content && (
          <div className={styles.messageActions}>
            <button
              className={styles.copyBtn}
              onClick={handleCopy}
              title={copied ? 'Copié !' : 'Copier le message'}
              aria-label="Copier le message"
            >
              {copied ? (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20 6 9 17l-5-5" />
                </svg>
              ) : (
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                </svg>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
