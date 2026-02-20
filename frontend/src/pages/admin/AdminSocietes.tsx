import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Societe {
  id: number;
  raison_sociale: string;
  ice: string;
  if_fiscal: string;
  rc: string;
  adresse: string;
}

export const AdminSocietes: React.FC = () => {
  const [societes, setSocietes] = useState<Societe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    raison_sociale: '',
    ice: '',
    if_fiscal: '',
    rc: '',
    adresse: '',
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8888';
  const token = localStorage.getItem('admin_token');

  useEffect(() => {
    fetchSocietes();
  }, []);

  const fetchSocietes = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/societes`, {
        params: { token },
      });
      setSocietes(Array.isArray(response.data) ? response.data : []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSociete = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(
        `${API_URL}/societes`,
        formData,
        { params: { token } }
      );
      setFormData({
        raison_sociale: '',
        ice: '',
        if_fiscal: '',
        rc: '',
        adresse: '',
      });
      setShowForm(false);
      fetchSocietes();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  return (
    <div className="page-content">
        <div className="page-header">
          <h1>Gestion des Sociétés</h1>
          <button
            className="btn-primary"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Annuler' : '+ Nouvelle Société'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {showForm && (
          <form className="form-card" onSubmit={handleCreateSociete}>
            <h2>Créer une nouvelle société</h2>
            <div className="form-group">
              <label>Raison Sociale</label>
              <input
                type="text"
                value={formData.raison_sociale}
                onChange={(e) =>
                  setFormData({ ...formData, raison_sociale: e.target.value })
                }
                required
              />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>ICE (15 chiffres)</label>
                <input
                  type="text"
                  value={formData.ice}
                  onChange={(e) =>
                    setFormData({ ...formData, ice: e.target.value })
                  }
                  placeholder="Ex: 123456789012345"
                />
              </div>
              <div className="form-group">
                <label>Identifiant Fiscal</label>
                <input
                  type="text"
                  value={formData.if_fiscal}
                  onChange={(e) =>
                    setFormData({ ...formData, if_fiscal: e.target.value })
                  }
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Registre de Commerce</label>
                <input
                  type="text"
                  value={formData.rc}
                  onChange={(e) =>
                    setFormData({ ...formData, rc: e.target.value })
                  }
                />
              </div>
              <div className="form-group">
                <label>Adresse</label>
                <input
                  type="text"
                  value={formData.adresse}
                  onChange={(e) =>
                    setFormData({ ...formData, adresse: e.target.value })
                  }
                />
              </div>
            </div>
            <button type="submit" className="btn-primary">
              Créer la société
            </button>
          </form>
        )}

        {loading ? (
          <div className="loading">Chargement des sociétés...</div>
        ) : (
          <div className="table-container">
            {societes.length === 0 ? (
              <p className="empty-state">Aucune société créée</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Raison Sociale</th>
                    <th>ICE</th>
                    <th>IF</th>
                    <th>RC</th>
                    <th>Adresse</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {societes.map((societe) => (
                    <tr key={societe.id}>
                      <td>{societe.raison_sociale}</td>
                      <td>{societe.ice}</td>
                      <td>{societe.if_fiscal}</td>
                      <td>{societe.rc}</td>
                      <td>{societe.adresse}</td>
                      <td>
                        <button className="btn-small">Éditer</button>
                        <button className="btn-small btn-danger">
                          Supprimer
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}

        <style>{`
          .page-content {
            max-width: 1200px;
          }

          .page-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
          }

          .page-header h1 {
            margin: 0;
            color: #2c3e50;
            font-size: 28px;
          }

          .btn-primary {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
          }

          .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
          }

          .error-message {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            border-left: 4px solid #c33;
          }

          .form-card {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
          }

          .form-card h2 {
            margin-top: 0;
            color: #2c3e50;
          }

          .form-group {
            margin-bottom: 20px;
          }

          .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
          }

          .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 500;
            font-size: 14px;
          }

          .form-group input {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
          }

          .form-group input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
          }

          .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
          }

          .table-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            overflow-x: auto;
          }

          table {
            width: 100%;
            border-collapse: collapse;
          }

          thead {
            background: #f8f9fa;
            border-bottom: 2px solid #ecf0f1;
          }

          th {
            padding: 15px;
            text-align: left;
            color: #2c3e50;
            font-weight: 600;
            font-size: 14px;
          }

          td {
            padding: 15px;
            border-bottom: 1px solid #ecf0f1;
            color: #34495e;
            font-size: 14px;
          }

          tbody tr:hover {
            background: #f8f9fa;
          }

          .btn-small {
            padding: 6px 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-right: 5px;
            transition: all 0.2s;
          }

          .btn-small:hover {
            background: #5568d3;
          }

          .btn-danger {
            background: #e74c3c;
          }

          .btn-danger:hover {
            background: #c0392b;
          }

          .empty-state {
            padding: 40px;
            text-align: center;
            color: #95a5a6;
          }

          @media (max-width: 768px) {
            .page-header {
              flex-direction: column;
              align-items: flex-start;
            }

            .form-row {
              grid-template-columns: 1fr;
            }

            table {
              font-size: 12px;
            }

            th, td {
              padding: 10px;
            }
          }
        `}</style>
      </div>
  );
};
