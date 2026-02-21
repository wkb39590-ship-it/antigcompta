import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getAdminToken } from '../../utils/adminTokenDecoder';

interface Agent {
  id: number;
  cabinet_id: number;
  username: string;
  email: string;
  nom: string;
  prenom: string;
  is_admin: boolean;
  is_active: boolean;
}

interface Cabinet {
  id: number;
  nom: string;
}

export const AdminAgents: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [cabinets, setCabinets] = useState<Cabinet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    nom: '',
    prenom: '',
    is_admin: false,
    cabinet_id: '',
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8888';

  const getErrorMessage = (err: any) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    return err.message || 'Une erreur est survenue';
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const token = getAdminToken();
    if (!token) {
      setError('Session expirée');
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const [agentsRes, cabsRes] = await Promise.all([
        axios.get(`${API_URL}/admin/agents`, {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get(`${API_URL}/admin/cabinets`, {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      setAgents(Array.isArray(agentsRes.data) ? agentsRes.data : []);
      setCabinets(Array.isArray(cabsRes.data) ? cabsRes.data : []);
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = getAdminToken();
    if (!token) {
      setError('Session expirée');
      return;
    }
    if (!formData.cabinet_id) {
      setError('Sélectionnez un cabinet');
      return;
    }
    try {
      await axios.post(
        `${API_URL}/admin/agents?cabinet_id=${formData.cabinet_id}`,
        {
          username: formData.username,
          email: formData.email,
          password: formData.password,
          nom: formData.nom,
          prenom: formData.prenom,
          is_admin: formData.is_admin,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setFormData({
        username: '',
        email: '',
        password: '',
        nom: '',
        prenom: '',
        is_admin: false,
        cabinet_id: '',
      });
      setShowForm(false);
      fetchData();
    } catch (err: any) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="aurora-page">
      <div className="aurora-page-header">
        <div>
          <h1 className="glass-text">Équipe Agents</h1>
          <p className="aurora-subtitle">Gérez les collaborateurs et leurs accès.</p>
        </div>
        <button
          className={`aurora-fab ${showForm ? 'active' : ''}`}
          onClick={() => { setShowForm(!showForm); setError(''); }}
        >
          {showForm ? '✕' : '+ Collaborateur'}
        </button>
      </div>

      {error && <div className="aurora-error-toast">{error}</div>}

      <div className="aurora-content-layout">
        {showForm && (
          <form className="aurora-glass-form aurora-card" onSubmit={handleCreateAgent}>
            <h2 className="glass-text">Nouvel Agent</h2>
            <div className="aurora-form-grid">
              <div className="aurora-input-group span-2">
                <label>Cabinet d'affectation</label>
                <select
                  className="aurora-select"
                  value={formData.cabinet_id}
                  onChange={(e) => setFormData({ ...formData, cabinet_id: e.target.value })}
                  required
                >
                  <option value="">Choisir un cabinet...</option>
                  {cabinets.map(cab => (
                    <option key={cab.id} value={cab.id}>{cab.nom}</option>
                  ))}
                </select>
              </div>
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
                <label>Username</label>
                <input
                  type="text"
                  placeholder="j.dupont"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>Email professionnel</label>
                <input
                  type="email"
                  placeholder="jean@cabinet.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>Mot de passe</label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group aurora-checkbox-group">
                <div className="aurora-toggle-wrapper">
                  <input
                    type="checkbox"
                    id="is_admin_check"
                    checked={formData.is_admin}
                    onChange={(e) => setFormData({ ...formData, is_admin: e.target.checked })}
                  />
                  <label htmlFor="is_admin_check">Droits administrateur</label>
                </div>
              </div>
            </div>
            <button type="submit" className="aurora-btn-submit">
              Créer le compte agent
            </button>
          </form>
        )}

        <div className="aurora-table-wrapper aurora-card">
          {loading ? (
            <div className="aurora-loader-inline">
              <div className="spinner-aurora"></div>
              <span>Extraction de l'équipe...</span>
            </div>
          ) : (
            <>
              {agents.length === 0 ? (
                <div className="aurora-empty">
                  <span>👥</span>
                  <p>Aucun agent n'est encore actif.</p>
                </div>
              ) : (
                <table className="aurora-table">
                  <thead>
                    <tr>
                      <th>Collaborateur</th>
                      <th>Cabinet</th>
                      <th>Identifiants</th>
                      <th>Rôle / État</th>
                      <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {agents.map((agent) => (
                      <tr key={agent.id} className="aurora-tr">
                        <td>
                          <div className="aurora-td-agent">
                            <div className="agent-avatar">{agent.prenom[0]}{agent.nom[0]}</div>
                            <div className="agent-info">
                              <span className="agent-name">{agent.prenom} {agent.nom}</span>
                              <span className="agent-id">ID: #{agent.id}</span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className="aurora-tag blue">
                            {cabinets.find(c => c.id === agent.cabinet_id)?.nom || 'Inconnu'}
                          </span>
                        </td>
                        <td>
                          <div className="aurora-ids">
                            <span className="user-tag">@{agent.username}</span>
                            <span className="email-tag">{agent.email}</span>
                          </div>
                        </td>
                        <td>
                          <div className="aurora-status-pills">
                            <span className={`aurora-pill ${agent.is_admin ? 'gold' : 'silver'}`}>
                              {agent.is_admin ? 'Admin' : 'Agent'}
                            </span>
                            <span className={`aurora-pill ${agent.is_active ? 'active' : 'inactive'}`}>
                              {agent.is_active ? 'Actif' : 'Bloqué'}
                            </span>
                          </div>
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <button className="aurora-btn-icon">⚙️</button>
                          <button className="aurora-btn-icon delete">🚫</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </>
          )}
        </div>
      </div>

      <style>{`
        .aurora-page { animation: pageEnter 0.6s ease-out; }
        @keyframes pageEnter { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .aurora-page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 40px; }
        .aurora-page-header h1 { font-size: 36px; font-weight: 900; margin: 0; letter-spacing: -1px; }
        .aurora-subtitle { color: var(--admin-text-dim); font-size: 14px; font-weight: 500; margin-top: 5px; }

        .aurora-fab {
          width: 160px; height: 48px; background: var(--admin-gradient); color: white;
          border: none; border-radius: 24px; font-weight: 800; cursor: pointer;
          transition: all 0.3s; box-shadow: 0 10px 20px var(--admin-accent-glow);
        }
        .aurora-fab:hover { transform: translateY(-2px); box-shadow: 0 15px 30px var(--admin-accent-glow); }
        .aurora-fab.active { background: #334155; box-shadow: none; }

        .aurora-error-toast {
          background: rgba(239, 68, 68, 0.1); color: #f87171; padding: 15px 25px;
          border-radius: 16px; border: 1px solid rgba(239, 68, 68, 0.2); margin-bottom: 25px;
        }

        .aurora-content-layout { display: grid; gap: 25px; }
        .aurora-glass-form { padding: 40px; }
        .aurora-glass-form h2 { margin: 0 0 30px 0; font-size: 20px; font-weight: 800; }

        .aurora-form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }
        .aurora-input-group.span-2 { grid-column: span 2; }
        
        .aurora-input-group label {
          display: block; font-size: 11px; font-weight: 800; color: var(--admin-text-dim);
          text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;
        }

        .aurora-input-group input, .aurora-select {
          width: 100%; padding: 15px; border-radius: 14px; border: 1px solid var(--admin-glass-border);
          background: rgba(255, 255, 255, 0.03); color: white; outline: none; transition: all 0.3s;
        }
        .aurora-input-group input:focus, .aurora-select:focus {
          border-color: var(--admin-accent); background: rgba(255, 255, 255, 0.06);
        }

        .aurora-checkbox-group { display: flex; align-items: center; padding: 10px 0; }
        .aurora-toggle-wrapper { display: flex; align-items: center; gap: 12px; cursor: pointer; }
        .aurora-toggle-wrapper input { width: 20px; height: 20px; cursor: pointer; accent-color: var(--admin-accent); }
        .aurora-toggle-wrapper label { margin: 0; text-transform: none; font-size: 14px; letter-spacing: 0; color: var(--admin-text); }

        .aurora-btn-submit {
          padding: 15px 30px; border-radius: 14px; border: none;
          background: var(--admin-gradient); color: white; font-weight: 800;
          cursor: pointer; transition: all 0.3s;
        }

        .aurora-table-wrapper { padding: 10px; }
        .aurora-table { width: 100%; border-collapse: collapse; }
        .aurora-table th {
          padding: 20px; font-size: 11px; font-weight: 800; color: var(--admin-text-dim);
          text-transform: uppercase; letter-spacing: 1px; border-bottom: 1px solid var(--admin-glass-border);
          text-align: left;
        }

        .aurora-tr:hover { background: rgba(255, 255, 255, 0.03); }
        .aurora-tr td { padding: 20px; color: var(--admin-text); border-bottom: 1px solid rgba(255, 255, 255, 0.03); }

        .aurora-td-agent { display: flex; align-items: center; gap: 15px; }
        .agent-avatar {
          width: 40px; height: 40px; border-radius: 12px; background: var(--admin-secondary);
          display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 14px; color: white;
        }
        .agent-info { display: flex; flex-direction: column; }
        .agent-name { font-weight: 800; font-size: 15px; }
        .agent-id { font-size: 11px; color: var(--admin-text-dim); }

        .aurora-tag.blue { background: rgba(59, 130, 246, 0.1); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.2); }

        .aurora-ids { display: flex; flex-direction: column; gap: 2px; }
        .user-tag { font-weight: 700; color: var(--admin-accent); font-size: 13px; }
        .email-tag { font-size: 12px; color: var(--admin-text-dim); }

        .aurora-status-pills { display: flex; gap: 8px; }
        .aurora-pill { padding: 4px 10px; border-radius: 8px; font-size: 10px; font-weight: 900; text-transform: uppercase; }
        .aurora-pill.gold { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
        .aurora-pill.silver { background: rgba(148, 163, 184, 0.1); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.2); }
        .aurora-pill.active { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
        .aurora-pill.inactive { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }

        .aurora-btn-icon { background: transparent; border: none; padding: 8px; cursor: pointer; border-radius: 8px; transition: all 0.2s; }
        .aurora-btn-icon:hover { background: rgba(255, 255, 255, 0.1); }

        .aurora-loader-inline { padding: 50px; display: flex; flex-direction: column; align-items: center; gap: 15px; }
        .spinner-aurora { width: 30px; height: 30px; border: 3px solid var(--admin-glass-border); border-top-color: var(--admin-accent); border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        @media (max-width: 768px) {
          .aurora-form-grid { grid-template-columns: 1fr; }
          .aurora-input-group.span-2 { grid-column: span 1; }
        }
      `}</style>
    </div>
  );
};
