import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { getAdminToken, getAdminUser } from '../../utils/adminTokenDecoder';
import {
  Users,
  UserPlus,
  X,
  Settings,
  UserX,
  Search,
  Filter,
  CheckCircle2,
  XCircle,
  Building
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
    societe_id: '', // Nouveau champ
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

      // Filtrage des agents
      const filteredAgents = (Array.isArray(agentsData) ? agentsData : [])
        .filter((a: any) => {
          // Si Super Admin, on ne montre que les administrateurs de cabinets (is_admin=true ET is_super_admin=false)
          if (isSuper) {
            return a.is_admin && !a.is_super_admin;
          }
          // Si Admin simple, on ne montre que les autres membres du cabinet
          return a.id !== adminUser?.id;
        });

      setAgents(filteredAgents);
      setCabinets(Array.isArray(cabsData) ? cabsData : []);
      setSocietes(Array.isArray(socData) ? socData : []);

      // Pré-remplir Cabinet pour Admin simple
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
        is_admin: isSuper ? true : formData.is_admin, // Forcer is_admin si Super Admin crée
      };

      if (formData.password) {
        payload.password = formData.password;
      }

      if (editingAgent) {
        await apiService.adminUpdateAgent(editingAgent.id, payload);
      } else {
        if (!formData.password) {
          setError('Le mot de passe est obligatoire pour un nouvel agent');
          return;
        }
        const newAgent = await apiService.adminCreateAgent(payload, formData.cabinet_id);

        // Nouvelle fonctionnalité: Assignation immédiate si société choisie
        if (formData.societe_id) {
          await apiService.adminAssignSocieteToAgent(
            Number(formData.cabinet_id),
            newAgent.id,
            Number(formData.societe_id)
          );
        }
      }
      setFormData({
        username: '',
        email: '',
        password: '',
        nom: '',
        prenom: '',
        is_admin: false,
        cabinet_id: isSuper ? '' : String(adminUser?.cabinet_id || ''),
        societe_id: '',
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
      username: agent.username,
      email: agent.email,
      password: '',
      nom: agent.nom,
      prenom: agent.prenom,
      is_admin: agent.is_admin,
      cabinet_id: String(agent.cabinet_id),
      societe_id: '', // On ne touche pas aux associations existantes ici
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
    <div className="aurora-page-v2">
      <div className="aurora-page-header">
        <div className="header-info">
          <h1 className="hero-title heading-font">
            {isSuper ? 'Administrateurs' : 'Agents de Comptabilité'}
          </h1>
          <p className="aurora-subtitle">
            {isSuper
              ? 'Supervision des accès root et administration des cabinets partenaires.'
              : 'Gérez l\'équipe opérationnelle et les habilitations de traitement.'}
          </p>
        </div>
        <button
          className={`aurora-btn-primary ${showForm ? 'active-form' : ''}`}
          onClick={() => {
            if (showForm) {
              setShowForm(false);
              setEditingAgent(null);
              setFormData({
                username: '',
                email: '',
                password: '',
                nom: '',
                prenom: '',
                is_admin: false,
                cabinet_id: isSuper ? '' : String(adminUser?.cabinet_id || ''),
                societe_id: '',
              });
            } else {
              setShowForm(true);
              if (!isSuper && adminUser?.cabinet_id) {
                setFormData(prev => ({ ...prev, cabinet_id: String(adminUser.cabinet_id) }));
              }
            }
            setError('');
          }}
        >
          {showForm ? <X size={20} /> : <><UserPlus size={18} /> <span>{isSuper ? 'Ajouter Admin' : 'Nouvel Agent'}</span></>}
        </button>
      </div>

      {error && <div className="aurora-error-toast">{error}</div>}

      <div className="aurora-content-grid">
        {showForm && (
          <form className="aurora-card premium-form" onSubmit={handleCreateAgent}>
            <div className="form-header">
              <h2 className="heading-font">{editingAgent ? 'Éditer l\'accès' : 'Création de compte'}</h2>
              <p>Remplissez les informations d'identification</p>
            </div>

            <div className="aurora-form-grid">
              <div className="aurora-input-group span-2">
                <label>Cabinet d'affectation</label>
                {isSuper ? (
                  <select
                    className="aurora-select"
                    value={formData.cabinet_id}
                    onChange={(e) => setFormData({ ...formData, cabinet_id: e.target.value, societe_id: '' })}
                    required
                  >
                    <option value="">Choisir un cabinet...</option>
                    {cabinets.map(cab => (
                      <option key={cab.id} value={cab.id}>{cab.nom}</option>
                    ))}
                  </select>
                ) : (
                  <div className="aurora-input-readonly">
                    {cabinets.find(c => String(c.id) === formData.cabinet_id)?.nom || (cabinets.length > 0 ? cabinets[0].nom : 'Chargement...')}
                  </div>
                )}
              </div>

              {!editingAgent && !isSuper && (
                <div className="aurora-input-group span-2">
                  <label>Assigner à une société (Facultatif)</label>
                  <select
                    className="aurora-select"
                    value={formData.societe_id}
                    onChange={(e) => setFormData({ ...formData, societe_id: e.target.value })}
                  >
                    <option value="">-- Affectation ultérieure --</option>
                    {societes
                      .filter(s => String(s.cabinet_id) === formData.cabinet_id)
                      .map(soc => (
                        <option key={soc.id} value={soc.id}>{soc.raison_sociale}</option>
                      ))
                    }
                  </select>
                </div>
              )}

              <div className="aurora-input-group">
                <label>Prénom</label>
                <input
                  type="text"
                  placeholder="Jean"
                  value={formData.prenom}
                  onChange={(e) => setFormData({ ...formData, prenom: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>Nom</label>
                <input
                  type="text"
                  placeholder="Dupont"
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>Nom d'utilisateur</label>
                <input
                  type="text"
                  placeholder="j.dupont"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>Email pro</label>
                <input
                  type="email"
                  placeholder="jean@cabinet.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>Mot de passe {editingAgent && '(laisser vide pour inchangé)'}</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required={!editingAgent}
                />
              </div>
              <div className="aurora-input-group aurora-checkbox-group">
                <div className="aurora-toggle-wrapper">
                  <div className="custom-checkbox">
                    <input
                      type="checkbox"
                      id="is_admin_check"
                      checked={formData.is_admin}
                      onChange={(e) => setFormData({ ...formData, is_admin: e.target.checked })}
                    />
                    <div className="checkbox-box"></div>
                  </div>
                  <label htmlFor="is_admin_check">Privilèges Administratifs</label>
                </div>
              </div>
            </div>

            <button type="submit" className="aurora-btn-primary full-width">
              {editingAgent ? 'Valider les modifications' : 'Créer l\'accès utilisateur'}
            </button>
          </form>
        )}

        <div className="aurora-card table-card">
          <div className="card-header-flex">
            <h2 className="heading-font">Liste des collaborateurs</h2>
            <div className="glass-pill">{agents.length} Actifs</div>
          </div>

          {loading ? (
            <div className="aurora-loader-inline">
              <div className="spinner-aurora"></div>
              <span>Extraction de la base agents...</span>
            </div>
          ) : (
            <div className="table-responsive">
              {agents.length === 0 ? (
                <div className="aurora-empty-v2">
                  <div className="empty-icon-box"><Users size={40} /></div>
                  <p>Aucun agent n'est enregistré dans ce périmètre.</p>
                </div>
              ) : (
                <table className="aurora-table-v2">
                  <thead>
                    <tr>
                      <th>Profil Utilisateur</th>
                      <th>Entité Cabinet</th>
                      <th>Contact & ID</th>
                      <th>Habilitations</th>
                      <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {agents.map((agent) => (
                      <tr key={agent.id}>
                        <td>
                          <div className="user-profile-td">
                            <div className="user-avatar-v2">{agent.prenom[0]}{agent.nom[0]}</div>
                            <div className="user-name-box">
                              <span className="name">{agent.prenom} {agent.nom}</span>
                              <span className="username">@{agent.username}</span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div className="cabinet-tag">
                            <Building size={14} />
                            {cabinets.find(c => c.id === agent.cabinet_id)?.nom || 'Cabinet Inconnu'}
                          </div>
                        </td>
                        <td>
                          <div className="contact-td">
                            <div className="email">{agent.email}</div>
                            <div className="id-tag">REF: {agent.id}</div>
                          </div>
                        </td>
                        <td>
                          <div className="perms-td">
                            <span className={`role-pill ${agent.is_super_admin || agent.is_admin ? 'gold' : 'silver'}`}>
                              {agent.is_super_admin ? 'Super' : (agent.is_admin ? 'Admin' : 'Agent')}
                            </span>
                            <span className={`status-pill ${agent.is_active ? 'active' : 'inactive'}`}>
                              {agent.is_active ? 'Actif' : 'Bloqué'}
                            </span>
                          </div>
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <div className="action-buttons">
                            <button className="icon-btn edit" title="Paramètres" onClick={() => handleEditClick(agent)}>
                              <Settings size={18} />
                            </button>
                            <button className="icon-btn del" title="Révoquer" onClick={() => handleDeleteAgent(agent.id)}>
                              <UserX size={18} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </div>
      </div>

      <style>{`
        .aurora-page-v2 { animation: pageFadeIn 0.8s ease-out; padding-bottom: 80px; }
        
        .aurora-page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 35px; }
        .hero-title { font-size: 38px; font-weight: 800; margin: 0; letter-spacing: -1.5px; }
        .aurora-subtitle { color: var(--text3); font-size: 14px; font-weight: 500; margin-top: 4px; }

        .aurora-btn-primary.active-form { background: #334155; box-shadow: none; }
        .full-width { width: 100%; margin-top: 20px; }

        .aurora-content-grid { display: flex; flex-direction: column; gap: 30px; }

        .premium-form { padding: 35px; animation: slideDown 0.4s ease-out; }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

        .form-header { margin-bottom: 30px; }
        .form-header h2 { font-size: 20px; font-weight: 800; margin: 0; }
        .form-header p { font-size: 13px; color: var(--text3); margin-top: 4px; }

        .aurora-form-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .span-2 { grid-column: span 2; }

        .aurora-input-group label {
          display: block; font-size: 11px; font-weight: 800; color: var(--text3);
          text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;
        }

        .aurora-input-group input, .aurora-select {
          width: 100%; padding: 14px 16px; border-radius: 14px; border: 1px solid var(--border);
          background: rgba(255, 255, 255, 0.5); color: var(--text); outline: none; transition: all 0.3s;
          font-family: 'Inter', sans-serif; font-size: 14px;
        }
        .aurora-input-group input:focus, .aurora-select:focus {
          border-color: var(--accent); background: white; box-shadow: 0 0 10px rgba(99, 102, 241, 0.1);
        }

        .aurora-input-readonly {
          padding: 14px 16px; border-radius: 14px; background: rgba(99, 102, 241, 0.05);
          color: var(--accent); font-weight: 700; font-size: 14px; border: 1px dashed var(--accent);
        }

        .aurora-toggle-wrapper { display: flex; align-items: center; gap: 12px; }
        .custom-checkbox { position: relative; width: 20px; height: 20px; }
        .custom-checkbox input { position: absolute; opacity: 0; cursor: pointer; height: 0; width: 0; }
        .checkbox-box { position: absolute; top: 0; left: 0; height: 20px; width: 20px; background: #eee; border-radius: 6px; transition: all 0.3s; }
        .custom-checkbox input:checked ~ .checkbox-box { background: var(--accent); }
        .checkbox-box:after { content: ""; position: absolute; display: none; left: 7px; top: 3px; width: 5px; height: 10px; border: solid white; border-width: 0 2px 2px 0; transform: rotate(45deg); }
        .custom-checkbox input:checked ~ .checkbox-box:after { display: block; }

        .table-card { padding: 30px; }
        .card-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
        .card-header-flex h2 { font-size: 20px; font-weight: 800; margin: 0; }

        .table-responsive { overflow-x: auto; }
        .aurora-table-v2 { width: 100%; border-collapse: collapse; }
        .aurora-table-v2 th {
          text-align: left; padding: 15px 20px; font-size: 11px; font-weight: 800;
          color: var(--text3); text-transform: uppercase; letter-spacing: 1.5px;
          border-bottom: 1px solid var(--border);
        }
        
        .aurora-table-v2 tr { transition: background 0.3s; }
        .aurora-table-v2 tr:hover { background: rgba(99, 102, 241, 0.02); }
        .aurora-table-v2 td { padding: 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }

        .user-profile-td { display: flex; align-items: center; gap: 15px; }
        .user-avatar-v2 {
          width: 44px; height: 44px; border-radius: 12px; 
          background: linear-gradient(145deg, #6366f1, #4338ca);
          color: white; display: flex; align-items: center; justify-content: center;
          font-weight: 800; font-size: 15px; 
          box-shadow: 0 8px 15px -3px rgba(99, 102, 241, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .user-name-box { display: flex; flex-direction: column; }
        .user-name-box .name { font-weight: 700; color: var(--text); font-size: 15px; }
        .user-name-box .username { font-size: 12px; color: var(--text3); font-weight: 600; }

        .cabinet-tag {
          display: inline-flex; align-items: center; gap: 8px;
          padding: 6px 12px; background: #f8fafc; border: 1px solid #e2e8f0;
          border-radius: 10px; font-size: 12px; font-weight: 700; color: var(--text2);
        }

        .contact-td .email { font-size: 13px; font-weight: 600; color: var(--text2); }
        .contact-td .id-tag { font-size: 10px; font-weight: 800; color: var(--text3); margin-top: 2px; }

        .perms-td { display: flex; gap: 8px; }
        .role-pill { padding: 4px 10px; border-radius: 8px; font-size: 10px; font-weight: 800; text-transform: uppercase; }
        .role-pill.gold { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
        .role-pill.silver { background: rgba(148, 163, 184, 0.1); color: #94a3b8; }
        
        .status-pill { padding: 4px 10px; border-radius: 8px; font-size: 10px; font-weight: 800; text-transform: uppercase; }
        .status-pill.active { background: rgba(16, 185, 129, 0.1); color: #10b981; }
        .status-pill.inactive { background: rgba(239, 68, 68, 0.1); color: #ef4444; }

        .action-buttons { display: flex; gap: 8px; justify-content: flex-end; }
        .icon-btn {
          width: 36px; height: 36px; border-radius: 10px; border: 1px solid #e2e8f0;
          background: white; color: var(--text3); cursor: pointer; transition: all 0.3s;
          display: flex; align-items: center; justify-content: center;
        }
        .icon-btn:hover { border-color: var(--accent); color: var(--accent); background: rgba(99, 102, 241, 0.05); transform: translateY(-2px); }
        .icon-btn.del:hover { border-color: var(--danger); color: var(--danger); background: rgba(239, 68, 68, 0.05); }

        .aurora-empty-v2 { padding: 60px 0; text-align: center; color: var(--text3); }
        .empty-icon-box { margin-bottom: 20px; opacity: 0.2; }

        .aurora-loader-inline { padding: 60px; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 15px; color: var(--text3); }
        .spinner-aurora { width: 32px; height: 32px; border: 3px solid #f1f5f9; border-top-color: var(--accent); border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        @media (max-width: 900px) {
          .aurora-form-grid { grid-template-columns: 1fr; }
          .span-2 { grid-column: span 1; }
        }
      `}</style>
    </div>
  );
};
