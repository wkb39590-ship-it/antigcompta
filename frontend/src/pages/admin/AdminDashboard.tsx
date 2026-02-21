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

  const getErrorMessage = (err: any) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    return err.message || 'Une erreur est survenue';
  };

  useEffect(() => {
    const fetchStats = async () => {
      const token = getAdminToken();
      if (!token) {
        setError('Session expirée');
        setLoading(false);
        return;
      }

      try {
        const res = await axios.get(`${API_URL}/admin/stats/global`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setStats(res.data);
      } catch (err: any) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [API_URL]);

  const AuroraWidget = ({ title, value, icon, color }: { title: string; value: number; icon: string; color: string }) => (
    <div className="aurora-widget aurora-card">
      <div className="widget-icon" style={{ background: color }}>{icon}</div>
      <div className="widget-content">
        <h3 className="widget-title">{title}</h3>
        <p className="widget-value">{value}</p>
      </div>
      <div className="widget-glow" style={{ background: color }} />
    </div>
  );

  return (
    <div className="admin-dashboard-aurora">
      <div className="dashboard-welcome">
        <h1 className="glass-text">Vue d'ensemble</h1>
        <p>Bienvenue dans votre centre de commande Aurora.</p>
      </div>

      {error && <div className="aurora-error">{error}</div>}

      {loading ? (
        <div className="aurora-loader">
          <div className="loader-spinner"></div>
          <span>Analyse des données en cours...</span>
        </div>
      ) : (
        <div className="dashboard-grid-aurora">
          <AuroraWidget title="Cabinets" value={stats.total_cabinets} icon="🏢" color="#6366f1" />
          <AuroraWidget title="Sociétés" value={stats.total_societes} icon="🏬" color="#a855f7" />
          <AuroraWidget title="Agents" value={stats.total_agents} icon="👥" color="#ec4899" />
          <AuroraWidget title="Factures" value={stats.total_factures} icon="📄" color="#f59e0b" />

          <div className="aurora-wide-card aurora-card span-2">
            <div className="card-header-premium">
              <h2 className="glass-text">Activités Récentes</h2>
              <span className="live-status">LIVE</span>
            </div>
            <div className="placeholder-list">
              <div className="list-item-glass">
                <span className="item-dot blue"></span>
                <p>Nouveau cabinet **ExpertCompta** ajouté au système</p>
                <span className="item-time">Il y a 2 min</span>
              </div>
              <div className="list-item-glass">
                <span className="item-dot purple"></span>
                <p>Agent **Wissal** a validé 15 factures pour **Société Alpha**</p>
                <span className="item-time">Il y a 1 heure</span>
              </div>
              <div className="list-item-glass">
                <span className="item-dot orange"></span>
                <p>Alerte: 3 factures en attente de classification</p>
                <span className="item-time">Il y a 3 heures</span>
              </div>
            </div>
          </div>

          <div className="aurora-info-card aurora-card">
            <h2 className="glass-text">Raccourcis</h2>
            <div className="shortcut-grid">
              <button className="shortcut-btn">Ajouter Cabinet</button>
              <button className="shortcut-btn">Nouvel Agent</button>
              <button className="shortcut-btn">Rapports PDF</button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .admin-dashboard-aurora {
          animation: fadeIn 0.8s ease-out;
        }

        .dashboard-welcome {
          margin-bottom: 40px;
        }

        .dashboard-welcome h1 {
          font-size: 48px;
          margin: 0;
          font-weight: 900;
          letter-spacing: -2px;
        }

        .dashboard-welcome p {
          color: var(--admin-text-dim);
          font-weight: 500;
          font-size: 16px;
        }

        .dashboard-grid-aurora {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 24px;
        }

        .aurora-widget {
          padding: 30px;
          position: relative;
          display: flex;
          align-items: center;
          gap: 20px;
          overflow: hidden;
        }

        .widget-icon {
          width: 50px;
          height: 50px;
          border-radius: 16px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          color: white;
          z-index: 2;
        }

        .widget-content {
          z-index: 2;
        }

        .widget-title {
          margin: 0;
          font-size: 14px;
          color: var(--admin-text-dim);
          text-transform: uppercase;
          letter-spacing: 1px;
          font-weight: 700;
        }

        .widget-value {
          margin: 5px 0 0 0;
          font-size: 32px;
          font-weight: 900;
          color: var(--admin-text);
        }

        .widget-glow {
          position: absolute;
          width: 100px;
          height: 100px;
          right: -50px;
          top: -50px;
          filter: blur(60px);
          opacity: 0.3;
        }

        .aurora-wide-card {
           grid-column: span 3;
           padding: 30px;
        }

        .card-header-premium {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 25px;
        }

        .card-header-premium h2 {
          margin: 0;
          font-size: 24px;
          font-weight: 800;
        }

        .live-status {
          font-size: 10px;
          font-weight: 900;
          color: #ef4444;
          background: rgba(239, 68, 68, 0.1);
          padding: 4px 10px;
          border-radius: 20px;
          border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .placeholder-list {
          display: grid;
          gap: 15px;
        }

        .list-item-glass {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 15px;
          background: rgba(255, 255, 255, 0.02);
          border-radius: 16px;
          border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .item-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        .item-dot.blue { background: #3b82f6; box-shadow: 0 0 10px #3b82f6; }
        .item-dot.purple { background: #a855f7; box-shadow: 0 0 10px #a855f7; }
        .item-dot.orange { background: #f59e0b; box-shadow: 0 0 10px #f59e0b; }

        .list-item-glass p {
          margin: 0;
          font-size: 14px;
          color: var(--admin-text);
          flex: 1;
        }

        .item-time {
          font-size: 12px;
          color: var(--admin-text-dim);
        }

        .aurora-info-card {
          padding: 30px;
        }

        .shortcut-grid {
          display: grid;
          gap: 10px;
          margin-top: 20px;
        }

        .shortcut-btn {
          padding: 12px;
          border-radius: 12px;
          border: 1px solid var(--admin-glass-border);
          background: rgba(255, 255, 255, 0.03);
          color: var(--admin-text);
          font-weight: 600;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .shortcut-btn:hover {
          background: var(--admin-gradient);
          border-color: transparent;
          color: white;
          transform: scale(1.02);
        }

        .aurora-loader {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 20px;
          padding: 100px;
          color: var(--admin-text-dim);
        }

        @keyframes spin { to { transform: rotate(360deg); } }
        .loader-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid var(--admin-glass-border);
          border-top-color: var(--admin-accent);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @media (max-width: 1200px) {
          .dashboard-grid-aurora { grid-template-columns: repeat(2, 1fr); }
          .aurora-wide-card { grid-column: span 2; }
        }
      `}</style>
    </div>
  );
};
