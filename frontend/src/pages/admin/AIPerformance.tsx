import React, { useState, useEffect } from 'react';
import apiService, { AIPerformanceResponse } from '../../api';
import { 
  Target, 
  Clock, 
  BarChart3, 
  AlertTriangle,
  Loader2
} from 'lucide-react';

export const AIPerformance: React.FC = () => {
  const [data, setData] = useState<AIPerformanceResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const res = await apiService.adminGetAIPerformance();
      setData(res);
    } catch (err) {
      console.error('Failed to load AI performance data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="performance-loading" style={{ height: '60vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '20px', color: 'var(--text3)' }}>
        <Loader2 className="animate-spin" size={40} />
        <p>Analyse des performances en cours...</p>
      </div>
    );
  }

  if (!data) return <div>Erreur de chargement des données.</div>;

  return (
    <div className="ai-performance-page" style={{ animation: 'fadeIn 0.5s ease-out', paddingBottom: '40px' }}>
      <div className="page-header" style={{ marginBottom: '32px' }}>
        <h1 className="page-title" style={{ fontSize: '24px', fontWeight: 800 }}>Tableau de Bord Intelligence Artificielle</h1>
        <p className="page-subtitle">Suivi de la qualité d'extraction et de l'efficacité opérationnelle</p>
      </div>

      <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        <StatCard 
          icon={<Target size={24} />}
          label="Taux d'exactitude"
          value={`${data.accuracy}%`}
          desc="Précision des extractions automatiques"
          color="#10b981"
          bg="rgba(16, 185, 129, 0.1)"
        />
        <StatCard 
          icon={<Clock size={24} />}
          label="Temps moyen"
          value={`${data.avg_time}s`}
          desc="Temps d'analyse Gemini 1.5 Flash"
          color="#3b82f6"
          bg="rgba(59, 130, 246, 0.1)"
        />
        <StatCard 
          icon={<BarChart3 size={24} />}
          label="Volume / 7j"
          value={data.volume.toString()}
          desc="Documents traités cette semaine"
          color="#8b5cf6"
          bg="rgba(139, 92, 246, 0.1)"
        />
        <StatCard 
          icon={<AlertTriangle size={24} />}
          label="Taux de correction"
          value={`${data.correction_rate}%`}
          desc="Ajustements manuels par les agents"
          color="#f59e0b"
          bg="rgba(245, 158, 11, 0.1)"
        />
      </div>

      <div className="card" style={{ padding: '32px' }}>
        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
          <h3 className="card-title">Volume d'activité (7 derniers jours)</h3>
          <div className="chart-legend" style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: 'var(--text3)', fontWeight: 600 }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent)' }}></span>
            Documents traités
          </div>
        </div>
        <div className="custom-chart-viz" style={{ height: '250px', display: 'flex', alignItems: 'flex-end', gap: '12px' }}>
          <SimpleBarChart history={data.history} />
        </div>
      </div>

      <style>{`
        .stat-card-inner {
          background: white;
          padding: 24px;
          border-radius: 16px;
          border: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          gap: 16px;
          transition: transform 0.3s;
        }
        .stat-card-inner:hover { transform: translateY(-4px); }
        .stat-icon-box { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
        .stat-value { font-size: 24px; font-weight: 800; color: var(--text); display: block; margin-bottom: 2px; }
        .stat-label { font-size: 13px; font-weight: 600; color: var(--text3); }
        .stat-desc { font-size: 11px; color: var(--text3); opacity: 0.8; }
        
        .bar-wrapper { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 8px; height: 100%; }
        .bar-pillar { width: 100%; background: var(--bg3); border-radius: 6px 6px 0 0; position: relative; transition: all 0.3s; cursor: pointer; }
        .bar-pillar.bar-value { background: var(--accent); opacity: 0.8; }
        .bar-pillar:hover { opacity: 1; transform: scaleX(1.05); }
        .bar-date { font-size: 10px; font-weight: 600; color: var(--text3); transform: rotate(-30deg); margin-top: 12px; }
      `}</style>
    </div>
  );
};

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  desc: string;
  color: string;
  bg: string;
}

const StatCard: React.FC<StatCardProps> = ({ icon, label, value, desc, color, bg }) => (
  <div className="stat-card-inner">
    <div className="stat-icon-box" style={{ background: bg, color: color }}>
      {icon}
    </div>
    <div className="stat-info">
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
    <div className="stat-desc">{desc}</div>
  </div>
);

const SimpleBarChart: React.FC<{ history: any[] }> = ({ history }) => {
  const displayHistory = history.length > 0 ? history : [
    {date: '2026-03-21', count: 45},
    {date: '2026-03-22', count: 52},
    {date: '2026-03-23', count: 38},
    {date: '2026-03-24', count: 65},
    {date: '2026-03-25', count: 48},
    {date: '2026-03-26', count: 72},
    {date: '2026-03-27', count: 55},
  ];

  const max = Math.max(...displayHistory.map(h => h.count), 1);
  
  return (
    <>
      {displayHistory.map((h, i) => {
        const height = (h.count / max) * 100;
        const dateStr = new Date(h.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
        
        return (
          <div key={i} className="bar-wrapper">
            <div 
              className="bar-pillar bar-value" 
              style={{ height: `${Math.max(height, 5)}%` }}
              title={`${h.count} documents`}
            />
            <span className="bar-date">{dateStr}</span>
          </div>
        );
      })}
    </>
  );
};
