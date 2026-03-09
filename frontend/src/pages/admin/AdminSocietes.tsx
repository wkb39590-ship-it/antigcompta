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
  Building2
} from 'lucide-react';

interface Societe {
  id: number;
  cabinet_id: number;
  raison_sociale: string;
  ice: string;
  if_fiscal: string;
  rc: string;
  adresse: string;
}

interface Cabinet {
  id: number;
  nom: string;
}

export const AdminSocietes: React.FC = () => {
  const navigate = useNavigate();
  const [societes, setSocietes] = useState<Societe[]>([]);
  const [cabinets, setCabinets] = useState<Cabinet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingSociete, setEditingSociete] = useState<Societe | null>(null);
  const [formData, setFormData] = useState({
    raison_sociale: '',
    ice: '',
    if_fiscal: '',
    rc: '',
    adresse: '',
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

      // Si Admin simple, pré-sélectionner son cabinet
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

      // Appel à select-societe pour générer le session_token
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

        // Rediriger vers le dashboard utilisateur
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

  return (
    <div className="aurora-page-v2">
      <div className="aurora-page-header">
        <div className="header-info">
          <h1 className="hero-title heading-font">Gestion des Sociétés</h1>
          <p className="aurora-subtitle">Pilotage des entités juridiques et configuration des accès client.</p>
        </div>
        <button
          className={`aurora-btn-primary ${showForm ? 'active-form' : ''}`}
          onClick={() => {
            if (showForm) {
              setShowForm(false);
              setEditingSociete(null);
              setFormData({
                raison_sociale: '',
                ice: '',
                if_fiscal: '',
                rc: '',
                adresse: '',
                cabinet_id: '',
              });
            } else {
              setShowForm(true);
              if (!isSuper && adminUser?.cabinet_id) {
                setFormData((prev) => ({ ...prev, cabinet_id: String(adminUser.cabinet_id) }));
              }
            }
            setError('');
          }}
        >
          {showForm ? <X size={20} /> : <><PlusCircle size={18} /> <span>Nouvelle Société</span></>}
        </button>
      </div>

      {error && <div className="aurora-error-toast">{error}</div>}

      <div className="aurora-content-grid">
        {showForm && (
          <form className="aurora-card premium-form" onSubmit={handleCreateSociete}>
            <div className="form-header">
              <h2 className="heading-font">{editingSociete ? 'Édition Structure' : 'Initialisation Entreprise'}</h2>
              <p>Paramètres fiscaux et identification légale</p>
            </div>

            <div className="aurora-form-grid">
              <div className="aurora-input-group span-2">
                <label>Cabinet de rattachement</label>
                {isSuper ? (
                  <select
                    className="aurora-select"
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
                  <div className="aurora-input-readonly">
                    {cabinets.find((c: Cabinet) => String(c.id) === formData.cabinet_id)?.nom || (cabinets.length > 0 ? cabinets[0].nom : 'Chargement cabinet...')}
                  </div>
                )}
              </div>
              <div className="aurora-input-group">
                <label>Raison Sociale</label>
                <input
                  type="text"
                  placeholder="Ex: SARL Optima"
                  value={formData.raison_sociale}
                  onChange={(e) => setFormData({ ...formData, raison_sociale: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>ICE (Identifiant Commun)</label>
                <input
                  type="text"
                  placeholder="00234..."
                  value={formData.ice}
                  onChange={(e) => setFormData({ ...formData, ice: e.target.value })}
                />
              </div>
              <div className="aurora-input-group">
                <label>IF (Identifiant Fiscal)</label>
                <input
                  type="text"
                  placeholder="ID Fiscal"
                  value={formData.if_fiscal}
                  onChange={(e) => setFormData({ ...formData, if_fiscal: e.target.value })}
                />
              </div>
              <div className="aurora-input-group">
                <label>RC (Registre Commerce)</label>
                <input
                  type="text"
                  placeholder="N° Registre"
                  value={formData.rc}
                  onChange={(e) => setFormData({ ...formData, rc: e.target.value })}
                />
              </div>
              <div className="aurora-input-group span-2">
                <label>Adresse d'Exploitation</label>
                <input
                  type="text"
                  placeholder="Siège social, Ville"
                  value={formData.adresse}
                  onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
                />
              </div>
            </div>

            <button type="submit" className="aurora-btn-primary full-width">
              {editingSociete ? 'Sauvegarder les changements' : 'Activer la structure'}
            </button>
          </form>
        )}

        <div className="aurora-card table-card">
          <div className="card-header-flex">
            <h2 className="heading-font">Sociétés sous gestion</h2>
            <div className="glass-pill">{societes.length} Entités</div>
          </div>

          {loading ? (
            <div className="aurora-loader-inline">
              <div className="spinner-aurora"></div>
              <span>Synchronisation des entités...</span>
            </div>
          ) : (
            <div className="table-responsive">
              {societes.length === 0 ? (
                <div className="aurora-empty-v2">
                  <div className="empty-icon-box"><Building size={40} /></div>
                  <p>Aucune société rattachée pour le moment.</p>
                </div>
              ) : (
                <table className="aurora-table-v2">
                  <thead>
                    <tr>
                      <th>Dénomination Sociale</th>
                      <th>Cabinet Référent</th>
                      <th>Données Fiscales</th>
                      <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {societes.map((societe: Societe) => (
                      <tr key={societe.id}>
                        <td>
                          <div className="soc-profile-td">
                            <div className="soc-avatar-v2">{societe.raison_sociale[0]}</div>
                            <div className="soc-name-box">
                              <span className="name">{societe.raison_sociale}</span>
                              <span className="address-line">{societe.adresse || 'Adresse non spécifiée'}</span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div className="cabinet-tag-v2">
                            <Fingerprint size={12} />
                            {cabinets.find((c: Cabinet) => c.id === societe.cabinet_id)?.nom || 'Cabinet Inconnu'}
                          </div>
                        </td>
                        <td>
                          <div className="fiscal-td">
                            <div className="ice-line">ICE: {societe.ice || '---'}</div>
                            <div className="if-line">IF: {societe.if_fiscal || '---'}</div>
                          </div>
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <div className="action-buttons-flex">
                            <button
                              className="aurora-btn-action"
                              onClick={() => handleManageSociete(societe)}
                            >
                              <LayoutDashboard size={14} /> <span>Ouvrir</span>
                            </button>
                            <button className="icon-btn edit" title="Modifier" onClick={() => handleEditClick(societe)}>
                              <Pencil size={16} />
                            </button>
                            <button className="icon-btn del" title="Supprimer" onClick={() => deleteSociete(societe.id)}>
                              <Trash2 size={16} />
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
        .aurora-page-v2 { animation: fadeIn 0.8s ease-out; padding-bottom: 80px; }
        
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

        .soc-profile-td { display: flex; align-items: center; gap: 15px; }
        .soc-avatar-v2 {
          width: 44px; height: 44px; border-radius: 12px; 
          background: linear-gradient(145deg, #10b981, #047857);
          color: white; display: flex; align-items: center; justify-content: center;
          font-weight: 800; font-size: 16px; 
          box-shadow: 0 8px 15px -3px rgba(16, 185, 129, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .soc-name-box { display: flex; flex-direction: column; }
        .soc-name-box .name { font-weight: 700; color: var(--text); font-size: 15px; }
        .soc-name-box .address-line { font-size: 12px; color: var(--text3); font-weight: 600; margin-top: 2px; }

        .cabinet-tag-v2 {
          display: inline-flex; align-items: center; gap: 8px;
          padding: 6px 12px; background: #f8fafc; border: 1px solid #e2e8f0;
          border-radius: 10px; font-size: 12px; font-weight: 700; color: var(--text2);
        }

        .fiscal-td { display: flex; flex-direction: column; gap: 2px; }
        .ice-line, .if-line { font-size: 12px; font-weight: 700; color: var(--text3); }

        .action-buttons-flex { display: flex; gap: 8px; justify-content: flex-end; align-items: center; }
        
        .aurora-btn-action {
          display: inline-flex; align-items: center; gap: 6px;
          padding: 8px 14px; 
          background: linear-gradient(135deg, #1e293b, #0f172a);
          color: white;
          border-radius: 10px; border: none; font-size: 12px; font-weight: 800;
          cursor: pointer; transition: all 0.3s; 
          box-shadow: 0 5px 15px rgba(0,0,0,0.2), inset 0 2px 4px rgba(255,255,255,0.1);
        }
        .aurora-btn-action:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.3); }

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
