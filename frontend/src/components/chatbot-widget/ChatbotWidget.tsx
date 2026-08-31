import { useState, useCallback, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useChatSession } from './useChatSession';
import ChatTrigger from './ChatTrigger';
import ChatWindow from './ChatWindow';
import styles from './chatbot.module.css';

export default function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const { messages, isTyping, error, sendMessage, cancelGeneration, clearHistory, initConversation } = useChatSession();
  const [notificationCount, setNotificationCount] = useState(0);
  const location = useLocation();

  const toggleOpen = useCallback(() => {
    setIsOpen((prev) => {
      if (!prev) {
        setNotificationCount(0);
      }
      return !prev;
    });
  }, []);

  useEffect(() => {
    const handleOpenChat = () => setIsOpen(true);
    window.addEventListener('wakala:open-chat', handleOpenChat);
    return () => window.removeEventListener('wakala:open-chat', handleOpenChat);
  }, []);

  const handleSend = useCallback(
    (text: string) => {
      sendMessage(text);
    },
    [sendMessage],
  );

  const hasNewMessage = messages.length > 0 && !isOpen;

  return (
    <>
      <motion.div 
        className={`${styles.widget} ${isOpen ? styles.widgetOpen : ''}`}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.2 }}
        style={{ pointerEvents: 'none' }}
      >
      {isOpen && (
        <ChatWindow
          messages={messages}
          isTyping={isTyping}
          error={error}
          onSend={handleSend}
          onCancel={cancelGeneration}
          onClear={clearHistory}
          onInitLanguage={initConversation}
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
      </motion.div>
    </>
  );
}
