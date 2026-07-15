import { useQuery } from '@tanstack/react-query';
import { BentoWidget } from '../BentoGrid';
import { Database, TrendingUp, AlertTriangle } from 'lucide-react';

export function ScrapingPipelineWidget() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-scraping'],
    queryFn: async () => {
      await new Promise(r => setTimeout(r, 600));
      return { total: 12543, today: 245, failed: 12 };
    }
  });

  return (
    <BentoWidget title="Pipeline Scraping" isLoading={isLoading} colSpan={1} rowSpan={1}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Database size={24} color="var(--color-accent)" />
          <div>
            <div style={{ fontSize: '1.4rem', fontWeight: 'bold' }}>{data?.today}</div>
            <div style={{ fontSize: '0.8rem', color: 'gray' }}>Annonces ajoutées (Aujourd'hui)</div>
          </div>
        </div>
        {data && data.failed > 0 && (
          <div style={{ color: '#EF4444', fontSize: '0.85rem', display: 'flex', gap: '4px' }}>
            <AlertTriangle size={14} /> {data.failed} sources en erreur
          </div>
        )}
      </div>
    </BentoWidget>
  );
}

export function MarketPriceChartWidget() {
  const { isLoading } = useQuery({
    queryKey: ['admin-market-chart'],
    queryFn: async () => {
      await new Promise(r => setTimeout(r, 1000));
      return true;
    }
  });

  return (
    <BentoWidget title="Tendance Marché (Temps Réel)" isLoading={isLoading} colSpan={2} rowSpan={2}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: 'gray', border: '1px dashed rgba(255,255,255,0.1)', borderRadius: '8px', padding: '20px' }}>
        <TrendingUp size={48} style={{ opacity: 0.2, marginBottom: '16px' }} />
        <p>Graphique des transactions (Cote Argus)</p>
        <p style={{ fontSize: '0.8rem' }}>*Le rendu Recharts/Chart.js serait injecté ici*</p>
      </div>
    </BentoWidget>
  );
}

export function FraudAlertsWidget() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-fraud'],
    queryFn: async () => {
      await new Promise(r => setTimeout(r, 900));
      return [
        { id: 'f1', issue: "Prix anormalement bas (60% sous argus)" },
        { id: 'f2', issue: "Même numéro de téléphone sur 5 comptes" }
      ];
    }
  });

  return (
    <BentoWidget title="Alertes Fraude (IA)" isLoading={isLoading} colSpan={1} rowSpan={1}>
      <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {data?.map(alert => (
          <li key={alert.id} style={{ display: 'flex', gap: '8px', alignItems: 'flex-start', background: 'rgba(239, 68, 68, 0.1)', padding: '12px', borderRadius: '8px', borderLeft: '3px solid #EF4444' }}>
            <AlertTriangle size={16} color="#EF4444" style={{ marginTop: '2px', flexShrink: 0 }} />
            <span style={{ fontSize: '0.85rem' }}>{alert.issue}</span>
          </li>
        ))}
      </ul>
    </BentoWidget>
  );
}
