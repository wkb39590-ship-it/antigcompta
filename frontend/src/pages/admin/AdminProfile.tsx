import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getAdminToken, getAdminUser, setAdminSession } from '../../utils/adminTokenDecoder';

interface GlobalStats {
  total_cabinets: number;
  total_agents: number;
  total_societes: number;
  total_factures: number;
}

export const AdminProfile: React.FC = () => {
  const [stats, setStats] = useState<GlobalStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const adminUser = getAdminUser();
  const [formData, setFormData] = useState({
    nom: adminUser?.nom || '',
    prenom: adminUser?.prenom || '',
    email: adminUser?.email || '',
    password: '',
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8888';

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    const token = getAdminToken();
    if (!token) return;
    try {
      const res = await axios.get(`${API_URL}/admin/stats/global`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(res.data);
    } catch (err) {
      console.error('Erreur stats globales:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAdminToken();
    if (!token) return;

    try {
      setError('');
      setMessage('');
      const res = await axios.put(`${API_URL}/admin/profile`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setAdminSession(token, res.data);
      setMessage('Profil synchronisé avec succès !');
      setIsEditing(false);
      setFormData(prev => ({ ...prev, password: '' }));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Échec de la synchronisation');
    }
  };

  const initials = `${adminUser?.prenom?.[0] || ''}${adminUser?.nom?.[0] || adminUser?.username?.[0] || ''}`.toUpperCase();

  return (
    <div className="aurora-profile-page">
      <div className="aurora-profile-hero aurora-card">
        <div className="hero-content">
          <div className="avatar-section">
            <div className="avatar-neon-ring">
              <div className="aurora-avatar-large">{initials}</div>
            </div>
            <div className="online-indicator neon-pulse"></div>
          </div>
          <div className="identity-section">
            <span className="aurora-tag gold">SUPER ADMINISTRATEUR</span>
            <h1 className="glass-text">{adminUser?.prenom} {adminUser?.nom}</h1>
            <p className="admin-email">@{adminUser?.username} • {adminUser?.email}</p>
          </div>
        </div>
        <div className="hero-actions">
          <button
            className={`aurora-btn-edit ${isEditing ? 'active' : ''}`}
            onClick={() => { setIsEditing(!isEditing); setError(''); setMessage(''); }}
          >
            {isEditing ? '✕ Annuler' : '⚙️ Paramètres'}
          </button>
        </div>
      </div>

      <div className="aurora-profile-grid">
        <div className="profile-stats-panel">
          <h2 className="panel-title glass-text">Impact Global</h2>
          <div className="aurora-mini-grid">
            <div className="aurora-stat-widget aurora-card">
              <span className="widget-label">Partenaires</span>
              <span className="widget-value">{stats?.total_cabinets || 0}</span>
              <div className="widget-progress blue"></div>
            </div>
            <div className="aurora-stat-widget aurora-card">
              <span className="widget-label">Collaborateurs</span>
              <span className="widget-value">{stats?.total_agents || 0}</span>
              <div className="widget-progress purple"></div>
            </div>
            <div className="aurora-stat-widget aurora-card">
              <span className="widget-label">Portefeuilles</span>
              <span className="widget-value">{stats?.total_societes || 0}</span>
              <div className="widget-progress green"></div>
            </div>
            <div className="aurora-stat-widget aurora-card">
              <span className="widget-label">Flux Totaux</span>
              <span className="widget-value">{stats?.total_factures || 0}</span>
              <div className="widget-progress gold"></div>
            </div>
          </div>

          <div className="aurora-system-info aurora-card">
            <h3 className="glass-text">État du Système</h3>
            <ul className="info-list">
              <li><span className="dot active"></span> Base de données : Connectée</li>
              <li><span className="dot active"></span> API Gateway : Opérationnel</li>
              <li><span className="dot active"></span> AI OCR Engine : Latence 120ms</li>
            </ul>
          </div>
        </div>

        <div className="profile-form-panel aurora-card">
          <h2 className="panel-title glass-text">Identité Numérique</h2>

          {error && <div className="aurora-error-toast">{error}</div>}
          {message && <div className="aurora-success-toast">{message}</div>}

          <form onSubmit={handleUpdateProfile} className="aurora-profile-form">
            <div className="aurora-form-row">
              <div className="aurora-input-group">
                <label>Prénom</label>
                <input
                  type="text"
                  value={formData.prenom}
                  disabled={!isEditing}
                  onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                  placeholder="Édition indisponible"
                />
              </div>
              <div className="aurora-input-group">
                <label>Nom</label>
                <input
                  type="text"
                  value={formData.nom}
                  disabled={!isEditing}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  placeholder="Édition indisponible"
                />
              </div>
            </div>

            <div className="aurora-input-group">
              <label>Canal de Communication (Email)</label>
              <input
                type="email"
                value={formData.email}
                disabled={!isEditing}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="Édition indisponible"
              />
            </div>

            <div className="aurora-input-group readonly">
              <label>Identifiant Système Unique</label>
              <div className="readonly-field">@{adminUser?.username}</div>
              <p className="field-hint">Cet identifiant est ancré et ne peut être modifié.</p>
            </div>

            {isEditing && (
              <div className="aurora-input-group aurora-fade-in neon-border-box">
                <label>Nouveau Clé d'Accès (Mot de Passe)</label>
                <input
                  type="password"
                  placeholder="Maintenir la clé actuelle..."
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </div>
            )}

            {isEditing && (
              <button type="submit" className="aurora-btn-submit full-width aurora-fade-in">
                Mettre à jour les paramètres 🛡️
              </button>
            )}
          </form>
        </div>
      </div>

      <style>{`
        .aurora-profile-page { animation: pageEnter 0.6s ease-out; }
        @keyframes pageEnter { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .aurora-profile-hero { 
          display: flex; justify-content: space-between; align-items: center; 
          padding: 60px; margin-bottom: 30px; 
          background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        }

        .hero-content { display: flex; align-items: center; gap: 40px; }
        
        .avatar-section { position: relative; }
        .avatar-neon-ring { 
          padding: 8px; border-radius: 40px; 
          background: linear-gradient(45deg, var(--admin-accent), #8b5cf6, var(--admin-accent));
          animation: rotateGradient 4s linear infinite;
        }
        @keyframes rotateGradient { 0% { filter: hue-rotate(0deg); } 100% { filter: hue-rotate(360deg); } }
        
        .aurora-avatar-large { 
          width: 120px; height: 120px; border-radius: 34px; 
          background: #0f172a; display: flex; align-items: center; justify-content: center;
          font-size: 48px; font-weight: 900; color: white; border: 4px solid #0f172a;
        }

        .online-indicator { 
          position: absolute; bottom: 8px; right: 8px; 
          width: 20px; height: 20px; border-radius: 50%;
          background: #10b981; border: 4px solid #1e293b;
        }
        .neon-pulse { animation: pulseGreen 2s infinite; }
        @keyframes pulseGreen { 0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); } 70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); } 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); } }

        .identity-section h1 { font-size: 42px; font-weight: 900; margin: 15px 0 5px 0; letter-spacing: -2px; }
        .admin-email { color: var(--admin-text-dim); font-size: 16px; font-weight: 500; }

        .aurora-btn-edit { 
          padding: 12px 25px; border-radius: 20px; border: 1px solid var(--admin-glass-border);
          background: rgba(255, 255, 255, 0.05); color: white; font-weight: 700; cursor: pointer;
          transition: all 0.3s;
        }
        .aurora-btn-edit:hover { background: rgba(255, 255, 255, 0.1); border-color: var(--admin-accent); }
        .aurora-btn-edit.active { background: #ef4444; border-color: #ef4444; }

        .aurora-profile-grid { display: grid; grid-template-columns: 400px 1fr; gap: 30px; }
        
        .panel-title { font-size: 20px; font-weight: 800; margin-bottom: 30px; }
        
        .aurora-mini-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px; }
        .aurora-stat-widget { padding: 25px; display: flex; flex-direction: column; gap: 5px; }
        .widget-label { font-size: 11px; font-weight: 800; color: var(--admin-text-dim); text-transform: uppercase; letter-spacing: 1px; }
        .widget-value { font-size: 28px; font-weight: 900; }
        .widget-progress { height: 4px; border-radius: 2px; width: 40%; margin-top: 10px; }
        .widget-progress.blue { background: #3b82f6; box-shadow: 0 0 10px rgba(59, 130, 246, 0.5); }
        .widget-progress.purple { background: #8b5cf6; box-shadow: 0 0 10px rgba(139, 92, 246, 0.5); }
        .widget-progress.green { background: #10b981; box-shadow: 0 0 10px rgba(16, 185, 129, 0.5); }
        .widget-progress.gold { background: #f59e0b; box-shadow: 0 0 10px rgba(245, 158, 11, 0.5); }

        .aurora-system-info { padding: 30px; }
        .info-list { list-style: none; padding: 0; margin: 20px 0 0 0; display: flex; flex-direction: column; gap: 15px; }
        .info-list li { display: flex; align-items: center; gap: 12px; font-size: 13px; font-weight: 700; color: var(--admin-text-dim); }
        .dot { width: 8px; height: 8px; border-radius: 50%; }
        .dot.active { background: #10b981; box-shadow: 0 0 8px #10b981; }

        .profile-form-panel { padding: 40px; }
        .aurora-profile-form { display: flex; flex-direction: column; gap: 25px; }
        
        .aurora-input-group label { display: block; font-size: 11px; font-weight: 800; color: var(--admin-text-dim); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
        .aurora-input-group input { 
          width: 100%; padding: 15px; border-radius: 14px; border: 1px solid var(--admin-glass-border); 
          background: rgba(255, 255, 255, 0.03); color: white; outline: none; transition: all 0.3s;
        }
        .aurora-input-group input:focus:not(:disabled) { border-color: var(--admin-accent); background: rgba(255, 255, 255, 0.06); }
        .aurora-input-group input:disabled { opacity: 0.5; cursor: not-allowed; border-style: dashed; }

        .readonly-field { padding: 15px; border-radius: 14px; background: rgba(255, 255, 255, 0.05); color: var(--admin-accent); font-weight: 800; border: 1px solid var(--admin-glass-border); }
        .field-hint { font-size: 12px; color: var(--admin-text-dim); margin-top: 8px; font-style: italic; }

        .neon-border-box { padding: 5px; border-radius: 16px; background: linear-gradient(45deg, transparent, var(--admin-accent), transparent); }
        .neon-border-box input { background: #0f172a !important; }

        .aurora-error-toast { background: rgba(239, 68, 68, 0.1); color: #f87171; padding: 15px 25px; border-radius: 16px; border: 1px solid rgba(239, 68, 68, 0.2); margin-bottom: 25px; }
        .aurora-success-toast { background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 15px 25px; border-radius: 16px; border: 1px solid rgba(16, 185, 129, 0.2); margin-bottom: 25px; font-weight: 700; text-align: center; }

        @media (max-width: 1100px) {
          .aurora-profile-grid { grid-template-columns: 1fr; }
          .aurora-profile-hero { flex-direction: column; text-align: center; gap: 30px; }
          .hero-content { flex-direction: column; }
        }
      `}</style>
    </div>
  );
};
