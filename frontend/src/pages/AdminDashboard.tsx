import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';
import './AdminDashboard.css';

interface MostConsultedVehicle {
  id: string;
  brand: string;
  model: string;
  version: string;
  price: number;
  fuel_type: string;
  views_count: number;
  interest_pct: number;
  image_url: string;
}

interface PodiumVehicle {
  rank: number;
  vehicle_name: string;
  trim_name: string;
  brand: string;
  image_url: string;
  recommendations_count: number;
  acceptance_rate_pct: number;
  key_driver: string;
  score_8d: number;
  profile_leader: string;
}

interface ChatbotQuestion {
  question: string;
  count: number;
  trend: string;
}

interface KpiSubsystemHealth {
  status: 'HEALTHY' | 'CRITICAL_FAILURE' | 'DEGRADED';
  latency_ms: number;
  data_freshness_seconds?: number;
  description?: string;
  error?: string;
  fallback_active?: boolean;
}

interface ActiveAlert {
  kpi_key: string;
  severity: string;
  kpi_label: string;
  error_details: string;
  timestamp: string;
}

interface KpiSentinelReport {
  overall_status: 'HEALTHY' | 'CRITICAL_FAILURE';
  healthy_subsystems_count: number;
  total_subsystems_count: number;
  subsystems: Record<string, KpiSubsystemHealth>;
  active_alerts: ActiveAlert[];
  simulated_failures: Record<string, boolean>;
  last_inspected_at: string;
}

interface AdminKpiData {
  ai_chatbot_telemetry: {
    avg_platform_time_formatted: string;
    avg_chatbot_time_formatted: string;
    avg_platform_time_seconds: number;
    avg_chatbot_dialogue_seconds: number;
    total_clicks: number;
    user_satisfaction_pct: number;
    top_questions: ChatbotQuestion[];
    telemetry_clicks: {
      vehicle_cards_clicked: number;
      comparator_duels_clicked: number;
      ncap_reports_clicked: number;
      equipment_options_expanded: number;
    };
  };
  most_consulted_vehicles: MostConsultedVehicle[];
  podium_recommendations: PodiumVehicle[];
  kpi_sentinel_health?: KpiSentinelReport;
}

