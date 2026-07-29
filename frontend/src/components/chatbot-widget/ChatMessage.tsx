import ReactMarkdown from 'react-markdown';
import type { Message } from './useChatSession';
import CarRecommendation from './CarRecommendation';
import styles from './chatbot.module.css';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

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
                         <div style={{ padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px dashed rgba(255,255,255,0.1)', textAlign: 'center', margin: '8px 0' }}>
                           <p style={{ fontSize: '0.8rem', color: 'var(--accent-gold)', margin: 0, opacity: 0.8 }}>
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
      </div>
    </div>
  );
}
