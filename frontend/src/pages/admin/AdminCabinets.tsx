import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import {
  Building2,
  Plus,
  X,
  Pencil,
  Trash2,
  Mail,
  MapPin,
  Phone,
  Fingerprint
} from 'lucide-react';

interface Cabinet {
  id: number;
  nom: string;
  email: string;
  telephone: string;
  adresse: string;
}

export const AdminCabinets: React.FC = () => {
  const [cabinets, setCabinets] = useState<Cabinet[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingCabinet, setEditingCabinet] = useState<Cabinet | null>(null);
  const [formData, setFormData] = useState({
    nom: '',
    email: '',
    telephone: '',
    adresse: '',
  });

  useEffect(() => {
    fetchCabinets();
  }, []);

  const getErrorMessage = (err: any) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    return err.message || 'Une erreur est survenue';
  };

  const fetchCabinets = async () => {
    try {
      setLoading(true);
      const data = await apiService.adminListCabinets();
      setCabinets(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCabinet = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError('');
      if (editingCabinet) {
        await apiService.adminUpdateCabinet(editingCabinet.id, formData);
      } else {
        await apiService.adminCreateCabinet(formData);
      }
      setFormData({ nom: '', email: '', telephone: '', adresse: '' });
      setShowForm(false);
      setEditingCabinet(null);
      fetchCabinets();
    } catch (err: any) {
      setError(getErrorMessage(err));
    }
  };

  const handleEditClick = (cabinet: Cabinet) => {
    setEditingCabinet(cabinet);
    setFormData({
      nom: cabinet.nom,
      email: cabinet.email,
      telephone: cabinet.telephone,
      adresse: cabinet.adresse,
    });
    setShowForm(true);
  };

  const handleDeleteCabinet = async (id: number) => {
    if (!window.confirm('Supprimer ce cabinet partenaire ?')) return;
    try {
      await apiService.adminDeleteCabinet(id);
      fetchCabinets();
    } catch (err: any) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="cabinets-page">
      <div className="page-header">
        <div className="header-info">
          <h1 className="page-title">Gestion des Cabinets</h1>
          <p className="page-subtitle">Administration des partenaires comptables et structures rattachées.</p>
        </div>
        <button
          className={`btn-primary ${showForm ? 'form-active' : ''}`}
          onClick={() => {
            if (showForm) {
              setShowForm(false);
              setEditingCabinet(null);
              setFormData({ nom: '', email: '', telephone: '', adresse: '' });
            } else {
              setShowForm(true);
            }
          }}
        >
          {showForm ? <X size={18} /> : <><Plus size={16} /> <span>Nouveau Cabinet</span></>}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="content-layout">
        {showForm && (
          <form className="pro-card side-form" onSubmit={handleCreateCabinet}>
            <div className="form-header">
              <h3>{editingCabinet ? 'Éditer le partenaire' : 'Nouveau Partenaire'}</h3>
              <p>Informations structurelles du cabinet</p>
            </div>

            <div className="form-grid">
              <div className="field-group span2">
                <label>Dénomination Sociale</label>
                <input className="pro-input" placeholder="Ex: ExpertCompta Solutions" value={formData.nom} onChange={e => setFormData({...formData, nom: e.target.value})} required/>
              </div>
              <div className="field-group">
                <label>Email de Contact</label>
                <input className="pro-input" type="email" placeholder="contact@cabinet.com" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} required/>
              </div>
              <div className="field-group">
                <label>Téléphone</label>
                <input className="pro-input" placeholder="+212..." value={formData.telephone} onChange={e => setFormData({...formData, telephone: e.target.value})}/>
              </div>
              <div className="field-group span2">
                <label>Adresse Siège</label>
                <input className="pro-input" placeholder="Rue, Ville, CP" value={formData.adresse} onChange={e => setFormData({...formData, adresse: e.target.value})}/>
              </div>
            </div>

            <button type="submit" className="btn-primary full-w">
              {editingCabinet ? 'Enregistrer les modifications' : 'Créer le cabinet'}
            </button>
          </form>
        )}

        <div className="pro-card table-section">
          <div className="section-header">
            <div className="header-label">
              <Building2 size={16} className="muted-icon" />
              <span>Répertoire des partenaires</span>
            </div>
            <div className="entity-count">{cabinets.length} Cabinets</div>
          </div>

          {loading ? (
            <div className="placeholder-state">
              <div className="dot-spinner"></div>
              <span>Synchronisation du réseau...</span>
            </div>
          ) : cabinets.length === 0 ? (
            <div className="placeholder-state empty">
              <Building2 size={48} className="muted-icon" />
              <p>Aucun cabinet répertorié.</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table className="pro-table">
                <thead>
                  <tr>
                    <th>Entité Cabinet</th>
                    <th>Coordonnées</th>
                    <th>Localisation</th>
                    <th style={{ textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {cabinets.map((cabinet) => (
                    <tr key={cabinet.id}>
                      <td>
                        <div className="cabinet-cell">
                          <div className="cabinet-icon">{cabinet.nom[0]}</div>
                          <div className="cabinet-info">
                            <span className="cabinet-name">{cabinet.nom}</span>
                            <span className="cabinet-id">REF: CAB-{cabinet.id}</span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div className="contact-labels">
                          <span className="email-line"><Mail size={10} /> {cabinet.email}</span>
                          <span className="phone-line"><Phone size={10} /> {cabinet.telephone || '-'}</span>
                        </div>
                      </td>
                      <td>
                        <div className="location-label">
                          <MapPin size={12} className="muted-icon" />
                          <span>{cabinet.adresse || 'Siège non localisé'}</span>
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div className="btn-group">
                          <button className="btn-icon" title="Éditer" onClick={() => handleEditClick(cabinet)}>
                            <Pencil size={14} />
                          </button>
                          <button className="btn-icon btn-danger" title="Supprimer" onClick={() => handleDeleteCabinet(cabinet.id)}>
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

      <style>{`
        .cabinets-page { padding: 24px; background: #fafafa; min-height: 100vh; font-family: 'Inter', sans-serif; }
        .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .page-title { font-size: 26px; font-weight: 700; color: #0f172a; margin: 0; letter-spacing: -0.5px; }
        .page-subtitle { color: #64748b; font-size: 14px; margin-top: 4px; }

        .btn-primary { background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 4px; font-weight: 600; font-size: 14px; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: background 0.2s; }
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

        .field-group label { display: block; font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 6px; }
        .pro-input { width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 14px; background: #fff; outline: none; }
        .pro-input:focus { border-color: #3b82f6; }

        .section-header { padding: 16px 20px; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
        .header-label { display: flex; align-items: center; gap: 8px; font-weight: 600; font-size: 14px; color: #334155; }
        .entity-count { font-size: 11px; font-weight: 700; color: #3b82f6; background: #eff6ff; padding: 2px 8px; border-radius: 4px; border: 1px solid #dbeafe; }

        .table-wrapper { overflow-x: auto; }
        .pro-table { width: 100%; border-collapse: collapse; }
        .pro-table th { text-align: left; padding: 12px 20px; font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #e2e8f0; }
        .pro-table td { padding: 14px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
        .pro-table tr:hover { background: #fafafa; }

        .cabinet-cell { display: flex; align-items: center; gap: 12px; }
        .cabinet-icon { width: 32px; height: 32px; background: #4f46e5; color: white; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; }
        .cabinet-name { display: block; font-weight: 600; color: #1e293b; font-size: 14px; }
        .cabinet-id { display: block; font-size: 11px; color: #94a3b8; font-family: monospace; }

        .contact-labels { display: flex; flex-direction: column; gap: 2px; }
        .email-line { font-size: 12px; font-weight: 500; color: #3b82f6; display: flex; align-items: center; gap: 4px; }
        .phone-line { font-size: 11px; color: #64748b; display: flex; align-items: center; gap: 4px; }

        .location-label { display: inline-flex; align-items: center; gap: 6px; padding: 4px 8px; border: 1px solid #e2e8f0; border-radius: 4px; font-size: 12px; font-weight: 600; color: #475569; }

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
