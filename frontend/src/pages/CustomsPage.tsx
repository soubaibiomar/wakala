import React, { useState } from 'react';
import { Calculator, ShieldAlert, Sparkles, TrendingUp, Info } from 'lucide-react';
import { customsService, CustomsRequest, CustomsResponse } from '../services/customsService';

export default function CustomsPage() {
  const [form, setForm] = useState<CustomsRequest>({
    brand: 'Volkswagen',
    model: 'Golf',
    year: new Date().getFullYear() - 3,
    fuel_type: 'Diesel',
    fiscal_power: 8,
    origin_eu: true,
    purchase_price_origin: 150000,
  });

  const [result, setResult] = useState<CustomsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await customsService.calculate(form);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur de calcul.");
    } finally {
      setLoading(false);
    }
  };

  const isGoodDeal = result ? result.financial_breakdown.total_cost <= result.local_market_price : false;

  return (
    <div className="container" style={{ padding: '40px 20px', maxWidth: 1200 }}>
      
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <h1 style={{ fontSize: '2.5rem', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
          <Calculator color="var(--accent-gold)" size={40} />
          Calculateur de Dédouanement
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', maxWidth: 600, margin: '0 auto' }}>
          Estimez les frais de douane marocains avec précision et obtenez l'avis de notre IA sur la rentabilité de votre importation par rapport au marché local.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 32, flexWrap: 'wrap' }}>
        
        {/* Formulaire */}
        <div style={{ flex: '1 1 400px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-card)', padding: 32, border: '1px solid var(--border-subtle)', boxShadow: '0 8px 30px rgba(0,0,0,0.05)' }}>
          <form onSubmit={handleCalculate} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div>
                <label style={{ display: 'block', marginBottom: 8, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Marque</label>
                <input 
                  type="text" 
                  value={form.brand} 
                  onChange={e => setForm({...form, brand: e.target.value})}
                  style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-button)', border: '1px solid var(--border-subtle)', background: 'var(--bg-surface)', color: 'var(--text-primary)' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: 8, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Modèle</label>
                <input 
                  type="text" 
                  value={form.model} 
                  onChange={e => setForm({...form, model: e.target.value})}
                  style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-button)', border: '1px solid var(--border-subtle)', background: 'var(--bg-surface)', color: 'var(--text-primary)' }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: 8, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Année de mise en circulation</label>
              <input 
                type="number" 
                value={form.year} 
                onChange={e => setForm({...form, year: parseInt(e.target.value)})}
                style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-button)', border: '1px solid var(--border-subtle)', background: 'var(--bg-surface)', color: 'var(--text-primary)' }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div>
                <label style={{ display: 'block', marginBottom: 8, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Énergie</label>
                <select 
                  value={form.fuel_type} 
                  onChange={e => setForm({...form, fuel_type: e.target.value})}
                  style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-button)', border: '1px solid var(--border-subtle)', background: 'var(--bg-surface)', color: 'var(--text-primary)' }}
                >
                  <option value="Diesel">Diesel</option>
                  <option value="Essence">Essence</option>
                  <option value="Hybride">Hybride</option>
                  <option value="Electrique">Électrique</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: 8, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Puissance Fiscale (CV)</label>
                <input 
                  type="number" 
                  value={form.fiscal_power} 
                  onChange={e => setForm({...form, fiscal_power: parseInt(e.target.value)})}
                  style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-button)', border: '1px solid var(--border-subtle)', background: 'var(--bg-surface)', color: 'var(--text-primary)' }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: 8, fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Prix d'achat (MAD)</label>
              <input 
                type="number" 
                value={form.purchase_price_origin} 
                onChange={e => setForm({...form, purchase_price_origin: parseFloat(e.target.value)})}
                style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-button)', border: '1px solid var(--border-subtle)', background: 'var(--bg-surface)', color: 'var(--text-primary)', fontSize: '1.2rem', fontFamily: 'Inter' }}
              />
            </div>

            <label style={{ display: 'flex', alignItems: 'center', gap: 12, cursor: 'pointer', padding: '16px', background: 'var(--bg-surface)', borderRadius: 'var(--radius-button)', border: '1px solid var(--border-subtle)' }}>
              <input 
                type="checkbox" 
                checked={form.origin_eu}
                onChange={e => setForm({...form, origin_eu: e.target.checked})}
                style={{ width: 20, height: 20, accentColor: 'var(--accent-gold)' }}
              />
              <span style={{ fontSize: '0.95rem' }}>Véhicule d'origine Européenne (Accords de libre-échange)</span>
            </label>

            <button 
              type="submit" 
              className="btn btn--primary" 
              disabled={loading}
              style={{ width: '100%', padding: '16px', fontSize: '1.1rem', marginTop: 16 }}
            >
              {loading ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
                  <div className="spinner" style={{ width: 20, height: 20, border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
                  Calcul en cours...
                </div>
              ) : 'Estimer les frais et la rentabilité'}
            </button>
            {error && <div style={{ color: 'var(--accent-red)', textAlign: 'center', marginTop: 8 }}>{error}</div>}
          </form>
        </div>

        {/* Dashboard Financier */}
        <div style={{ flex: '1 1 500px', display: 'flex', flexDirection: 'column', gap: 24 }}>
          {result ? (
            <>
              {/* Verdict IA */}
              <div style={{ 
                background: isGoodDeal ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.05)', 
                border: `1px solid ${isGoodDeal ? 'var(--accent-green)' : 'var(--accent-red)'}`, 
                borderRadius: 'var(--radius-card)', padding: 32,
                boxShadow: isGoodDeal ? '0 0 40px rgba(16, 185, 129, 0.1)' : '0 0 40px rgba(239, 68, 68, 0.1)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                  {isGoodDeal ? <TrendingUp size={28} color="var(--accent-green)" /> : <ShieldAlert size={28} color="var(--accent-red)" />}
                  <h2 style={{ margin: 0, fontSize: '1.5rem', color: isGoodDeal ? 'var(--accent-green)' : 'var(--accent-red)' }}>
                    {isGoodDeal ? "Bonne Affaire" : "Non Rentable"}
                  </h2>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24, padding: '20px', background: 'var(--bg-surface)', borderRadius: 'var(--radius-button)' }}>
                  <div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: 4 }}>Coût de revient total</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'Inter' }}>
                      {new Intl.NumberFormat('fr-MA').format(result.financial_breakdown.total_cost)} MAD
                    </div>
                  </div>
                  <div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: 4 }}>Argus Wakala (Marché Local)</div>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'Inter' }}>
                      {new Intl.NumberFormat('fr-MA').format(result.local_market_price)} MAD
                    </div>
                  </div>
                </div>

                <div style={{ color: 'var(--text-primary)', lineHeight: 1.6, fontSize: '1.05rem' }}>
                  <p style={{ display: 'flex', gap: 8, alignItems: 'flex-start', margin: 0 }}>
                    <Sparkles size={20} color="var(--accent-gold)" style={{ flexShrink: 0, marginTop: 4 }} />
                    <span dangerouslySetInnerHTML={{ __html: result.ai_verdict.replace(/\n/g, '<br/>') }} />
                  </p>
                </div>
              </div>

              {/* Détail Financier */}
              <div style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius-card)', padding: 32, border: '1px solid var(--border-subtle)' }}>
                <h3 style={{ margin: '0 0 24px 0', fontSize: '1.2rem' }}>Ventilation des Frais de Douane</h3>
                
                {/* Bar Graph */}
                <div style={{ display: 'flex', height: 40, borderRadius: 'var(--radius-button)', overflow: 'hidden', marginBottom: 32 }}>
                  {result.financial_breakdown.breakdown.map((item, idx) => (
                    <div 
                      key={idx} 
                      style={{ 
                        width: `${(item.amount / result.financial_breakdown.total_cost) * 100}%`, 
                        background: item.color,
                        borderRight: idx < result.financial_breakdown.breakdown.length - 1 ? '1px solid var(--bg-elevated)' : 'none'
                      }}
                      title={`${item.label}: ${new Intl.NumberFormat('fr-MA').format(item.amount)} MAD`}
                    />
                  ))}
                </div>

                {/* List */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  {result.financial_breakdown.breakdown.map((item, idx) => (
                    <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{ width: 12, height: 12, borderRadius: '50%', background: item.color }} />
                        <span style={{ color: 'var(--text-secondary)' }}>{item.label}</span>
                      </div>
                      <strong style={{ fontFamily: 'Inter' }}>{new Intl.NumberFormat('fr-MA').format(item.amount)} MAD</strong>
                    </div>
                  ))}
                  
                  <div style={{ height: 1, background: 'var(--border-subtle)', margin: '8px 0' }} />
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '1.2rem' }}>
                    <strong>Frais de Douane Total</strong>
                    <strong style={{ color: 'var(--accent-gold)', fontFamily: 'Inter' }}>
                      {new Intl.NumberFormat('fr-MA').format(result.financial_breakdown.total_customs_fees)} MAD
                    </strong>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-card)', border: '1px solid var(--border-subtle)', borderStyle: 'dashed' }}>
              <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                <Calculator size={48} style={{ opacity: 0.2, marginBottom: 16 }} />
                <p>Remplissez le formulaire pour générer<br/>votre rapport douanier.</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div style={{ marginTop: 40, padding: 24, background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)', display: 'flex', gap: 16, color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        <Info size={24} style={{ flexShrink: 0 }} />
        <div>
          <strong>Avertissement Légal :</strong> Les résultats de ce simulateur sont fournis à titre indicatif et se basent sur un modèle simplifié des règles de l'Administration des Douanes et Impôts Indirects (ADII) du Maroc. Les montants exacts peuvent varier en fonction des accords commerciaux, des options d'équipements spécifiques ou des mises à jour réglementaires. Wakala décline toute responsabilité quant à l'exactitude absolue de ces chiffres. Consultez un transitaire agréé pour un chiffrage officiel.
        </div>
      </div>
    </div>
  );
}
