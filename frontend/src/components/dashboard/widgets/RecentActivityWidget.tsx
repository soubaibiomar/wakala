import { useQuery } from '@tanstack/react-query';
import { BentoWidget } from '../BentoGrid';
import { Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export function RecentActivityWidget() {
  const { data, isLoading } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: async () => {
      // Mock data representing recent views or favorites
      await new Promise(r => setTimeout(r, 1200));
      return [
        { id: '1', title: 'Peugeot 208 Active', price: '120 000 MAD', time: 'Il y a 2h' },
        { id: '2', title: 'Renault Clio 5', price: '145 000 MAD', time: 'Il y a 5h' },
        { id: '3', title: 'Dacia Duster', price: '160 000 MAD', time: 'Hier' },
      ];
    }
  });

  return (
    <BentoWidget title="Activité Récente" isLoading={isLoading} colSpan={1} rowSpan={2}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {data?.map(item => (
          <Link 
            key={item.id} 
            to={`/vehicule/${item.id}`}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '12px', background: 'rgba(255,255,255,0.03)',
              borderRadius: '8px', textDecoration: 'none', color: 'inherit',
              border: '1px solid rgba(255,255,255,0.05)'
            }}
          >
            <div>
              <h4 style={{ margin: '0 0 4px 0', fontSize: '0.9rem' }}>{item.title}</h4>
              <span style={{ fontSize: '0.8rem', color: 'var(--color-accent)' }}>{item.price}</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: 'gray' }}>
              <Clock size={12} />
              {item.time}
            </div>
          </Link>
        ))}
      </div>
    </BentoWidget>
  );
}
