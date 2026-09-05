import { X } from 'lucide-react';

interface ChatBubbleIconProps {
  open: boolean;
  onClick: () => void;
  hasActiveConversation?: boolean;
}

export function ChatBubbleIcon({ open, onClick, hasActiveConversation }: ChatBubbleIconProps) {
  return (
    <button
      type="button"
      className={`recommendation-experience__bubble ${open ? 'recommendation-experience__bubble--open' : ''}`}
      onClick={onClick}
      aria-label={open ? 'Fermer le conseiller' : 'Ouvrir le conseiller'}
    >
      {open ? (
        <X size={22} aria-hidden="true" />
      ) : (
        <div className="recommendation-experience__bubble-car" aria-hidden="true">
          <img
            src="/assets/chatlogo.png"
            alt="Wakala"
            className="recommendation-experience__bubble-img"
          />
        </div>
      )}
      {hasActiveConversation && !open && (
        <span className="recommendation-experience__bubble-badge" title="Conversation active" aria-hidden="true" />
      )}
    </button>
  );
}
