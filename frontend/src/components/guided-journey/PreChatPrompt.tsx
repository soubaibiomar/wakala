import React from 'react';
import './PreChatPrompt.css';

export interface PreChatPromptProps {
  score: number;
  onOpenChat: () => void;
}

export default function PreChatPrompt({ score, onOpenChat }: PreChatPromptProps) {
  if (score >= 80) return null; // No need to prompt if very reliable

  return (
    <div className="pre-chat-prompt">
      <div className="pre-chat-icon">🤖</div>
      <div className="pre-chat-content">
        <h4>Une question sur ce véhicule ?</h4>
        <p>Le score de confiance est de {score}%. Je peux vous aider à identifier les risques potentiels.</p>
      </div>
      <button className="pre-chat-button" onClick={onOpenChat}>
        Discuter
      </button>
    </div>
  );
}
