import { BentoGrid } from '../../components/dashboard/BentoGrid';
import { AiStatusWidget } from '../../components/dashboard/widgets/AiStatusWidget';
import { ArgusQuickWidget } from '../../components/dashboard/widgets/ArgusQuickWidget';
import { RecentActivityWidget } from '../../components/dashboard/widgets/RecentActivityWidget';

export default function BuyerDashboard() {
  return (
    <div>
      <h1 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '8px' }}>
        Tableau de bord
      </h1>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
        Bienvenue dans votre espace Wakala. Trouvez votre prochaine voiture avec l'IA.
      </p>

      <BentoGrid>
        <AiStatusWidget />
        <RecentActivityWidget />
        <ArgusQuickWidget />
      </BentoGrid>
    </div>
  );
}
