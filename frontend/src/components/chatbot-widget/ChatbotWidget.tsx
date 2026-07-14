import { useState, useCallback } from 'react';
import { useChatSession } from './useChatSession';
import ChatTrigger from './ChatTrigger';
import ChatWindow from './ChatWindow';
import styles from './chatbot.module.css';

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const { messages, isTyping, error, sendMessage, clearHistory } = useChatSession();
  const [notificationCount, setNotificationCount] = useState(0);

  const toggleOpen = useCallback(() => {
    setIsOpen((prev) => {
      if (!prev) {
        setNotificationCount(0);
      }
      return !prev;
    });
  }, []);

  const handleSend = useCallback(
    (text: string) => {
      sendMessage(text);
    },
    [sendMessage],
  );

  const hasNewMessage = messages.length > 0 && !isOpen;

  return (
    <div className={styles.widget}>
      {isOpen && (
        <ChatWindow
          messages={messages}
          isTyping={isTyping}
          error={error}
          onSend={handleSend}
          onClear={clearHistory}
          onClose={toggleOpen}
        />
      )}

      {notificationCount > 0 && !isOpen && (
        <div className={styles.notificationBadge}>{notificationCount}</div>
      )}

      <ChatTrigger
        isOpen={isOpen}
        hasNewMessage={hasNewMessage}
        onClick={toggleOpen}
      />
    </div>
  );
}
