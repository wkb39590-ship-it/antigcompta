import React, { useState, useEffect } from 'react';
import apiService from '../../api';

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
    <div className="aurora-page">
      <div className="aurora-page-header">
        <div>
          <h1 className="glass-text">Gestion des Cabinets</h1>
          <p className="aurora-subtitle">Gérez les partenaires comptables de la plateforme.</p>
        </div>
        <button
          className={`aurora-fab ${showForm ? 'active' : ''}`}
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
          {showForm ? '✕' : '+ Nouveau'}
        </button>
      </div>

      {error && <div className="aurora-error-toast">{error}</div>}

      <div className="aurora-content-layout">
        {showForm && (
          <form className="aurora-glass-form aurora-card" onSubmit={handleCreateCabinet}>
            <h2 className="glass-text">{editingCabinet ? 'Modifier le Cabinet' : 'Nouveau Cabinet'}</h2>
            <div className="aurora-form-grid">
              <div className="aurora-input-group">
                <label>Nom du cabinet</label>
                <input
                  type="text"
                  placeholder="Ex: ExpertCompta"
                  value={formData.nom}
                  onChange={(e) => setFormData({ ...formData, nom: e.target.value })}
                  required
                />
              </div>
              <div className="aurora-input-group">
                <label>Email professionnel</label>
                <input
                  type="email"
                  placeholder="contact@cabinet.com"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                />
              </div>
            </div>
            <button type="submit" className="aurora-btn-submit">
              Enregistrer le partenaire
            </button>
          </form>
        )}

        <div className="aurora-table-wrapper aurora-card">
          {loading ? (
            <div className="aurora-loader-inline">
              <div className="spinner-aurora"></div>
              <span>Synchronisation...</span>
            </div>
          ) : (
            <>
              {cabinets.length === 0 ? (
                <div className="aurora-empty">
                  <span>📭</span>
                  <p>Aucun cabinet n'a encore été enregistré.</p>
                </div>
              ) : (
                <table className="aurora-table">
                  <thead>
                    <tr>
                      <th>Partenaire</th>
                      <th>Email</th>
                      <th style={{ textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cabinets.map((cabinet) => (
                      <tr key={cabinet.id} className="aurora-tr">
                        <td>
                          <div className="aurora-td-name">
                            <div className="name-avatar">{cabinet.nom[0]}</div>
                            <span>{cabinet.nom}</span>
                          </div>
                        </td>
                        <td><span className="aurora-td-email">{cabinet.email}</span></td>
                        <td style={{ textAlign: 'right' }}>
                          <button className="aurora-btn-icon" onClick={() => handleEditClick(cabinet)}>✏️</button>
                          <button className="aurora-btn-icon delete" onClick={() => handleDeleteCabinet(cabinet.id)}>🗑️</button>
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
        .aurora-page {
          animation: pageEnter 0.6s ease-out;
        }

        @keyframes pageEnter {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .aurora-page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
          margin-bottom: 40px;
        }

        .aurora-page-header h1 {
          font-size: 36px;
          font-weight: 900;
          margin: 0;
          letter-spacing: -1px;
        }

        .aurora-subtitle {
          color: var(--admin-text-dim);
          font-size: 14px;
          font-weight: 500;
          margin-top: 5px;
        }

        .aurora-fab {
          width: 140px;
          height: 48px;
          background: var(--admin-gradient);
          color: white;
          border: none;
          border-radius: 24px;
          font-weight: 800;
          cursor: pointer;
          transition: all 0.3s;
          box-shadow: 0 10px 20px var(--admin-accent-glow);
        }

        .aurora-fab:hover {
          transform: translateY(-2px);
          box-shadow: 0 15px 30px var(--admin-accent-glow);
        }

        .aurora-fab.active {
          background: #334155;
          box-shadow: none;
        }

        .aurora-error-toast {
          background: rgba(239, 68, 68, 0.1);
          color: #f87171;
          padding: 15px 25px;
          border-radius: 16px;
          border: 1px solid rgba(239, 68, 68, 0.2);
          margin-bottom: 25px;
          font-weight: 600;
        }

        .aurora-content-layout {
          display: grid;
          gap: 25px;
        }

        .aurora-glass-form {
          padding: 40px;
          margin-bottom: 10px;
        }

        .aurora-glass-form h2 {
          margin: 0 0 30px 0;
          font-size: 20px;
          font-weight: 800;
        }

        .aurora-form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 30px;
        }

        .aurora-input-group label {
          display: block;
          font-size: 11px;
          font-weight: 800;
          color: var(--admin-text-dim);
          text-transform: uppercase;
          letter-spacing: 1px;
          margin-bottom: 10px;
        }

        .aurora-input-group input {
          width: 100%;
          padding: 15px;
          border-radius: 14px;
          border: 1px solid var(--admin-glass-border);
          background: rgba(255, 255, 255, 0.03);
          color: white;
          outline: none;
          transition: all 0.3s;
        }

        .aurora-input-group input:focus {
          border-color: var(--admin-accent);
          background: rgba(255, 255, 255, 0.06);
        }

        .aurora-btn-submit {
          padding: 15px 30px;
          border-radius: 14px;
          border: none;
          background: var(--admin-gradient);
          color: white;
          font-weight: 800;
          cursor: pointer;
          transition: all 0.3s;
        }

        .aurora-btn-submit:hover { transform: scale(1.02); }

        .aurora-table-wrapper {
          padding: 10px;
          overflow: hidden;
        }

        .aurora-table {
          width: 100%;
          border-collapse: collapse;
        }

        .aurora-table th {
          padding: 20px;
          font-size: 11px;
          font-weight: 800;
          color: var(--admin-text-dim);
          text-transform: uppercase;
          letter-spacing: 1px;
          border-bottom: 1px solid var(--admin-glass-border);
          text-align: left;
        }

        .aurora-tr {
          transition: all 0.3s;
        }

        .aurora-tr:last-child {
          border-bottom: none;
        }

        .aurora-tr:hover {
          background: rgba(255, 255, 255, 0.03);
        }

        .aurora-tr td {
          padding: 20px;
          color: var(--admin-text);
          font-weight: 500;
          border-bottom: 1px solid rgba(255, 255, 255, 0.03);
        }

        .aurora-td-name {
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .name-avatar {
          width: 36px;
          height: 36px;
          border-radius: 10px;
          background: var(--admin-accent);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 800;
          font-size: 14px;
        }

        .aurora-td-email {
          font-size: 13px;
          color: var(--admin-text-dim);
        }

        .aurora-btn-icon {
          background: transparent;
          border: none;
          font-size: 16px;
          cursor: pointer;
          padding: 8px;
          border-radius: 8px;
          transition: all 0.2s;
        }

        .aurora-btn-icon:hover { background: rgba(255, 255, 255, 0.1); }
        .aurora-btn-icon.delete:hover { background: rgba(239, 68, 68, 0.1); }

        .aurora-loader-inline {
          padding: 50px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 15px;
          color: var(--admin-text-dim);
        }

        .spinner-aurora {
          width: 30px;
          height: 30px;
          border: 3px solid var(--admin-glass-border);
          border-top-color: var(--admin-accent);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin { to { transform: rotate(360deg); } }

        .aurora-empty {
          padding: 60px;
          text-align: center;
          color: var(--admin-text-dim);
        }

        .aurora-empty span { font-size: 40px; display: block; margin-bottom: 15px; opacity: 0.5; }

        @media (max-width: 768px) {
          .aurora-form-grid { grid-template-columns: 1fr; }
          .aurora-page-header { flex-direction: column; align-items: flex-start; gap: 20px; }
        }
      `}</style>
    </div>
  );
};
