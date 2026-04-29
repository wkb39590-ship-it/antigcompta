import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { getAdminUser, setAdminSession } from '../../utils/adminTokenDecoder';
import {
  User,
  Settings,
  Building2,
  Users,
  Building,
  FileText,
  ShieldCheck,
  X,
  Lock,
  Mail,
  Fingerprint,
  Calendar,
  History,
  Save,
  UserCircle
} from 'lucide-react';

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

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const data = await apiService.adminGetGlobalStats();
      setStats(data);
    } catch (err) {
      console.error('Erreur stats globales:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError('');
      setMessage('');
      const data = await apiService.adminUpdateProfile(formData);

      const token = localStorage.getItem('admin_token') || '';
      setAdminSession(token, data);

      setMessage('Profil mis à jour avec succès !');
      setIsEditing(false);
      setFormData(prev => ({ ...prev, password: '' }));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Échec de la mise à jour');
    }
  };

  const initials = `${adminUser?.prenom?.[0] || ''}${adminUser?.nom?.[0] || adminUser?.username?.[0] || ''}`.toUpperCase();

  if (loading) {
     return <div style={{ padding: '60px', textAlign: 'center', color: '#94a3b8' }}>Chargement du profil...</div>;
  }

  return (
    <div className="profile-wrapper">
      {/* HEADER SECTION */}
      <div className="profile-header-card">
        <div className="header-bg"></div>
        <div className="header-content">
          <div className="avatar-wrapper">
            <div className="avatar-large">{initials}</div>
            <div className="badge-admin"><ShieldCheck size={16} /></div>
          </div>
          <div className="user-meta">
            <span className="role-chip">Administrateur Système</span>
            <h1>{adminUser?.prenom} {adminUser?.nom}</h1>
            <div className="contact-pills">
              <div className="pill"><Fingerprint size={14} /> @{adminUser?.username}</div>
              <div className="pill"><Mail size={14} /> {adminUser?.email}</div>
            </div>
          </div>
          <button 
            className={`edit-toggle-btn ${isEditing ? 'active' : ''}`}
            onClick={() => { setIsEditing(!isEditing); setError(''); setMessage(''); }}
          >
            {isEditing ? <X size={18} /> : <Settings size={18} />}
            {isEditing ? 'Annuler' : 'Modifier le profil'}
          </button>
        </div>
      </div>

      <div className="profile-grid">
        {/* LEFT COLUMN: IMPACT & SECURITY */}
        <div className="side-column">
          <div className="info-card">
            <div className="card-header">
              <Users size={18} className="icon-blue" />
              <h3>Indice d'Impact</h3>
            </div>
            <div className="stats-list">
              <CompactStat label="Cabinets" value={stats?.total_cabinets || 0} unit="Unités" />
              <CompactStat label="Collaborateurs" value={stats?.total_agents || 0} unit="Actifs" />
              <CompactStat label="Sociétés" value={stats?.total_societes || 0} unit="Entités" />
              <CompactStat label="Flux Totaux" value={stats?.total_factures || 0} unit="Docs" />
            </div>
          </div>

          <div className="info-card">
            <div className="card-header">
              <History size={18} className="icon-orange" />
              <h3>Activité</h3>
            </div>
            <div className="activity-tiny">
              <div className="activity-row">
                <span className="label">Dernière connexion</span>
                <span className="value">Aujourd'hui</span>
              </div>
              <div className="activity-row">
                <span className="label">Membre depuis</span>
                <span className="value">Janvier 2026</span>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: MAIN FORM */}
        <div className="main-column">
          <div className="form-card">
            <div className="card-header">
              <UserCircle size={20} />
              <h3>Informations Identitaires</h3>
            </div>
            
            {error && <div className="alert-box error">{error}</div>}
            {message && <div className="alert-box success">{message}</div>}

            <form onSubmit={handleUpdateProfile} className="profile-form">
              <div className="form-row">
                <div className="input-group">
                  <label>Prénom</label>
                  <input 
                    type="text" 
                    value={formData.prenom} 
                    disabled={!isEditing}
                    onChange={e => setFormData({...formData, prenom: e.target.value})}
                  />
                </div>
                <div className="input-group">
                  <label>Nom</label>
                  <input 
                    type="text" 
                    value={formData.nom} 
                    disabled={!isEditing}
                    onChange={e => setFormData({...formData, nom: e.target.value})}
                  />
                </div>
              </div>

              <div className="input-group">
                <label>Adresse Mail Professionnelle</label>
                <input 
                  type="email" 
                  value={formData.email} 
                  disabled={!isEditing}
                  onChange={e => setFormData({...formData, email: e.target.value})}
                />
              </div>

              <div className="input-group locked">
                <label>Identifiant Système</label>
                <div className="locked-field">
                  <Lock size={14} />
                  <span>{adminUser?.username}</span>
                  <span className="tag-lock">IMMUTABLE</span>
                </div>
              </div>

              {isEditing && (
                <div className="editing-zone">
                  <div className="input-group">
                    <label>Nouveau mot de passe (optionnel)</label>
                    <input 
                      type="password" 
                      placeholder="Laisser vide pour ne pas changer" 
                      value={formData.password}
                      onChange={e => setFormData({...formData, password: e.target.value})}
                    />
                  </div>
                  <button type="submit" className="save-btn">
                    <Save size={18} />
                    Enregistrer les modifications
                  </button>
                </div>
              )}
            </form>
          </div>
        </div>
      </div>

      <style>{`
        .profile-wrapper { padding: 32px; max-width: 1100px; margin: 0 auto; animation: slideUp 0.4s ease-out; }
        
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        /* HEADER */
        .profile-header-card { 
          background: #fff; border-radius: 12px; overflow: hidden; 
          border: 1px solid #e2e8f0; margin-bottom: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }
        .header-bg { height: 100px; background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); opacity: 0.1; }
        .header-content { padding: 0 32px 32px; display: flex; align-items: flex-end; gap: 24px; margin-top: -40px; position: relative; }
        .avatar-large { 
          width: 100px; height: 100px; background: #6366f1; color: white; 
          border-radius: 16px; display: flex; align-items: center; justify-content: center;
          font-size: 36px; font-weight: 800; border: 4px solid #fff; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        }
        .badge-admin { 
          position: absolute; bottom: 32px; left: 108px; width: 28px; height: 28px;
          background: #10b981; color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center;
          border: 3px solid #fff;
        }
        .user-meta { flex: 1; padding-bottom: 4px; }
        .role-chip { font-size: 10px; font-weight: 800; color: #6366f1; text-transform: uppercase; letter-spacing: 0.5px; }
        .user-meta h1 { font-size: 24px; font-weight: 800; color: #0f172a; margin: 4px 0 8px; }
        .contact-pills { display: flex; gap: 12px; }
        .pill { font-size: 13px; color: #64748b; display: flex; align-items: center; gap: 6px; background: #f8fafc; padding: 4px 10px; border-radius: 6px; }

        .edit-toggle-btn { 
          padding: 10px 16px; border-radius: 8px; font-size: 14px; font-weight: 600; 
          display: flex; align-items: center; gap: 8px; cursor: pointer; transition: all 0.2s;
          border: 1px solid #e2e8f0; background: #fff; color: #475569;
        }
        .edit-toggle-btn:hover { background: #f1f5f9; }
        .edit-toggle-btn.active { background: #fee2e2; color: #ef4444; border-color: #fecaca; }

        /* GRID */
        .profile-grid { display: grid; grid-template-columns: 320px 1fr; gap: 24px; }
        .info-card { background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 20px; }
        .card-header h3 { font-size: 15px; font-weight: 700; color: #1e293b; margin: 0; }
        .icon-blue { color: #3b82f6; }
        .icon-orange { color: #f59e0b; }

        /* STATS */
        .stats-list { display: flex; flex-direction: column; gap: 16px; }
        .c-stat { display: flex; justify-content: space-between; align-items: flex-end; padding-bottom: 12px; border-bottom: 1px solid #f1f5f9; }
        .c-stat:last-child { border-bottom: none; }
        .c-stat .label { font-size: 12px; color: #64748b; font-weight: 600; }
        .c-stat .val-group { text-align: right; }
        .c-stat .val { font-size: 20px; font-weight: 800; color: #0f172a; display: block; }
        .c-stat .unit { font-size: 10px; color: #94a3b8; font-weight: 700; text-transform: uppercase; }

        .activity-tiny { display: flex; flex-direction: column; gap: 12px; }
        .activity-row { display: flex; flex-direction: column; }
        .activity-row .label { font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase; }
        .activity-row .value { font-size: 14px; font-weight: 700; color: #334155; }

        /* FORM */
        .form-card { background: #fff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .profile-form { display: flex; flex-direction: column; gap: 24px; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .input-group { display: flex; flex-direction: column; gap: 8px; }
        .input-group label { font-size: 12px; font-weight: 700; color: #64748b; }
        .input-group input { 
          padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; font-size: 14px; 
          color: #1e293b; background: #fff; transition: all 0.2s;
        }
        .input-group input:focus { outline: none; border-color: #6366f1; box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1); }
        .input-group input:disabled { background: #f8fafc; color: #64748b; cursor: not-allowed; }

        .locked-field { 
          display: flex; align-items: center; gap: 12px; padding: 12px; 
          background: #f1f5f9; border-radius: 8px; color: #475569; font-weight: 600; border: 1px solid #e2e8f0;
        }
        .tag-lock { margin-left: auto; font-size: 9px; font-weight: 800; background: #cbd5e1; color: #64748b; padding: 2px 6px; border-radius: 4px; }

        .editing-zone { 
          margin-top: 24px; padding: 24px; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; 
          display: flex; flex-direction: column; gap: 20px; animation: fadeIn 0.3s ease-out;
        }
        .save-btn { 
          background: #6366f1; color: white; padding: 12px; border-radius: 8px; 
          font-weight: 700; display: flex; align-items: center; justify-content: center; gap: 10px;
          border: none; cursor: pointer; transition: background 0.2s;
        }
        .save-btn:hover { background: #4f46e5; }

        .alert-box { padding: 12px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; margin-bottom: 20px; }
        .alert-box.success { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
        .alert-box.error { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }

        @media (max-width: 900px) {
          .profile-grid { grid-template-columns: 1fr; }
          .profile-header-card { text-align: center; }
          .header-content { flex-direction: column; align-items: center; margin-top: -60px; }
          .badge-admin { left: calc(50% + 30px); }
          .user-meta h1 { text-align: center; }
          .contact-pills { justify-content: center; flex-wrap: wrap; }
        }
      `}</style>
    </div>
  );
};

const CompactStat: React.FC<{ label: string, value: number, unit: string }> = ({ label, value, unit }) => (
  <div className="c-stat">
    <span className="label">{label}</span>
    <div className="val-group">
      <span className="val">{value}</span>
      <span className="unit">{unit}</span>
    </div>
  </div>
);
