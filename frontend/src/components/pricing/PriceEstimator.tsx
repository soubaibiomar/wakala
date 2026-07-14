import { useState, useEffect, useRef } from 'react';
import { pricingService } from '../../services/pricingService';
import type { PricePredictionInput, PricePredictionResult } from '../../services/pricingService';

interface PriceEstimatorProps {
  initialValues?: Partial<PricePredictionInput>;
  onPriceChange?: (predicted: number) => void;
}

function GaugeSvg({ value, max, label }: { value: number; max: number; label: string }) {
  const ratio = Math.min(value / max, 1);
  const angle = ratio * 180;
  const radians = (angle - 90) * (Math.PI / 180);
  const cx = 60;
  const cy = 60;
  const r = 45;
  const x = cx + r * Math.cos(radians);
  const y = cy + r * Math.sin(radians);

  const color = ratio < 0.5 ? '#22c55e' : ratio < 0.8 ? '#eab308' : '#ef4444';

  return (
    <svg width="140" height="90" viewBox="0 0 120 80" style={{ display: 'block' }}>
      <path
        d="M 15 70 A 45 45 0 0 1 105 70"
        fill="none"
        stroke="rgba(255,255,255,0.08)"
        strokeWidth="8"
        strokeLinecap="round"
      />
      <path
        d="M 15 70 A 45 45 0 0 1 105 70"
        fill="none"
        stroke={color}
        strokeWidth="8"
        strokeLinecap="round"
        strokeDasharray={`${ratio * 141.37} 141.37`}
      />
      <line
        x1={cx}
        y1={cy}
        x2={x}
        y2={y}
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
      />
      <circle cx={cx} cy={cy} r="3" fill={color} />
      <text x={cx} y={cy + 22} textAnchor="middle" fill="rgba(255,255,255,0.8)"
        fontSize="11" fontWeight="600" fontFamily="monospace">
        {label}
      </text>
    </svg>
  );
}

