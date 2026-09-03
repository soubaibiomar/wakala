import { MessageCircle, X } from 'lucide-react';

interface ChatBubbleIconProps {
  open: boolean;
  onClick: () => void;
}

export function ChatBubbleIcon({ open, onClick }: ChatBubbleIconProps) {
  return (
    <button className="recommendation-experience__bubble" onClick={onClick} aria-label={open ? 'Fermer le conseiller' : 'Ouvrir le conseiller'}>
      {open ? <X size={22} aria-hidden="true" /> : <MessageCircle size={24} aria-hidden="true" />}
    </button>
  );
}
