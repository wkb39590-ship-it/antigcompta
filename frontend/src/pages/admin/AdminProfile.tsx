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
    <div className="admin-profile-container" style={{ animation: 'fadeIn 0.5s ease-out', paddingBottom: '40px' }}>
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div style={{ position: 'relative' }}>
            <div style={{ width: '80px', height: '80px', background: 'var(--bg3)', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '32px', fontWeight: 800, color: 'var(--accent)', border: '2px solid var(--border)' }}>
              {initials}
            </div>
            <div style={{ position: 'absolute', bottom: '-4px', right: '-4px', width: '24px', height: '24px', background: 'var(--accent)', color: 'white', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '3px solid white' }}>
              <ShieldCheck size={14} />
            </div>
          </div>
          <div>
            <div style={{ display: 'inline-block', padding: '4px 10px', borderRadius: '6px', background: 'var(--bg3)', color: 'var(--accent)', fontSize: '10px', fontWeight: 800, textTransform: 'uppercase', marginBottom: '8px' }}>
              Administrateur Système
            </div>
            <h1 className="page-title" style={{ fontSize: '24px', fontWeight: 800 }}>{adminUser?.prenom} {adminUser?.nom}</h1>
            <div style={{ display: 'flex', gap: '16px', color: 'var(--text3)', fontSize: '14px', marginTop: '4px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Fingerprint size={14} /> @{adminUser?.username}</span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><Mail size={14} /> {adminUser?.email}</span>
            </div>
          </div>
        </div>
        <button
          className={`btn ${isEditing ? 'btn-ghost' : 'btn-primary'}`}
          onClick={() => { setIsEditing(!isEditing); setError(''); setMessage(''); }}
        >
          {isEditing ? <X size={20} /> : <Settings size={20} />}
          <span>{isEditing ? 'Annuler' : 'Modifier le profil'}</span>
        </button>
      </div>

      <div className="content-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        <div className="sidebar-column" style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <div className="card" style={{ padding: '24px', width: '100%' }}>
            <h3 className="card-title" style={{ fontSize: '16px', marginBottom: '20px' }}>Indice d'Impact</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <ImpactStat icon={<Building2 size={18} />} label="Cabinets" value={stats?.total_cabinets || 0} color="var(--accent)" bg="rgba(99, 102, 241, 0.1)" />
              <ImpactStat icon={<Users size={18} />} label="Collaborateurs" value={stats?.total_agents || 0} color="#3b82f6" bg="rgba(59, 130, 246, 0.1)" />
              <ImpactStat icon={<Building size={18} />} label="Sociétés" value={stats?.total_societes || 0} color="#10b981" bg="rgba(16, 185, 129, 0.1)" />
              <ImpactStat icon={<FileText size={18} />} label="Flux Totaux" value={stats?.total_factures || 0} color="#f59e0b" bg="rgba(245, 158, 11, 0.1)" />
            </div>
          </div>

          <div className="card" style={{ padding: '24px', background: 'var(--bg3)', width: '100%' }}>
            <h3 className="card-title" style={{ fontSize: '16px', marginBottom: '16px' }}>Accès & Connectivité</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '32px', height: '32px', background: 'white', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text3)', border: '1px solid var(--border)' }}><History size={16} /></div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text3)', fontWeight: 700, textTransform: 'uppercase' }}>Dernière connexion</div>
                  <div style={{ fontSize: '13px', fontWeight: 600 }}>Aujourd'hui</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{ width: '32px', height: '32px', background: 'white', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text3)', border: '1px solid var(--border)' }}><Calendar size={16} /></div>
                <div>
                  <div style={{ fontSize: '10px', color: 'var(--text3)', fontWeight: 700, textTransform: 'uppercase' }}>Membre depuis</div>
                  <div style={{ fontSize: '13px', fontWeight: 600 }}>2026</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="main-column" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="card" style={{ padding: '32px', flex: 1 }}>
            <div style={{ marginBottom: '32px' }}>
              <h2 className="card-title">Informations Identitaires</h2>
              <p className="card-subtitle">Gérez vos informations personnelles et identifiants de sécurité.</p>
            </div>

            {error && <div className="alert alert-error" style={{ marginBottom: '24px' }}>{error}</div>}
            {message && <div className="alert alert-success" style={{ marginBottom: '24px' }}>{message}</div>}

            <form onSubmit={handleUpdateProfile} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
                <div className="form-group">
                  <label className="form-label">Prénom</label>
                  <input
                    className="form-input"
                    type="text"
                    value={formData.prenom}
                    disabled={!isEditing}
                    onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Nom</label>
                  <input
                    className="form-input"
                    type="text"
                    value={formData.nom}
                    disabled={!isEditing}
                    onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Adresse Mail Professionnelle</label>
                <input
                  className="form-input"
                  type="email"
                  value={formData.email}
                  disabled={!isEditing}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Identifiant Unique</label>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', background: 'var(--bg3)', borderRadius: '12px', color: 'var(--text3)', fontWeight: 600, border: '1px solid var(--border)' }}>
                  <Lock size={16} />
                  <span>@{adminUser?.username}</span>
                  <span style={{ marginLeft: 'auto', fontSize: '9px', fontWeight: 800, padding: '2px 6px', background: 'var(--border)', borderRadius: '4px' }}>IMMUTABLE</span>
                </div>
              </div>

              {isEditing && (
                <div style={{ marginTop: '24px', padding: '24px', background: 'rgba(99, 102, 241, 0.05)', borderRadius: '16px', border: '1px solid rgba(99, 102, 241, 0.2)', animation: 'slideIn 0.3s ease-out' }}>
                  <div className="form-group" style={{ marginBottom: '20px' }}>
                    <label className="form-label">Nouveau mot de passe</label>
                    <input
                      className="form-input"
                      type="password"
                      placeholder="••••••••••••"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    />
                  </div>
                  <button type="submit" className="btn btn-primary" style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}>
                    <ShieldCheck size={18} />
                    <span>Sauvegarder les modifications</span>
                  </button>
                </div>
              )}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

const ImpactStat: React.FC<{ icon: React.ReactNode, label: string, value: number, color: string, bg: string }> = ({ icon, label, value, color, bg }) => (
  <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
    <div style={{ width: '40px', height: '40px', background: bg, color: color, borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {icon}
    </div>
    <div>
      <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text3)', textTransform: 'uppercase' }}>{label}</div>
      <div style={{ fontSize: '18px', fontWeight: 800 }}>{value}</div>
    </div>
  </div>
);
