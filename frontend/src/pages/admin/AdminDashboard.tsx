import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { useNavigate } from 'react-router-dom';
import { getAdminUser } from '../../utils/adminTokenDecoder';

interface Stats {
  total_agents: number;
  total_societes: number;
  total_cabinets: number;
  total_factures: number;
}

interface Activity {
  id: string;
  type: string;
  title: string;
  time: string;
  dot_color: string;
}

export const AdminDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<Stats>({
    total_agents: 0,
    total_societes: 0,
    total_cabinets: 0,
    total_factures: 0,
  });
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const getErrorMessage = (err: any) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    return err.message || 'Une erreur est survenue';
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, activitiesData] = await Promise.all([
          apiService.adminGetGlobalStats(),
          apiService.adminGetActivities()
        ]);
        setStats(statsData);
        setActivities(activitiesData.activities);
      } catch (err: any) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

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

  const formatMarkdown = (text: string) => {
    // Remplacer **texte** par <strong>texte</strong>
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  const cabinets = JSON.parse(localStorage.getItem('cabinets') || '[]');
  const isSuper = localStorage.getItem('is_super_admin') === 'true';
  const cabinetId = getAdminUser()?.cabinet_id;
  const currentCabinet = cabinets.find((c: any) => c.id === cabinetId);
  const cabinetName = currentCabinet ? currentCabinet.nom : '';

  return (
    <div className="admin-dashboard-aurora">
      <div className="dashboard-welcome">
        <h1 className="glass-text">
          {isSuper ? "Vue d'ensemble" : `Dashboard - ${cabinetName}`}
        </h1>
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
          {isSuper && (
            <AuroraWidget title="Cabinets" value={stats.total_cabinets} icon="🏢" color="#6366f1" />
          )}

          {/* Masquer Sociétés et Factures pour le Super Admin */}
          {!isSuper && (
            <>
              <AuroraWidget title="Sociétés" value={stats.total_societes} icon="🏬" color="#a855f7" />
              <AuroraWidget title="Factures" value={stats.total_factures} icon="📄" color="#f59e0b" />
            </>
          )}

          <AuroraWidget
            title={isSuper ? "Administrateurs" : "Agents"}
            value={stats.total_agents}
            icon="👥"
            color="#ec4899"
          />

          <div className={`aurora-wide-card aurora-card ${isSuper ? 'span-3' : 'span-2'}`}>
            <div className="card-header-premium">
              <h2 className="glass-text">Activités Récentes</h2>
              <span className="live-status">LIVE</span>
            </div>
            <div className="placeholder-list">
              {activities.length > 0 ? (
                activities.map((act) => (
                  <div key={act.id} className="list-item-glass">
                    <span className={`item-dot ${act.dot_color}`}></span>
                    <p>{formatMarkdown(act.title)}</p>
                    <span className="item-time">{act.time}</span>
                  </div>
                ))
              ) : (
                <div className="list-item-glass">
                  <p>Aucune activité récente pour le moment.</p>
                </div>
              )}
            </div>
          </div>

          <div className="aurora-info-card aurora-card">
            <h2 className="glass-text">Raccourcis</h2>
            <div className="shortcut-grid">
              <button className="shortcut-btn" onClick={() => navigate(isSuper ? '/admin/cabinets' : '/admin/societes')}>
                {isSuper ? 'Gérer Cabinets' : 'Gérer Sociétés'}
              </button>
              <button className="shortcut-btn" onClick={() => navigate('/admin/agents')}>
                {isSuper ? 'Gérer Admins' : 'Nouvel Agent'}
              </button>
              {!isSuper && (
                <button className="shortcut-btn" onClick={() => alert('Fonctionnalité de rapports PDF bientôt disponible !')}>
                  Rapports PDF
                </button>
              )}
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
