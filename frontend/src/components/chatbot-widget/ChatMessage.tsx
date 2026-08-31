import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import type { Message } from './useChatSession';
import CarRecommendation from './CarRecommendation';
import styles from './chatbot.module.css';

interface ChatMessageProps {
  message: Message;
  isStreaming?: boolean;
}

export default function ChatMessage({ message, isStreaming = false }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
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
      <div
        className={styles.messageAvatar}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: 8,
          width: 30,
          height: 30,
          flexShrink: 0,
          overflow: 'hidden',
          background: isUser ? '#1E293B' : '#FFFFFF',
          border: isUser ? 'none' : '1px solid rgba(18, 33, 53, 0.1)',
        }}
      >
        {isUser ? (
          <span style={{ fontSize: '0.72rem', fontWeight: 800, color: '#94A3B8' }}>V</span>
        ) : (
          <img
            src="/assets/chatlogo.png"
            alt="Wakala"
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
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
                    const cleanJson = rawJson.replace(/,\s*([\]}])/g, '$1').trim();
                    const data = JSON.parse(cleanJson);

                    if (data.type === 'CAR_RECOMMENDATION') {
                      return <CarRecommendation {...data} />;
                    }
                  } catch (e) {
                    const rawStr = Array.isArray(children) ? children.join('') : String(children);
                    if (rawStr.includes('CAR_RECOMMENDATION')) {
                      return (
                        <div
                          style={{
                            padding: '12px',
                            background: 'rgba(245, 158, 11, 0.06)',
                            borderRadius: '10px',
                            border: '1px dashed rgba(245, 158, 11, 0.3)',
                            textAlign: 'center',
                            margin: '10px 0',
                          }}
                        >
                          <p style={{ fontSize: '0.82rem', color: '#D97706', margin: 0, fontWeight: 600 }}>
                            Chargement du véhicule recommandé...
                          </p>
                        </div>
                      );
                    }
                  }
                }
                return inline ? (
                  <code className={className} {...props}>
                    {children}
                  </code>
                ) : (
                  <pre
                    style={{
                      background: 'rgba(15, 23, 42, 0.05)',
                      padding: '10px 12px',
                      borderRadius: '8px',
                      overflowX: 'auto',
                      fontSize: '0.82rem',
                    }}
                  >
                    <code className={className} {...props}>
                      {children}
                    </code>
                  </pre>
                );
              },
            }}
          >
            {message.content}
          </ReactMarkdown>

          {/* Curseur animé de streaming */}
          {isStreaming && (
            <span
              style={{
                display: 'inline-block',
                width: '6px',
                height: '14px',
                marginLeft: '4px',
                verticalAlign: 'middle',
                background: '#10B981',
                borderRadius: '1px',
                animation: 'cursor-blink 0.8s infinite',
              }}
            />
          )}
        </div>

        {/* Bouton de copie textuel épuré */}
        {message.content && !isStreaming && (
          <div className={styles.messageActions}>
            <button
              onClick={handleCopy}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#94A3B8',
                fontSize: '0.72rem',
                fontWeight: 600,
                cursor: 'pointer',
                padding: '2px 6px',
                borderRadius: 4,
              }}
            >
              {copied ? 'Copié' : 'Copier'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
