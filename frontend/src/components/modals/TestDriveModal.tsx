import React, { useState, useEffect } from 'react';
import { newCatalogService, ShowroomItem } from '../../services/newCatalogService';
import './TestDriveModal.css';

interface TestDriveModalProps {
  isOpen: boolean;
  onClose: () => void;
  trimId: string;
  vehicleName: string;
  brandName?: string;
}

export const TestDriveModal: React.FC<TestDriveModalProps> = ({
  isOpen,
  onClose,
  trimId,
  vehicleName,
  brandName
}) => {
  const [fullName, setFullName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [email, setEmail] = useState('');
  const [city, setCity] = useState('Casablanca');
  const [showrooms, setShowrooms] = useState<ShowroomItem[]>([]);
  const [selectedShowroom, setSelectedShowroom] = useState<string>('');
  const [preferredDate, setPreferredDate] = useState('');
  const [cndpConsent, setCndpConsent] = useState(true);
  const [loading, setLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const CITIES = ['Casablanca', 'Rabat', 'Tanger', 'Marrakech', 'Fès', 'Agadir', 'Oujda', 'Kénitra'];

  useEffect(() => {
    if (isOpen) {
      setSuccessMsg(null);
      setErrorMsg(null);
      loadShowrooms(city);
    }
  }, [isOpen, city, brandName]);

  const loadShowrooms = async (selectedCity: string) => {
    try {
      const data = await newCatalogService.getShowrooms({ city: selectedCity, brand: brandName });
      setShowrooms(data);
      if (data.length > 0) {
        setSelectedShowroom(data[0].id);
      } else {
        setSelectedShowroom('');
      }
    } catch (err) {
      console.error('Failed to load showrooms', err);
    }
  };

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    if (!cndpConsent) {
      setErrorMsg("Le consentement CNDP est obligatoire pour transmettre votre demande.");
      return;
    }

    setLoading(true);
    try {
      const res = await newCatalogService.bookTestDrive({
        trim_id: trimId,
        showroom_id: selectedShowroom || undefined,
        full_name: fullName,
        phone_number: phoneNumber,
        email: email || undefined,
        city: city,
        preferred_date: preferredDate || undefined,
        cndp_consent_accepted: true
      });
      setSuccessMsg(res.message);
    } catch (err: any) {
      const msg = err.response?.data?.detail || "Une erreur est survenue lors de l'enregistrement de votre demande.";
      setErrorMsg(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="test-drive-modal-overlay" onClick={onClose}>
      <div className="test-drive-modal-container" onClick={(e) => e.stopPropagation()}>
        <button className="test-drive-modal-close" onClick={onClose} aria-label="Fermer">
          &times;
        </button>

        <div className="test-drive-modal-header">
          <div className="test-drive-badge">Showroom Officiel Maroc</div>
          <h2>Réserver un Essai sur Route</h2>
          <p className="test-drive-subtitle">
            Essayez gratuitement la <strong>{vehicleName}</strong> dans votre concessionnaire agréé le plus proche.
          </p>
        </div>

        {successMsg ? (
          <div className="test-drive-success-card">
            <div className="success-icon">✓</div>
            <h3>Demande Confirmée !</h3>
            <p>{successMsg}</p>
            <button className="btn-primary" onClick={onClose}>
              Fermer
            </button>
          </div>
        ) : (
          <form className="test-drive-form" onSubmit={handleSubmit}>
            {errorMsg && <div className="test-drive-error-banner">{errorMsg}</div>}

            <div className="form-group">
              <label>Nom et Prénom *</label>
              <input
                type="text"
                required
                placeholder="Ex: Karim Benjelloun"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Numéro de Téléphone (Maroc) *</label>
                <input
                  type="tel"
                  required
                  placeholder="06 61 23 45 67"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Email (optionnel)</label>
                <input
                  type="email"
                  placeholder="karim@gmail.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Ville *</label>
                <select value={city} onChange={(e) => setCity(e.target.value)}>
                  {CITIES.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Date souhaitée</label>
                <input
                  type="date"
                  value={preferredDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={(e) => setPreferredDate(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Showroom / Concessionnaire de rattachement</label>
              <select
                value={selectedShowroom}
                onChange={(e) => setSelectedShowroom(e.target.value)}
              >
                {showrooms.length > 0 ? (
                  showrooms.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} — {s.address}
                    </option>
                  ))
                ) : (
                  <option value="">Concessionnaire agréé {city} (affectation automatique)</option>
                )}
              </select>
            </div>

            <div className="cndp-consent-box">
              <label className="cndp-checkbox-label">
                <input
                  type="checkbox"
                  checked={cndpConsent}
                  onChange={(e) => setCndpConsent(e.target.checked)}
                />
                <span>
                  J'accepte que mes coordonnées soient transmises au concessionnaire agréé pour organiser cet essai. Données protégées conformément à la <strong>Loi n° 09-08 de la CNDP</strong>.
                </span>
              </label>
            </div>

            <div className="test-drive-modal-actions">
              <button type="button" className="btn-secondary" onClick={onClose}>
                Annuler
              </button>
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Envoi en cours...' : 'Confirmer mon Essai Gratuit'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