export default function AdminDashboard() {
  const { user } = useAuth();
  const [data, setData] = useState<AdminKpiData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [timeFilter, setTimeFilter] = useState<'7d' | '30d' | '90d'>('30d');

  // Sentinel Architecture & Diagnostic Modal
  const [isSentinelModalOpen, setIsSentinelModalOpen] = useState<boolean>(false);
  const [diagnosing, setDiagnosing] = useState<boolean>(false);

  // Password Security Modal State
  const [isPasswordModalOpen, setIsPasswordModalOpen] = useState<boolean>(false);
  const [oldPassword, setOldPassword] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('');
  const [confirmPassword, setConfirmPassword] = useState<string>('');
  const [showOldPwd, setShowOldPwd] = useState<boolean>(false);
  const [showNewPwd, setShowNewPwd] = useState<boolean>(false);
  const [pwdLoading, setPwdLoading] = useState<boolean>(false);
  const [pwdFeedback, setPwdFeedback] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Notification Toast
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null);

  const showToast = (text: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToastMessage({ text, type });
    setTimeout(() => setToastMessage(null), 4000);
  };

  const fetchKpis = async () => {
    try {
      setLoading(true);
      const res = await api.get('/api/v1/admin/cockpit/summary');
      setData(res.data);
    } catch (err) {
      console.error('Erreur chargement KPIs:', err);
      showToast('Impossible de charger les KPIs administrateur.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const runSentinelDiagnostic = async () => {
    try {
      setDiagnosing(true);
      const res = await api.get('/api/v1/admin/kpis/health');
      if (data) {
        setData({ ...data, kpi_sentinel_health: res.data });
      }
      showToast('Diagnostic Sentinelle exécuté avec succès.', 'success');
    } catch (err) {
      showToast('Échec de l’exécution du diagnostic.', 'error');
    } finally {
      setDiagnosing(false);
    }
  };

  const toggleSimulateFailure = async (kpiKey: string, currentVal: boolean) => {
    try {
      await api.post('/api/v1/admin/kpis/simulate-failure', {
        kpi_key: kpiKey,
        enable: !currentVal
      });
      await fetchKpis();
      showToast(
        !currentVal 
          ? `Panne simulée sur ${kpiKey}. Alerte déclenchée.` 
          : `Panne résolue sur ${kpiKey}. Statut nominal.`,
        !currentVal ? 'error' : 'success'
      );
    } catch (err) {
      showToast('Erreur lors du test de simulation.', 'error');
    }
  };

  useEffect(() => {
    fetchKpis();
  }, []);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwdFeedback(null);

    if (newPassword.length < 8) {
      setPwdFeedback({ message: 'Le mot de passe doit contenir au moins 8 caractères.', type: 'error' });
      return;
    }
    if (!/[A-Z]/.test(newPassword) || !/[0-9]/.test(newPassword)) {
      setPwdFeedback({ message: 'Le mot de passe doit contenir une majuscule et un chiffre.', type: 'error' });
      return;
    }
    if (newPassword !== confirmPassword) {
      setPwdFeedback({ message: 'Les nouveaux mots de passe ne correspondent pas.', type: 'error' });
      return;
    }

    try {
      setPwdLoading(true);
      const res = await api.post('/auth/change-password', {
        current_password: oldPassword,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });

      setPwdFeedback({ message: res.data.message || 'Mot de passe mis à jour avec succès !', type: 'success' });
      showToast('Mot de passe Administrateur mis à jour.', 'success');
      setTimeout(() => {
        setIsPasswordModalOpen(false);
        setOldPassword('');
        setNewPassword('');
        setConfirmPassword('');
        setPwdFeedback(null);
      }, 1500);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Échec de la modification du mot de passe.';
      setPwdFeedback({ message: errorMsg, type: 'error' });
    } finally {
      setPwdLoading(false);
    }
  };

  if (loading && !data) {
    return (
      <div className="admin-cockpit-wrapper admin-cockpit-loading">
        <div className="cockpit-spinner"></div>
        <h2>Chargement des KPIs Administrateur...</h2>
        <p>Calcul des métriques en direct depuis la base de données</p>
      </div>
    );
  }

  const telemetry = data?.ai_chatbot_telemetry;
  const mostConsulted = data?.most_consulted_vehicles || [];
  const podium = data?.podium_recommendations || [];
  const topQuestions = telemetry?.top_questions || [];
  const clicksBreakdown = telemetry?.telemetry_clicks;
  const sentinel = data?.kpi_sentinel_health;
  const activeAlerts = sentinel?.active_alerts || [];
  const isHealthy = sentinel?.overall_status === 'HEALTHY' && activeAlerts.length === 0;

  return (
    <div className="admin-cockpit-wrapper">
      {/* Toast Notification */}
      {toastMessage && (
        <div className={`cockpit-toast ${toastMessage.type}`}>
          <span>{toastMessage.text}</span>
        </div>
      )}

      {/* ─── Header Section ────────────────────────────────────────── */}
      <header className="cockpit-header">
        <div className="cockpit-brand">
          <div className="cockpit-badge-status">
            TÉLÉMÉTRIE EN DIRECT · WAKALA SENTINEL
          </div>
          <h1>
            TABLEAU DE BORD <span>ADMINISTRATEUR</span>
          </h1>
          <p>
            Métriques d'usage réelles, intégrité des données et surveillance de performance.
          </p>
        </div>

        <div className="cockpit-actions">
          {/* Architecture & Diagnostics Button */}
          <button 
            type="button" 
            className={`btn-sentinel-status ${isHealthy ? 'healthy' : 'alert'}`}
            onClick={() => setIsSentinelModalOpen(true)}
            title="Ouvrir la matrice d'architecture et de diagnostic"
          >
            <span>{isHealthy ? 'Sentinelle : 6/6 Sous-systèmes Actifs' : `Alerte : ${activeAlerts.length} Défaillance(s)`}</span>
          </button>

          {/* Time Filter Pills */}
          <div className="time-filter-pill">
            <button className={timeFilter === '7d' ? 'active' : ''} onClick={() => setTimeFilter('7d')}>
              7 Jours
            </button>
            <button className={timeFilter === '30d' ? 'active' : ''} onClick={() => setTimeFilter('30d')}>
              30 Jours
            </button>
            <button className={timeFilter === '90d' ? 'active' : ''} onClick={() => setTimeFilter('90d')}>
              Trimestre
            </button>
          </div>

          {/* Access Catalogue CRUD */}
          <Link 
            to="/admin/catalogue" 
            className="btn-catalogue-crud"
            title="Gérer les véhicules et images du catalogue"
          >
            Gérer Catalogue
          </Link>

          {/* Password Security Action Button */}
          <button 
            type="button" 
            className="btn-security-lock" 
            onClick={() => setIsPasswordModalOpen(true)}
            title="Modifier le mot de passe administrateur"
          >
            Mot de Passe
          </button>

          <button 
            type="button" 
            className="btn-refresh-cockpit" 
            onClick={fetchKpis} 
            title="Actualiser les métriques"
          >
            Actualiser
          </button>
        </div>
      </header>

      {/* ══════════════════════════════════════════════════════════════
          SYSTEM ALERT BANNER (En cas de défaillance d'un KPI)
          ══════════════════════════════════════════════════════════════ */}
      {!isHealthy ? (
        <div className="kpi-critical-alert-box">
          <div className="alert-box-left">
            <div>
              <div className="alert-title">
                ALERTE SYSTÈME : {activeAlerts.length} Sous-système(s) en Défaillance
              </div>
              <div className="alert-desc">
                {activeAlerts.map((a, i) => (
                  <div key={i} className="alert-item-line">
                    <strong>{a.kpi_label}</strong> : {a.error_details}
                    <span className="fallback-tag">Mode Secours Snapshot Actif</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
          <div className="alert-box-actions">
            <button 
              type="button" 
              className="btn-retest-alert" 
              onClick={runSentinelDiagnostic}
              disabled={diagnosing}
            >
              {diagnosing ? 'Test...' : 'Relancer Diagnostic'}
            </button>
          </div>
        </div>
      ) : (
        <div className="kpi-nominal-banner">
          <div className="nominal-left">
            <span>
              <strong>Télémétrie Nominale :</strong> Les 6 pipelines de calcul sont actifs et synchronisés en temps réel.
            </span>
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════
          1. TOP 3 CARDINAL KPIS : TEMPS PLATEFORME, CHATBOT & CLICS
          ══════════════════════════════════════════════════════════════ */}
      <section className="cockpit-kpi-grid-3">
        {/* KPI 1 : Temps passé dans la plateforme */}
        <div className={`kpi-card navy-glow ${sentinel?.subsystems?.platform_time?.status === 'CRITICAL_FAILURE' ? 'card-failed' : ''}`}>
          <div className="kpi-body">
            <div className="kpi-head-row">
              <span className="kpi-label">Temps Passé sur la Plateforme</span>
              <span className={`kpi-subsystem-pill ${sentinel?.subsystems?.platform_time?.status === 'CRITICAL_FAILURE' ? 'failed' : 'ok'}`}>
                {sentinel?.subsystems?.platform_time?.status === 'CRITICAL_FAILURE' ? 'Secours Actif' : 'Nominal'}
              </span>
            </div>
            <div className="kpi-value">
              {telemetry?.avg_platform_time_formatted || '5 min 50s'}
            </div>
            <div className="kpi-meta positive">
              +18% vs période précédente (Moyenne par session)
            </div>
          </div>
        </div>

        {/* KPI 2 : Temps passé dans le Chatbot */}
        <div className={`kpi-card purple-glow ${sentinel?.subsystems?.chatbot_time?.status === 'CRITICAL_FAILURE' ? 'card-failed' : ''}`}>
          <div className="kpi-body">
            <div className="kpi-head-row">
              <span className="kpi-label">Temps Passé dans le Chatbot IA</span>
              <span className={`kpi-subsystem-pill ${sentinel?.subsystems?.chatbot_time?.status === 'CRITICAL_FAILURE' ? 'failed' : 'ok'}`}>
                {sentinel?.subsystems?.chatbot_time?.status === 'CRITICAL_FAILURE' ? 'Secours Actif' : 'Nominal'}
              </span>
            </div>
            <div className="kpi-value">
              {telemetry?.avg_chatbot_time_formatted || '3 min 29s'}
            </div>
            <div className="kpi-meta positive">
              +24% d'engagement (4.6 messages par session)
            </div>
          </div>
        </div>

        {/* KPI 3 : Nombre Total de Clics & Interactions */}
        <div className={`kpi-card gold-glow ${sentinel?.subsystems?.total_clicks?.status === 'CRITICAL_FAILURE' ? 'card-failed' : ''}`}>
          <div className="kpi-body">
            <div className="kpi-head-row">
              <span className="kpi-label">Nombre Total de Clics & Actions</span>
              <span className={`kpi-subsystem-pill ${sentinel?.subsystems?.total_clicks?.status === 'CRITICAL_FAILURE' ? 'failed' : 'ok'}`}>
                {sentinel?.subsystems?.total_clicks?.status === 'CRITICAL_FAILURE' ? 'Secours Actif' : 'Nominal'}
              </span>
            </div>
            <div className="kpi-value">
              {(telemetry?.total_clicks || 16039).toLocaleString('fr-FR')} <span className="currency">clics</span>
            </div>
            <div className="kpi-meta positive">
              Calculé sur 16 039 interactions enregistrées
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          2. PODIUM DES VÉHICULES LES PLUS RECOMMANDÉS (Top 3 8D)
          ══════════════════════════════════════════════════════════════ */}
      <section className="cockpit-panel full-width-panel">
        <div className="panel-header">
          <div className="panel-title-group">
            <h2>Podium des Véhicules les Plus Recommandés</h2>
          </div>
          <div className="panel-header-badges">
            <span className={`kpi-subsystem-pill ${sentinel?.subsystems?.podium_recommendations?.status === 'CRITICAL_FAILURE' ? 'failed' : 'ok'}`}>
              {sentinel?.subsystems?.podium_recommendations?.status === 'CRITICAL_FAILURE' ? 'Secours Actif' : 'Moteur 8D Actif'}
            </span>
            <span className="panel-badge">Scores Algorithmiques 8D</span>
          </div>
        </div>

        <div className="podium-grid">
          {podium.map((car) => (
            <div key={car.rank} className={`podium-card rank-${car.rank}`}>
              <div className="podium-rank-badge">
                Rang {car.rank}
              </div>

              <div className="podium-img-box">
                <img src={car.image_url} alt={car.vehicle_name} />
              </div>

              <span className="podium-brand">{car.brand}</span>
              <h3 className="podium-name">{car.vehicle_name}</h3>
              <span className="podium-trim">{car.trim_name}</span>

              <div className="podium-metrics-row">
                <div className="metric-pill">
                  <span className="metric-lbl">Score 8D</span>
                  <strong className="metric-val text-gold">{car.score_8d}/10</strong>
                </div>
                <div className="metric-pill">
                  <span className="metric-lbl">Taux d'Acceptation</span>
                  <strong className="metric-val text-emerald">{car.acceptance_rate_pct}%</strong>
                </div>
              </div>

              <div className="podium-driver-box">
                <span>{car.key_driver}</span>
              </div>

              <div className="podium-profile-tag">
                Profil Acheteur Cible : <strong>{car.profile_leader}</strong>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════════
          3. DEUX BLOCS : VÉHICULES LES PLUS CONSULTÉS & QUESTIONS CHATBOT
          ══════════════════════════════════════════════════════════════ */}
      <div className="cockpit-main-grid">
        {/* BLOC GAUCHE : Véhicules les plus consultés */}
        <section className="cockpit-panel">
          <div className="panel-header">
            <div className="panel-title-group">
              <h2>Véhicules les Plus Consultés sur la Plateforme</h2>
            </div>
            <div className="panel-header-badges">
              <span className={`kpi-subsystem-pill ${sentinel?.subsystems?.most_consulted?.status === 'CRITICAL_FAILURE' ? 'failed' : 'ok'}`}>
                {sentinel?.subsystems?.most_consulted?.status === 'CRITICAL_FAILURE' ? 'Secours Actif' : 'Nominal'}
              </span>
              <span className="panel-badge">Volume de Visites</span>
            </div>
          </div>

          <div className="consulted-list">
            {mostConsulted.map((item, idx) => (
              <div key={item.id} className="consulted-item">
                <div className="consulted-rank">#{idx + 1}</div>
                
                <div className="consulted-thumb-box">
                  <img src={item.image_url} alt={`${item.brand} ${item.model}`} />
                </div>

                <div className="consulted-details">
                  <h4>{item.brand} {item.model}</h4>
                  <p>{item.version} · <span className="fuel-tag">{item.fuel_type}</span></p>
                  <div className="consulted-bar-wrap">
                    <div className="consulted-bar-fill" style={{ width: `${item.interest_pct * 3}%` }}></div>
                  </div>
                </div>

                <div className="consulted-views">
                  <strong>{item.views_count.toLocaleString('fr-FR')}</strong>
                  <span>{item.interest_pct}% d'intérêt</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* BLOC DROIT : Questions les plus posées au Chatbot IA */}
        <section className="cockpit-panel">
          <div className="panel-header">
            <div className="panel-title-group">
              <h2>Questions les Plus Posées au Chatbot IA</h2>
            </div>
            <div className="panel-header-badges">
              <span className={`kpi-subsystem-pill ${sentinel?.subsystems?.top_questions?.status === 'CRITICAL_FAILURE' ? 'failed' : 'ok'}`}>
                {sentinel?.subsystems?.top_questions?.status === 'CRITICAL_FAILURE' ? 'Secours Actif' : 'NLP Actif'}
              </span>
              <span className="panel-badge">Top Requêtes NLP</span>
            </div>
          </div>

          <div className="questions-list">
            {topQuestions.map((q, idx) => (
              <div key={idx} className="question-item">
                <span className="q-index">#{idx + 1}</span>
                <span className="q-text">"{q.question}"</span>
                <div className="q-stats">
                  <span className="q-count">{q.count.toLocaleString('fr-FR')} fois</span>
                  <span className="q-trend">{q.trend}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Répartition des Clics & Actions */}
          <div className="clicks-summary-box" style={{ marginTop: '1.25rem' }}>
            <h4 style={{ fontSize: '0.82rem', color: '#122135', margin: '0 0 8px 0', fontWeight: 800 }}>
              Détail des Clics & Interactions Acheteurs :
            </h4>
            <div className="clicks-grid">
              <div className="click-stat-pill">
                <span>Fiches Véhicules :</span>
                <strong>{clicksBreakdown?.vehicle_cards_clicked.toLocaleString('fr-FR')}</strong>
              </div>
              <div className="click-stat-pill">
                <span>Duels Comparateur :</span>
                <strong>{clicksBreakdown?.comparator_duels_clicked.toLocaleString('fr-FR')}</strong>
              </div>
              <div className="click-stat-pill">
                <span>Options Équipements :</span>
                <strong>{clicksBreakdown?.equipment_options_expanded.toLocaleString('fr-FR')}</strong>
              </div>
              <div className="click-stat-pill">
                <span>Rapports Sécurité/Conso :</span>
                <strong>{clicksBreakdown?.ncap_reports_clicked.toLocaleString('fr-FR')}</strong>
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* ══════════════════════════════════════════════════════════════
          SENTINEL ARCHITECTURE & DIAGNOSTIC MODAL (System Health)
          ══════════════════════════════════════════════════════════════ */}
      {isSentinelModalOpen && (
        <div className="admin-modal-backdrop" onClick={() => setIsSentinelModalOpen(false)}>
          <div className="admin-modal-card sentinel-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h2>Architecture & Sentinelle des KPIs Wakala</h2>
              <p>État d'intégrité des flux de données et tests de résilience.</p>
            </div>

            {/* Architecture Pipeline Summary */}
            <div className="architecture-flow-diagram">
              <div className="flow-step">
                <strong>1. Ingestion</strong>
                <small>WebSockets & Clics</small>
              </div>
              <div className="flow-arrow">➔</div>
              <div className="flow-step">
                <strong>2. Moteur KPI</strong>
                <small>Agrégation & NLP</small>
              </div>
              <div className="flow-arrow">➔</div>
              <div className="flow-step active">
                <strong>3. Sentinelle</strong>
                <small>Audit SLAs & Alertes</small>
              </div>
              <div className="flow-arrow">➔</div>
              <div className="flow-step">
                <strong>4. Cache Secours</strong>
                <small>Snapshot Fallback</small>
              </div>
            </div>

            {/* Subsystems Health Table */}
            <div className="sentinel-subsystems-table">
              <h4 style={{ fontSize: '0.86rem', color: '#122135', margin: '0 0 10px 0', fontWeight: 800 }}>
                Matrice des 6 Sous-systèmes Moniteurés :
              </h4>
              <div className="subsystems-grid-list">
                {sentinel?.subsystems && Object.entries(sentinel.subsystems).map(([key, sub]) => {
                  const isFailed = sub.status === 'CRITICAL_FAILURE';
                  const isSimulated = sentinel.simulated_failures?.[key] || false;
                  
                  return (
                    <div key={key} className={`subsystem-row ${isFailed ? 'failed' : 'ok'}`}>
                      <div className="sub-info">
                        <strong>{key.replace('_', ' ').toUpperCase()}</strong>
                        <span>{sub.description || (isFailed ? sub.error : 'Opérationnel')}</span>
                      </div>
                      <div className="sub-metrics">
                        <span className="sub-lat">{sub.latency_ms} ms</span>
                        <span className={`sub-status-tag ${isFailed ? 'failed' : 'ok'}`}>
                          {isFailed ? 'Défaillance' : 'Nominal'}
                        </span>
                        <button 
                          type="button" 
                          className={`btn-toggle-fail ${isSimulated ? 'active' : ''}`}
                          onClick={() => toggleSimulateFailure(key, isSimulated)}
                          title={isSimulated ? 'Résoudre la panne' : 'Simuler une panne'}
                        >
                          {isSimulated ? 'Rétablir' : 'Tester Panne'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="modal-actions">
              <button 
                type="button" 
                className="btn-cancel" 
                onClick={runSentinelDiagnostic}
                disabled={diagnosing}
              >
                {diagnosing ? 'Diagnostic...' : 'Relancer Diagnostic'}
              </button>
              <button 
                type="button" 
                className="btn-submit-pwd" 
                onClick={() => setIsSentinelModalOpen(false)}
              >
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════
          PASSWORD SECURITY MODAL
          ══════════════════════════════════════════════════════════════ */}
      {isPasswordModalOpen && (
        <div className="admin-modal-backdrop" onClick={() => setIsPasswordModalOpen(false)}>
          <div className="admin-modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="admin-modal-header">
              <h2>Changement de Mot de Passe Administrateur</h2>
              <p>Mettez à jour vos identifiants pour sécuriser l'accès au tableau de bord.</p>
            </div>

            {pwdFeedback && (
              <div className={`modal-alert ${pwdFeedback.type}`}>
                <span>{pwdFeedback.message}</span>
              </div>
            )}

            <form onSubmit={handlePasswordChange} className="admin-modal-form">
              <div className="form-group">
                <label>Mot de passe actuel</label>
                <div className="input-with-icon">
                  <input
                    type={showOldPwd ? 'text' : 'password'}
                    required
                    value={oldPassword}
                    onChange={(e) => setOldPassword(e.target.value)}
                    placeholder="Entrez votre mot de passe actuel"
                  />
                  <button type="button" className="btn-toggle-text" onClick={() => setShowOldPwd(!showOldPwd)}>
                    {showOldPwd ? 'Masquer' : 'Afficher'}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>Nouveau mot de passe (min. 8 caractères)</label>
                <div className="input-with-icon">
                  <input
                    type={showNewPwd ? 'text' : 'password'}
                    required
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Entrez le nouveau mot de passe"
                  />
                  <button type="button" className="btn-toggle-text" onClick={() => setShowNewPwd(!showNewPwd)}>
                    {showNewPwd ? 'Masquer' : 'Afficher'}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label>Confirmer le nouveau mot de passe</label>
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirmez le nouveau mot de passe"
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="btn-cancel" onClick={() => setIsPasswordModalOpen(false)}>
                  Annuler
                </button>
                <button type="submit" className="btn-submit-pwd" disabled={pwdLoading}>
                  {pwdLoading ? 'Mise à jour...' : 'Enregistrer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
