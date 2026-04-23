import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { getAdminUser } from '../../utils/adminTokenDecoder';
import {
  Users,
  UserPlus,
  X,
  Settings,
  UserX,
  Building,
  Mail,
  Fingerprint,
  ShieldCheck,
  ShieldAlert
} from 'lucide-react';

interface Agent {
  id: number;
  cabinet_id: number;
  username: string;
  email: string;
  nom: string;
  prenom: string;
  is_admin: boolean;
  is_super_admin: boolean;
  is_active: boolean;
}

interface Cabinet {
  id: number;
  nom: string;
}

interface Societe {
  id: number;
  raison_sociale: string;
  cabinet_id: number;
}

export const AdminAgents: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [cabinets, setCabinets] = useState<Cabinet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    nom: '',
    prenom: '',
    is_admin: false,
    cabinet_id: '',
    societe_id: '',
  });

  const [societes, setSocietes] = useState<Societe[]>([]);
  const adminUser = getAdminUser();
  const isSuper = adminUser?.is_super_admin === true;

  const getErrorMessage = (err: any) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    return err.message || 'Une erreur est survenue';
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [agentsData, cabsData, socData] = await Promise.all([
        apiService.adminListAgents(),
        isSuper ? apiService.adminListCabinets() : Promise.resolve(JSON.parse(localStorage.getItem('cabinets') || '[]')),
        apiService.adminListSocietes()
      ]);

      const filteredAgents = (Array.isArray(agentsData) ? agentsData : [])
        .filter((a: any) => {
          if (isSuper) return a.is_admin && !a.is_super_admin;
          return a.id !== adminUser?.id;
        });

      setAgents(filteredAgents);
      setCabinets(Array.isArray(cabsData) ? cabsData : []);
      setSocietes(Array.isArray(socData) ? socData : []);

      if (!isSuper && adminUser?.cabinet_id) {
        setFormData(prev => ({ ...prev, cabinet_id: String(adminUser.cabinet_id) }));
      }
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.cabinet_id) {
      setError('Sélectionnez un cabinet');
      return;
    }
    try {
      const payload: any = {
        username: formData.username,
        email: formData.email,
        nom: formData.nom,
        prenom: formData.prenom,
        is_admin: isSuper ? true : formData.is_admin,
      };

      if (formData.password) payload.password = formData.password;

      if (editingAgent) {
        await apiService.adminUpdateAgent(editingAgent.id, payload);
      } else {
        if (!formData.password) {
          setError('Le mot de passe est obligatoire');
          return;
        }
        const newAgent = await apiService.adminCreateAgent(payload, formData.cabinet_id);
        if (formData.societe_id) {
          await apiService.adminAssignSocieteToAgent(Number(formData.cabinet_id), newAgent.id, Number(formData.societe_id));
        }
      }
      setFormData({
        username: '', email: '', password: '', nom: '', prenom: '', is_admin: false,
        cabinet_id: isSuper ? '' : String(adminUser?.cabinet_id || ''), societe_id: '',
      });
      setShowForm(false);
      setEditingAgent(null);
      fetchData();
    } catch (err: any) {
      setError(getErrorMessage(err));
    }
  };

  const handleEditClick = (agent: Agent) => {
    setEditingAgent(agent);
    setFormData({
      username: agent.username, email: agent.email, password: '', nom: agent.nom, prenom: agent.prenom,
      is_admin: agent.is_admin, cabinet_id: String(agent.cabinet_id), societe_id: '',
    });
    setShowForm(true);
  };

  const handleDeleteAgent = async (id: number) => {
    if (!window.confirm('Supprimer cet agent ?')) return;
    try {
      await apiService.adminDeleteAgent(id);
      fetchData();
    } catch (err: any) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="agents-page">
      <div className="page-header">
        <div className="header-info">
          <h1 className="page-title">{isSuper ? 'Administrateurs Cabinets' : 'Collaborateurs'}</h1>
          <p className="page-subtitle">Gestion des accès opérationnels et des habilitations de traitement.</p>
        </div>
        <button
          className={`btn-primary ${showForm ? 'form-active' : ''}`}
          onClick={() => {
            if (showForm) {
              setShowForm(false);
              setEditingAgent(null);
              setFormData({ username: '', email: '', password: '', nom: '', prenom: '', is_admin: false, cabinet_id: isSuper ? '' : String(adminUser?.cabinet_id || ''), societe_id: '' });
            } else {
              setShowForm(true);
              if (!isSuper && adminUser?.cabinet_id) {
                setFormData(prev => ({ ...prev, cabinet_id: String(adminUser.cabinet_id) }));
              }
            }
            setError('');
          }}
        >
          {showForm ? <X size={18} /> : <><UserPlus size={16} /> <span>{isSuper ? 'Ajouter Admin' : 'Nouvel Agent'}</span></>}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="content-layout">
        {showForm && (
          <form className="pro-card side-form" onSubmit={handleCreateAgent}>
            <div className="form-header">
              <h3>{editingAgent ? 'Modifier l\'accès' : 'Création de compte'}</h3>
              <p>Paramètres d'identification et privilèges</p>
            </div>

            <div className="form-grid">
              <div className="field-group span2">
                <label>Structure de rattachement</label>
                {isSuper ? (
                  <select
                    className="pro-select"
                    value={formData.cabinet_id}
                    onChange={(e) => setFormData({ ...formData, cabinet_id: e.target.value, societe_id: '' })}
                    required
                  >
                    <option value="">Sélectionner un cabinet...</option>
                    {cabinets.map(cab => (
                      <option key={cab.id} value={cab.id}>{cab.nom}</option>
                    ))}
                  </select>
                ) : (
                  <div className="pro-input-read">
                    {cabinets.find(c => String(c.id) === formData.cabinet_id)?.nom || (cabinets.length > 0 ? cabinets[0].nom : 'Cabinet local')}
                  </div>
                )}
              </div>

              {!editingAgent && !isSuper && (
                <div className="field-group span2">
                  <label>Assigner à une société (Optionnel)</label>
                  <select
                    className="pro-select"
                    value={formData.societe_id}
                    onChange={(e) => setFormData({ ...formData, societe_id: e.target.value })}
                  >
                    <option value="">-- Affectation manuelle plus tard --</option>
                    {societes.filter(s => String(s.cabinet_id) === formData.cabinet_id).map(soc => (
                      <option key={soc.id} value={soc.id}>{soc.raison_sociale}</option>
                    ))}
                  </select>
                </div>
              )}

              <div className="field-group">
                <label>Prénom</label>
                <input className="pro-input" placeholder="Jean" value={formData.prenom} onChange={e => setFormData({...formData, prenom: e.target.value})} required/>
              </div>
              <div className="field-group">
                <label>Nom</label>
                <input className="pro-input" placeholder="Dupont" value={formData.nom} onChange={e => setFormData({...formData, nom: e.target.value})} required/>
              </div>
              <div className="field-group">
                <label>Username</label>
                <input className="pro-input" placeholder="j.dupont" value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} required/>
              </div>
              <div className="field-group">
                <label>Email</label>
                <input className="pro-input" type="email" placeholder="pro@example.com" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} required/>
              </div>
              <div className="field-group">
                <label>Mot de passe</label>
                <input className="pro-input" type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} required={!editingAgent}/>
              </div>
              <div className="field-group checkbox-group">
                <input type="checkbox" id="admin_toggle" checked={formData.is_admin} onChange={e => setFormData({...formData, is_admin: e.target.checked})}/>
                <label htmlFor="admin_toggle">Droits d'administration</label>
              </div>
            </div>

            <button type="submit" className="btn-primary full-w">
              {editingAgent ? 'Sauvegarder les modifications' : 'Activer le compte'}
            </button>
          </form>
        )}

        <div className="pro-card table-section">
          <div className="section-header">
            <div className="header-label">
              <Users size={16} className="muted-icon" />
              <span>Équipe opérationnelle</span>
            </div>
            <div className="entity-count">{agents.length} Actifs</div>
          </div>

          {loading ? (
            <div className="placeholder-state">
              <div className="dot-spinner"></div>
              <span>Chargement de l'équipe...</span>
            </div>
          ) : agents.length === 0 ? (
            <div className="placeholder-state empty">
              <Users size={48} className="muted-icon" />
              <p>Aucun agent configuré.</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="pro-table">
                <thead>
                  <tr>
                    <th>Collaborateur</th>
                    <th>Cabinet</th>
                    <th>Contact</th>
                    <th>Rôles</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {agents.map((agent) => (
                    <tr key={agent.id}>
                      <td>
                        <div className="profile-cell">
                          <div className="profile-square">{agent.prenom[0]}{agent.nom[0]}</div>
                          <div className="profile-info">
                            <span className="profile-name">{agent.prenom} {agent.nom}</span>
                            <span className="profile-handle">@{agent.username}</span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div className="cabinet-label">
                          <Building size={12} className="muted-icon" />
                          {cabinets.find(c => c.id === agent.cabinet_id)?.nom || '...'}
                        </div>
                      </td>
                      <td>
                        <div className="contact-labels">
                          <span className="email-line"><Mail size={10} /> {agent.email}</span>
                          <span className="id-line"><Fingerprint size={10} /> ID: {agent.id}</span>
                        </div>
                      </td>
                      <td>
                        <div className="role-tags">
                          <span className={`tag ${agent.is_admin ? 'tag-admin' : 'tag-agent'}`}>
                            {agent.is_admin ? <ShieldCheck size={10} /> : <ShieldAlert size={10} />}
                            {agent.is_admin ? 'Admin' : 'Agent'}
                          </span>
                          <span className={`tag ${agent.is_active ? 'tag-active' : 'tag-inactive'}`}>
                            {agent.is_active ? 'Actif' : 'Désactivé'}
                          </span>
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div className="btn-group">
                          <button className="btn-icon" title="Éditer" onClick={() => handleEditClick(agent)}>
                            <Settings size={14} />
                          </button>
                          <button className="btn-icon btn-danger" title="Supprimer" onClick={() => handleDeleteAgent(agent.id)}>
                            <UserX size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .agents-page { padding: 24px; background: #fafafa; min-height: 100vh; font-family: 'Inter', sans-serif; }
        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .page-title { font-size: 26px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -0.5px; }
        .page-subtitle { color: #64748b; font-size: 14px; margin-top: 4px; }

        .btn-primary { 
          background: #3b82f6; color: white; border: none; padding: 10px 20px; 
          border-radius: 4px; font-weight: 600; font-size: 14px; cursor: pointer;
          display: flex; align-items: center; gap: 8px; transition: background 0.2s;
        }
        .btn-primary:hover { background: #2563eb; }
        .btn-primary.form-active { background: #475569; }
        .full-w { width: 100%; margin-top: 15px; }

        .content-layout { display: flex; flex-direction: column; gap: 24px; }
        .pro-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

        .side-form { padding: 24px; border-left: 4px solid #3b82f6; animation: slideIn 0.3s ease-out; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

        .form-header { margin-bottom: 20px; }
        .form-header h3 { font-size: 16px; font-weight: 700; margin: 0; }
        .form-header p { font-size: 12px; color: #64748b; margin-top: 2px; }

        .form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
        .span2 { grid-column: span 2; }
        .checkbox-group { display: flex; align-items: center; gap: 10px; padding-top: 10px; }
        .checkbox-group input { width: 16px; height: 16px; cursor: pointer; }
        .checkbox-group label { text-transform: none; font-size: 13px; font-weight: 600; margin-bottom: 0; cursor: pointer; }

        .field-group label { display: block; font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 6px; }
        .pro-input, .pro-select { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 14px; background: #fff; outline: none; }
        .pro-input:focus, .pro-select:focus { border-color: #3b82f6; }
        .pro-input-read { padding: 10px 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; color: #3b82f6; font-weight: 600; font-size: 14px; }

        .section-header { padding: 16px 20px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
        .header-label { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; color: #334155; }
        .entity-count { font-size: 11px; font-weight: 700; color: #3b82f6; background: #eff6ff; padding: 2px 8px; border-radius: 4px; border: 1px solid #dbeafe; }

        .table-wrapper { overflow-x: auto; }
        .pro-table { width: 100%; border-collapse: collapse; }
        .pro-table th { text-align: left; padding: 12px 20px; font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #e2e8f0; }
        .pro-table td { padding: 12px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
        .pro-table tr:hover { background: #fafafa; }

        .profile-cell { display: flex; align-items: center; gap: 12px; }
        .profile-square { width: 32px; height: 32px; background: #f1f5f9; border: 1px solid #e2e8f0; color: #475569; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; }
        .profile-name { display: block; font-weight: 600; color: #1e293b; font-size: 14px; }
        .profile-handle { display: block; font-size: 11px; color: #94a3b8; font-family: monospace; }

        .cabinet-label { display: inline-flex; align-items: center; gap: 6px; padding: 4px 8px; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 12px; font-weight: 600; color: #475569; }
        .contact-labels { display: flex; flex-direction: column; gap: 2px; }
        .email-line { font-size: 12px; font-weight: 500; color: #3b82f6; display: flex; align-items: center; gap: 4px; }
        .id-line { font-size: 10px; color: #94a3b8; display: flex; align-items: center; gap: 4px; }

        .role-tags { display: flex; gap: 6px; }
        .tag { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
        .tag-admin { background: #fef2f2; color: #dc2626; border: 1px solid #fee2e2; }
        .tag-agent { background: #f8fafc; color: #475569; border: 1px solid #e2e8f0; }
        .tag-active { background: #f0fdf4; color: #166534; border: 1px solid #dcfce7; }
        .tag-inactive { background: #f1f5f9; color: #64748b; border: 1px solid #e2e8f0; }

        .btn-group { display: flex; gap: 6px; justify-content: flex-end; }
        .btn-icon { width: 30px; height: 30px; border: 1px solid #e2e8f0; background: #fff; color: #64748b; border-radius: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .btn-icon:hover { color: #3b82f6; border-color: #3b82f6; }
        .btn-icon.btn-danger:hover { color: #ef4444; border-color: #ef4444; background: #fef2f2; }

        .muted-icon { color: #94a3b8; }
        .placeholder-state { padding: 48px; text-align: center; color: #64748b; }
        .dot-spinner { width: 24px; height: 24px; border: 3px solid #f1f5f9; border-top-color: #3b82f6; border-radius: 50%; animation: rot 0.8s linear infinite; margin: 0 auto 12px; }
        @keyframes rot { to { transform: rotate(360deg); } }

        .error-banner { padding: 12px; background: #fef2f2; color: #dc2626; font-size: 13px; border-radius: 4px; margin-bottom: 24px; border: 1px solid #fee2e2; font-weight: 600; }

        @media (max-width: 800px) { .form-grid { grid-template-columns: 1fr; } .span2 { grid-column: span 1; } }
      `}</style>
    </div>
  );
};
