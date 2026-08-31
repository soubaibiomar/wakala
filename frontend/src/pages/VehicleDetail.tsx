import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Box, Sparkles, Compass, Scale, MapPin, CreditCard } from 'lucide-react';
import { vehicleService, reviewService } from '../services/vehicleService';
import { vehicleOptionsService, type VehicleConfiguratorData, type VehicleColorItem, type VehicleOptionItem } from '../services/vehicleOptionsService';
import { pricingService } from '../services/pricingService';
import { messageService } from '../services/messageService';
import { favoriteService } from '../services/favoriteService';
import { has3DModel } from '../components/configurator/model_registry';
import { ConfiguratorModal } from '../components/configurator/ConfiguratorModal';
import { TestDriveModal } from '../components/modals/TestDriveModal';

import { formatDistanceToNow } from 'date-fns';
import { fr as dateFnsFr } from 'date-fns/locale';
import type { Vehicle } from '../types/vehicle';
import type { Review } from '../types/listing';
import type { PricePredictionResult } from '../services/pricingService';
import { FUEL_LABELS, BODY_LABELS, TRANSMISSION_LABELS } from '../types/vehicle';
import { useAuth } from '../context/AuthContext';
import fr from '../i18n/fr';
import PriceBadge from '../components/pricing/PriceBadge';
import VehicleSEO from '../components/seo/VehicleSEO';
import VehicleStructuredData from '../components/seo/VehicleStructuredData';
import BreadcrumbStructuredData from '../components/seo/BreadcrumbStructuredData';
import FormattedDescription from '../components/formatted-description/FormattedDescription';

import './VehicleDetail.css';

function DetailSkeleton() {
  return (
    <div style={{ maxWidth: 'var(--max-width, 1280px)', margin: '0 auto', padding: 'var(--space-xl)' }}>
      <div className="vehicle-detail-grid">
        <div>
          <div style={{ height: 420, borderRadius: 'var(--radius-card)', marginBottom: 24, background: 'var(--bg-surface)' }} />
          <div style={{ height: 150, borderRadius: 'var(--radius-card)', background: 'var(--bg-surface)' }} />
        </div>
        <div style={{ height: 550, borderRadius: 'var(--radius-card)', background: 'var(--bg-surface)' }} />
      </div>
    </div>
  );
}

function DetailError({ message }: { message: string }) {
  return (
    <div style={{ maxWidth: 'var(--max-width, 1280px)', margin: '0 auto', textAlign: 'center', padding: '80px 24px' }}>
      <p style={{ fontSize: '3rem', marginBottom: 16 }}>⚠️</p>
      <h2 style={{ fontFamily: 'var(--font-display)', marginBottom: 8, color: 'var(--text-primary)' }}>{message}</h2>
      <Link to="/catalogue" style={{
        display: 'inline-flex', padding: '12px 24px', background: 'var(--accent-gold)',
        color: '#0f1a2b', borderRadius: 'var(--radius-pill)', fontWeight: 600,
        textDecoration: 'none', marginTop: 16,
      }}>
        {fr.general.back}
      </Link>
    </div>
  );
}

function ReviewsList({ reviews }: { reviews: Review[] }) {
  if (reviews.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      style={{
        padding: 'var(--space-lg)', marginTop: 'var(--space-lg)',
        background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
        border: '1px solid var(--border-subtle)',
      }}
    >
      <h3 style={{ fontSize: '1rem', fontFamily: 'var(--font-display)', fontWeight: 700, marginBottom: 16, color: 'var(--text-primary)' }}>
        Avis ({reviews.length})
      </h3>
      {reviews.map((r) => (
        <div key={r.id} style={{
          padding: '12px 0', borderBottom: '1px solid var(--border-subtle)',
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
            <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--accent-gold)' }}>
              {'★'.repeat(r.rating)}{'☆'.repeat(5 - r.rating)}
            </span>
            {r.sentiment_label && (
              <span style={{
                padding: '2px 8px', borderRadius: 'var(--radius-pill)',
                fontSize: '0.65rem', fontWeight: 600, textTransform: 'uppercase',
                background: r.sentiment_label === 'positive' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)',
                color: r.sentiment_label === 'positive' ? 'var(--accent-green)' : 'var(--accent-red)',
              }}>
                {r.sentiment_label}
              </span>
            )}
          </div>
          {r.title && <p style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: 4, color: 'var(--text-primary)' }}>{r.title}</p>}
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>{r.comment}</p>
          {r.author && (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 4, display: 'block' }}>
              — {r.author.name}
            </span>
          )}
        </div>
      ))}
    </motion.div>
  );
}

