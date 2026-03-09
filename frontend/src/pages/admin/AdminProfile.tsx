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
  Activity,
  Cpu,
  X,
  CheckCircle2,
  Lock,
  Mail,
  Fingerprint,
  Calendar,
  History,
  Key
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

      setMessage('Profil synchronisé avec succès !');
      setIsEditing(false);
      setFormData(prev => ({ ...prev, password: '' }));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Échec de la synchronisation');
    }
  };

  const initials = `${adminUser?.prenom?.[0] || ''}${adminUser?.nom?.[0] || adminUser?.username?.[0] || ''}`.toUpperCase();

  return (
    <div className="profile-v5-container">
      {/* ── Glass Hero Header ─────────────────────────────────── */}
      <div className="hero-glass-v5">
        <div className="hero-content">
          <div className="avatar-wrapper-v5">
            <div className="avatar-main">{initials}</div>
            <div className="verified-badge"><ShieldCheck size={16} /></div>
          </div>

          <div className="hero-info-v5">
            <div className="hero-badge-v5">Administrateur Système</div>
            <h1 className="hero-name-v5">{adminUser?.prenom} {adminUser?.nom}</h1>
            <div className="hero-meta-v5">
              <span className="meta-item"><Fingerprint size={14} /> @{adminUser?.username}</span>
              <span className="meta-sep">/</span>
              <span className="meta-item"><Mail size={14} /> {adminUser?.email}</span>
            </div>
          </div>
        </div>

        <button
          className={`edit-trigger-v5 ${isEditing ? 'active' : ''}`}
          onClick={() => { setIsEditing(!isEditing); setError(''); setMessage(''); }}
        >
          {isEditing ? <X size={20} /> : <Settings size={20} />}
          <span>{isEditing ? 'Annuler' : 'Édition'}</span>
        </button>
      </div>

      <div className="profile-grid-v5">
        {/* ── Left Column: Functional Summary ──────────────────────── */}
        <div className="side-column-v5">
          {/* Stats Card */}
          <div className="panel-v5 stats-panel">
            <h3 className="panel-title-v5">Indice d'Impact</h3>
            <div className="stats-v5-list">
              <div className="stat-v5-item">
                <div className="v5-icon purple"><Building2 size={18} /></div>
                <div className="v5-data">
                  <span className="v5-label">Cabinets</span>
                  <span className="v5-value">{stats?.total_cabinets || 0}</span>
                </div>
              </div>
              <div className="stat-v5-item">
                <div className="v5-icon blue"><Users size={18} /></div>
                <div className="v5-data">
                  <span className="v5-label">Collaborateurs</span>
                  <span className="v5-value">{stats?.total_agents || 0}</span>
                </div>
              </div>
              <div className="stat-v5-item">
                <div className="v5-icon green"><Building size={18} /></div>
                <div className="v5-data">
                  <span className="v5-label">Sociétés</span>
                  <span className="v5-value">{stats?.total_societes || 0}</span>
                </div>
              </div>
              <div className="stat-v5-item">
                <div className="v5-icon amber"><FileText size={18} /></div>
                <div className="v5-data">
                  <span className="v5-label">Flux Totaux</span>
                  <span className="v5-value">{stats?.total_factures || 0}</span>
                </div>
              </div>
            </div>
          </div>

          {/* ── Connectivity Sidebar ─────────────────────────────── */}
          <div className="panel-v5 connectivity-panel-v5">
            <h3 className="panel-title-v5">Accès & Connectivité</h3>
            <div className="connectivity-list-v5">
              <div className="conn-item-v5">
                <div className="conn-icon"><History size={16} /></div>
                <div className="conn-text">
                  <span>Dernière connexion</span>
                  <p>Aujourd'hui</p>
                </div>
              </div>
              <div className="conn-item-v5">
                <div className="conn-icon"><Calendar size={16} /></div>
                <div className="conn-text">
                  <span>Membre depuis</span>
                  <p>2026</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Right Column: Identity Form ──────────────────────────── */}
        <div className="main-column-v5">
          <div className="panel-v5 form-panel-v5">
            <div className="panel-header-v5">
              <h2 className="panel-title-v5">Informations Identitaires</h2>
              <p className="panel-subtitle-v5">Gérez vos informations personnelles et identifiants de sécurité.</p>
            </div>

            {error && <div className="toast-v5 error-v5">{error}</div>}
            {message && <div className="toast-v5 success-v5">{message}</div>}

            <form onSubmit={handleUpdateProfile} className="identity-form-v5">
              <div className="form-row-v5">
                <div className="input-field-v5">
                  <label>Prénom</label>
                  <div className="input-wrapper-v5">
                    <User className="field-icon-v5" size={18} />
                    <input
                      type="text"
                      value={formData.prenom}
                      disabled={!isEditing}
                      onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                      placeholder="Prénom"
                    />
                  </div>
                </div>
                <div className="input-field-v5">
                  <label>Nom</label>
                  <div className="input-wrapper-v5">
                    <User className="field-icon-v5" size={18} />
                    <input
                      type="text"
                      value={formData.nom}
                      disabled={!isEditing}
                      onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                      placeholder="Nom"
                    />
                  </div>
                </div>
              </div>

              <div className="input-field-v5">
                <label>Adresse Mail Professionnelle</label>
                <div className="input-wrapper-v5">
                  <Mail className="field-icon-v5" size={18} />
                  <input
                    type="email"
                    value={formData.email}
                    disabled={!isEditing}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="email@cabinet.com"
                  />
                </div>
              </div>

              <div className="input-field-v5 readonly-v5">
                <label>Identifiant Unique (Immuable)</label>
                <div className="locked-box-v5">
                  <Lock className="locked-icon" size={16} />
                  <span>@{adminUser?.username}</span>
                  <div className="immutable-tag">IMMUTABLE</div>
                </div>
              </div>

              {isEditing && (
                <div className="auth-upgrade-v5 animate-in">
                  <div className="input-field-v5">
                    <label>Nouvelle Clé d'Accès (Sécurité)</label>
                    <div className="input-wrapper-v5">
                      <Key className="field-icon-v5" size={18} />
                      <input
                        type="password"
                        placeholder="••••••••••••"
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      />
                    </div>
                  </div>
                  <button type="submit" className="save-button-v5">
                    <ShieldCheck size={18} />
                    <span>Synchroniser les Données</span>
                  </button>
                </div>
              )}
            </form>
          </div>
        </div>
      </div>

      <style>{`
        .profile-v5-container {
          animation: pageSlideIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
          padding-bottom: 100px;
        }

        @keyframes pageSlideIn {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        /* ── Hero section ─────────────────────────────────────── */
        .hero-glass-v5 {
          background: rgba(255, 255, 255, 0.6);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border: 1px solid rgba(255, 255, 255, 0.4);
          border-radius: 30px;
          padding: 40px;
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 30px;
          box-shadow: 0 10px 30px -10px rgba(0,0,0,0.05);
        }

        .hero-content { display: flex; align-items: center; gap: 30px; }

        .avatar-wrapper-v5 { position: relative; }
        .avatar-main {
          width: 100px; height: 100px;
          background: linear-gradient(135deg, #020617 0%, #1e293b 100%);
          border-radius: 28px;
          display: flex; align-items: center; justify-content: center;
          font-size: 38px; font-weight: 900; color: white;
          box-shadow: 0 15px 30px -5px rgba(0,0,0,0.2);
          border: 4px solid white;
        }
        .verified-badge {
          position: absolute; top: -5px; right: -5px;
          width: 28px; height: 28px; background: #6366f1;
          color: white; border-radius: 50%; display: flex;
          align-items: center; justify-content: center;
          border: 3px solid white; box-shadow: 0 4px 10px rgba(99,102,241,0.3);
        }

        .hero-badge-v5 {
          display: inline-block; padding: 4px 12px; border-radius: 20px;
          background: rgba(99,102,241,0.1); color: #6366f1;
          font-size: 11px; font-weight: 800; text-transform: uppercase;
          letter-spacing: 0.5px; margin-bottom: 8px;
        }
        .hero-name-v5 { font-size: 44px; font-weight: 900; margin: 0; letter-spacing: -2px; color: #020617; }
        .hero-meta-v5 { display: flex; align-items: center; gap: 12px; margin-top: 8px; color: #64748b; font-weight: 600; font-size: 15px; }
        .meta-item { display: flex; align-items: center; gap: 6px; }
        .meta-sep { opacity: 0.3; }

        .edit-trigger-v5 {
          background: white; border: 1px solid #e2e8f0;
          padding: 12px 24px; border-radius: 16px;
          display: flex; align-items: center; gap: 10px;
          font-weight: 700; color: #1e293b; cursor: pointer;
          transition: all 0.3s; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }
        .edit-trigger-v5:hover { background: #f8fafc; transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
        .edit-trigger-v5.active { background: #020617; color: white; border-color: #020617; }

        /* ── Grid & Panels ────────────────────────────────────── */
        .profile-grid-v5 { display: grid; grid-template-columns: 320px 1fr; gap: 30px; }
        
        .panel-v5 {
          background: white; border: 1px solid #f1f5f9;
          border-radius: 24px; padding: 30px;
          box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
        }

        .panel-title-v5 { font-size: 18px; font-weight: 800; margin-bottom: 20px; color: #0f172a; }

        .side-column-v5 { display: flex; flex-direction: column; gap: 30px; }
        
        .stats-v5-list { display: flex; flex-direction: column; gap: 16px; }
        .stat-v5-item { display: flex; align-items: center; gap: 15px; }
        .v5-icon {
          width: 44px; height: 44px; border-radius: 14px;
          display: flex; align-items: center; justify-content: center;
        }
        .v5-icon.purple { background: #f5f3ff; color: #8b5cf6; }
        .v5-icon.blue { background: #eff6ff; color: #3b82f6; }
        .v5-icon.green { background: #ecfdf5; color: #10b981; }
        .v5-icon.amber { background: #fffbeb; color: #d97706; }

        .v5-data { display: flex; flex-direction: column; }
        .v5-label { font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; }
        .v5-value { font-size: 18px; font-weight: 800; color: #1e293b; }


        /* ── Main Panel ───────────────────────────────────────── */
        .form-panel-v5 { position: relative; }
        .panel-header-v5 { margin-bottom: 35px; }
        .panel-header-v5 h2 { font-size: 24px; font-weight: 900; margin: 0; letter-spacing: -0.5px; }
        .panel-subtitle-v5 { font-size: 15px; color: #64748b; margin-top: 6px; }

        .identity-form-v5 { display: flex; flex-direction: column; gap: 24px; }
        .form-row-v5 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }

        .input-field-v5 label {
          display: block; font-size: 12px; font-weight: 700;
          color: #475569; margin-bottom: 10px;
        }
        .input-wrapper-v5 { position: relative; }
        .field-icon-v5 {
          position: absolute; left: 18px; top: 50%;
          transform: translateY(-50%); color: #94a3b8;
          transition: color 0.3s;
        }
        .input-wrapper-v5 input {
          width: 100%; padding: 16px 18px 16px 52px;
          border: 2px solid #f1f5f9; border-radius: 16px;
          font-size: 15px; font-weight: 600; color: #1e293b;
          background: #f8fafc; transition: all 0.3s; outline: none;
        }
        .input-wrapper-v5 input:focus:not(:disabled) {
          background: white; border-color: #6366f1;
          box-shadow: 0 0 0 4px rgba(99,102,241,0.1);
        }
        .input-wrapper-v5 input:focus ~ .field-icon-v5 { color: #6366f1; }
        .input-wrapper-v5 input:disabled { background: #f8fafc; color: #94a3b8; cursor: default; }

        /* ── Readonly Block ───────────────────────────────────── */
        .locked-box-v5 {
          background: #f1f5f9; border: 2px dashed #cbd5e1;
          border-radius: 16px; padding: 16px 18px;
          display: flex; align-items: center; gap: 12px;
          color: #475569; font-weight: 700; font-size: 15px;
          position: relative;
        }
        .immutable-tag {
          margin-left: auto; background: #cbd5e1;
          color: white; font-size: 9px; font-weight: 900;
          padding: 2px 8px; border-radius: 6px;
        }

        /* ── Footer Elements ──────────────────────────────────── */
        .auth-upgrade-v5 { 
          margin-top: 20px; padding: 30px; border-radius: 20px;
          background: #eff6ff; border: 1px solid #dbeafe;
          display: flex; flex-direction: column; gap: 20px;
        }
        .save-button-v5 {
          background: #6366f1; color: white; border: none;
          padding: 18px; border-radius: 16px; font-weight: 800;
          display: flex; align-items: center; justify-content: center;
          gap: 12px; cursor: pointer; transition: all 0.3s;
          box-shadow: 0 10px 20px -5px rgba(99,102,241,0.4);
        }
        .save-button-v5:hover { background: #4f46e5; transform: translateY(-2px); }

        .system-info-v5 { margin-top: 30px; padding: 25px 30px; background: #f8fafc; }
        .system-grid-v5 { display: flex; gap: 30px; }
        .sys-item-v5 { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: #64748b; }

        .toast-v5 { padding: 16px 24px; border-radius: 14px; margin-bottom: 25px; font-weight: 700; text-align: center; font-size: 14px; }
        .error-v5 { background: #fef2f2; color: #dc2626; border: 1px solid #fee2e2; }
        .success-v5 { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; }

        @media (max-width: 1000px) {
          .profile-grid-v5 { grid-template-columns: 1fr; }
          .hero-glass-v5 { flex-direction: column; gap: 30px; text-align: center; }
          .hero-content { flex-direction: column; }
          .form-row-v5 { grid-template-columns: 1fr; }
        }
        .connectivity-panel-v5 {
          background: #f8fafc;
          border: 1px solid #e2e8f0;
          padding: 24px;
        }

        .connectivity-list-v5 {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .conn-item-v5 {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .conn-icon {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          background: white;
          border: 1px solid #e2e8f0;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #64748b;
        }

        .conn-text span {
          display: block;
          font-size: 11px;
          font-weight: 700;
          color: #94a3b8;
          text-transform: uppercase;
        }

        .conn-text p {
          font-size: 13px;
          font-weight: 700;
          color: #1e293b;
          margin: 0;
        }
      `}</style>
    </div>
  );
};
