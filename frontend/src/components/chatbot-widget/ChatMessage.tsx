import type { Message } from './useChatSession';
import SourceVehicleCard from './SourceVehicleCard';
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
        <p className={styles.messageText}>{message.content}</p>

        {message.sources && message.sources.length > 0 && (
          <div className={styles.messageSources}>
            {message.sources.slice(0, 3).map((source) => (
              <SourceVehicleCard key={source.vehicle_id} source={source} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
