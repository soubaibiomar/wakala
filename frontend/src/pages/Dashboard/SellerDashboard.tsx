import { BentoGrid, BentoWidget } from '../../components/dashboard/BentoGrid';
import { AiStatusWidget } from '../../components/dashboard/widgets/AiStatusWidget';
import { ArgusQuickWidget } from '../../components/dashboard/widgets/ArgusQuickWidget';
import { ListingHealthWidget } from '../../components/dashboard/widgets/ListingHealthWidget';
import { PlusCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function SellerDashboard() {
  const navigate = useNavigate();

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '8px' }}>
            Espace Vendeur
          </h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            Gérez vos annonces et analysez vos performances.
          </p>
        </div>
        <button
          onClick={() => navigate('/dashboard/new-listing')}
          style={{
            display: 'flex', alignItems: 'center', gap: '8px',
            background: 'var(--color-accent)', color: '#fff',
            border: 'none', padding: '12px 20px', borderRadius: '8px',
            fontWeight: 600, cursor: 'pointer', transition: 'transform 0.2s',
            boxShadow: '0 4px 12px rgba(174, 140, 78, 0.3)'
          }}
          onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
          onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
        >
          <PlusCircle size={20} />
          <span style={{ display: 'none' }} className="desktop-only">Déposer une annonce</span>
        </button>
      </div>

      <BentoGrid>
        <ListingHealthWidget />
        <AiStatusWidget />
        <ArgusQuickWidget />
      </BentoGrid>
    </div>
  );
}
