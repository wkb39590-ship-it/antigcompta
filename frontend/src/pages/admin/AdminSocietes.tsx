import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../../api';
import { getAdminUser } from '../../utils/adminTokenDecoder';
import { API_CONFIG } from '../../config/apiConfig';
import {
  Building,
  PlusCircle,
  X,
  LayoutDashboard,
  Pencil,
  Trash2,
  MapPin,
  Fingerprint,
  Building2,
  KeyRound,
  UserPlus,
  Users
} from 'lucide-react';

interface Societe {
  id: number;
  cabinet_id: number;
  raison_sociale: string;
  ice: string;
  if_fiscal: string;
  rc: string;
  adresse: string;
  cnss: string;
}

interface Cabinet {
  id: number;
  nom: string;
}

interface ClientUser {
  id: number;
  username: string;
  email: string;
  nom: string;
  prenom: string;
  is_active: boolean;
}

export const AdminSocietes: React.FC = () => {
  const navigate = useNavigate();
  const [societes, setSocietes] = useState<Societe[]>([]);
  const [cabinets, setCabinets] = useState<Cabinet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingSociete, setEditingSociete] = useState<Societe | null>(null);
  const [clientModal, setClientModal] = useState<Societe | null>(null);
  const [clients, setClients] = useState<ClientUser[]>([]);
  const [clientLoading, setClientLoading] = useState(false);
  const [clientForm, setClientForm] = useState({ username: '', email: '', password: '', nom: '', prenom: '' });
  const [clientError, setClientError] = useState('');
  const [formData, setFormData] = useState({
    raison_sociale: '',
    ice: '',
    if_fiscal: '',
    rc: '',
    adresse: '',
    cnss: '',
    cabinet_id: '',
  });

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
      const [socData, cabData] = await Promise.all([
        apiService.adminListSocietes(),
        isSuper ? apiService.adminListCabinets() : Promise.resolve(JSON.parse(localStorage.getItem('cabinets') || '[]'))
      ]);
      setSocietes(Array.isArray(socData) ? socData : []);
      setCabinets(Array.isArray(cabData) ? cabData : []);

      if (!isSuper && adminUser?.cabinet_id) {
        setFormData((prev) => ({ ...prev, cabinet_id: String(adminUser.cabinet_id) }));
      }
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSociete = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.cabinet_id) {
      setError('Veuillez sélectionner un cabinet');
      return;
    }

    try {
      const payload = {
        raison_sociale: formData.raison_sociale,
        ice: formData.ice,
        if_fiscal: formData.if_fiscal,
        rc: formData.rc,
        adresse: formData.adresse,
        cnss: formData.cnss,
      };

      if (editingSociete) {
        await apiService.adminUpdateSociete(editingSociete.id, payload);
      } else {
        await apiService.adminCreateSociete(payload, formData.cabinet_id);
      }
      setFormData({
        raison_sociale: '',
        ice: '',
        if_fiscal: '',
        rc: '',
        adresse: '',
        cnss: '',
        cabinet_id: '',
      });
      setShowForm(false);
      setEditingSociete(null);
      fetchData();
    } catch (err: any) {
      setError(getErrorMessage(err));
    }
  };

  const handleEditClick = (societe: Societe) => {
    setEditingSociete(societe);
    setFormData({
      raison_sociale: societe.raison_sociale,
      ice: societe.ice || '',
      if_fiscal: societe.if_fiscal || '',
      rc: societe.rc || '',
      adresse: societe.adresse || '',
      cnss: societe.cnss || '',
      cabinet_id: String(societe.cabinet_id),
    });
    setShowForm(true);
  };

  const deleteSociete = async (id: number) => {
    if (!window.confirm('Supprimer cette société ?')) return;
    try {
      await apiService.adminDeleteSociete(id);
      fetchData();
    } catch (err: any) {
      setError("Erreur de suppression");
    }
  }

  const handleManageSociete = async (societe: Societe) => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('Token manquant');

      const response = await fetch(`${API_CONFIG.AUTH.SELECT_SOCIETE}?token=${encodeURIComponent(token)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cabinet_id: societe.cabinet_id,
          societe_id: societe.id
        })
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('session_token', data.session_token);
        localStorage.setItem('current_societe_id', String(societe.id));
        localStorage.setItem('current_cabinet_id', String(societe.cabinet_id));
        window.location.href = '/dashboard';
      } else {
        throw new Error('Échec du basculement vers la société');
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const openClientModal = async (societe: Societe) => {
    setClientModal(societe);
    setClientError('');
    setClientForm({ username: '', email: '', password: '', nom: '', prenom: '' });
    setClientLoading(true);
    try {
      const data = await apiService.adminListClientUsers(societe.id);
      setClients(Array.isArray(data) ? data : []);
    } catch {
      setClients([]);
    } finally {
      setClientLoading(false);
    }
  };

  const handleCreateClient = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!clientModal) return;
    setClientError('');
    try {
      await apiService.adminCreateClientUser(clientModal.id, clientForm);
      setClientForm({ username: '', email: '', password: '', nom: '', prenom: '' });
      const data = await apiService.adminListClientUsers(clientModal.id);
      setClients(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setClientError(err.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  const handleDeleteClient = async (clientId: number) => {
    if (!window.confirm('Révoquer cet accès client ?')) return;
    try {
      await apiService.adminDeleteClientUser(clientId);
      setClients(prev => prev.filter(c => c.id !== clientId));
    } catch (err: any) {
      setClientError(err.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  return (
    <div className="societes-page">
      <div className="page-header">
        <div className="header-info">
          <h1 className="page-title">Gestion des Sociétés</h1>
          <p className="page-subtitle">Pilotage des entités juridiques et configuration des accès client.</p>
        </div>
        <button
          className={`btn-primary ${showForm ? 'form-active' : ''}`}
          onClick={() => {
            if (showForm) {
              setShowForm(false);
              setEditingSociete(null);
              setFormData({ raison_sociale: '', ice: '', if_fiscal: '', rc: '', adresse: '', cnss: '', cabinet_id: '' });
            } else {
              setShowForm(true);
              if (!isSuper && adminUser?.cabinet_id) {
                setFormData((prev) => ({ ...prev, cabinet_id: String(adminUser.cabinet_id) }));
              }
            }
            setError('');
          }}
        >
          {showForm ? <X size={18} /> : <><PlusCircle size={16} /> <span>Nouvelle Société</span></>}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="content-layout">
        {showForm && (
          <form className="pro-card side-form" onSubmit={handleCreateSociete}>
            <div className="form-header">
              <h3>{editingSociete ? 'Éditer la structure' : 'Nouvelle Entreprise'}</h3>
              <p>Identifiants légaux et fiscaux</p>
            </div>

            <div className="form-grid">
              <div className="field-group span2">
                <label>Cabinet de rattachement</label>
                {isSuper ? (
                  <select
                    className="pro-select"
                    value={formData.cabinet_id}
                    onChange={(e) => setFormData({ ...formData, cabinet_id: e.target.value })}
                    required
                  >
                    <option value="">Sélectionner un cabinet...</option>
                    {cabinets.map((cab: Cabinet) => (
                      <option key={cab.id} value={cab.id}>{cab.nom}</option>
                    ))}
                  </select>
                ) : (
                  <div className="pro-input-read">
                    {cabinets.find((c: Cabinet) => String(c.id) === formData.cabinet_id)?.nom || 'Cabinet local'}
                  </div>
                )}
              </div>
              <div className="field-group">
                <label>Raison Sociale</label>
                <input
                  className="pro-input"
                  type="text"
                  placeholder="Ex: SARL Optima"
                  value={formData.raison_sociale}
                  onChange={(e) => setFormData({ ...formData, raison_sociale: e.target.value })}
                  required
                />
              </div>
              <div className="field-group">
                <label>ICE (Identifiant Commun)</label>
                <input
                  className="pro-input"
                  type="text"
                  placeholder="00123..."
                  value={formData.ice}
                  onChange={(e) => setFormData({ ...formData, ice: e.target.value })}
                />
              </div>
              <div className="field-group">
                <label>IF (Identifiant Fiscal)</label>
                <input
                  className="pro-input"
                  type="text"
                  placeholder="ID Fiscal"
                  value={formData.if_fiscal}
                  onChange={(e) => setFormData({ ...formData, if_fiscal: e.target.value })}
                />
              </div>
              <div className="field-group">
                <label>RC (Registre Commerce)</label>
                <input
                  className="pro-input"
                  type="text"
                  placeholder="N° Registre"
                  value={formData.rc}
                  onChange={(e) => setFormData({ ...formData, rc: e.target.value })}
                />
              </div>
            </div>

            <button type="submit" className="btn-primary full-w">
              {editingSociete ? 'Enregistrer les modifications' : 'Créer la société'}
            </button>
          </form>
        )}

        <div className="pro-card table-section">
          <div className="section-header">
            <div className="header-label">
              <Building2 size={16} className="muted-icon" />
              <span>Sociétés enregistrées</span>
            </div>
            <div className="entity-count">{societes.length} Entités</div>
          </div>

          {loading ? (
            <div className="placeholder-state">
              <div className="dot-spinner"></div>
              <span>Synchronisation en cours...</span>
            </div>
          ) : societes.length === 0 ? (
            <div className="placeholder-state empty">
              <Building size={48} className="muted-icon" />
              <p>Aucune société configurée.</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="pro-table">
                <thead>
                  <tr>
                    <th>Dénomination</th>
                    <th>Cabinet</th>
                    <th>Identifiants</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {societes.map((societe: Societe) => (
                    <tr key={societe.id}>
                      <td>
                        <div className="company-cell">
                          <div className="company-icon">{societe.raison_sociale[0]}</div>
                          <div className="company-info">
                            <span className="company-name">{societe.raison_sociale}</span>
                            <span className="company-address">{societe.adresse || 'Siège non localisé'}</span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div className="cabinet-label">
                          <Fingerprint size={12} className="muted-icon" />
                          {cabinets.find((c: Cabinet) => c.id === societe.cabinet_id)?.nom || 'Cabinet...'}
                        </div>
                      </td>
                      <td>
                        <div className="fiscal-labels">
                          <span>ICE: {societe.ice || '-'}</span>
                          <span>IF: {societe.if_fiscal || '-'}</span>
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div className="btn-group">
                          <button className="btn-action-sm btn-open" onClick={() => handleManageSociete(societe)}>
                            <LayoutDashboard size={14} /> <span>Ouvrir</span>
                          </button>
                          <button className="btn-icon" title="Accès client" onClick={() => openClientModal(societe)}>
                            <KeyRound size={14} />
                          </button>
                          <button className="btn-icon" title="Éditer" onClick={() => handleEditClick(societe)}>
                            <Pencil size={14} />
                          </button>
                          <button className="btn-icon btn-danger" title="Supprimer" onClick={() => deleteSociete(societe.id)}>
                            <Trash2 size={14} />
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

      {/* === Modal Accès Client === */}
      {clientModal && (
        <div className="modal-backdrop" onClick={() => setClientModal(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-title">
                <KeyRound size={18} className="color-accent" />
                <div>
                  <h4>Gestion des Accès</h4>
                  <p>{clientModal.raison_sociale}</p>
                </div>
              </div>
              <button className="btn-close" onClick={() => setClientModal(null)}>
                <X size={18} />
              </button>
            </div>

            <div className="modal-body">
              <div className="client-section-label">Comptes Clients Actifs</div>
              {clientLoading ? (
                <div className="modal-loading">Chargement des accès...</div>
              ) : clients.length === 0 ? (
                <div className="modal-empty">Aucun utilisateur client rattaché.</div>
              ) : (
                <div className="client-list">
                  {clients.map(c => (
                    <div key={c.id} className="client-card">
                      <div className="client-avatar-square">{c.username[0].toUpperCase()}</div>
                      <div className="client-data">
                        <span className="client-full">@{c.username} ({c.prenom} {c.nom})</span>
                        <span className="client-email">{c.email}</span>
                      </div>
                      <button className="btn-icon-sm btn-danger" onClick={() => handleDeleteClient(c.id)}>
                        <Trash2 size={12} />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              <form className="client-creation-form" onSubmit={handleCreateClient}>
                <div className="form-sub-label"><UserPlus size={14} /> Ajouter un accès utilisateur</div>
                {clientError && <div className="client-error-box">{clientError}</div>}
                <div className="client-inputs-grid">
                  <input placeholder="Prénom" value={clientForm.prenom} onChange={e => setClientForm({...clientForm, prenom: e.target.value})}/>
                  <input placeholder="Nom" value={clientForm.nom} onChange={e => setClientForm({...clientForm, nom: e.target.value})}/>
                  <input placeholder="Username *" required value={clientForm.username} onChange={e => setClientForm({...clientForm, username: e.target.value})}/>
                  <input placeholder="Email *" type="email" required value={clientForm.email} onChange={e => setClientForm({...clientForm, email: e.target.value})}/>
                  <input placeholder="Mot de passe *" type="password" required value={clientForm.password} onChange={e => setClientForm({...clientForm, password: e.target.value})} className="span2"/>
                </div>
                <button type="submit" className="btn-primary-sm full-w">Créer l'accès client</button>
              </form>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .societes-page { padding: 24px; background: #fafafa; min-height: 100vh; font-family: 'Inter', sans-serif; }

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
        .btn-primary-sm { 
          background: #3b82f6; color: white; border: none; padding: 12px;
          border-radius: 4px; font-weight: 600; font-size: 13px; cursor: pointer;
        }
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

        .field-group label { display: block; font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 6px; }
        .pro-input, .pro-select {
          width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 4px;
          font-size: 14px; background: #fff; outline: none; transition: border-color 0.2s;
        }
        .pro-input:focus, .pro-select:focus { border-color: #3b82f6; }
        .pro-input-read { padding: 10px 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; color: #3b82f6; font-weight: 600; font-size: 14px; }

        .table-section { padding: 0; overflow: hidden; }
        .section-header { padding: 16px 20px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
        .header-label { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; color: #334155; }
        .entity-count { font-size: 11px; font-weight: 700; color: #3b82f6; background: #eff6ff; padding: 2px 8px; border-radius: 4px; border: 1px solid #dbeafe; }

        .table-wrapper { overflow-x: auto; }
        .pro-table { width: 100%; border-collapse: collapse; }
        .pro-table th { text-align: left; padding: 12px 20px; font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #e2e8f0; }
        .pro-table td { padding: 14px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
        .pro-table tr:hover { background: #fafafa; }

        .company-cell { display: flex; align-items: center; gap: 12px; }
        .company-icon { width: 32px; height: 32px; background: #10b981; color: white; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
        .company-name { display: block; font-weight: 600; color: #1e293b; font-size: 14px; }
        .company-address { display: block; font-size: 12px; color: #64748b; margin-top: 1px; }

        .cabinet-label { display: inline-flex; align-items: center; gap: 6px; padding: 4px 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 12px; font-weight: 600; color: #475569; }
        .fiscal-labels { display: flex; flex-direction: column; gap: 2px; font-size: 11px; font-weight: 600; color: #64748b; }
        .muted-icon { color: #94a3b8; }

        .btn-group { display: flex; gap: 6px; justify-content: flex-end; }
        .btn-action-sm { 
          display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px;
          background: #1e293b; color: white; border-radius: 4px; border: none;
          font-size: 12px; font-weight: 600; cursor: pointer;
        }
        .btn-icon { width: 30px; height: 30px; border: 1px solid #e2e8f0; background: #fff; color: #64748b; border-radius: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
        .btn-icon:hover { color: #3b82f6; border-color: #3b82f6; }
        .btn-icon.btn-danger:hover { color: #ef4444; border-color: #ef4444; background: #fef2f2; }

        .modal-backdrop { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(2px); z-index: 1000; display: flex; align-items: center; justify-content: center; animation: fadeIn 0.15s; }
        .modal-content { background: #fff; border-radius: 6px; width: 500px; max-width: 90vw; max-height: 85vh; overflow-y: auto; box-shadow: 0 10px 25px rgba(0,0,0,0.1); animation: popScale 0.2s ease-out; }
        @keyframes popScale { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }

        .modal-header { padding: 20px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; }
        .modal-title { display: flex; align-items: center; gap: 12px; }
        .modal-title h4 { margin: 0; font-size: 16px; font-weight: 700; color: #1e293b; }
        .modal-title p { margin: 0; font-size: 12px; color: #64748b; }
        .color-accent { color: #3b82f6; }
        .btn-close { background: none; border: none; color: #94a3b8; cursor: pointer; }

        .modal-body { padding: 20px; }
        .client-section-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 12px; }
        .client-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 24px; }
        .client-card { display: flex; align-items: center; gap: 12px; padding: 10px; border: 1px solid #f1f5f9; border-radius: 4px; background: #fafafa; }
        .client-avatar-square { width: 32px; height: 32px; background: #3b82f6; color: white; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 13px; }
        .client-data { flex: 1; overflow: hidden; }
        .client-full { display: block; font-size: 13px; font-weight: 600; color: #1e293b; }
        .client-email { font-size: 11px; color: #64748b; }

        .client-creation-form { border-top: 1px solid #e2e8f0; padding-top: 20px; }
        .form-sub-label { font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }
        .client-inputs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .client-inputs-grid input { padding: 8px 10px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 13px; font-family: inherit; }
        .client-error-box { padding: 8px; background: #fef2f2; color: #dc2626; font-size: 12px; border-radius: 4px; margin-bottom: 10px; border: 1px solid #fee2e2; }

        .placeholder-state { padding: 48px; text-align: center; color: #64748b; }
        .dot-spinner { width: 24px; height: 24px; border: 3px solid #f1f5f9; border-top-color: #3b82f6; border-radius: 50%; animation: rot 0.8s linear infinite; margin: 0 auto 12px; }
        @keyframes rot { to { transform: rotate(360deg); } }

        @media (max-width: 800px) { .form-grid { grid-template-columns: 1fr; } .span2 { grid-column: span 1; } }
      `}</style>
    </div>
  );
};
