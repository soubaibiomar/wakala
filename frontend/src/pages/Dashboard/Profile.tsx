import { useState, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Camera, Save, Lock, User, Mail, AlertCircle } from 'lucide-react';
import { BentoGrid, BentoWidget } from '../../components/dashboard/BentoGrid';
import api from '../../services/api';

export default function Profile() {
  const { user, updateUser } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.full_name || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const getAvatarUrl = (url?: string) => {
    if (!url) return undefined;
    if (url.startsWith('http')) return url;
    const baseUrl = import.meta.env.VITE_API_URL || '/api';
    return `${baseUrl.replace('/api', '')}${url}`;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.put('/users/me', {
        full_name: formData.name,
        email: formData.email
      });
      updateUser(response.data);
      alert('Profil mis à jour avec succès');
    } catch (error) {
      console.error('Erreur lors de la mise à jour:', error);
      alert('Erreur lors de la mise à jour du profil');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const formDataUpload = new FormData();
      formDataUpload.append('file', file);
      setLoading(true);
      try {
        const response = await api.post('/users/me/avatar', formDataUpload, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        updateUser(response.data);
        alert('Photo de profil mise à jour');
      } catch (error) {
        console.error('Erreur lors de la mise à jour de la photo:', error);
        alert('Erreur lors de la mise à jour de la photo');
      } finally {
        setLoading(false);
      }
    }
  };

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.newPassword !== formData.confirmPassword) {
      alert('Les nouveaux mots de passe ne correspondent pas');
      return;
    }
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
      setFormData(prev => ({ ...prev, currentPassword: '', newPassword: '', confirmPassword: '' }));
      alert('Mot de passe mis à jour');
    }, 1000);
  };

  return (
    <div>
      <h1 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '8px' }}>
        Mon Profil
      </h1>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: '24px' }}>
        Gérez vos informations personnelles et vos paramètres de sécurité.
      </p>

      <BentoGrid>
        <BentoWidget title="Informations Personnelles" colSpan={2}>
          <div style={{ display: 'flex', gap: '30px', alignItems: 'flex-start', flexWrap: 'wrap', marginTop: '10px' }}>
            {/* Avatar */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '15px' }}>
              <div 
                style={{ 
                  width: '120px', 
                  height: '120px', 
                  borderRadius: '50%', 
                  backgroundColor: 'var(--color-bg)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  position: 'relative',
                  overflow: 'hidden',
                  border: '2px dashed var(--color-border)'
                }}
              >
                {user?.avatar_url ? (
                  <img 
                    src={getAvatarUrl(user.avatar_url)} 
                    alt="Profile" 
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }} 
                  />
                ) : (
                  <User size={50} color="var(--color-text-muted)" />
                )}
                <button 
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    background: 'rgba(0,0,0,0.5)',
                    color: 'white',
                    border: 'none',
                    padding: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'center'
                  }}
                >
                  <Camera size={16} />
                </button>
              </div>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileChange} 
                accept="image/*" 
                style={{ display: 'none' }} 
              />
              <span style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>Changer la photo</span>
            </div>

            {/* Form */}
            <form onSubmit={handleUpdateProfile} style={{ flex: 1, minWidth: '300px', width: '100%' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
                <label style={{ fontWeight: 600, fontSize: '0.95rem' }}>Nom complet</label>
                <div style={{ position: 'relative' }}>
                  <User size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    style={{ 
                      width: '100%', 
                      padding: '12px 12px 12px 40px', 
                      borderRadius: 'var(--radius-md)', 
                      border: '1px solid var(--color-border)', 
                      backgroundColor: 'transparent',
                      color: 'var(--color-text)'
                    }}
                    required
                  />
                </div>
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
                <label style={{ fontWeight: 600, fontSize: '0.95rem' }}>Adresse email</label>
                <div style={{ position: 'relative' }}>
                  <Mail size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    style={{ 
                      width: '100%', 
                      padding: '12px 12px 12px 40px', 
                      borderRadius: 'var(--radius-md)', 
                      border: '1px solid var(--color-border)', 
                      backgroundColor: 'transparent',
                      color: 'var(--color-text)'
                    }}
                    required
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
                <button type="submit" className="btn btn--primary" disabled={loading}>
                  <Save size={18} style={{ marginRight: '8px' }} />
                  Sauvegarder les modifications
                </button>
              </div>
            </form>
          </div>
        </BentoWidget>

        <BentoWidget title="Sécurité et Mot de passe" colSpan={1}>
          <div style={{ padding: '15px', backgroundColor: 'rgba(174, 140, 78, 0.1)', border: '1px solid var(--color-accent)', borderRadius: 'var(--radius-md)', marginBottom: '20px', display: 'flex', gap: '10px', alignItems: 'center', marginTop: '10px' }}>
            <AlertCircle size={24} color="var(--color-accent)" />
            <span style={{ fontSize: '0.9rem' }}>Pour modifier votre mot de passe, vous devez entrer votre mot de passe actuel.</span>
          </div>

          <form onSubmit={handleUpdatePassword} style={{ maxWidth: '500px', width: '100%' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
              <label style={{ fontWeight: 600, fontSize: '0.95rem' }}>Mot de passe actuel</label>
              <input
                type="password"
                name="currentPassword"
                value={formData.currentPassword}
                onChange={handleChange}
                style={{ 
                  width: '100%', 
                  padding: '12px', 
                  borderRadius: 'var(--radius-md)', 
                  border: '1px solid var(--color-border)', 
                  backgroundColor: 'transparent',
                  color: 'var(--color-text)'
                }}
                required
              />
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
              <label style={{ fontWeight: 600, fontSize: '0.95rem' }}>Nouveau mot de passe</label>
              <input
                type="password"
                name="newPassword"
                value={formData.newPassword}
                onChange={handleChange}
                style={{ 
                  width: '100%', 
                  padding: '12px', 
                  borderRadius: 'var(--radius-md)', 
                  border: '1px solid var(--color-border)', 
                  backgroundColor: 'transparent',
                  color: 'var(--color-text)'
                }}
                required
                minLength={8}
              />
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
              <label style={{ fontWeight: 600, fontSize: '0.95rem' }}>Confirmer le nouveau mot de passe</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                style={{ 
                  width: '100%', 
                  padding: '12px', 
                  borderRadius: 'var(--radius-md)', 
                  border: '1px solid var(--color-border)', 
                  backgroundColor: 'transparent',
                  color: 'var(--color-text)'
                }}
                required
                minLength={8}
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-start', marginTop: '20px' }}>
              <button type="submit" className="btn btn--outline" disabled={loading}>
                <Lock size={18} style={{ marginRight: '8px' }} />
                Mettre à jour le mot de passe
              </button>
            </div>
          </form>
        </BentoWidget>

        {/* Widget Statut & Rôle du compte */}
        <BentoWidget title="Statut du Compte" colSpan={3}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '16px',
            padding: '16px 0 8px 0',
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.95rem', fontWeight: 600 }}>Rôle actuel :</span>
                <span style={{
                  background: user?.role === 'seller' ? 'rgba(52, 211, 153, 0.15)' : 'rgba(174, 140, 78, 0.2)',
                  color: user?.role === 'seller' ? '#34d399' : '#d4af37',
                  padding: '4px 12px',
                  borderRadius: '20px',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  textTransform: 'uppercase',
                  border: user?.role === 'seller' ? '1px solid rgba(52, 211, 153, 0.3)' : '1px solid rgba(174, 140, 78, 0.4)'
                }}>
                  {user?.role === 'seller' ? 'Vendeur' : user?.role === 'admin' ? 'Administrateur' : 'Acheteur'}
                </span>
              </div>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.9rem', margin: 0, maxWidth: '650px' }}>
                {user?.role === 'seller' 
                  ? 'Vous disposez d\'un compte vendeur actif vous permettant de déposer des annonces et de gérer vos ventes.'
                  : 'Votre compte est actuellement configuré en mode Acheteur. Vous pouvez passer au statut Vendeur pour publier des annonces automobiles sur Wakala.'}
              </p>
            </div>

            {user?.role === 'buyer' && (
              <button
                type="button"
                onClick={async () => {
                  if (window.confirm('Voulez-vous passer au statut Vendeur et débloquer la publication d\'annonces ?')) {
                    try {
                      setLoading(true);
                      const response = await api.post('/users/me/become-seller');
                      updateUser(response.data);
                      alert('Félicitations ! Vous êtes désormais Vendeur sur Wakala.');
                    } catch (error) {
                      console.error('Erreur:', error);
                      alert('Impossible de changer de statut pour le moment.');
                    } finally {
                      setLoading(false);
                    }
                  }
                }}
                disabled={loading}
                style={{
                  background: 'linear-gradient(135deg, #ae8c4e 0%, #d4af37 100%)',
                  color: '#fff',
                  border: 'none',
                  padding: '10px 20px',
                  borderRadius: '8px',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  boxShadow: '0 4px 12px rgba(174, 140, 78, 0.35)',
                }}
              >
                ✨ Devenir Vendeur
              </button>
            )}
          </div>
        </BentoWidget>
      </BentoGrid>
    </div>
  );
}
