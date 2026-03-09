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
  Phone
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
        // Note: adminUpdateCabinet not yet in apiService, let's add it if needed or use a generic put
        // For now I only added adminListAgents/Cabinets. Let's add the rest to api.ts properly.
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
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce cabinet ?')) return;
    try {
      await apiService.adminDeleteCabinet(id);
      fetchCabinets();
    } catch (err: any) {
      setError(getErrorMessage(err));
    }
  };

  return (
    <div className="aurora-page-v2">
      <div className="aurora-page-header">
        <div className="header-info">
          <h1 className="hero-title heading-font">Gestion des Cabinets</h1>
          <p className="aurora-subtitle">Administration des partenaires comptables et structures rattachées.</p>
        </div>
        <button
          className={`aurora-btn-primary ${showForm ? 'active-form' : ''}`}
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
          {showForm ? <X size={20} /> : <><Plus size={18} /> <span>Nouveau Cabinet</span></>}
        </button>
      </div>

      {error && <div className="aurora-error-toast">{error}</div>}

      <div className="aurora-content-grid">
        {showForm && (
          <form className="aurora-card premium-form" onSubmit={handleCreateCabinet}>
            <div className="form-header">
              <h2 className="heading-font">{editingCabinet ? 'Édition Partenaire' : 'Nouveau Partenaire'}</h2>
              <p>Configurez les informations structurelles du cabinet</p>
            </div>

            <div className="aurora-form-grid">
              <div className="aurora-input-group">
                <label>Dénomination Sociale</label>
                <input
                  type="text"
                  placeholder="Ex: ExpertCompta Solutions"
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>Email de Contact</label>
                <input
                  type="email"
                  placeholder="direction@cabinet.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>Téléphone</label>
                <input
                  type="text"
                  placeholder="+33..."
                  value={formData.telephone}
                  onChange={(e) => setFormData({ ...formData, telephone: e.target.value })}
                />
              </div>
              <div className="aurora-input-group">
                <label>Adresse Siège</label>
                <input
                  type="text"
                  placeholder="Rue, Ville, CP"
                  value={formData.adresse}
                  onChange={(e) => setFormData({ ...formData, adresse: e.target.value })}
                />
              </div>
            </div>

            <button type="submit" className="aurora-btn-primary full-width">
              {editingCabinet ? 'Mettre à jour le partenaire' : 'Enregistrer le nouveau cabinet'}
            </button>
          </form>
        )}

        <div className="aurora-card table-card">
          <div className="card-header-flex">
            <h2 className="heading-font">Répertoire des Cabinets</h2>
            <div className="glass-pill">{cabinets.length} Partenaires</div>
          </div>

          {loading ? (
            <div className="aurora-loader-inline">
              <div className="spinner-aurora"></div>
              <span>Synchronisation du réseau...</span>
            </div>
          ) : (
            <div className="table-responsive">
              {cabinets.length === 0 ? (
                <div className="aurora-empty-v2">
                  <div className="empty-icon-box"><Building2 size={40} /></div>
                  <p>Aucun cabinet partenaire n'est configuré.</p>
                </div>
              ) : (
                <table className="aurora-table-v2">
                  <thead>
                    <tr>
                      <th>Entité Cabinet</th>
                      <th>Coordonnées Directes</th>
                      <th>Localisation</th>
                      <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cabinets.map((cabinet) => (
                      <tr key={cabinet.id}>
                        <td>
                          <div className="cabinet-profile-td">
                            <div className="cabinet-avatar-v2">{cabinet.nom[0]}</div>
                            <div className="cabinet-name-box">
                              <span className="name">{cabinet.nom}</span>
                              <span className="id-tag">REF: CAB-{cabinet.id}</span>
                            </div>
                          </div>
                        </td>
                        <td>
                          <div className="contact-td">
                            <div className="email-line"><Mail size={12} /> {cabinet.email}</div>
                            <div className="phone-line"><Phone size={12} /> {cabinet.telephone || 'Non renseigné'}</div>
                          </div>
                        </td>
                        <td>
                          <div className="location-td">
                            <MapPin size={14} />
                            <span>{cabinet.adresse || 'Siège non défini'}</span>
                          </div>
                        </td>
                        <td style={{ textAlign: 'right' }}>
                          <div className="action-buttons">
                            <button className="icon-btn edit" title="Modifier" onClick={() => handleEditClick(cabinet)}>
                              <Pencil size={16} />
                            </button>
                            <button className="icon-btn del" title="Supprimer" onClick={() => handleDeleteCabinet(cabinet.id)}>
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

        .aurora-input-group label {
          display: block; font-size: 11px; font-weight: 800; color: var(--text3);
          text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;
        }

        .aurora-input-group input {
          width: 100%; padding: 14px 16px; border-radius: 14px; border: 1px solid var(--border);
          background: rgba(255, 255, 255, 0.5); color: var(--text); outline: none; transition: all 0.3s;
          font-family: 'Inter', sans-serif; font-size: 14px;
        }
        .aurora-input-group input:focus {
          border-color: var(--accent); background: white; box-shadow: 0 0 10px rgba(99, 102, 241, 0.1);
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

        .cabinet-profile-td { display: flex; align-items: center; gap: 15px; }
        .cabinet-avatar-v2 {
          width: 44px; height: 44px; border-radius: 12px; 
          background: linear-gradient(145deg, #3b82f6, #1d4ed8);
          color: white; display: flex; align-items: center; justify-content: center;
          font-weight: 800; font-size: 18px; 
          box-shadow: 0 8px 15px -3px rgba(59, 130, 246, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.3);
          border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .cabinet-name-box { display: flex; flex-direction: column; }
        .cabinet-name-box .name { font-weight: 700; color: var(--text); font-size: 15px; }
        .cabinet-name-box .id-tag { font-size: 10px; color: var(--text3); font-weight: 800; margin-top: 2px; }

        .contact-td { display: flex; flex-direction: column; gap: 4px; }
        .email-line, .phone-line { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: var(--text2); }
        .email-line svg, .phone-line svg { color: var(--text3); }

        .location-td { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: var(--text3); max-width: 250px; }
        .location-td svg { color: var(--accent); flex-shrink: 0; }

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
        }
      `}</style>
    </div>
  );
};
