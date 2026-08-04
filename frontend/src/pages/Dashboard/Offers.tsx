import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { offerService, Offer } from '../../services/offerService';
import { useAuth } from '../../context/AuthContext';
import { Check, X, Clock, MessageSquare, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Offers() {
  const { user } = useAuth();
  const [sentOffers, setSentOffers] = useState<Offer[]>([]);
  const [receivedOffers, setReceivedOffers] = useState<Offer[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'sent' | 'received'>('sent');

  const fetchOffers = async () => {
    try {
      setLoading(true);
      const [sent, received] = await Promise.all([
        offerService.getSentOffers(),
        offerService.getReceivedOffers()
      ]);
      setSentOffers(sent);
      setReceivedOffers(received);
    } catch (error) {
      console.error("Erreur lors de la récupération des offres:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchOffers();
    }
  }, [user]);

  const handleUpdateStatus = async (offerId: string, status: 'accepted' | 'rejected') => {
    try {
      await offerService.updateOfferStatus(offerId, status);
      await fetchOffers();
    } catch (error) {
      console.error("Erreur lors de la mise à jour de l'offre:", error);
      alert("Une erreur s'est produite lors de la mise à jour.");
    }
  };

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'pending': return <span style={{ background: '#fef08a', color: '#854d0e', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}><Clock size={14}/> En attente</span>;
      case 'accepted': return <span style={{ background: '#bbf7d0', color: '#166534', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}><Check size={14}/> Acceptée</span>;
      case 'rejected': return <span style={{ background: '#fecaca', color: '#991b1b', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 4 }}><X size={14}/> Refusée</span>;
      default: return <span style={{ background: '#e5e7eb', color: '#374151', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 600 }}>{status}</span>;
    }
  };

  if (loading) {
    return <div style={{ padding: 'var(--space-xl)', textAlign: 'center' }}>Chargement des offres...</div>;
  }

  const displayedOffers = activeTab === 'sent' ? sentOffers : receivedOffers;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ padding: 'var(--space-xl)', maxWidth: 'var(--max-width, 1280px)', margin: '0 auto' }}
    >
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 12 }}>
          <MessageSquare color="var(--accent-gold)" /> 
          Mes Négociations
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Suivez vos offres d'achat envoyées et répondez aux offres reçues pour vos annonces.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 16, borderBottom: '1px solid var(--border-subtle)', marginBottom: 24 }}>
        <button 
          onClick={() => setActiveTab('sent')}
          style={{ 
            padding: '12px 16px', background: 'none', border: 'none', borderBottom: activeTab === 'sent' ? '2px solid var(--accent-gold)' : '2px solid transparent',
            color: activeTab === 'sent' ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: 600, cursor: 'pointer'
          }}
        >
          Offres Envoyées ({sentOffers.length})
        </button>
        {user?.role === 'seller' && (
          <button 
            onClick={() => setActiveTab('received')}
            style={{ 
              padding: '12px 16px', background: 'none', border: 'none', borderBottom: activeTab === 'received' ? '2px solid var(--accent-gold)' : '2px solid transparent',
              color: activeTab === 'received' ? 'var(--text-primary)' : 'var(--text-muted)', fontWeight: 600, cursor: 'pointer'
            }}
          >
            Offres Reçues ({receivedOffers.length})
          </button>
        )}
      </div>

      {displayedOffers.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)', border: '1px solid var(--border-subtle)' }}>
          <AlertCircle size={48} color="var(--border-subtle)" style={{ marginBottom: 16 }} />
          <p style={{ color: 'var(--text-secondary)' }}>
            {activeTab === 'sent' ? "Vous n'avez envoyé aucune offre pour le moment." : "Vous n'avez reçu aucune offre sur vos véhicules."}
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {displayedOffers.map((offer) => (
            <div key={offer.id} style={{ 
              background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', 
              borderRadius: 'var(--radius-card)', padding: 20, display: 'flex', flexDirection: 'column', gap: 16,
              boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ margin: '0 0 4px 0', fontSize: '1.1rem' }}>
                    Offre pour: <Link to={`/vehicule/${offer.vehicle_id}`} style={{ color: 'var(--accent-gold)', textDecoration: 'none' }}>
                      {offer.vehicle?.brand} {offer.vehicle?.model}
                    </Link>
                  </h3>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                    Le {new Date(offer.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
                {getStatusBadge(offer.status)}
              </div>
              
              <div style={{ display: 'flex', gap: 24, background: 'var(--bg-elevated)', padding: 16, borderRadius: '8px' }}>
                <div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Prix demandé</div>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                    {offer.vehicle?.price.toLocaleString('fr-FR')} DH
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{activeTab === 'sent' ? 'Votre offre' : 'Offre reçue'}</div>
                  <div style={{ fontWeight: 700, color: 'var(--accent-gold)', fontSize: '1.1rem' }}>
                    {offer.amount.toLocaleString('fr-FR')} DH
                  </div>
                </div>
              </div>

              {offer.message && (
                <div style={{ fontStyle: 'italic', color: 'var(--text-secondary)', borderLeft: '3px solid var(--border-subtle)', paddingLeft: 12 }}>
                  "{offer.message}"
                </div>
              )}

              {activeTab === 'received' && offer.status === 'pending' && (
                <div style={{ display: 'flex', gap: 12, marginTop: 8 }}>
                  <button 
                    onClick={() => handleUpdateStatus(offer.id, 'accepted')}
                    className="btn btn--primary" style={{ padding: '8px 16px', flex: 1, background: '#16a34a', border: 'none' }}>
                    Accepter l'offre
                  </button>
                  <button 
                    onClick={() => handleUpdateStatus(offer.id, 'rejected')}
                    className="btn btn--outline" style={{ padding: '8px 16px', flex: 1, color: '#dc2626', borderColor: '#dc2626' }}>
                    Refuser
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
