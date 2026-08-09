import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PlusCircle, Search, Edit3, Trash2, Eye, PauseCircle, PlayCircle } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { listingService } from '../../services/listingService';
import type { Listing } from '../../types/listing';

export default function SellerListings() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  const fetchListings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listingService.getMyListings(50, 0);
      setListings(data);
    } catch (err) {
      console.error('Erreur lors du chargement des annonces', err);
      setError('Impossible de charger vos annonces.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchListings();
  }, []);

  const handleToggleStatus = async (id: string, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'active' ? 'draft' : 'active';
      await listingService.updateListing(id, { status: newStatus as any });
      await fetchListings();
    } catch (err) {
      console.error('Erreur lors de la mise à jour', err);
    }
  };

  const filteredListings = listings.filter((l) =>
    (l.vehicle?.brand + ' ' + l.vehicle?.model).toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{ padding: '0 0 2rem 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 'bold', marginBottom: '8px' }}>
            Mes Annonces
          </h1>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            Gérez vos annonces, suivez vos vues et analysez vos performances.
          </p>
        </div>
        <button
          onClick={() => navigate('/dashboard/new-listing')}
          className="btn btn--primary"
          style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 20px' }}
        >
          <PlusCircle size={20} />
          <span>Déposer une annonce</span>
        </button>
      </div>

      <div style={{
        background: 'var(--color-surface)',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.05)',
        border: '1px solid var(--color-border)'
      }}>
        
        <div style={{ display: 'flex', alignItems: 'center', background: 'var(--color-bg)', padding: '10px 16px', borderRadius: '8px', marginBottom: '24px', maxWidth: '400px' }}>
          <Search size={18} style={{ color: 'var(--color-text-muted)', marginRight: '10px' }} />
          <input
            type="text"
            placeholder="Rechercher par marque ou modèle..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              border: 'none',
              background: 'transparent',
              outline: 'none',
              width: '100%',
              fontSize: '1rem',
              color: 'var(--color-text)'
            }}
          />
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-secondary)' }}>
            Chargement de vos annonces...
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '40px', color: 'red' }}>
            {error}
          </div>
        ) : filteredListings.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'var(--color-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-muted)' }}>
              🚗
            </div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>Aucune annonce trouvée</h3>
            <p style={{ color: 'var(--color-text-secondary)', maxWidth: '400px', margin: '0 auto' }}>
              Vous n'avez pas encore d'annonces ou votre recherche ne correspond à aucun véhicule.
            </p>
            <button
              onClick={() => navigate('/dashboard/new-listing')}
              className="btn btn--outline"
              style={{ marginTop: '16px' }}
            >
              Créer votre première annonce
            </button>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', minWidth: '700px', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '2px solid var(--color-bg)' }}>
                  <th style={{ padding: '12px 16px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>Véhicule</th>
                  <th style={{ padding: '12px 16px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>Prix</th>
                  <th style={{ padding: '12px 16px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>Statut</th>
                  <th style={{ padding: '12px 16px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>Vues</th>
                  <th style={{ padding: '12px 16px', color: 'var(--color-text-secondary)', fontWeight: 600 }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredListings.map((listing, i) => (
                  <motion.tr
                    key={listing.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    style={{ borderBottom: '1px solid var(--color-bg)' }}
                  >
                    <td style={{ padding: '16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ 
                          width: '60px', height: '40px', borderRadius: '6px', 
                          background: '#f0f0f0', overflow: 'hidden', flexShrink: 0 
                        }}>
                          {listing.images_urls?.[0] ? (
                            <img src={listing.images_urls[0]} alt="Car" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                          ) : (
                            <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#aaa', fontSize: '0.8rem' }}>No img</div>
                          )}
                        </div>
                        <div>
                          <div style={{ fontWeight: 600 }}>{listing.vehicle?.brand} {listing.vehicle?.model}</div>
                          <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>
                            {listing.vehicle?.year} • {listing.vehicle?.mileage} km
                          </div>
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '16px', fontWeight: 600 }}>
                      {listing.vehicle?.price.toLocaleString('fr-FR')} MAD
                    </td>
                    <td style={{ padding: '16px' }}>
                      <span style={{
                        display: 'inline-flex', alignItems: 'center', padding: '4px 8px',
                        borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600,
                        textTransform: 'uppercase',
                        background: listing.status === 'active' ? 'rgba(46, 204, 113, 0.1)' : 'rgba(231, 76, 60, 0.1)',
                        color: listing.status === 'active' ? '#2ecc71' : '#e74c3c'
                      }}>
                        {listing.status === 'active' ? 'En ligne' : listing.status}
                      </span>
                    </td>
                    <td style={{ padding: '16px', color: 'var(--color-text-secondary)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Eye size={16} /> {listing.view_count}
                      </div>
                    </td>
                    <td style={{ padding: '16px' }}>
                      <div style={{ display: 'flex', gap: '12px' }}>
                        <button
                          onClick={() => handleToggleStatus(listing.id, listing.status)}
                          title={listing.status === 'active' ? "Suspendre" : "Publier"}
                          style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--color-text-secondary)', padding: 0 }}
                        >
                          {listing.status === 'active' ? <PauseCircle size={18} /> : <PlayCircle size={18} />}
                        </button>
                        <button style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--color-text-secondary)', padding: 0 }}>
                          <Edit3 size={18} />
                        </button>
                        <button style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: '#e74c3c', padding: 0 }}>
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
