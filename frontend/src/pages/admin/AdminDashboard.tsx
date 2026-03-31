import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { useNavigate } from 'react-router-dom';
import { getAdminUser } from '../../utils/adminTokenDecoder';
import {
  LayoutDashboard,
  Building2,
  Building,
  FileText,
  Users2,
  Activity as ActivityIcon,
  ArrowRight,
  PlusCircle,
  FileSpreadsheet,
  TrendingUp,
  Globe,
  Briefcase,
  History,
  Zap
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

  const formatMarkdown = (text: string) => {
    const parts = text.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} style={{ color: 'var(--accent)' }}>{part.slice(2, -2)}</strong>;
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
    <div className="aurora-loader-context">
      <div className="creative-spinner"></div>
      <p>Synchronisation Système...</p>
    </div>
  );

  return (
    <div className="admin-dashboard-aurora-2">
      {/* ── Dashboard Header ── */}
      <div className="dashboard-hero-section">
        <div className="hero-text">
          <h1 className="hero-title heading-font">
            Bonjour, <span className="glass-text">{getAdminUser()?.prenom || 'Admin'}</span>
          </h1>
          <p className="hero-subtitle">
            {isSuper ? "Superviseur Central" : `Gestionnaire • ${cabinetName}`} — Voici l'état de votre infrastructure.
          </p>
        </div>
      </div>

      <div className="dashboard-grid-v2">
        {/* ── Stats Row ── */}
        <div className="stats-row">
          {isSuper ? (
            <div className="stat-card-v2 aurora-card">
              <div className="stat-top">
                <span className="value">{stats.total_cabinets}</span>
                <Globe size={24} className="stat-icon purple" />
              </div>
              <span className="label">Cabinets Partenaires</span>
            </div>
          ) : (
            <>
              <div className="stat-card-v2 aurora-card">
                <div className="stat-top">
                  <span className="value">{stats.total_societes}</span>
                  <Briefcase size={24} className="stat-icon blue" />
                </div>
                <span className="label">Sociétés Gérées</span>
              </div>
              <div className="stat-card-v2 aurora-card">
                <div className="stat-top">
                  <span className="value">{stats.total_factures}</span>
                  <FileText size={24} className="stat-icon gold" />
                </div>
                <span className="label">Flux Documentaires</span>
              </div>
            </>
          )}

          <div className="stat-card-v2 aurora-card">
            <div className="stat-top">
              <span className="value">{stats.total_agents}</span>
              <Users2 size={24} className="stat-icon green" />
            </div>
            <span className="label">{isSuper ? "Admins Système" : "Collaborateurs"}</span>
          </div>
        </div>

        {/* ── Main Content Area ── */}
        <div className="dashboard-main-area">
          {/* Timeline Activities */}
          <div className="timeline-card aurora-card">
            <div className="area-header">
              <h2 className="heading-font">Flux d'Activité</h2>
              <div className="live-indicator"><span className="dot"></span> Temps Réel</div>
            </div>
            <div className="timeline-content">
              {activities.length > 0 ? (
                activities.map((act) => (
                  <div key={act.id} className="timeline-item">
                    <div className="timeline-marker">
                      <div className={`marker-dot ${act.dot_color}`}></div>
                      <div className="marker-line"></div>
                    </div>
                    <div className="timeline-info">
                      <div className="timeline-text">{formatMarkdown(act.title)}</div>
                      <div className="timeline-time">{act.time}</div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-activities">
                  <History size={40} opacity={0.3} />
                  <p>Aucune activité enregistrée</p>
                </div>
              )}
            </div>
          </div>

          {/* Shortcuts Grid */}
          <div className="shortcuts-area">
            <h2 className="area-title heading-font">Actions Rapides</h2>
            <div className="modern-shortcut-grid">
              <div className="m-shortcut-card aurora-card" onClick={() => navigate(isSuper ? '/admin/cabinets' : '/admin/societes')}>
                <div className="m-icon blue"><Building2 size={20} /></div>
                <div className="m-text">
                  <h3>{isSuper ? 'Gérer Cabinets' : 'Gérer Sociétés'}</h3>
                  <p>Configuration et paramètres</p>
                </div>
                <ArrowRight size={16} className="m-arrow" />
              </div>

              <div className="m-shortcut-card aurora-card" onClick={() => navigate('/admin/agents')}>
                <div className="m-icon purple"><Users2 size={20} /></div>
                <div className="m-text">
                  <h3>{isSuper ? 'Gérer Admins' : 'Agents'}</h3>
                  <p>Droits et accès utilisateurs</p>
                </div>
                <ArrowRight size={16} className="m-arrow" />
              </div>

              {!isSuper && (
                <div className="m-shortcut-card aurora-card" onClick={() => alert('Rapports PDF bientôt disponible')}>
                  <div className="m-icon gold"><FileSpreadsheet size={20} /></div>
                  <div className="m-text">
                    <h3>Rapports PDF</h3>
                    <p>Télécharger les statistiques</p>
                  </div>
                  <ArrowRight size={16} className="m-arrow" />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      <style>{`
        .admin-dashboard-aurora-2 {
          animation: pageFadeIn 0.8s ease-out;
          padding-bottom: 80px;
        }

        @keyframes pageFadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .dashboard-hero-section {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 40px;
          padding: 0 10px;
        }

        .hero-title { font-size: 42px; font-weight: 800; margin: 0; letter-spacing: -1.5px; }
        .hero-subtitle { color: var(--text3); font-size: 16px; margin-top: 5px; font-weight: 500; }

        .hero-badge {
          display: flex;
          align-items: center;
          gap: 10px;
          background: linear-gradient(135deg, #1e293b, #0f172a);
          padding: 10px 24px;
          border-radius: 40px;
          color: white;
          font-weight: 800;
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 1px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2), inset 0 2px 4px rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .dashboard-grid-v2 {
          display: flex;
          flex-direction: column;
          gap: 30px;
        }

        .stats-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
          gap: 20px;
        }

        .stat-card-v2 {
          display: flex;
          flex-direction: column;
          gap: 12px;
          padding: 24px;
        }

        .stat-top {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          width: 100%;
        }

        .stat-icon {
          opacity: 0.5;
          transition: transform 0.3s;
        }
        .stat-card-v2:hover .stat-icon { transform: scale(1.1) rotate(5deg); opacity: 0.8; }

        .stat-icon.blue { color: #3b82f6; }
        .stat-icon.purple { color: #8b5cf6; }
        .stat-icon.green { color: #10b981; }
        .stat-icon.gold { color: #f59e0b; }
        .stat-icon.indigo { color: #6366f1; }

        .stat-card-v2 .label { display: block; font-size: 11px; font-weight: 800; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; }
        .stat-card-v2 .value { display: block; font-size: 32px; font-weight: 900; color: var(--text); font-family: 'Outfit', sans-serif; }

        .dashboard-main-area {
          display: grid;
          grid-template-columns: 1fr 340px;
          gap: 30px;
        }

        .area-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }
        .area-header h2 { font-size: 20px; font-weight: 800; margin: 0; }

        .live-indicator {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 11px;
          font-weight: 800;
          color: var(--danger);
          padding: 4px 12px;
          background: rgba(239, 68, 68, 0.05);
          border-radius: 20px;
        }
        .live-indicator .dot { width: 6px; height: 6px; background: #ef4444; border-radius: 50%; animation: pulseRed 2s infinite; }
        @keyframes pulseRed { 0% { transform: scale(0.9); opacity: 0.7; } 50% { transform: scale(1.2); opacity: 1; } 100% { transform: scale(0.9); opacity: 0.7; } }

        .timeline-card { padding: 30px; }
        .timeline-content { position: relative; }

        .timeline-item { display: flex; gap: 20px; margin-bottom: 25px; }
        .timeline-marker { display: flex; flex-direction: column; align-items: center; }
        .marker-dot { width: 12px; height: 12px; border-radius: 50%; background: #e2e8f0; border: 3px solid white; z-index: 2; }
        .marker-dot.blue { background: #3b82f6; box-shadow: 0 0 10px rgba(59, 130, 246, 0.5); }
        .marker-dot.purple { background: #a855f7; box-shadow: 0 0 10px rgba(168, 85, 247, 0.5); }
        .marker-dot.orange { background: #f59e0b; box-shadow: 0 0 10px rgba(245, 158, 11, 0.5); }
        .marker-dot.green { background: #10b981; box-shadow: 0 0 10px rgba(16, 185, 129, 0.5); }
        .marker-line { width: 2px; flex: 1; background: #f1f5f9; margin-top: 5px; }
        .timeline-item:last-child .marker-line { display: none; }

        .timeline-info { padding-bottom: 10px; }
        .timeline-text { font-size: 14px; font-weight: 600; color: var(--text); line-height: 1.5; }
        .timeline-time { font-size: 12px; color: var(--text3); margin-top: 4px; }

        .area-title { font-size: 18px; font-weight: 800; margin: 0 0 20px 0; }
        .modern-shortcut-grid { display: flex; flex-direction: column; gap: 15px; }
        .m-shortcut-card {
          padding: 20px;
          display: flex;
          align-items: center;
          gap: 15px;
          cursor: pointer;
        }
        .m-icon { 
          width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center;
          box-shadow: 0 8px 15px -5px rgba(0,0,0,0.1), inset 0 2px 4px rgba(255,255,255,0.8);
          border: 1px solid rgba(0,0,0,0.05);
          transition: transform 0.3s;
        }
        .m-icon.blue { background: #eff6ff; color: #3b82f6; }
        .m-icon.purple { background: #f5f3ff; color: #8b5cf6; }
        .m-icon.gold { background: #fffbeb; color: #f59e0b; }
        
        .m-shortcut-card:hover .m-icon { transform: scale(1.05) rotate(-3deg); }
        
        .m-text { flex: 1; }
        .m-text h3 { margin: 0; font-size: 14px; font-weight: 800; }
        .m-text p { margin: 2px 0 0 0; font-size: 11px; color: var(--text3); font-weight: 600; }
        .m-arrow { color: var(--text3); opacity: 0.5; transition: transform 0.3s; }
        .m-shortcut-card:hover .m-arrow { transform: translateX(5px); opacity: 1; color: var(--accent); }

        .aurora-loader-context { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; gap: 20px; color: var(--text3); }
        .creative-spinner { width: 40px; height: 40px; border: 4px solid #f1f5f9; border-top-color: var(--accent); border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        @media (max-width: 1200px) {
          .dashboard-main-area { grid-template-columns: 1fr; }
        }
      `}</style>
    </div>
  );
};
