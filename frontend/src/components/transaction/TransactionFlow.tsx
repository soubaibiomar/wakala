import React, { useState } from 'react';
import { Lock, ShieldCheck, FileCheck, CheckCircle, AlertTriangle, UploadCloud } from 'lucide-react';
import { transactionService } from '../../services/transactionService';

interface TransactionFlowProps {
  listingId: string;
  price: number;
}

type Step = 'INIT' | 'PENDING' | 'FUNDS_SECURED' | 'COMPLETED' | 'DISPUTED';

export default function TransactionFlow({ listingId, price }: TransactionFlowProps) {
  const [step, setStep] = useState<Step>('INIT');
  const [txId, setTxId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);

  const handleInitiate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await transactionService.initiateTransaction(listingId);
      setTxId(res.id);
      setStep('PENDING');
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur d'initialisation.");
    } finally {
      setLoading(false);
    }
  };

  const handleSimulatePayment = async () => {
    if (!txId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await transactionService.simulateWebhookPayment(txId);
      if (res.status === 'FUNDS_SECURED') setStep('FUNDS_SECURED');
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur de paiement.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    if (!txId || !file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await transactionService.uploadDocument(txId, file);
      if (res.status === 'COMPLETED') setStep('COMPLETED');
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur OCR.");
      setStep('DISPUTED');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ background: 'var(--bg-elevated)', borderRadius: 'var(--radius-card)', border: '1px solid var(--border-subtle)', padding: 32, maxWidth: 600, margin: '0 auto' }}>
      
      {error && (
        <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)', padding: 16, borderRadius: 'var(--radius-button)', marginBottom: 24, display: 'flex', gap: 12 }}>
          <AlertTriangle size={24} />
          {error}
        </div>
      )}

      {/* Étapes Visuelles */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 40, position: 'relative' }}>
        <div style={{ position: 'absolute', top: 20, left: 30, right: 30, height: 2, background: 'var(--border-subtle)', zIndex: 0 }} />
        
        <StepIcon icon={<Lock />} active={step !== 'INIT'} label="Paiement" />
        <StepIcon icon={<ShieldCheck />} active={step === 'FUNDS_SECURED' || step === 'COMPLETED'} label="Sécurisé" />
        <StepIcon icon={<FileCheck />} active={step === 'COMPLETED'} label="Transfert" />
        <StepIcon icon={<CheckCircle />} active={step === 'COMPLETED'} label="Libéré" />
      </div>

      {/* Contenu de l'étape actuelle */}
      {step === 'INIT' && (
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.5rem', marginBottom: 16 }}>Acheter ce véhicule</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>Vos fonds seront bloqués sur un compte séquestre sécurisé (Escrow) jusqu'à la signature de la cession.</p>
          <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'Inter', marginBottom: 24 }}>
            {new Intl.NumberFormat('fr-MA').format(price)} MAD
          </div>
          <button className="btn btn--primary" onClick={handleInitiate} disabled={loading} style={{ width: '100%', padding: 16, fontSize: '1.1rem' }}>
            {loading ? 'Création du compte...' : 'Initier le paiement sécurisé'}
          </button>
        </div>
      )}

      {step === 'PENDING' && (
        <div style={{ textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.5rem', marginBottom: 16 }}>Paiement en attente</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>Veuillez procéder au paiement via notre partenaire (Simulation).</p>
          <button className="btn btn--secondary" onClick={handleSimulatePayment} disabled={loading} style={{ width: '100%', padding: 16, fontSize: '1.1rem' }}>
            {loading ? 'Validation...' : 'Simuler le succès du paiement (Webhook)'}
          </button>
        </div>
      )}

      {step === 'FUNDS_SECURED' && (
        <div style={{ textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', padding: 16, borderRadius: '50%', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-green)', marginBottom: 16 }}>
            <ShieldCheck size={48} />
          </div>
          <h3 style={{ fontSize: '1.5rem', marginBottom: 16 }}>Fonds Sécurisés par Wakala</h3>
          <p style={{ color: 'var(--text-secondary)', marginBottom: 24 }}>Le vendeur a été notifié. Pour libérer les fonds, le vendeur (ou vous) doit uploader le Certificat de Cession ou la Carte Grise barrée pour validation IA.</p>
          
          <div style={{ border: '1px dashed var(--border-subtle)', borderRadius: 'var(--radius-button)', padding: 24, marginBottom: 24 }}>
            <input type="file" id="docUpload" style={{ display: 'none' }} onChange={e => setFile(e.target.files?.[0] || null)} />
            <label htmlFor="docUpload" style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
              <UploadCloud size={32} color="var(--accent-gold)" />
              <span style={{ color: 'var(--text-primary)' }}>{file ? file.name : 'Sélectionner le document (JPG/PNG/PDF)'}</span>
            </label>
          </div>
          
          <button className="btn btn--primary" onClick={handleUpload} disabled={loading || !file} style={{ width: '100%', padding: 16, fontSize: '1.1rem' }}>
            {loading ? 'Analyse OCR en cours...' : 'Vérifier et Libérer les fonds'}
          </button>
        </div>
      )}

      {step === 'COMPLETED' && (
        <div style={{ textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', padding: 16, borderRadius: '50%', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-green)', marginBottom: 16 }}>
            <CheckCircle size={48} />
          </div>
          <h3 style={{ fontSize: '1.5rem', marginBottom: 16, color: 'var(--accent-green)' }}>Transaction Terminée !</h3>
          <p style={{ color: 'var(--text-secondary)' }}>L'Intelligence Artificielle a validé le transfert de propriété. Les fonds ont été libérés avec succès vers le compte du vendeur.</p>
        </div>
      )}

      {step === 'DISPUTED' && (
        <div style={{ textAlign: 'center' }}>
          <div style={{ display: 'inline-flex', padding: 16, borderRadius: '50%', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)', marginBottom: 16 }}>
            <AlertTriangle size={48} />
          </div>
          <h3 style={{ fontSize: '1.5rem', marginBottom: 16, color: 'var(--accent-red)' }}>Transaction Bloquée (Litige)</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Le document fourni ne correspond pas à l'identité du vendeur enregistré. Les fonds restent bloqués et notre équipe de modération a été alertée.</p>
        </div>
      )}
    </div>
  );
}

function StepIcon({ icon, active, label }: { icon: React.ReactNode, active: boolean, label: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8, zIndex: 1 }}>
      <div style={{ 
        width: 40, height: 40, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: active ? 'var(--accent-gold)' : 'var(--bg-surface)',
        color: active ? '#fff' : 'var(--text-muted)',
        border: `2px solid ${active ? 'var(--accent-gold)' : 'var(--border-subtle)'}`,
        transition: 'all 0.3s ease'
      }}>
        {React.cloneElement(icon as React.ReactElement, { size: 20 })}
      </div>
      <span style={{ fontSize: '0.8rem', color: active ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: active ? 600 : 400 }}>{label}</span>
    </div>
  );
}
