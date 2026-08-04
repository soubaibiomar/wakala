import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { favoriteService } from '../../services/favoriteService';
import { Vehicle } from '../../types/vehicle';
import VehicleCard from '../../components/vehicle-card/VehicleCard';

export default function Favorites() {
  const [favorites, setFavorites] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    favoriteService.getFavorites()
      .then(setFavorites)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div style={{ padding: 'var(--space-xl)', textAlign: 'center' }}>Chargement...</div>;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ padding: 'var(--space-xl)', maxWidth: 'var(--max-width, 1280px)', margin: '0 auto' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xl)' }}>
        <div>
          <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: 8 }}>
            Mes Véhicules Enregistrés
          </h1>
          <p style={{ color: 'var(--text-secondary)' }}>
            Retrouvez ici tous les véhicules que vous avez mis en favoris.
          </p>
        </div>
      </div>

      {favorites.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)', border: '1px solid var(--border-subtle)' }}>
          <p style={{ fontSize: '3rem', marginBottom: 16 }}>❤️</p>
          <h3 style={{ fontSize: '1.2rem', marginBottom: 8, color: 'var(--text-primary)' }}>Aucun véhicule enregistré</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Vous n'avez pas encore ajouté de véhicule à vos favoris.</p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: 'var(--space-lg)'
        }}>
          {favorites.map((vehicle) => (
            <VehicleCard key={vehicle.id} vehicle={vehicle} />
          ))}
        </div>
      )}
    </motion.div>
  );
}
