import { useQuery } from '@tanstack/react-query';
import { BentoWidget } from '../BentoGrid';
import { ArrowUpCircle, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

export function ListingHealthWidget() {
  const { data, isLoading } = useQuery({
    queryKey: ['listing-health'],
    queryFn: async () => {
      await new Promise(r => setTimeout(r, 800));
      return {
        score: 78,
        tips: [
          "Ajoutez plus de photos de l'intérieur (gain estimé: +10%)",
          "Le prix est 3% au-dessus du marché. Ajustez-le pour plus de clics."
        ]
      };
    }
  });

  return (
    <BentoWidget title="Santé de vos Annonces" isLoading={isLoading} colSpan={2} rowSpan={1}>
      <div style={{ display: 'flex', gap: '24px', alignItems: 'center', height: '100%' }}>
        
        {/* Score gauge */}
        <div style={{ position: 'relative', width: '80px', height: '80px', flexShrink: 0 }}>
          <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="3"
            />
            <path
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              fill="none" stroke="var(--color-accent)" strokeWidth="3"
              strokeDasharray={`${data?.score || 0}, 100`}
            />
          </svg>
          <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.2rem', fontWeight: 'bold' }}>
            {data?.score}%
          </div>
        </div>

        {/* Tips */}
        <div style={{ flex: 1 }}>
          <p style={{ margin: '0 0 12px 0', fontSize: '0.9rem', color: 'rgba(255,255,255,0.7)' }}>
            Insights IA pour améliorer votre visibilité :
          </p>
          <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {data?.tips.map((tip, idx) => (
              <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.85rem' }}>
                <ArrowUpCircle size={16} color="var(--color-accent)" style={{ marginTop: '2px', flexShrink: 0 }} />
                <span>{tip}</span>
              </li>
            ))}
          </ul>
          <div style={{ marginTop: '16px' }}>
            <Link to="/dashboard/listings" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--color-accent)', textDecoration: 'none', fontWeight: 500 }}>
              Gérer mes annonces <ExternalLink size={14} />
            </Link>
          </div>
        </div>
      </div>
    </BentoWidget>
  );
}
