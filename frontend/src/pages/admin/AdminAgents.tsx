import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Agent {
  id: number;
  username: string;
  email: string;
  nom: string;
  prenom: string;
  is_admin: boolean;
  is_active: boolean;
}

export const AdminAgents: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
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
  });

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8888';
  const token = localStorage.getItem('admin_token');

  useEffect(() => {
    // Placeholder: Récupérer les agents depuis le backend
    setLoading(false);
    setAgents([
      {
        id: 4,
        username: 'wissal',
        email: 'wissal@expertise-cpt.ma',
        nom: 'Bennani',
        prenom: 'Wissal',
        is_admin: true,
        is_active: true,
      },
      {
        id: 5,
        username: 'fatima',
        email: 'fatima@expertise-cpt.ma',
        nom: 'Ahmed',
        prenom: 'Fatima',
        is_admin: false,
        is_active: true,
      },
    ]);
  }, []);

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(
        `${API_URL}/auth/register`,
        formData,
        { params: { token, cabinet_id: 4 } }
      );
      setFormData({
        username: '',
        email: '',
        password: '',
        nom: '',
        prenom: '',
        is_admin: false,
      });
      setShowForm(false);
      // Recharger la liste
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la création');
    }
  };

  return (
    <div className="page-content">
        <div className="page-header">
          <h1>Gestion des Agents</h1>
          <button
            className="btn-primary"
            onClick={() => setShowForm(!showForm)}
          >
            {showForm ? 'Annuler' : '+ Nouvel Agent'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {showForm && (
          <form className="form-card" onSubmit={handleCreateAgent}>
            <h2>Créer un nouvel agent</h2>
            <div className="form-row">
              <div className="form-group">
                <label>Prénom</label>
                <input
                  type="text"
                  value={formData.prenom}
                  onChange={(e) =>
                    setFormData({ ...formData, prenom: e.target.value })
                  }
                  required
                />
              </div>
              <div className="form-group">
                <label>Nom</label>
                <input
                  type="text"
                  value={formData.nom}
                  onChange={(e) =>
                    setFormData({ ...formData, nom: e.target.value })
                  }
                  required
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) =>
                    setFormData({ ...formData, username: e.target.value })
                  }
                  required
                />
              </div>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData({ ...formData, email: e.target.value })
                  }
                  required
                />
              </div>
            </div>
            <div className="form-group">
              <label>Mot de passe</label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                required
              />
            </div>
            <div className="form-group checkbox">
              <input
                type="checkbox"
                id="is_admin"
                checked={formData.is_admin}
                onChange={(e) =>
                  setFormData({ ...formData, is_admin: e.target.checked })
                }
              />
              <label htmlFor="is_admin">Admin</label>
            </div>
            <button type="submit" className="btn-primary">
              Créer l'agent
            </button>
          </form>
        )}

        {loading ? (
          <div className="loading">Chargement des agents...</div>
        ) : (
          <div className="table-container">
            {agents.length === 0 ? (
              <p className="empty-state">Aucun agent créé</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Nom</th>
                    <th>Prénom</th>
                    <th>Email</th>
                    <th>Rôle</th>
                    <th>Statut</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {agents.map((agent) => (
                    <tr key={agent.id}>
                      <td>{agent.username}</td>
                      <td>{agent.nom}</td>
                      <td>{agent.prenom}</td>
                      <td>{agent.email}</td>
                      <td>
                        <span
                          className={
                            agent.is_admin ? 'badge-admin' : 'badge-user'
                          }
                        >
                          {agent.is_admin ? 'Admin' : 'Utilisateur'}
                        </span>
                      </td>
                      <td>
                        <span
                          className={
                            agent.is_active ? 'badge-active' : 'badge-inactive'
                          }
                        >
                          {agent.is_active ? 'Actif' : 'Inactif'}
                        </span>
                      </td>
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

          .form-group.checkbox {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
          }

          .form-group.checkbox input {
            width: auto;
            margin-right: 10px;
          }

          .form-group.checkbox label {
            margin: 0;
            font-weight: normal;
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

          .badge-admin {
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
          }

          .badge-user {
            background: #bdc3c7;
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
          }

          .badge-active {
            background: #27ae60;
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
          }

          .badge-inactive {
            background: #e74c3c;
            color: white;
            padding: 4px 8px;
            border-radius: 3px;
            font-size: 12px;
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
