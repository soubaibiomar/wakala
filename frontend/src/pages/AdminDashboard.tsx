import React, { useEffect, useState } from 'react';
import { ShieldAlert, RefreshCw, CheckCircle, UserX } from 'lucide-react';
import api from '../services/api';

interface FlaggedUser {
  id: string;
  name: string;
  email: string;
  phone: string;
  role: string;
  created_at: string;
}

export default function AdminDashboard() {
  const [brokers, setBrokers] = useState<FlaggedUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [detecting, setDetecting] = useState(false);
  const [detectionResult, setDetectionResult] = useState<{ suspects_found: number; newly_flagged: number } | null>(null);

  const fetchBrokers = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/v1/admin/brokers');
      setBrokers(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBrokers();
  }, []);

  const handleDetect = async () => {
    setDetecting(true);
    setDetectionResult(null);
    try {
      const { data } = await api.post('/v1/admin/detect-brokers');
      setDetectionResult(data);
      fetchBrokers(); // Refresh the list
    } catch (err) {
      console.error("Erreur de détection", err);
    } finally {
      setDetecting(false);
    }
  };

  return (
    <div className="container" style={{ padding: '40px 20px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 }}>
        <h1 style={{ fontSize: '2rem', display: 'flex', alignItems: 'center', gap: 12, margin: 0 }}>
          <ShieldAlert size={32} color="var(--accent-red)" />
          Alerte Fraude (Courtiers Clandestins)
        </h1>
        
        <button 
          onClick={handleDetect} 
          disabled={detecting}
          className="btn btn--primary"
          style={{ display: 'flex', alignItems: 'center', gap: 8 }}
        >
          <RefreshCw size={18} className={detecting ? "spin" : ""} />
          Lancer l'analyse Neo4j
        </button>
      </div>

      {detectionResult && (
        <div style={{ 
          background: 'rgba(16,185,129,0.1)', border: '1px solid var(--accent-green)', 
          padding: 16, borderRadius: 'var(--radius-card)', marginBottom: 24,
          display: 'flex', alignItems: 'center', gap: 12, color: 'var(--accent-green)'
        }}>
          <CheckCircle size={24} />
          <div>
            <div style={{ fontWeight: 600 }}>Analyse Graph Data Science terminée avec succès.</div>
            <div style={{ fontSize: '0.9rem' }}>
              Clusters détectés : {detectionResult.suspects_found} | Nouveaux comptes taggés : {detectionResult.newly_flagged}
            </div>
          </div>
        </div>
      )}

      <div style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius-card)', border: '1px solid var(--border-subtle)', overflow: 'hidden' }}>
        <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border-subtle)', background: 'var(--bg-surface)' }}>
          <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Comptes flaggés `is_pro = true`</h3>
        </div>
        
        {loading ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>Chargement...</div>
        ) : brokers.length === 0 ? (
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
            Aucun courtier clandestin détecté pour le moment.
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-subtle)', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                <th style={{ padding: '12px 24px' }}>Utilisateur</th>
                <th style={{ padding: '12px 24px' }}>Email</th>
                <th style={{ padding: '12px 24px' }}>Téléphone</th>
                <th style={{ padding: '12px 24px' }}>Rôle d'origine</th>
                <th style={{ padding: '12px 24px' }}>Statut</th>
              </tr>
            </thead>
            <tbody>
              {brokers.map(b => (
                <tr key={b.id} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                  <td style={{ padding: '16px 24px', fontWeight: 500 }}>{b.name}</td>
                  <td style={{ padding: '16px 24px', color: 'var(--text-secondary)' }}>{b.email}</td>
                  <td style={{ padding: '16px 24px', color: 'var(--text-secondary)' }}>{b.phone || 'N/A'}</td>
                  <td style={{ padding: '16px 24px' }}>
                    <span className="badge" style={{ background: 'rgba(255,255,255,0.1)' }}>{b.role}</span>
                  </td>
                  <td style={{ padding: '16px 24px' }}>
                    <span className="badge" style={{ background: 'rgba(239,68,68,0.15)', color: 'var(--accent-red)', display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                      <UserX size={12} /> Courtier
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <style>{`
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
