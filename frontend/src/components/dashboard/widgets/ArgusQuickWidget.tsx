import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { BentoWidget } from '../BentoGrid';
import { Calculator } from 'lucide-react';
import { PriceGauge } from '../../pricing/PriceGauge';

export function ArgusQuickWidget() {
  const [formData, setFormData] = useState({ brand: '', model: '', year: 2020 });
  
  const estimateMutation = useMutation({
    mutationFn: async (data: any) => {
      const res = await fetch('http://localhost:8000/api/vehicles/estimate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...data,
          mileage: 50000,
          fuel_type: "diesel",
          body_type: "berline",
          transmission: "manuelle",
          city: "Casablanca"
        })
      });
      if (!res.ok) throw new Error('Erreur estimation');
      return res.json();
    }
  });

  return (
    <BentoWidget title="Argus Express" colSpan={1} rowSpan={2}>
      <form 
        onSubmit={(e) => {
          e.preventDefault();
          estimateMutation.mutate(formData);
        }}
        style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1 }}
      >
        <input 
          type="text" 
          placeholder="Marque (ex: Renault)"
          value={formData.brand}
          onChange={e => setFormData({...formData, brand: e.target.value})}
          style={{ padding: '10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(0,0,0,0.2)', color: 'white' }}
          required
        />
        <input 
          type="text" 
          placeholder="Modèle (ex: Clio)"
          value={formData.model}
          onChange={e => setFormData({...formData, model: e.target.value})}
          style={{ padding: '10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(0,0,0,0.2)', color: 'white' }}
          required
        />
        <input 
          type="number" 
          placeholder="Année"
          value={formData.year}
          onChange={e => setFormData({...formData, year: parseInt(e.target.value) || 2020})}
          style={{ padding: '10px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(0,0,0,0.2)', color: 'white' }}
          min="1990" max="2030"
        />
        <button 
          type="submit"
          disabled={estimateMutation.isPending}
          style={{
            background: 'var(--color-primary-light, #334155)', color: 'white',
            border: 'none', padding: '10px', borderRadius: '8px', cursor: 'pointer',
            display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px',
            marginTop: '8px'
          }}
        >
          <Calculator size={18} />
          {estimateMutation.isPending ? 'Calcul en cours...' : 'Estimer'}
        </button>
      </form>

      {estimateMutation.data && (
        <div style={{ marginTop: '20px' }}>
          <PriceGauge 
            currentPrice={estimateMutation.data.predicted_price} 
            argusPrice={estimateMutation.data.predicted_price}
            trend={estimateMutation.data.market_trend}
          />
        </div>
      )}
    </BentoWidget>
  );
}
