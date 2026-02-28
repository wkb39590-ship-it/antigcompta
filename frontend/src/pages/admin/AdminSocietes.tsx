import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../../api';
import { getAdminUser } from '../../utils/adminTokenDecoder';
import { API_CONFIG } from '../../config/apiConfig';

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
    <div className="aurora-page">
      <div className="aurora-page-header">
        <div>
          <h1 className="glass-text">Gestion des Sociétés</h1>
          <p className="aurora-subtitle">Pilotez les entités juridiques par cabinet.</p>
        </div>
        <button
          className={`aurora-fab ${showForm ? 'active' : ''}`}
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
              // Pré-remplir pour Admin simple
              if (!isSuper && adminUser?.cabinet_id) {
                setFormData((prev) => ({ ...prev, cabinet_id: String(adminUser.cabinet_id) }));
              }
            }
            setError('');
          }}
        >
          {showForm ? '✕' : '+ Société'}
        </button>
      </div>

      {error && <div className="aurora-error-toast">{error}</div>}

      <div className="aurora-content-layout">
        {showForm && (
          <form className="aurora-glass-form aurora-card" onSubmit={handleCreateSociete}>
            <h2 className="glass-text">{editingSociete ? 'Modifier la Société' : 'Nouvelle Société'}</h2>
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
                    {cabinets.find((c: Cabinet) => String(c.id) === formData.cabinet_id)?.nom || (cabinets.length > 0 ? cabinets[0].nom : 'Chargement...')}
                  </div>
                )}
              </div>
              <div className="aurora-input-group">
                <label>Raison Sociale</label>
                <input
                  type="text"
                  placeholder="Ex: SARL Alpha"
                  value={formData.raison_sociale}
                  onChange={(e) => setFormData({ ...formData, raison_sociale: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>ICE (15 chiffres)</label>
                <input
                  type="text"
                  placeholder="000234567..."
                  value={formData.ice}
                  onChange={(e) => setFormData({ ...formData, ice: e.target.value })}
                />
              </div>
              <div className="aurora-input-group">
                <label>IF (Identifiant Fiscal)</label>
                <input
                  type="text"
                  value={formData.if_fiscal}
                  onChange={(e) => setFormData({ ...formData, if_fiscal: e.target.value })}
                />
              </div>
              <div className="aurora-input-group">
                <label>RC (Registre du Commerce)</label>
                <input
                  type="text"
                  placeholder="Ex: 12345"
                  value={formData.rc}
                  onChange={(e) => setFormData({ ...formData, rc: e.target.value })}
                />
              </div>
              <div className="aurora-input-group span-2">
                <label>Adresse complète</label>
                <input
                  type="text"
                  placeholder="Ex: 123 Rue des Palmiers, Casablanca"
                  value={formData.adresse}
                  onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
                />
              </div>
            </div>
            <button type="submit" className="aurora-btn-submit">
              Initialiser la société
            </button>
          </form>
        )}

        <div className="aurora-table-wrapper aurora-card">
          {loading ? (
            <div className="aurora-loader-inline">
              <div className="spinner-aurora"></div>
              <span>Chargement des entités...</span>
            </div>
          ) : (
            <>
              {societes.length === 0 ? (
                <div className="aurora-empty">
                  <span>🏢</span>
                  <p>Aucune société configurée.</p>
                </div>
              ) : (
                <table className="aurora-table">
                  <thead>
                    <tr>
                      <th>Entreprise / Adresse</th>
                      <th>Cabinet Partenaire</th>
                      <th>ICE / IF / RC</th>
                      <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {societes.map((societe: Societe) => (
                      <tr key={societe.id} className="aurora-tr">
                        <td>
                          <div className="aurora-td-soc">
                            <span className="soc-name">{societe.raison_sociale}</span>
                            <span className="soc-address">{societe.adresse || 'N/A'}</span>
                          </div>
                        </td>
                        <td>
                          <span className="aurora-tag purple">
                            {cabinets.find((c: Cabinet) => c.id === societe.cabinet_id)?.nom || 'Inconnu'}
                          </span>
                        </td>
                        <td>
                          <div className="aurora-ids">
                            <span>ICE: {societe.ice || '-'}</span>
                            <span>IF: {societe.if_fiscal || '-'}</span>
                          </div>
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <button
                            className="aurora-btn-manage"
                            title="Gérer les factures"
                            onClick={() => handleManageSociete(societe)}
                          >
                            📑 Gérer
                          </button>
                          <button className="aurora-btn-icon" onClick={() => handleEditClick(societe)}>✏️</button>
                          <button className="aurora-btn-icon delete" onClick={() => deleteSociete(societe.id)}>🗑️</button>
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
          width: 140px; height: 48px; background: var(--admin-gradient); color: white;
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

        .aurora-input-readonly {
          padding: 15px; border-radius: 14px; border: 1px solid var(--admin-glass-border);
          background: rgba(255, 255, 255, 0.02); color: var(--admin-accent); font-weight: 700;
        }

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

        .aurora-td-soc { display: flex; flex-direction: column; gap: 4px; }
        .soc-name { font-weight: 800; font-size: 15px; }
        .soc-address { font-size: 12px; color: var(--admin-text-dim); }

        .aurora-tag {
          padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 800;
        }
        .aurora-tag.purple { background: rgba(168, 85, 247, 0.1); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.2); }

        .aurora-ids { display: flex; flex-direction: column; gap: 2px; font-size: 12px; color: var(--admin-text-dim); }

        .aurora-btn-icon { background: transparent; border: none; padding: 8px; cursor: pointer; border-radius: 8px; transition: all 0.2s; }
        .aurora-btn-icon:hover { background: rgba(255, 255, 255, 0.1); }
        
        .aurora-btn-manage {
          background: rgba(99, 102, 241, 0.1);
          color: var(--admin-accent);
          border: 1px solid rgba(99, 102, 241, 0.2);
          padding: 6px 12px;
          border-radius: 10px;
          font-size: 12px;
          font-weight: 700;
          cursor: pointer;
          margin-right: 10px;
          transition: all 0.2s;
        }
        .aurora-btn-manage:hover {
          background: var(--admin-accent);
          color: white;
          transform: translateY(-1px);
        }

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
