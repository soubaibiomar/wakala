import { useState } from 'react';
import { BentoGrid, BentoWidget } from '../../components/dashboard/BentoGrid';
import { AiStatusWidget } from '../../components/dashboard/widgets/AiStatusWidget';
import { ArgusQuickWidget } from '../../components/dashboard/widgets/ArgusQuickWidget';
import { RecentActivityWidget } from '../../components/dashboard/widgets/RecentActivityWidget';
import { Sparkles, Car, TrendingUp, ShieldCheck, ArrowRight, CheckCircle2, X } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { authService } from '../../services/authService';

export default function BuyerDashboard() {
  const { user, updateUser } = useAuth();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleBecomeSeller = async () => {
    setLoading(true);
    setError(null);
    try {
      const updatedUser = await authService.becomeSeller();
      updateUser(updatedUser);
      setIsModalOpen(false);
    } catch (err: any) {
      console.error('Erreur lors du passage au statut vendeur:', err);
      setError(err?.response?.data?.detail || 'Une erreur est survenue. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* En-tête avec bouton d'action Devenir Vendeur */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
        gap: '16px',
        marginBottom: '24px'
      }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '8px' }}>
            Tableau de bord Acheteur
          </h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            Bienvenue dans votre espace Wakala. Trouvez votre prochaine voiture avec l'IA.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: 'linear-gradient(135deg, #ae8c4e 0%, #d4af37 100%)',
            color: '#fff',
            border: 'none',
            padding: '12px 20px',
            borderRadius: '10px',
            fontWeight: 600,
            fontSize: '0.95rem',
            cursor: 'pointer',
            boxShadow: '0 4px 14px rgba(174, 140, 78, 0.35)',
            transition: 'all 0.2s ease',
          }}
          onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-2px)';
            e.currentTarget.style.boxShadow = '0 6px 18px rgba(174, 140, 78, 0.45)';
          }}
          onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 4px 14px rgba(174, 140, 78, 0.35)';
          }}
        >
          <Sparkles size={18} />
          <span>Devenir Vendeur</span>
        </button>
      </div>

      {/* Bannière d'incitation Devenir Vendeur */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(174, 140, 78, 0.12) 0%, rgba(26, 35, 50, 0.6) 100%)',
        border: '1px solid rgba(174, 140, 78, 0.3)',
        borderRadius: '14px',
        padding: '20px 24px',
        marginBottom: '28px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '20px',
      }}>
        <div style={{ maxWidth: '600px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span style={{
              background: 'rgba(174, 140, 78, 0.25)',
              color: '#d4af37',
              fontSize: '0.75rem',
              fontWeight: 700,
              padding: '3px 10px',
              borderRadius: '20px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              Nouveau
            </span>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, margin: 0, color: 'var(--color-text-primary)' }}>
              Vous souhaitez vendre un véhicule ?
            </h3>
          </div>
          <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.92rem', margin: 0, lineHeight: 1.5 }}>
            Passez au statut vendeur en 1 clic pour déposer vos annonces, estimer votre prix avec l'IA Argus et négocier directement avec les acheteurs.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: 'var(--color-accent, #ae8c4e)',
            color: '#fff',
            border: 'none',
            padding: '10px 18px',
            borderRadius: '8px',
            fontWeight: 600,
            fontSize: '0.9rem',
            cursor: 'pointer',
            transition: 'background 0.2s',
          }}
        >
          <span>Commencer à vendre</span>
          <ArrowRight size={16} />
        </button>
      </div>

      {/* Grille principale des widgets */}
      <BentoGrid>
        <AiStatusWidget />
        <RecentActivityWidget />
        <ArgusQuickWidget />
      </BentoGrid>

      {/* Modal Devenir Vendeur */}
      {isModalOpen && (
        <div style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '20px',
        }}>
          <div style={{
            background: '#161b22',
            border: '1px solid rgba(174, 140, 78, 0.4)',
            borderRadius: '16px',
            maxWidth: '520px',
            width: '100%',
            padding: '28px',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5)',
            position: 'relative',
            color: '#fff',
          }}>
            {/* Bouton fermer */}
            <button
              onClick={() => setIsModalOpen(false)}
              style={{
                position: 'absolute',
                top: '16px',
                right: '16px',
                background: 'transparent',
                border: 'none',
                color: '#8b949e',
                cursor: 'pointer',
                padding: '4px',
              }}
            >
              <X size={20} />
            </button>

            {/* En-tête modal */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '18px' }}>
              <div style={{
                width: '48px',
                height: '48px',
                borderRadius: '12px',
                background: 'rgba(174, 140, 78, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#d4af37',
              }}>
                <Car size={24} />
              </div>
              <div>
                <h2 style={{ fontSize: '1.35rem', fontWeight: 700, margin: 0 }}>
                  Devenir Vendeur Wakala
                </h2>
                <p style={{ color: '#8b949e', fontSize: '0.88rem', margin: '4px 0 0 0' }}>
                  Débloquez tous les outils de vente automobile
                </p>
              </div>
            </div>

            {/* Avantages */}
            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              borderRadius: '12px',
              padding: '16px',
              marginBottom: '20px',
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
            }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <CheckCircle2 size={18} color="#d4af37" style={{ marginTop: '2px', flexShrink: 0 }} />
                <div>
                  <strong style={{ fontSize: '0.92rem' }}>Publication d'annonces illimitée</strong>
                  <p style={{ margin: '2px 0 0 0', color: '#8b949e', fontSize: '0.82rem' }}>
                    Publiez vos voitures avec photos HD et fiches techniques certifiées.
                  </p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <CheckCircle2 size={18} color="#d4af37" style={{ marginTop: '2px', flexShrink: 0 }} />
                <div>
                  <strong style={{ fontSize: '0.92rem' }}>Estimation Argus IA & Santé d'annonce</strong>
                  <p style={{ margin: '2px 0 0 0', color: '#8b949e', fontSize: '0.82rem' }}>
                    Optimisez votre prix de vente grâce à notre modèle d'évaluation de marché en temps réel.
                  </p>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
                <CheckCircle2 size={18} color="#d4af37" style={{ marginTop: '2px', flexShrink: 0 }} />
                <div>
                  <strong style={{ fontSize: '0.92rem' }}>Gestion des offres & Négociations</strong>
                  <p style={{ margin: '2px 0 0 0', color: '#8b949e', fontSize: '0.82rem' }}>
                    Recevez et acceptez directement les propositions des acheteurs intéressés.
                  </p>
                </div>
              </div>
            </div>

            {error && (
              <div style={{
                background: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: '#f87171',
                padding: '10px 14px',
                borderRadius: '8px',
                fontSize: '0.88rem',
                marginBottom: '16px',
              }}>
                {error}
              </div>
            )}

            {/* Actions */}
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => setIsModalOpen(false)}
                disabled={loading}
                style={{
                  background: 'transparent',
                  border: '1px solid #30363d',
                  color: '#c9d1d9',
                  padding: '10px 18px',
                  borderRadius: '8px',
                  fontWeight: 600,
                  cursor: 'pointer',
                }}
              >
                Annuler
              </button>

              <button
                onClick={handleBecomeSeller}
                disabled={loading}
                style={{
                  background: 'linear-gradient(135deg, #ae8c4e 0%, #d4af37 100%)',
                  color: '#fff',
                  border: 'none',
                  padding: '10px 22px',
                  borderRadius: '8px',
                  fontWeight: 600,
                  cursor: loading ? 'not-allowed' : 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 12px rgba(174, 140, 78, 0.4)',
                }}
              >
                {loading ? 'Activation en cours...' : 'Confirmer et Devenir Vendeur'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
