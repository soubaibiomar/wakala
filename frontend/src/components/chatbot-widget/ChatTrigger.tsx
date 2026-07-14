import { useEffect, useState } from 'react';
import '../../styles/car-motifs.css';
import styles from './chatbot.module.css';

interface ChatTriggerProps {
  isOpen: boolean;
  hasNewMessage: boolean;
  onClick: () => void;
}

export default function ChatTrigger({ isOpen, hasNewMessage, onClick }: ChatTriggerProps) {
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    if (hasNewMessage && !isOpen) {
      setPulse(true);
      const timer = setTimeout(() => setPulse(false), 800);
      return () => clearTimeout(timer);
    }
  }, [hasNewMessage, isOpen]);

  return (
    <button
      className={`${styles.trigger} ${isOpen ? styles.triggerOpen : ''}`}
      onClick={onClick}
      aria-label={isOpen ? 'Fermer le chat' : 'Ouvrir le chat'}
    >
      <div className={styles.triggerCar} style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', borderRadius: '50%', backgroundColor: '#FFFFFF' }}>
        <img
          src="/assets/chatlogo.png"
          alt="Chat Wakala"
          style={{ width: '100%', height: '100%', objectFit: 'contain', transform: 'scale(2.5)', transformOrigin: 'center' }}
        />
      </div>
      
      {hasNewMessage && !isOpen && (
        <span className={styles.notificationBadge}>1</span>
      )}
    </button>
  );
}
