import { useQuery } from '@tanstack/react-query';
import { BentoWidget } from '../BentoGrid';
import { MessageSquare, Sparkles } from 'lucide-react';
import { useAuth } from '../../../context/AuthContext';

export function AiStatusWidget() {
  const { user } = useAuth();
  
  // Fake API call for demonstration (would be an actual endpoint getting user insights)
  const { data, isLoading } = useQuery({
    queryKey: ['ai-status'],
    queryFn: async () => {
      await new Promise(r => setTimeout(r, 1000));
      return {
        matchingListings: 3,
        message: "3 annonces correspondent à vos critères de recherche récents.",
      };
    }
  });

  return (
    <BentoWidget isLoading={isLoading} className="ai-widget">
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
        <div style={{ background: 'rgba(174, 140, 78, 0.2)', padding: '12px', borderRadius: '50%', color: 'var(--color-accent)' }}>
          <Sparkles size={24} />
        </div>
        <div>
          <h3 style={{ fontSize: '1.2rem', margin: '0 0 8px 0' }}>Assistant IA Wakala</h3>
          <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: '0.9rem', marginBottom: '16px' }}>
            Bonjour {user?.full_name?.split(' ')[0]}, {data?.message}
          </p>
          <button 
            style={{
              display: 'flex', alignItems: 'center', gap: '8px',
              background: 'var(--color-accent)', color: '#fff',
              border: 'none', padding: '8px 16px', borderRadius: '8px',
              fontWeight: 600, cursor: 'pointer', transition: 'background 0.2s'
            }}
            onClick={() => {
              // Trigger global chatbot open event
              window.dispatchEvent(new CustomEvent('wakala:open-chat'));
            }}
          >
            <MessageSquare size={18} />
            Voir avec l'assistant
          </button>
        </div>
      </div>
    </BentoWidget>
  );
}
