import { BentoGrid } from '../../components/dashboard/BentoGrid';
import { ScrapingPipelineWidget, MarketPriceChartWidget, FraudAlertsWidget } from '../../components/dashboard/widgets/AdminWidgets';

export default function AdminDashboardBento() {
  return (
    <div>
      <h1 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '8px' }}>
        Administration (Wakala Core)
      </h1>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
        Vue globale de l'ingestion, des tendances de marché et des alertes sécurité.
      </p>

      <BentoGrid>
        <MarketPriceChartWidget />
        <ScrapingPipelineWidget />
        <FraudAlertsWidget />
      </BentoGrid>
    </div>
  );
}
