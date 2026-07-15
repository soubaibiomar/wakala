import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Shield } from 'lucide-react';
import TransactionFlow from '../components/transaction/TransactionFlow';
import api from '../services/api';

interface VehicleSummary {
  id: string;
  brand: string;
  model: string;
  price: number;
}

export default function TransactionPage() {
  const { id } = useParams<{ id: string }>(); // ID de l'annonce
  const navigate = useNavigate();
  const [vehicle, setVehicle] = useState<VehicleSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    api.get(`/v1/vehicles/${id}`)
      .then(res => setVehicle(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div style={{ padding: 100, textAlign: 'center' }}>Chargement...</div>;
  if (!vehicle) return <div style={{ padding: 100, textAlign: 'center' }}>Annonce introuvable.</div>;

  return (
    <div className="container" style={{ padding: '40px 20px', minHeight: '80vh' }}>
      
      <button 
        onClick={() => navigate(-1)} 
        style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', marginBottom: 32, fontSize: '1rem' }}
      >
        <ArrowLeft size={20} />
        Retour à l'annonce
      </button>

      <div style={{ textAlign: 'center', marginBottom: 40 }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 12, padding: '8px 24px', background: 'var(--bg-elevated)', border: '1px solid var(--border-subtle)', borderRadius: 100, marginBottom: 24 }}>
          <Shield size={20} color="var(--accent-gold)" />
          <span style={{ fontWeight: 500 }}>Transaction Sécurisée Wakala Escrow</span>
        </div>
        
        <h1 style={{ fontSize: '2.5rem', margin: '0 0 16px 0' }}>{vehicle.brand} {vehicle.model}</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Achetez en toute sérénité. Vos fonds sont bloqués jusqu'à la signature de la cession.</p>
      </div>

      <TransactionFlow listingId={vehicle.id} price={vehicle.price} />

    </div>
  );
}
