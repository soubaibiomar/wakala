import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { CheckCircle2, ChevronRight, ChevronLeft, UploadCloud, AlertCircle } from 'lucide-react';
import { vehicleService } from '../../services/vehicleService';
import { listingService } from '../../services/listingService';
import { pricingService, PricePredictionResult } from '../../services/pricingService';

const BRANDS = ['Renault', 'Peugeot', 'Dacia', 'Volkswagen', 'Hyundai', 'Kia', 'BMW', 'Mercedes-Benz'];
const FUEL_TYPES = ['essence', 'diesel', 'hybride', 'electrique'];
const BODY_TYPES = ['citadine', 'berline', 'suv', 'break', 'utilitaire'];

export default function NewListing() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form Data
  const [formData, setFormData] = useState({
    brand: '',
    model: '',
    year: new Date().getFullYear(),
    mileage: 0,
    fuel_type: 'diesel',
    body_type: 'berline',
    city: 'Casablanca',
    price: 0,
    description: '',
    images_urls: [] as string[]
  });

  const [imgUrlInput, setImgUrlInput] = useState('');
  const [pricePrediction, setPricePrediction] = useState<PricePredictionResult | null>(null);

  const handleNext = async () => {
    setError(null);
    if (step === 2) {
      // Fetch AI price estimation
      try {
        setLoading(true);
        const prediction = await pricingService.predict({
          brand: formData.brand,
          model: formData.model,
          year: formData.year,
          mileage: formData.mileage,
          fuel_type: formData.fuel_type,
          body_type: formData.body_type,
          city: formData.city
        });
        setPricePrediction(prediction);
        if (formData.price === 0) {
          setFormData(prev => ({ ...prev, price: Math.round(prediction.predicted_price) }));
        }
        setStep(3);
      } catch (err) {
        console.error('Erreur prix AI', err);
        setError("Erreur lors de l'estimation IA. Veuillez définir un prix manuellement.");
        setStep(3); // Proceed anyway
      } finally {
        setLoading(false);
      }
    } else {
      setStep(step + 1);
    }
  };

  const handlePrev = () => setStep(step - 1);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setError(null);
      // 1. Create Vehicle
      const vehicle = await vehicleService.createVehicle({
        brand: formData.brand,
        model: formData.model,
        year: formData.year,
        mileage: formData.mileage,
        fuel_type: formData.fuel_type as any,
        body_type: formData.body_type as any,
        transmission: 'manuelle', // Simplification
        doors: 5,
        seats: 5,
        city: formData.city,
        price: formData.price,
        description: formData.description
      });

      // 2. Create Listing
      await listingService.createListing({
        vehicle_id: vehicle.id,
        status: 'active',
        images_urls: formData.images_urls.length > 0 ? formData.images_urls : undefined
      });

      // 3. Success
      setStep(4);
    } catch (err) {
      console.error(err);
      setError('Erreur lors de la création de votre annonce.');
    } finally {
      setLoading(false);
    }
  };

  const addImageUrl = () => {
    if (imgUrlInput && !formData.images_urls.includes(imgUrlInput)) {
      setFormData(prev => ({ ...prev, images_urls: [...prev.images_urls, imgUrlInput] }));
      setImgUrlInput('');
    }
  };

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', paddingBottom: '3rem' }}>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 'bold' }}>Déposer une annonce</h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>Vendez votre véhicule rapidement au meilleur prix estimé par notre IA.</p>
      </div>

      {/* Stepper */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '40px' }}>
        {[1, 2, 3].map(i => (
          <div key={i} style={{ flex: 1, height: '4px', background: step >= i ? 'var(--color-accent)' : 'var(--color-bg)', borderRadius: '2px', transition: '0.3s' }} />
        ))}
      </div>

      <div style={{ background: 'var(--color-surface)', borderRadius: '16px', padding: '32px', boxShadow: '0 4px 20px rgba(0,0,0,0.05)', border: '1px solid var(--color-border)' }}>
        
        {error && (
          <div style={{ background: 'rgba(231, 76, 60, 0.1)', color: '#e74c3c', padding: '16px', borderRadius: '8px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 style={{ fontSize: '1.4rem', marginBottom: '24px', fontWeight: 600 }}>1. Photos & Description</h2>
              
              <div style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Photos (URLs)</label>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <input
                    type="url"
                    placeholder="https://exemple.com/photo.jpg"
                    value={imgUrlInput}
                    onChange={(e) => setImgUrlInput(e.target.value)}
                    style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--color-border)', outline: 'none' }}
                  />
                  <button onClick={addImageUrl} className="btn btn--outline" type="button">Ajouter</button>
                </div>
                
                {formData.images_urls.length > 0 && (
                  <div style={{ display: 'flex', gap: '12px', marginTop: '16px', overflowX: 'auto' }}>
                    {formData.images_urls.map((url, i) => (
                      <div key={i} style={{ position: 'relative', width: '100px', height: '70px', borderRadius: '8px', overflow: 'hidden' }}>
                        <img src={url} alt={`Preview ${i}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        <button 
                          onClick={() => setFormData(prev => ({ ...prev, images_urls: prev.images_urls.filter((_, idx) => idx !== i) }))}
                          style={{ position: 'absolute', top: 4, right: 4, background: 'rgba(0,0,0,0.5)', color: '#fff', border: 'none', borderRadius: '50%', width: 24, height: 24, cursor: 'pointer' }}
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                {formData.images_urls.length === 0 && (
                  <div style={{ marginTop: '16px', padding: '32px', border: '2px dashed var(--color-border)', borderRadius: '8px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                    <UploadCloud size={40} style={{ margin: '0 auto 8px auto' }} />
                    <p>Ajoutez l'URL de votre photo ci-dessus</p>
                  </div>
                )}
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Description</label>
                <textarea
                  rows={4}
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Décrivez l'état général, les options, l'historique d'entretien..."
                  style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--color-border)', outline: 'none', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '32px' }}>
                <button onClick={handleNext} className="btn btn--primary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  Suivant <ChevronRight size={18} />
                </button>
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 style={{ fontSize: '1.4rem', marginBottom: '24px', fontWeight: 600 }}>2. Caractéristiques</h2>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Marque</label>
                  <select
                    value={formData.brand}
                    onChange={(e) => setFormData(prev => ({ ...prev, brand: e.target.value }))}
                    style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--color-border)', outline: 'none' }}
                  >
                    <option value="">Sélectionnez...</option>
                    {BRANDS.map(b => <option key={b} value={b}>{b}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Modèle</label>
                  <input
                    type="text"
                    value={formData.model}
                    onChange={(e) => setFormData(prev => ({ ...prev, model: e.target.value }))}
                    placeholder="Ex: Clio 4"
                    style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--color-border)', outline: 'none' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Année</label>
                  <input
                    type="number"
                    value={formData.year}
                    onChange={(e) => setFormData(prev => ({ ...prev, year: parseInt(e.target.value) || 2020 }))}
                    style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--color-border)', outline: 'none' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Kilométrage (km)</label>
                  <input
                    type="number"
                    value={formData.mileage}
                    onChange={(e) => setFormData(prev => ({ ...prev, mileage: parseInt(e.target.value) || 0 }))}
                    style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--color-border)', outline: 'none' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Carburant</label>
                  <select
                    value={formData.fuel_type}
                    onChange={(e) => setFormData(prev => ({ ...prev, fuel_type: e.target.value }))}
                    style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--color-border)', outline: 'none' }}
                  >
                    {FUEL_TYPES.map(b => <option key={b} value={b}>{b}</option>)}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Carrosserie</label>
                  <select
                    value={formData.body_type}
                    onChange={(e) => setFormData(prev => ({ ...prev, body_type: e.target.value }))}
                    style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--color-border)', outline: 'none' }}
                  >
                    {BODY_TYPES.map(b => <option key={b} value={b}>{b}</option>)}
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
                <button onClick={handlePrev} className="btn btn--outline" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ChevronLeft size={18} /> Précédent
                </button>
                <button 
                  onClick={handleNext} 
                  disabled={loading || !formData.brand || !formData.model} 
                  className="btn btn--primary" 
                  style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                >
                  {loading ? 'Estimation...' : 'Estimer le prix'} <ChevronRight size={18} />
                </button>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div key="step3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <h2 style={{ fontSize: '1.4rem', marginBottom: '24px', fontWeight: 600 }}>3. Prix & Publication</h2>
              
              {pricePrediction && (
                <div style={{ background: 'linear-gradient(135deg, rgba(174, 140, 78, 0.1) 0%, rgba(174, 140, 78, 0.05) 100%)', padding: '24px', borderRadius: '12px', marginBottom: '24px', border: '1px solid rgba(174, 140, 78, 0.2)' }}>
                  <h3 style={{ fontSize: '1.1rem', marginBottom: '8px', color: 'var(--color-accent)' }}>Estimation Argus IA</h3>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginBottom: '8px' }}>
                    <span style={{ fontSize: '2rem', fontWeight: 'bold' }}>
                      {Math.round(pricePrediction.predicted_price).toLocaleString('fr-FR')} MAD
                    </span>
                    <span style={{ color: 'var(--color-text-muted)' }}>Prix recommandé</span>
                  </div>
                  <p style={{ fontSize: '0.85rem', color: 'var(--color-text-secondary)' }}>
                    Fourchette de confiance : {Math.round(pricePrediction.confidence_interval.low).toLocaleString('fr-FR')} - {Math.round(pricePrediction.confidence_interval.high).toLocaleString('fr-FR')} MAD. 
                    Tendance marché : <strong>{pricePrediction.market_trend}</strong>.
                  </p>
                </div>
              )}

              <div style={{ marginBottom: '32px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>Votre Prix de vente (MAD)</label>
                <input
                  type="number"
                  value={formData.price}
                  onChange={(e) => setFormData(prev => ({ ...prev, price: parseInt(e.target.value) || 0 }))}
                  style={{ width: '100%', padding: '16px', fontSize: '1.2rem', fontWeight: 'bold', borderRadius: '8px', border: '2px solid var(--color-accent)', outline: 'none' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
                <button onClick={handlePrev} className="btn btn--outline" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ChevronLeft size={18} /> Précédent
                </button>
                <button 
                  onClick={handleSubmit} 
                  disabled={loading || formData.price <= 0} 
                  className="btn btn--primary" 
                  style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                >
                  {loading ? 'Publication...' : 'Publier mon annonce'}
                </button>
              </div>
            </motion.div>
          )}

          {step === 4 && (
            <motion.div key="step4" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} style={{ textAlign: 'center', padding: '40px 20px' }}>
              <CheckCircle2 size={64} style={{ color: '#2ecc71', margin: '0 auto 24px auto' }} />
              <h2 style={{ fontSize: '1.8rem', marginBottom: '16px', fontWeight: 600 }}>Annonce publiée !</h2>
              <p style={{ color: 'var(--color-text-secondary)', marginBottom: '32px' }}>
                Votre {formData.brand} {formData.model} est maintenant visible sur la plateforme. Notre IA analyse déjà votre annonce pour la recommander aux bons acheteurs.
              </p>
              <button 
                onClick={() => navigate('/dashboard/listings')} 
                className="btn btn--primary"
              >
                Voir mes annonces
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
