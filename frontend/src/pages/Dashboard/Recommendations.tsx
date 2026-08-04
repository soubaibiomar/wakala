import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { recommendationService, RecommendationResult } from '../../services/recommendationService';
import { vehicleService } from '../../services/vehicleService';
import { Vehicle } from '../../types/vehicle';
import VehicleCard from '../../components/vehicle-card/VehicleCard';
import { useAuth } from '../../context/AuthContext';

interface RecommendedVehicle extends Vehicle {
  match_score?: number;
}

export default function Recommendations() {
  const { user } = useAuth();
  const [recommendedVehicles, setRecommendedVehicles] = useState<RecommendedVehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [methodUsed, setMethodUsed] = useState<string>('');

  useEffect(() => {
    if (!user) return;

    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        // Call recommendation API
        const response = await recommendationService.search({
          user_id: user.id,
          page_size: 6
        });
        
        setMethodUsed(response.method);

        // Fetch full vehicle details for each recommendation
        const vehiclesPromises = response.items.map(async (item: RecommendationResult) => {
          try {
            const v = await vehicleService.getVehicleById(item.vehicle_id);
            return {
              ...v,
              match_score: item.match_score
            } as RecommendedVehicle;
          } catch (e) {
            return null;
          }
        });

        const vehicles = (await Promise.all(vehiclesPromises)).filter(v => v !== null) as RecommendedVehicle[];
        setRecommendedVehicles(vehicles);
      } catch (error) {
        console.error("Failed to fetch recommendations:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [user]);

  if (loading) {
    return (
      <div style={{ padding: 'var(--space-xl)', textAlign: 'center', height: '50vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
        <div className="spinner" style={{
          width: 40, height: 40, border: '3px solid var(--border-subtle)',
          borderTopColor: 'var(--accent-gold)', borderRadius: '50%', animation: 'spin 1s linear infinite', marginBottom: 16
        }} />
        <div style={{ color: 'var(--text-muted)' }}>Génération de vos recommandations sur mesure...</div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ padding: 'var(--space-xl)', maxWidth: 'var(--max-width, 1280px)', margin: '0 auto' }}
    >
      <div style={{ marginBottom: 'var(--space-xl)' }}>
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', marginBottom: 8, display: 'flex', alignItems: 'center', gap: 12 }}>
          <Sparkles color="var(--accent-gold)" /> 
          Sélection "Pour Vous"
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Grâce à l'Intelligence Artificielle de Wakala, découvrez les véhicules qui correspondent le mieux à vos goûts et à vos recherches précédentes.
        </p>
        
        {methodUsed === 'cold-start' && (
          <div style={{ background: 'var(--bg-surface)', padding: '12px 16px', borderRadius: '8px', borderLeft: '4px solid var(--accent-gold)', marginTop: 16, fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            <strong>Nouveau ici ?</strong> Les recommandations actuelles sont générales car nous n'avons pas encore assez d'informations sur vos préférences. Mettez des véhicules en favoris pour affiner vos recommandations !
          </div>
        )}
      </div>

      {recommendedVehicles.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)', border: '1px solid var(--border-subtle)' }}>
          <p style={{ color: 'var(--text-secondary)' }}>Nous n'avons pas trouvé de recommandations pour le moment.</p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: 'var(--space-lg)'
        }}>
          {recommendedVehicles.map((vehicle) => (
            <VehicleCard 
              key={vehicle.id} 
              vehicle={vehicle} 
              matchScore={vehicle.match_score ? Math.round(vehicle.match_score * 100) : undefined} 
            />
          ))}
        </div>
      )}
    </motion.div>
  );
}
