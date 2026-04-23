import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { useNavigate } from 'react-router-dom';
import { getAdminUser } from '../../utils/adminTokenDecoder';
import {
  Building2,
  FileText,
  Users2,
  ArrowRight,
  Globe,
  Briefcase,
  History
} from 'lucide-react';

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

  const fetchData = async () => {
    try {
      setLoading(true);
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

  useEffect(() => {
    fetchData();
  }, []);

  const formatMarkdown = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} style={{ color: '#3b82f6' }}>{part.slice(2, -2)}</strong>;
      }
      return part;
    });
  };

  const isSuper = localStorage.getItem('is_super_admin') === 'true';
  const cabinetId = getAdminUser()?.cabinet_id;
  const cabinets = JSON.parse(localStorage.getItem('cabinets') || '[]');
  const currentCabinet = cabinets.find((c: any) => c.id === cabinetId);
  const cabinetName = currentCabinet ? currentCabinet.nom : '';

  if (loading) return (
    <div className="placeholder-state">
      <div className="dot-spinner"></div>
      <p>Chargement du tableau de bord...</p>
    </div>
  );

  return (
    <div className="dashboard-page">
      <div className="page-header-simple">
        <h1>Bonjour, {getAdminUser()?.prenom || 'Admin'}</h1>
        <p>{isSuper ? "Superviseur Central" : `Gestionnaire • ${cabinetName}`} — État global de l'infrastructure.</p>
      </div>

      <div className="stats-strip">
        {isSuper ? (
          <div className="stat-box">
            <div className="stat-icon-square purple"><Globe size={20} /></div>
            <div className="stat-data">
              <span className="stat-num">{stats.total_cabinets}</span>
              <span className="stat-name">Cabinets Partenaires</span>
            </div>
          </div>
        ) : (
          <>
            <div className="stat-box">
              <div className="stat-icon-square blue"><Briefcase size={20} /></div>
              <div className="stat-data">
                <span className="stat-num">{stats.total_societes}</span>
                <span className="stat-name">Sociétés Gérées</span>
              </div>
            </div>
            <div className="stat-box">
              <div className="stat-icon-square orange"><FileText size={20} /></div>
              <div className="stat-data">
                <span className="stat-num">{stats.total_factures}</span>
                <span className="stat-name">Documents Traités</span>
              </div>
            </div>
          </>
        )}
        <div className="stat-box">
          <div className="stat-icon-square green"><Users2 size={20} /></div>
          <div className="stat-data">
            <span className="stat-num">{stats.total_agents}</span>
            <span className="stat-name">{isSuper ? "Admins Système" : "Collaborateurs"}</span>
          </div>
        </div>
      </div>

      <div className="dashboard-main-grid">
        <div className="pro-card activity-feed">
          <div className="feed-header">
            <h3>Flux d'Activité</h3>
            <div className="real-time-badge">
              <span className="pulse-dot"></span> TEMPS RÉEL
            </div>
          </div>
          <div className="feed-content">
            {activities.length > 0 ? (
              activities.map((act) => (
                <div key={act.id} className="feed-item">
                  <div className={`feed-dot ${act.dot_color}`}></div>
                  <div className="feed-body">
                    <p className="feed-text">{formatMarkdown(act.title)}</p>
                    <span className="feed-time">{act.time}</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="feed-empty">
                <History size={32} />
                <p>Aucun événement récent.</p>
              </div>
            )}
          </div>
        </div>

        <div className="shortcuts-column">
          <h3 className="section-title">Navigation Rapide</h3>
          <div className="shortcut-list">
            <div className="shortcut-item" onClick={() => navigate(isSuper ? '/admin/cabinets' : '/admin/societes')}>
              <div className="shortcut-icon"><Building2 size={18} /></div>
              <div className="shortcut-text">
                <span className="shortcut-title">{isSuper ? 'Gérer les Cabinets' : 'Gérer les Sociétés'}</span>
                <span className="shortcut-desc">Configuration des entités</span>
              </div>
              <ArrowRight size={14} className="shortcut-arrow" />
            </div>

            <div className="shortcut-item" onClick={() => navigate('/admin/agents')}>
              <div className="shortcut-icon"><Users2 size={18} /></div>
              <div className="shortcut-text">
                <span className="shortcut-title">{isSuper ? 'Gérer les Admins' : 'Gérer les Agents'}</span>
                <span className="shortcut-desc">Contrôle des accès</span>
              </div>
              <ArrowRight size={14} className="shortcut-arrow" />
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .dashboard-page { padding: 24px; animation: fadeIn 0.4s ease-out; }
        .page-header-simple h1 { font-size: 24px; font-weight: 800; color: #0f172a; margin: 0; }
        .page-header-simple p { font-size: 14px; color: #64748b; margin: 8px 0 24px; }

        .stats-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .stat-box { 
          background: #fff; border: 1px solid #e2e8f0; border-radius: 4px; padding: 16px;
          display: flex; align-items: center; gap: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .stat-icon-square { width: 44px; height: 44px; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: white; }
        .stat-icon-square.blue { background: #3b82f6; }
        .stat-icon-square.purple { background: #8b5cf6; }
        .stat-icon-square.orange { background: #f59e0b; }
        .stat-icon-square.green { background: #10b981; }
        .stat-data { display: flex; flex-direction: column; }
        .stat-num { font-size: 20px; font-weight: 800; color: #0f172a; }
        .stat-name { font-size: 12px; font-weight: 600; color: #64748b; }

        .dashboard-main-grid { display: grid; grid-template-columns: 1fr 320px; gap: 24px; }
        .pro-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        
        .activity-feed { padding: 24px; }
        .feed-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .feed-header h3 { font-size: 16px; font-weight: 700; color: #0f172a; margin: 0; }
        .real-time-badge { font-size: 10px; font-weight: 800; color: #10b981; display: flex; align-items: center; gap: 6px; }
        .pulse-dot { width: 6px; height: 6px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite; }
        @keyframes pulse { 0% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.5); opacity: 0.5; } 100% { transform: scale(1); opacity: 1; } }

        .feed-content { display: flex; flex-direction: column; gap: 16px; }
        .feed-item { display: flex; gap: 12px; }
        .feed-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
        .feed-dot.blue { background: #3b82f6; }
        .feed-dot.purple { background: #8b5cf6; }
        .feed-dot.orange { background: #f59e0b; }
        .feed-dot.green { background: #10b981; }
        .feed-dot.red { background: #ef4444; }
        .feed-body { flex: 1; }
        .feed-text { font-size: 13px; color: #334155; line-height: 1.5; margin: 0; font-weight: 500; }
        .feed-time { font-size: 11px; color: #94a3b8; display: block; margin-top: 4px; }
        .feed-empty { padding: 48px; text-align: center; color: #cbd5e1; }

        .section-title { font-size: 14px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 16px; }
        .shortcut-list { display: flex; flex-direction: column; gap: 12px; }
        .shortcut-item { 
          background: #fff; border: 1px solid #e2e8f0; border-radius: 4px; padding: 12px;
          display: flex; align-items: center; gap: 12px; cursor: pointer; transition: all 0.2s;
        }
        .shortcut-item:hover { border-color: #3b82f6; transform: translateX(4px); }
        .shortcut-icon { width: 36px; height: 36px; background: #f1f5f9; color: #475569; border-radius: 4px; display: flex; align-items: center; justify-content: center; }
        .shortcut-text { flex: 1; display: flex; flex-direction: column; }
        .shortcut-title { font-size: 13px; font-weight: 700; color: #1e293b; }
        .shortcut-desc { font-size: 11px; color: #94a3b8; }
        .shortcut-arrow { color: #cbd5e1; }

        .placeholder-state { padding: 60px; text-align: center; }
        .dot-spinner { width: 24px; height: 24px; border: 3px solid #f1f5f9; border-top-color: #3b82f6; border-radius: 50%; animation: rot 0.8s linear infinite; margin: 0 auto 12px; }
        @keyframes rot { to { transform: rotate(360deg); } }

        @media (max-width: 1000px) {
          .dashboard-main-grid { grid-template-columns: 1fr; }
        }
      `}</style>
    </div>
  );
};
