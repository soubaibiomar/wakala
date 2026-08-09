import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Trophy } from 'lucide-react';
import { recommendationService, RecommendationResult, Top3Response } from '../../services/recommendationService';
import { vehicleService } from '../../services/vehicleService';
import { Vehicle } from '../../types/vehicle';
import VehicleCard from '../../components/vehicle-card/VehicleCard';
import Top3Recommendations from '../../components/recommendation/Top3Recommendations';
import { useAuth } from '../../context/AuthContext';

interface RecommendedVehicle extends Vehicle {
  match_score?: number;
  key_facts?: string[];
  budget_margin?: number | null;
  best_version_name?: string | null;
}

export default function Recommendations() {
  const { user } = useAuth();
  const [recommendedVehicles, setRecommendedVehicles] = useState<RecommendedVehicle[]>([]);
  const [top3Data, setTop3Data] = useState<Top3Response | null>(null);
  const [loading, setLoading] = useState(true);
  const [methodUsed, setMethodUsed] = useState<string>('');

  useEffect(() => {
    if (!user) return;

    const fetchRecommendations = async () => {
      try {
        setLoading(true);

        // 1. Fetch Top 3 Wakala
        try {
          const top3Res = await recommendationService.getTop3({
            query: 'voiture recommandée',
            user_id: user.id,
          });
          setTop3Data(top3Res);
        } catch (e) {
          console.warn('Top3 fetch fallback:', e);
        }

        // 2. Call recommendation API
        const response = await recommendationService.search({
          user_id: user.id,
          page_size: 6,
        });
        
        setMethodUsed(response.method);

        // Fetch full vehicle details for each recommendation
        const vehiclesPromises = response.items.map(async (item: RecommendationResult) => {
          try {
            const v = await vehicleService.getVehicleById(item.vehicle_id);
            return {
              ...v,
              match_score: item.match_score,
              key_facts: item.key_facts,
              budget_margin: item.budget_margin,
              best_version_name: item.best_version_name,
            } as RecommendedVehicle;
          } catch (e) {
            return null;
          }
        });

        const vehicles = (await Promise.all(vehiclesPromises)).filter(v => v !== null) as RecommendedVehicle[];
        setRecommendedVehicles(vehicles);
      } catch (error) {
        console.error('Failed to fetch recommendations:', error);
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
        <div style={{ color: 'var(--text-muted)' }}>Génération de votre classement certifié Wakala...</div>
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
          Sélection "Pour Vous" (Algorithme Wakala)
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          Notation transparente basée sur notre formule à 3 ingrédients (57% Qualité, 25% Budget, 18% Pratique) avec preuves factuelles chiffrées.
        </p>
        
        {methodUsed === 'cold-start' && (
          <div style={{ background: 'var(--bg-surface)', padding: '12px 16px', borderRadius: '8px', borderLeft: '4px solid var(--accent-gold)', marginTop: 16, fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            <strong>Nouveau ici ?</strong> Les recommandations actuelles sont calibrées sur les meilleurs modèles du marché marocain. En interagissant avec les modèles, vos poids se personnaliseront automatiquement !
          </div>
        )}
      </div>

      {/* ─── Top 3 Wakala Section ─────────────────────────────── */}
      {top3Data && top3Data.items.length > 0 && (
        <Top3Recommendations data={top3Data} />
      )}

      <h2 style={{ fontSize: '1.3rem', fontWeight: 700, margin: '32px 0 16px 0', color: 'var(--text-primary)' }}>
        Toutes vos suggestions personnalisées
      </h2>

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
              matchScore={vehicle.match_score ? Math.round(vehicle.match_score) : undefined}
              keyFacts={vehicle.key_facts}
              budgetMargin={vehicle.budget_margin}
              bestVersionName={vehicle.best_version_name}
            />
          ))}
        </div>
      )}
    </motion.div>
  );
}

