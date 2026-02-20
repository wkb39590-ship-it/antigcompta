import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { getAdminToken } from '../../utils/adminTokenDecoder';

interface Stats {
  total_agents: number;
  total_societes: number;
  total_cabinets: number;
  total_factures: number;
}

export const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats>({
    total_agents: 0,
    total_societes: 0,
    total_cabinets: 0,
    total_factures: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8888';
  const token = getAdminToken();

  useEffect(() => {
    const fetchStats = async () => {
      try {
        // Récupérer les statistiques
        const agentsRes = await axios.get(`${API_URL}/auth/me?token=${token}`);
        const societeRes = await axios.get(`${API_URL}/societes?token=${token}`);
        const cabinetRes = await axios.get(`${API_URL}/admin/cabinets/${agentsRes.data.cabinet_id}`);
        const facturesRes = await axios.get(`${API_URL}/factures?token=${token}`);

        setStats({
          total_agents: 10, // Vous pouvez récupérer depuis un endpoint /admin/agents
          total_societes: Array.isArray(societeRes.data) ? societeRes.data.length : 0,
          total_cabinets: 1,
          total_factures: Array.isArray(facturesRes.data) ? facturesRes.data.length : 0,
        });
      } catch (err: any) {
        setError(err.message || 'Erreur lors du chargement des statistiques');
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchStats();
    }
  }, [token, API_URL]);

  const StatCard = ({ title, value }: { title: string; value: number }) => (
    <div className="stat-card">
      <h3>{title}</h3>
      <p className="stat-value">{value}</p>
    </div>
  );

  return (
    <div className="dashboard">
        <h1>📊 Tableau de Bord - Admin</h1>

        {error && <div className="error-message">{error}</div>}

        {loading ? (
          <div className="loading">Chargement des statistiques...</div>
        ) : (
          <>
            <div className="stats-grid">
              <StatCard title="Total Agents" value={stats.total_agents} />
              <StatCard title="Total Sociétés" value={stats.total_societes} />
              <StatCard title="Total Cabinets" value={stats.total_cabinets} />
              <StatCard
                title="Total Factures"
                value={stats.total_factures}
              />
            </div>

            <div className="info-section">
              <h2>Bienvenue sur le Panneau d'Administration</h2>
              <p>
                Utilisez le menu latéral pour accéder aux différentes
                fonctionnalités :
              </p>
              <ul>
                <li>
                  <strong>Cabinets :</strong> Gérer les cabinets de
                  comptabilité
                </li>
                <li>
                  <strong>Sociétés :</strong> Créer et gérer les sociétés
                  clientes
                </li>
                <li>
                  <strong>Agents :</strong> Gérer les utilisateurs comptables
                </li>
                <li>
                  <strong>Associations :</strong> Lier les sociétés aux
                  cabinets
                </li>
              </ul>
            </div>
          </>
        )}

        <style>{`
          .dashboard {
            max-width: 1200px;
          }

          .dashboard h1 {
            margin-top: 0;
            color: #2c3e50;
            font-size: 32px;
          }

          .error-message {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            border-left: 4px solid #c33;
          }

          .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
            font-size: 16px;
          }

          .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
          }

          .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-top: 4px solid #667eea;
          }

          .stat-card h3 {
            margin: 0 0 15px 0;
            color: #7f8c8d;
            font-size: 14px;
            text-transform: uppercase;
            font-weight: 600;
          }

          .stat-value {
            margin: 0;
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
          }

          .info-section {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          }

          .info-section h2 {
            margin-top: 0;
            color: #2c3e50;
          }

          .info-section ul {
            list-style: none;
            padding: 0;
            margin: 0;
          }

          .info-section li {
            padding: 10px 0;
            border-bottom: 1px solid #ecf0f1;
            color: #34495e;
          }

          .info-section li:last-child {
            border-bottom: none;
          }

          .info-section strong {
            color: #667eea;
          }
        `}</style>
      </div>
  );
};