function SpecsGrid({ vehicle }: { vehicle: Vehicle }) {
  const specs = [
    { label: fr.vehicle.year, value: String(vehicle.year) },
    { label: fr.vehicle.mileage, value: "Neuf" },  // PIVOT: all vehicles are new
    { label: fr.vehicle.fuel, value: FUEL_LABELS[vehicle.fuel_type] || vehicle.fuel_type },
    { label: fr.vehicle.bodyType, value: BODY_LABELS[vehicle.body_type] || vehicle.body_type },
    { label: fr.vehicle.transmission, value: TRANSMISSION_LABELS[vehicle.transmission] || vehicle.transmission },
    { label: fr.vehicle.power, value: vehicle.engine_power_hp ? `${vehicle.engine_power_hp} ch` : '—' },
    { label: fr.vehicle.doors, value: String(vehicle.doors) },
    { label: fr.vehicle.seats, value: String(vehicle.seats) },
    { label: fr.vehicle.color, value: vehicle.color || '—' },
    { label: fr.vehicle.city, value: vehicle.city },
  ];

  return (
    <div style={{ marginTop: 20 }}>
      <h3 style={{
        fontSize: '0.85rem', fontFamily: 'var(--font-display)', fontWeight: 700,
        marginBottom: 12, color: 'var(--text-secondary)',
      }}>
        Aperçu Rapide
      </h3>
      <table className="vehicle-specs">
        <tbody>
          {specs.slice(0, 5).map((s) => (
            <tr key={s.label}>
              <th>{s.label}</th>
              <td>{s.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function DetailedTechSpecs({ vehicle }: { vehicle: Vehicle }) {
  const specs = [
    {
      category: "Informations Générales",
      items: [
        { label: "Marque", value: vehicle.brand },
        { label: "Modèle", value: vehicle.model },
        { label: "Année", value: String(vehicle.year) },
        { label: "Kilométrage", value: vehicle.mileage === 0 && vehicle.year >= new Date().getFullYear() - 2 ? "Neuf" : vehicle.mileage === 0 || vehicle.mileage === -1 || vehicle.mileage === undefined ? "N/C" : `${vehicle.mileage?.toLocaleString('fr-FR')} km` },
        { label: "Ville", value: vehicle.city },
        { label: "Condition", value: "Véhicule Neuf Garanti" },
      ]
    },
    {
      category: "Moteur & Performances",
      items: [
        { label: "Énergie", value: FUEL_LABELS[vehicle.fuel_type] || vehicle.fuel_type },
        { label: "Motorisation", value: vehicle.engine_type || "Thermique" },
        { label: "Puissance", value: vehicle.engine_power_hp ? `${vehicle.engine_power_hp} ch` : '—' },
        { label: "Boîte de vitesses", value: TRANSMISSION_LABELS[vehicle.transmission] || vehicle.transmission },
        { label: "Transmission 4x4", value: vehicle.is_4x4 ? "Oui (Intégrale 4WD/AWD)" : "Non (Traction/Propulsion)" },
      ]
    },
    {
      category: "Écologie & Sécurité",
      items: [
        { label: "Sécurité Crash-Test", value: vehicle.ncap_rating || "Non testé" },
        { label: "Consommation mixte", value: vehicle.fuel_consumption ? `${vehicle.fuel_consumption} L/100km` : '—' },
        { label: "Émissions CO2", value: vehicle.co2_emissions ? `${vehicle.co2_emissions} g/km` : '—' },
      ]
    },
    {
      category: "Carrosserie & Dimensions",
      items: [
        { label: "Type de carrosserie", value: BODY_LABELS[vehicle.body_type] || vehicle.body_type },
        { label: "Volume du coffre", value: vehicle.trunk_volume_l ? `${vehicle.trunk_volume_l} Litres` : '—' },
        { label: "Longueur hors-tout", value: vehicle.length_cm ? `${vehicle.length_cm} cm` : '—' },
        { label: "Nombre de portes", value: String(vehicle.doors) },
        { label: "Nombre de places", value: String(vehicle.seats) },
      ]
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.25 }}
      style={{
        padding: '32px',
        background: 'var(--bg-surface)',
        borderRadius: 'var(--radius-card)',
        border: '1px solid var(--border-subtle)',
        marginBottom: '32px',
        color: 'var(--text-primary)'
      }}
    >
      <h3 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-display)', fontWeight: 700, marginBottom: 20, color: 'var(--text-primary)' }}>
        Fiche Technique Complète & Homologation
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {specs.map((section) => (
          <div key={section.category}>
            <div style={{ 
              backgroundColor: 'var(--bg-elevated)',
              padding: '12px 18px',
              borderRadius: '8px',
              borderLeft: '4px solid var(--accent-gold)',
              marginBottom: '12px',
            }}>
              <h4 style={{ 
                fontSize: '1rem', 
                fontWeight: 700, 
                color: 'var(--text-primary)', 
                margin: 0
              }}>
                {section.category}
              </h4>
            </div>
            
            <div style={{ padding: '0 12px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.95rem' }}>
                <tbody>
                  {section.items.map((item) => (
                    <tr key={item.label} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                      <td style={{ padding: '12px 0', color: 'var(--text-secondary)', width: '45%', fontWeight: 500 }}>
                        {item.label}
                      </td>
                      <td style={{ padding: '12px 0', color: 'var(--text-primary)', fontWeight: 600 }}>
                        {item.value}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

function WakalaScoresSection({ scores }: { scores?: import('../services/vehicleOptionsService').VehicleWakalaScoreData | null }) {
  if (!scores || !scores.overall_score) return null;

  const scoreItems = [
    { label: "Espace à bord", score: scores.space_score, icon: "💺" },
    { label: "Sécurité", score: scores.safety_score, icon: "🛡️" },
    { label: "Coût réel d'usage", score: scores.real_cost_score, icon: "💰" },
    { label: "Prix d'accès", score: scores.access_price_score, icon: "🏷️" },
    { label: "Pratique en ville", score: scores.city_practicality_score, icon: "🏙️" },
    { label: "Performance", score: scores.performance_score, icon: "⚡" },
    { label: "Écologie & Conso", score: scores.ecology_score, icon: "🌿" },
    { label: "Tout terrain", score: scores.offroad_score, icon: "🏔️" },
  ].filter(item => item.score !== undefined && item.score !== null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.28 }}
      style={{
        padding: '28px',
        background: 'linear-gradient(135deg, rgba(200, 169, 106, 0.08), var(--bg-surface))',
        borderRadius: 'var(--radius-card)',
        border: '1px solid var(--accent-gold)',
        marginBottom: '32px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--accent-gold)', fontWeight: 700 }}>
            Évaluation Indépendante Wakala
          </span>
          <h3 style={{ fontSize: '1.3rem', fontFamily: 'var(--font-display)', fontWeight: 800, margin: '4px 0 0', color: 'var(--text-primary)' }}>
            Fiche de Vérité & Notes Experts
          </h3>
        </div>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8, padding: '8px 18px',
          background: 'var(--accent-gold)', color: '#0f1a2b',
          borderRadius: 'var(--radius-pill)', fontWeight: 800, fontSize: '1.2rem',
        }}>
          <span>★ {scores.overall_score.toFixed(1)} / 5</span>
        </div>
      </div>

      {scores.data_reliability && (
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 18, fontStyle: 'italic' }}>
          {scores.data_reliability}
        </p>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '14px', marginBottom: 20 }}>
        {scoreItems.map((item) => (
          <div key={item.label} style={{
            padding: '12px 16px', background: 'var(--bg-elevated)', borderRadius: '10px',
            border: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: 6
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>{item.icon} {item.label}</span>
              <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{item.score?.toFixed(1)} / 5</span>
            </div>
            <div style={{ width: '100%', height: 6, background: 'rgba(255,255,255,0.08)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{
                width: `${((item.score || 0) / 5) * 100}%`, height: '100%',
                background: (item.score || 0) >= 4 ? 'var(--accent-green, #10B981)' : (item.score || 0) >= 3 ? 'var(--accent-gold)' : '#F59E0B',
                borderRadius: 3
              }} />
            </div>
          </div>
        ))}
      </div>

      {scores.observations && (
        <div style={{ padding: '14px', background: 'var(--bg-elevated)', borderRadius: '8px', borderLeft: '3px solid var(--accent-gold)' }}>
          <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            <strong style={{ color: 'var(--text-primary)' }}>Constat officiel : </strong>
            {scores.observations}
          </p>
        </div>
      )}
    </motion.div>
  );
}

function VehicleConfiguratorSection({
  configData,
  selectedColor,
  setSelectedColor,
  selectedOptionIds,
  toggleOption,
  canConfigure3D,
  onOpen3D,
}: {
  configData: import('../services/vehicleOptionsService').VehicleConfiguratorData;
  selectedColor: import('../services/vehicleOptionsService').VehicleColorItem | null;
  setSelectedColor: (c: import('../services/vehicleOptionsService').VehicleColorItem) => void;
  selectedOptionIds: string[];
  toggleOption: (id: string) => void;
  canConfigure3D?: boolean;
  onOpen3D?: () => void;
}) {
  const categories = Object.keys(configData.options_by_category || {});
  const categoryLabels: Record<string, string> = {
    couleur: "Teintes de carrosserie",
    jante: "Jantes & Roues",
    sellerie: "Sellerie & Habitacle",
    pack: "Packs Technologie & Confort",
    accessoire: "Accessoires & Équipements",
  };

  const totalOptionsPrice = configData.options
    .filter(opt => selectedOptionIds.includes(opt.id))
    .reduce((sum, opt) => sum + opt.price_delta, 0);

  const colorPrice = selectedColor ? selectedColor.price_delta : 0;
  const totalPrice = configData.base_price + totalOptionsPrice + colorPrice;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.26 }}
      style={{
        padding: '32px',
        background: 'var(--bg-surface)',
        borderRadius: 'var(--radius-card)',
        border: '1px solid var(--border-subtle)',
        marginBottom: '32px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--accent-gold)', fontWeight: 700 }}>
            Configurateur en ligne
          </span>
          <h3 style={{ fontSize: '1.3rem', fontFamily: 'var(--font-display)', fontWeight: 800, margin: '4px 0 0', color: 'var(--text-primary)' }}>
            Personnalisez votre véhicule
          </h3>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {canConfigure3D && onOpen3D && (
            <button
              type="button"
              onClick={onOpen3D}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '10px 18px',
                borderRadius: 'var(--radius-pill)',
                background: 'linear-gradient(135deg, var(--accent-gold), #b89742)',
                color: '#000',
                fontWeight: 700,
                fontSize: '0.85rem',
                border: 'none',
                cursor: 'pointer',
                boxShadow: '0 4px 14px rgba(200, 169, 106, 0.35)',
              }}
            >
              <Box size={16} />
              <span>Studio 3D (360°)</span>
            </button>
          )}

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Prix configuré :</span>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-gold)' }}>
              {totalPrice.toLocaleString('fr-FR')} DH
            </div>
          </div>
        </div>
      </div>

      {/* 1. Sélecteur de Couleurs */}
      {configData.colors && configData.colors.length > 0 && (
        <div style={{ marginBottom: 28, padding: '20px', background: 'var(--bg-elevated)', borderRadius: '12px' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: 14, color: 'var(--text-primary)' }}>
            🎨 Coloris Carrosserie
          </h4>
          <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
            {configData.colors.map((color) => {
              const isSelected = selectedColor?.id === color.id;
              return (
                <button
                  key={color.id}
                  onClick={() => setSelectedColor(color)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10, padding: '8px 14px',
                    borderRadius: 'var(--radius-pill)', border: isSelected ? '2px solid var(--accent-gold)' : '1px solid var(--border-subtle)',
                    background: isSelected ? 'rgba(200, 169, 106, 0.12)' : 'var(--bg-surface)',
                    color: 'var(--text-primary)', cursor: 'pointer', transition: 'all 0.2s ease',
                  }}
                >
                  <span style={{
                    width: 20, height: 20, borderRadius: '50%', background: color.hex_code,
                    border: '2px solid rgba(255,255,255,0.4)', display: 'inline-block',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
                  }} />
                  <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>{color.color_name}</span>
                  <span style={{ fontSize: '0.75rem', color: color.price_delta > 0 ? 'var(--accent-gold)' : 'var(--text-muted)', fontWeight: 700 }}>
                    {color.price_delta > 0 ? `+${color.price_delta.toLocaleString('fr-FR')} DH` : 'Inclus'}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* 2. Options par Catégories */}
      {categories.map((catKey) => {
        const catOptions = configData.options_by_category[catKey] || [];
        if (catOptions.length === 0) return null;
        return (
          <div key={catKey} style={{ marginBottom: 24 }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12, color: 'var(--text-primary)' }}>
              {categoryLabels[catKey] || catKey.toUpperCase()}
            </h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 12 }}>
              {catOptions.map((opt) => {
                const isSelected = selectedOptionIds.includes(opt.id) || opt.is_default;
                return (
                  <div
                    key={opt.id}
                    onClick={() => !opt.is_default && toggleOption(opt.id)}
                    style={{
                      padding: '14px 16px', borderRadius: '10px',
                      border: isSelected ? '1px solid var(--accent-gold)' : '1px solid var(--border-subtle)',
                      background: isSelected ? 'rgba(200, 169, 106, 0.08)' : 'var(--bg-elevated)',
                      cursor: opt.is_default ? 'default' : 'pointer',
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        disabled={opt.is_default}
                        onChange={() => {}}
                        style={{ cursor: opt.is_default ? 'default' : 'pointer', accentColor: 'var(--accent-gold)' }}
                      />
                      <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {opt.name}
                      </span>
                    </div>
                    <span style={{
                      fontSize: '0.8rem', fontWeight: 700,
                      color: opt.is_default ? 'var(--text-muted)' : 'var(--accent-gold)',
                      whiteSpace: 'nowrap', marginLeft: 8,
                    }}>
                      {opt.is_default ? 'De série' : `+${opt.price_delta.toLocaleString('fr-FR')} DH`}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}

      {/* 3. Récapitulatif Total du Configurateur */}
      <div style={{
        marginTop: 24, padding: '16px 20px', background: 'var(--bg-elevated)',
        borderRadius: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        border: '1px dashed var(--accent-gold)', flexWrap: 'wrap', gap: 12
      }}>
        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          <div>Prix de base : <strong>{configData.base_price.toLocaleString('fr-FR')} DH</strong></div>
          {colorPrice > 0 && <div>Couleur ({selectedColor?.color_name}) : <strong>+{colorPrice.toLocaleString('fr-FR')} DH</strong></div>}
          {totalOptionsPrice > 0 && <div>Options sélectionnées : <strong>+{totalOptionsPrice.toLocaleString('fr-FR')} DH</strong></div>}
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Montant Clé en Main estimé :</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--accent-gold)' }}>
            {totalPrice.toLocaleString('fr-FR')} DH
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default function VehicleDetail() {
  const { id: routeId, brandName, modelName, versionSlug } = useParams<{ id?: string, brandName?: string, modelName?: string, versionSlug?: string }>();
  
  // Extrait le short ID de 8 caractères à la fin de l'URL pour les occasions (ex: renault-clio-2015-8d284cc3)
  const shortIdRegex = /-([0-9a-f]{8})$/i;
  // Ou l'ancien UUID pour compatibilité
  const uuidRegex = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  
  const extractedId = routeId ? (routeId.match(uuidRegex)?.[0] || routeId.match(shortIdRegex)?.[1] || routeId) : undefined;

  
  const { user, isAuthenticated } = useAuth();
  const [isFavorite, setIsFavorite] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);
  const [vehicle, setVehicle] = useState<Vehicle | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [marketPrice, setMarketPrice] = useState<PricePredictionResult | null>(null);
  
  // Offer modal state
  const [showOfferModal, setShowOfferModal] = useState(false);
  const [offerAmount, setOfferAmount] = useState('');
  const [offerMessage, setOfferMessage] = useState('');
  const [offerLoading, setOfferLoading] = useState(false);
  
  // Chat Modal State
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatMessage, setChatMessage] = useState('');
  const [chatSending, setChatSending] = useState(false);
  const [chatSuccess, setChatSuccess] = useState(false);
  
  const [priceLoading, setPriceLoading] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  // Configurator & Options state
  const [configData, setConfigData] = useState<VehicleConfiguratorData | null>(null);
  const [selectedColor, setSelectedColor] = useState<VehicleColorItem | null>(null);
  const [selectedOptionIds, setSelectedOptionIds] = useState<string[]>([]);
  const [isConfigurator3DOpen, setIsConfigurator3DOpen] = useState(false);
  const [isTestDriveOpen, setIsTestDriveOpen] = useState(false);

  const toggleOption = (id: string) => {
    setSelectedOptionIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const modelSlugOrId = vehicle ? `${vehicle.brand}-${vehicle.model}-${vehicle.version || ''}` : '';
  const canConfigure3D = vehicle ? (has3DModel(modelSlugOrId) || has3DModel(`${vehicle.brand}-${vehicle.model}`) || has3DModel(vehicle.model)) : false;

  useEffect(() => {
    if (!extractedId && !versionSlug) return;
    setLoading(true);
    setError(null);

    const fetchVehicle = brandName && modelName && versionSlug
      ? vehicleService.getVehicleBySlug(brandName, modelName, versionSlug)
      : vehicleService.getVehicleById(extractedId!);

    fetchVehicle
      .then((v) => {
        setVehicle(v);
        if (isAuthenticated) {
          favoriteService.getFavorites().then(favorites => {
            setIsFavorite(favorites.some(fav => fav.id === v.id));
          }).catch(console.error);
        }

        // Fetch options & configurator data additively
        vehicleOptionsService.getVehicleOptions(v.id)
          .then((cfg) => {
            setConfigData(cfg);
            if (cfg.colors && cfg.colors.length > 0) {
              const defColor = cfg.colors.find(c => c.is_default) || cfg.colors[0];
              setSelectedColor(defColor);
            }
            if (cfg.options) {
              const defOpts = cfg.options.filter(o => o.is_default).map(o => o.id);
              setSelectedOptionIds(defOpts);
            }
          })
          .catch(() => {});

        return reviewService.getReviews({ vehicle_id: v.id, limit: 10 }).catch(() => []);
      })
      .then((r) => {
        setReviews(r);
      })
      .catch((err) => {
        console.error('Erreur chargement véhicule:', err);
        setError(err.response?.status === 404 ? fr.error.notFound : fr.error.generic);
      })
      .finally(() => setLoading(false));
  }, [extractedId, versionSlug, brandName, modelName, isAuthenticated]);

  useEffect(() => {
    if (!vehicle) return;
    setPriceLoading(true);
    pricingService.predict({
      brand: vehicle.brand,
      model: vehicle.model,
      year: vehicle.year,
      mileage: vehicle.mileage,
      fuel_type: vehicle.fuel_type,
      body_type: vehicle.body_type,
      transmission: vehicle.transmission,
      engine_power_hp: vehicle.engine_power_hp ?? null,
      doors: vehicle.doors,
      seats: vehicle.seats,
      city: vehicle.city,
    })
      .then(setMarketPrice)
      .catch(() => { })
      .finally(() => setPriceLoading(false));
  }, [vehicle]);

  if (loading) return <DetailSkeleton />;
  if (error || !vehicle) return <DetailError message={error || fr.error.notFound} />;

  return (
    <>
      <VehicleSEO vehicle={vehicle} />
      <div style={{ background: 'var(--bg-primary)', minHeight: '100vh', paddingTop: 'calc(var(--nav-height) + var(--space-xl))' }}>
        <div style={{ maxWidth: 'var(--max-width, 1280px)', margin: '0 auto', padding: '0 var(--space-lg)' }}>
          <nav style={{ marginBottom: 'var(--space-lg)', fontSize: '0.85rem' }} aria-label="Fil d'Ariane">
            <Link to="/" style={{ color: 'var(--text-muted)' }}>{fr.nav.home}</Link>
            <span style={{ margin: '0 8px', color: 'var(--text-muted)' }}>/</span>
            <Link to="/catalogue" style={{ color: 'var(--text-muted)' }}>{fr.nav.catalogue}</Link>
            <span style={{ margin: '0 8px', color: 'var(--text-muted)' }}>/</span>
            <span style={{ color: 'var(--text-secondary)' }}>{vehicle.brand} {vehicle.model}</span>
          </nav>

          <div className="vehicle-detail-grid">
            <div>
              <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                style={{
                  height: 420,
                  background: 'linear-gradient(135deg, var(--bg-elevated), var(--bg-surface))',
                  borderRadius: 'var(--radius-card)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  border: '1px solid var(--border-subtle)', position: 'relative',
                  marginBottom: 'var(--space-lg)', overflow: 'hidden',
                }}
              >
                {vehicle.images && vehicle.images.length > 0 ? (
                  <>
                    <img src={vehicle.images[currentImageIndex].file_path} alt={vehicle.model} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    {vehicle.images.length > 1 && (
                      <div style={{ position: 'absolute', bottom: 16, right: 16, display: 'flex', gap: 8 }}>
                        <button onClick={() => setCurrentImageIndex(prev => (prev > 0 ? prev - 1 : vehicle.images!.length - 1))} style={{ padding: '8px 12px', background: 'rgba(0,0,0,0.6)', color: '#fff', border: 'none', borderRadius: 'var(--radius-pill)', cursor: 'pointer', fontFamily: 'var(--font-sans)', fontWeight: 600 }}>◀</button>
                        <button onClick={() => setCurrentImageIndex(prev => (prev < vehicle.images!.length - 1 ? prev + 1 : 0))} style={{ padding: '8px 12px', background: 'rgba(0,0,0,0.6)', color: '#fff', border: 'none', borderRadius: 'var(--radius-pill)', cursor: 'pointer', fontFamily: 'var(--font-sans)', fontWeight: 600 }}>▶</button>
                      </div>
                    )}
                    <div style={{ position: 'absolute', bottom: 16, left: 16, background: 'rgba(0,0,0,0.6)', color: 'white', padding: '4px 10px', borderRadius: 'var(--radius-pill)', fontSize: '0.8rem', fontWeight: 600 }}>
                      {currentImageIndex + 1} / {vehicle.images.length}
                    </div>
                  </>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: 0.4 }}>
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2" />
                      <circle cx="7" cy="17" r="2" />
                      <path d="M9 17h6" />
                      <circle cx="17" cy="17" r="2" />
                    </svg>
                    <span style={{ marginTop: 12, fontWeight: 600, fontSize: '0.9rem' }}>Image non disponible</span>
                  </div>
                )}

                <div style={{ position: 'absolute', top: 16, left: 16, display: 'flex' }}>
                    <span style={{
                      padding: '8px 14px', borderRadius: 'var(--radius-pill)',
                      fontSize: '0.8rem', fontWeight: 600,
                      background: 'rgba(217, 119, 6, 0.1)', color: '#d97706',
                      border: '1px solid rgba(217, 119, 6, 0.3)',
                      boxShadow: 'var(--shadow-sm)',
                    }}>
                      ✨ Neuf Maroc 2026 (0 km)
                    </span>
                </div>

                {canConfigure3D && (
                  <button
                    type="button"
                    onClick={() => setIsConfigurator3DOpen(true)}
                    style={{
                      position: 'absolute',
                      top: 16,
                      right: 16,
                      zIndex: 10,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      padding: '10px 18px',
                      borderRadius: 'var(--radius-pill)',
                      background: 'linear-gradient(135deg, rgba(200, 169, 106, 0.95), rgba(166, 134, 69, 0.95))',
                      color: '#000',
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      border: 'none',
                      cursor: 'pointer',
                      boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
                      backdropFilter: 'blur(6px)',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <Box size={17} />
                    <span>Configurer en 3D (360°)</span>
                  </button>
                )}

              </motion.div>

              {vehicle.description && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  style={{
                    padding: 'var(--space-lg)',
                    background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
                    border: '1px solid var(--border-subtle)', marginBottom: 'var(--space-lg)',
                  }}
                >
                  <h3 style={{ fontSize: '1.2rem', fontFamily: 'var(--font-display)', fontWeight: 700, marginBottom: 16, color: 'var(--text-primary)' }}>
                    Description & Fiche Technique
                  </h3>
                  <div className="markdown-content">
                    <FormattedDescription text={vehicle.description} />
                  </div>
                </motion.div>
              )}

              {configData && (configData.colors?.length > 0 || configData.options?.length > 0) && (
                <VehicleConfiguratorSection
                  configData={configData}
                  selectedColor={selectedColor}
                  setSelectedColor={setSelectedColor}
                  selectedOptionIds={selectedOptionIds}
                  toggleOption={toggleOption}
                  canConfigure3D={canConfigure3D}
                  onOpen3D={() => setIsConfigurator3DOpen(true)}
                />
              )}

              {configData?.wakala_scores && (
                <WakalaScoresSection scores={configData.wakala_scores} />
              )}

              <DetailedTechSpecs vehicle={vehicle} />

              <ReviewsList reviews={reviews} />
            </div>

            <div style={{ position: 'sticky', top: 'calc(var(--nav-height) + 24px)' }}>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5 }}
                style={{
                  padding: 'var(--space-xl)',
                  background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                <h1 style={{ fontSize: '1.6rem', fontFamily: 'var(--font-display)', fontWeight: 800, marginBottom: 4, color: 'var(--text-primary)' }}>
                  {vehicle.brand} {vehicle.model} - {vehicle.year}
                </h1>
                {vehicle.version && (
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: 8 }}>
                    {vehicle.version}
                  </p>
                )}

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: 4 }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--accent-gold)' }}>
                    {vehicle.price.toLocaleString('fr-FR')} {fr.vehicle.mad}
                  </div>
                </div>



                <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
                  <button
                    id="cta-contact-seller"
                    style={{
                      flex: 1, padding: '14px 24px', background: 'var(--accent-gold)',
                      color: '#0f1a2b', border: 'none', borderRadius: 'var(--radius-pill)',
                      fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer',
                    }}
                    onClick={() => {
                      if (!isAuthenticated) window.location.href = '/login';
                      else setIsChatOpen(true);
                    }}
                  >
                    {isAuthenticated ? fr.vehicle.contact : fr.auth.loginTitle}
                  </button>
                  
                  <button
                    onClick={() => setIsTestDriveOpen(true)}
                    style={{
                      flex: 1, padding: '14px 24px', background: 'transparent',
                      color: 'var(--text-primary)', border: '2px solid var(--accent-gold)', 
                      borderRadius: 'var(--radius-pill)',
                      fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer',
                      textAlign: 'center',
                    }}
                  >
                    Réserver un essai
                  </button>
                </div>


                <button
                  onClick={async () => {
                    if (!isAuthenticated) {
                      window.location.href = `/login?returnUrl=/vehicle/${vehicle.id}`;
                      return;
                    }
                    try {
                      setFavoriteLoading(true);
                      if (isFavorite) {
                        await favoriteService.removeFavorite(vehicle.id);
                        setIsFavorite(false);
                      } else {
                        await favoriteService.addFavorite(vehicle.id);
                        setIsFavorite(true);
                      }
                    } catch (error) {
                      console.error("Failed to toggle favorite:", error);
                    } finally {
                      setFavoriteLoading(false);
                    }
                  }}
                  disabled={favoriteLoading}
                  style={{
                    width: '100%', padding: '12px 24px', background: 'transparent',
                    color: isFavorite ? 'var(--accent-red)' : 'var(--text-secondary)', border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-pill)', fontWeight: 600, fontSize: '0.9rem',
                    cursor: favoriteLoading ? 'wait' : 'pointer',
                  }}>
                  {isFavorite ? '♥' : '♡'} {fr.general.save}
                </button>



                <SpecsGrid vehicle={vehicle} />
              </motion.div>
            </div>
          </div>

          {/* ─── CONTEXTUAL SEMANTIC MESH (SEO & GEO) ────────── */}
          <div style={{ marginTop: '40px', padding: '24px', background: 'var(--bg-surface)', borderRadius: 'var(--radius-card)', border: '1px solid var(--border-subtle)' }}>
            <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Compass size={18} color="var(--accent-gold)" /> Maillage Sémantique &amp; Univers {vehicle.brand}
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px' }}>
              <Link
                to={`/marque/${vehicle.brand.toLowerCase()}`}
                style={{ padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', border: '1px solid var(--border-subtle)', textDecoration: 'none', color: 'var(--text-primary)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <Sparkles size={15} color="var(--accent-gold)" />
                <span>Tous les modèles <strong>{vehicle.brand}</strong></span>
              </Link>

              <Link
                to="/comparateur"
                style={{ padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', border: '1px solid var(--border-subtle)', textDecoration: 'none', color: 'var(--text-primary)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <Scale size={15} color="#60a5fa" />
                <span>Comparer ce véhicule</span>
              </Link>

              <Link
                to={`/voitures-neuves/${(vehicle.city || 'casablanca').toLowerCase()}`}
                style={{ padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', border: '1px solid var(--border-subtle)', textDecoration: 'none', color: 'var(--text-primary)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <MapPin size={15} color="#ef4444" />
                <span>Concessions à {vehicle.city || 'Maroc'}</span>
              </Link>

              <Link
                to="/financement-auto-maroc"
                style={{ padding: '12px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: '10px', border: '1px solid var(--border-subtle)', textDecoration: 'none', color: 'var(--text-primary)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}
              >
                <CreditCard size={15} color="#a855f7" />
                <span>Calculer vos mensualités</span>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Offer Modal */}
      {showOfferModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000 }}>
          <div style={{ background: 'var(--bg-surface)', padding: 32, borderRadius: 'var(--radius-card)', width: 400, border: '1px solid var(--border-subtle)' }}>
            <h3 style={{ margin: '0 0 16px 0' }}>Faire une offre</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 24, fontSize: '0.9rem' }}>Proposez un prix au vendeur. Si l'offre est acceptée, vous pourrez finaliser la transaction.</p>
            
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', marginBottom: 8, fontWeight: 600, fontSize: '0.9rem' }}>Votre prix (DH)</label>
              <input 
                type="number" 
                value={offerAmount} 
                onChange={e => setOfferAmount(e.target.value)}
                style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-input)', border: '1px solid var(--border-subtle)', background: 'var(--bg-elevated)', color: 'white', fontSize: '1.1rem', fontWeight: 600 }}
              />
            </div>
            
            <div style={{ marginBottom: 24 }}>
              <label style={{ display: 'block', marginBottom: 8, fontWeight: 600, fontSize: '0.9rem' }}>Message (optionnel)</label>
              <textarea 
                value={offerMessage} 
                onChange={e => setOfferMessage(e.target.value)}
                rows={3}
                placeholder="Ex: Je suis très intéressé, paiement comptant."
                style={{ width: '100%', padding: '12px 16px', borderRadius: 'var(--radius-input)', border: '1px solid var(--border-subtle)', background: 'var(--bg-elevated)', color: 'white' }}
              />
            </div>
            
            <div style={{ display: 'flex', gap: 12 }}>
              <button 
                onClick={() => setShowOfferModal(false)}
                style={{ flex: 1, padding: '12px', background: 'transparent', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-pill)', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                Annuler
              </button>
              <button 
                onClick={async () => {
                  try {
                    setOfferLoading(true);
                    const { offerService } = await import('../services/offerService');
                    await offerService.createOffer({
                      vehicle_id: vehicle.id,
                      amount: Number(offerAmount),
                      message: offerMessage
                    });
                    setShowOfferModal(false);
                    alert("Offre envoyée avec succès ! Vous pouvez la suivre dans votre tableau de bord.");
                  } catch (e: any) {
                    alert(e.response?.data?.detail || "Erreur lors de l'envoi de l'offre.");
                  } finally {
                    setOfferLoading(false);
                  }
                }}
                disabled={offerLoading || !offerAmount}
                style={{ flex: 1, padding: '12px', background: 'var(--accent-gold)', border: 'none', borderRadius: 'var(--radius-pill)', color: '#111827', fontWeight: 600, cursor: offerLoading ? 'wait' : 'pointer' }}>
                {offerLoading ? 'Envoi...' : 'Envoyer l\'offre'}
              </button>
            </div>
          </div>
        </div>
      )}

      <AnimatePresence>
        {isChatOpen && vehicle?.seller && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{
              position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
              background: 'rgba(0,0,0,0.8)', zIndex: 9999,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              padding: 20
            }}
            onClick={() => setIsChatOpen(false)}
          >
            <motion.div
              initial={{ y: 20, scale: 0.95 }}
              animate={{ y: 0, scale: 1 }}
              exit={{ y: 20, scale: 0.95 }}
              style={{
                background: 'var(--bg-primary)',
                borderRadius: 'var(--radius-card)',
                width: '100%', maxWidth: '400px',
                padding: '24px',
                boxShadow: '0 10px 40px rgba(0,0,0,0.5)'
              }}
              onClick={e => e.stopPropagation()}
            >
              <h3 style={{ margin: '0 0 16px 0', fontSize: '1.2rem' }}>
                Contacter {vehicle.seller.name || vehicle.seller.full_name}
              </h3>
              {chatSuccess ? (
                <div style={{ color: 'var(--accent-green)', textAlign: 'center', padding: '20px 0' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '10px' }}>✓</div>
                  Votre message a été envoyé avec succès. Le vendeur vous répondra dans votre Espace Messagerie.
                  <button onClick={() => setIsChatOpen(false)} style={{ marginTop: '20px', width: '100%', padding: '12px', background: 'var(--bg-elevated)', color: 'var(--text-primary)', border: 'none', borderRadius: 'var(--radius-pill)', cursor: 'pointer' }}>
                    Fermer
                  </button>
                </div>
              ) : (
                <form onSubmit={async (e) => {
                  e.preventDefault();
                  if (!chatMessage.trim()) return;
                  setChatSending(true);
                  try {
                    await messageService.sendMessage({
                      recipient_id: vehicle.seller!.id,
                      listing_id: vehicle.id, // Assuming listing ID is same as vehicle ID for this mock or closely related
                      content: chatMessage
                    });
                    setChatSuccess(true);
                  } catch(err) {
                    console.error(err);
                    alert("Erreur lors de l'envoi du message.");
                  } finally {
                    setChatSending(false);
                  }
                }}>
                  <textarea
                    value={chatMessage}
                    onChange={e => setChatMessage(e.target.value)}
                    placeholder={`Bonjour, je suis intéressé par votre ${vehicle.brand} ${vehicle.model}...`}
                    rows={5}
                    style={{
                      width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-subtle)',
                      background: 'var(--bg-elevated)', color: 'var(--text-primary)', outline: 'none', resize: 'vertical',
                      marginBottom: '16px'
                    }}
                    required
                  />
                  <div style={{ display: 'flex', gap: '12px' }}>
                    <button type="button" onClick={() => setIsChatOpen(false)} style={{ flex: 1, padding: '12px', background: 'transparent', border: '1px solid var(--border-subtle)', color: 'var(--text-primary)', borderRadius: 'var(--radius-pill)', cursor: 'pointer' }}>
                      Annuler
                    </button>
                    <button type="submit" disabled={chatSending || !chatMessage.trim()} style={{ flex: 1, padding: '12px', background: 'var(--accent-gold)', border: 'none', color: '#0f1a2b', fontWeight: 600, borderRadius: 'var(--radius-pill)', cursor: 'pointer', opacity: (chatSending || !chatMessage.trim()) ? 0.5 : 1 }}>
                      {chatSending ? 'Envoi...' : 'Envoyer'}
                    </button>
                  </div>
                </form>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Modale de Configuration 3D Studio */}
      {vehicle && (
        <ConfiguratorModal
          isOpen={isConfigurator3DOpen}
          onClose={() => setIsConfigurator3DOpen(false)}
          vehicleIdOrSlug={modelSlugOrId}
          vehicleName={`${vehicle.brand} ${vehicle.model}${vehicle.version ? ` - ${vehicle.version}` : ''}`}
          basePrice={vehicle.price}
          availableColors={configData?.colors}
          availableOptions={configData?.options}
          optionsByCategory={configData?.options_by_category}
          onApplyConfiguration={(total, col, opts) => {
            if (col) setSelectedColor(col);
            if (opts) setSelectedOptionIds(opts.map(o => o.id));
          }}
        />
      )}

      {/* Modale de Réservation d'Essai sur Route */}
      {vehicle && (
        <TestDriveModal
          isOpen={isTestDriveOpen}
          onClose={() => setIsTestDriveOpen(false)}
          trimId={vehicle.id}
          vehicleName={`${vehicle.brand} ${vehicle.model}`}
          brandName={vehicle.brand}
        />
      )}
    </>
  );
}