export default function PriceEstimator({ initialValues, onPriceChange }: PriceEstimatorProps) {
  const [form, setForm] = useState<PricePredictionInput>({
    brand: initialValues?.brand || '',
    model: initialValues?.model || '',
    year: initialValues?.year || 2020,
    mileage: initialValues?.mileage || 0,
    fuel_type: initialValues?.fuel_type || 'essence',
    body_type: initialValues?.body_type || 'berline',
    transmission: initialValues?.transmission || 'manuelle',
    engine_power_hp: initialValues?.engine_power_hp ?? null,
    doors: initialValues?.doors || 5,
    seats: initialValues?.seats || 5,
    city: initialValues?.city || 'Casablanca',
  });

  const [result, setResult] = useState<PricePredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [enteredPrice, setEnteredPrice] = useState<number | ''>('');
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  const canPredict = form.brand && form.model && form.city && form.year > 1990;

  useEffect(() => {
    if (!canPredict) {
      setResult(null);
      return;
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await pricingService.predict(form);
        setResult(res);
        onPriceChange?.(res.predicted_price);
      } catch {
        setResult(null);
      } finally {
        setLoading(false);
      }
    }, 600);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [form, canPredict, onPriceChange]);

  const update = <K extends keyof PricePredictionInput>(field: K, value: PricePredictionInput[K]) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const priceDiff = result && enteredPrice !== ''
    ? ((Number(enteredPrice) - result.predicted_price) / result.predicted_price) * 100
    : null;

  return (
    <div style={{
      padding: 'var(--space-lg)',
      background: 'var(--bg-surface)',
      borderRadius: 'var(--radius-card)',
      border: '1px solid var(--border-subtle)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        <span style={{
          padding: '2px 8px', borderRadius: 'var(--radius-pill)', fontSize: '0.65rem',
          fontWeight: 600, background: 'rgba(91,192,222,0.15)', color: 'var(--accent-cyan)',
        }}>
          IA
        </span>
        <span style={{ fontWeight: 600, fontSize: '0.95rem', color: 'var(--text-primary)' }}>
          Estimation du prix marché
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
        <label style={{ gridColumn: 'span 2' }}>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>Marque</span>
          <input value={form.brand} onChange={(e) => update('brand', e.target.value)}
            placeholder="Renault" style={inputStyle} />
        </label>

        <label>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>Modèle</span>
          <input value={form.model} onChange={(e) => update('model', e.target.value)}
            placeholder="Clio" style={inputStyle} />
        </label>

        <label>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>Ville</span>
          <input value={form.city} onChange={(e) => update('city', e.target.value)}
            placeholder="Casablanca" style={inputStyle} />
        </label>

        <label>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>Année</span>
          <input type="number" value={form.year} onChange={(e) => update('year', Number(e.target.value))}
            min={1990} max={2030} style={inputStyle} />
        </label>

        <label>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>Kilométrage</span>
          <input type="number" value={form.mileage} onChange={(e) => update('mileage', Number(e.target.value))}
            min={0} style={inputStyle} />
        </label>

        <label>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>Carburant</span>
          <select value={form.fuel_type} onChange={(e) => update('fuel_type', e.target.value)} style={inputStyle}>
            {['essence', 'diesel', 'hybride', 'hybride_rechargeable', 'electrique', 'gpl'].map((f) => (
              <option key={f} value={f}>{f}</option>
            ))}
          </select>
        </label>

        <label>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>Carrosserie</span>
          <select value={form.body_type} onChange={(e) => update('body_type', e.target.value)} style={inputStyle}>
            {['citadine', 'berline', 'suv', 'break', 'coupe', 'cabriolet', 'monospace'].map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </label>

        <label>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>Puissance (ch)</span>
          <input type="number" value={form.engine_power_hp ?? ''}
            onChange={(e) => update('engine_power_hp', e.target.value ? Number(e.target.value) : null)}
            min={0} style={inputStyle} />
        </label>

        <label>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>Transmission</span>
          <select value={form.transmission} onChange={(e) => update('transmission', e.target.value)} style={inputStyle}>
            <option value="manuelle">Manuelle</option>
            <option value="automatique">Automatique</option>
            <option value="semi_auto">Semi-auto</option>
          </select>
        </label>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: 12, color: 'var(--text-muted)', fontSize: '0.8rem' }}>
          Estimation en cours...
        </div>
      )}

      {result && !loading && (
        <div style={{ marginTop: 16 }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 16,
            padding: 12, background: 'var(--bg-elevated)', borderRadius: 'var(--radius-card)',
          }}>
            <GaugeSvg
              value={result.predicted_price}
              max={400000}
              label={`${(result.predicted_price / 1000).toFixed(0)}k`}
            />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-gold)' }}>
                {result.predicted_price.toLocaleString('fr-FR')} MAD
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 2 }}>
                Intervalle : {result.confidence_interval.low.toLocaleString('fr-FR', { maximumFractionDigits: 0 })} – {result.confidence_interval.high.toLocaleString('fr-FR', { maximumFractionDigits: 0 })} MAD
              </div>
              <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 2 }}>
                Méthode : {result.method === 'xgboost' ? 'XGBoost (entraîné)' : 'Fallback (moyenne marché)'}
              </div>
            </div>
          </div>

          <div style={{ marginTop: 12 }}>
            <label>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: 2 }}>
                Prix que vous souhaitez afficher (MAD)
              </span>
              <input type="number" value={enteredPrice} onChange={(e) => setEnteredPrice(e.target.value ? Number(e.target.value) : '')}
                placeholder="Ex: 180000" style={inputStyle} />
            </label>
            {priceDiff !== null && (
              <div style={{
                marginTop: 8, padding: '8px 12px', borderRadius: 'var(--radius-pill)',
                fontSize: '0.8rem', fontWeight: 600,
                background: Math.abs(priceDiff) < 10 ? 'rgba(16,185,129,0.15)' : Math.abs(priceDiff) < 20 ? 'rgba(234,179,8,0.15)' : 'rgba(239,68,68,0.15)',
                color: Math.abs(priceDiff) < 10 ? 'var(--accent-green)' : Math.abs(priceDiff) < 20 ? 'var(--accent-gold)' : 'var(--accent-red)',
              }}>
                {priceDiff > 0
                  ? `↑ ${priceDiff.toFixed(1)}% au-dessus du prix marché`
                  : `↓ ${Math.abs(priceDiff).toFixed(1)}% en dessous du prix marché`
                }
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '8px 10px', fontSize: '0.85rem',
  background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)',
  borderRadius: 'var(--radius-pill)', color: 'var(--text-primary)',
  outline: 'none', boxSizing: 'border-box',
};
