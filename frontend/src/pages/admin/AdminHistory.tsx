import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { getAdminUser } from '../../utils/adminTokenDecoder';
import {
    History,
    PlusCircle,
    RotateCw,
    Trash2,
    CheckCircle2,
    Clock,
    User,
    FileText,
    AlertCircle,
    Zap
} from 'lucide-react';

interface AdminLog {
    id: number;
    cabinet_id: number | null;
    agent_username: string | null;
    action_type: string;
    entity_type: string;
    details: string | null;
    created_at: string;
}

export const AdminHistory: React.FC = () => {
    const [logs, setLogs] = useState<AdminLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const adminUser = getAdminUser();

    const fetchData = async () => {
        try {
            setLoading(true);
            const data = await apiService.adminGetLogs(0, 100);
            setLogs(data.logs);
            setError('');
        } catch (err: any) {
            setError("Impossible de charger l'historique.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const getActionContent = (type: string) => {
        switch (type) {
            case 'CREATE': return { icon: <PlusCircle size={14} />, label: 'Création', className: 'badge-create' };
            case 'UPDATE': return { icon: <RotateCw size={14} />, label: 'Mise à jour', className: 'badge-update' };
            case 'DELETE': return { icon: <Trash2 size={14} />, label: 'Suppression', className: 'badge-delete' };
            case 'VALIDATE': return { icon: <CheckCircle2 size={14} />, label: 'Validation', className: 'badge-validate' };
            default: return { icon: <History size={14} />, label: type, className: 'badge-default' };
        }
    };

    const formatDate = (dateStr: string) => {
        const d = new Date(dateStr);
        return d.toLocaleString('fr-FR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="aurora-page-v2">
            <div className="aurora-page-header">
                <div className="header-info">
                    <h1 className="hero-title heading-font">Historique Système</h1>
                    <p className="aurora-subtitle">Audit trail complet des flux et opérations transverses.</p>
                </div>
            </div>

            <div className="aurora-content-grid">
                <div className="aurora-card table-card history-container">
                    <div className="card-header-flex">
                        <h2 className="heading-font">Flux d'activités récentes</h2>
                        <div className="glass-pill">Audit Trail Actif</div>
                    </div>

                    {loading ? (
                        <div className="aurora-loader-inline">
                            <div className="spinner-aurora"></div>
                            <span>Récupération des logs sécurisés...</span>
                        </div>
                    ) : error ? (
                        <div className="aurora-error-v2">
                            <AlertCircle size={40} />
                            <p>{error}</p>
                        </div>
                    ) : (
                        <div className="table-responsive">
                            <table className="aurora-table-v2">
                                <thead>
                                    <tr>
                                        <th>Horodatage</th>
                                        <th>Événement</th>
                                        <th>Module</th>
                                        <th>Responsable</th>
                                        <th>Description</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {logs.length > 0 ? (
                                        logs.map((log) => {
                                            const action = getActionContent(log.action_type);
                                            return (
                                                <tr key={log.id}>
                                                    <td>
                                                        <div className="time-td-v2">
                                                            <Clock size={12} />
                                                            <span>{formatDate(log.created_at)}</span>
                                                        </div>
                                                    </td>
                                                    <td>
                                                        <span className={`status-pill ${action.className}`}>
                                                            {action.icon}
                                                            {action.label}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        <div className="module-tag-v2">
                                                            {log.entity_type === 'DEMANDE_ACCES' ? <Zap size={12} /> : <FileText size={12} />}
                                                            {log.entity_type}
                                                        </div>
                                                    </td>
                                                    <td>
                                                        <div className="agent-box-v2">
                                                            <div className="agent-avatar-mini">{log.agent_username?.[0]?.toUpperCase() || 'S'}</div>
                                                            <span className="agent-un">@{log.agent_username || 'système'}</span>
                                                        </div>
                                                    </td>
                                                    <td>
                                                        <div className="details-col-v2" title={log.details || ''}>
                                                            {log.details || <span className="no-details">Aucun détail additionnel</span>}
                                                        </div>
                                                    </td>
                                                </tr>
                                            );
                                        })
                                    ) : (
                                        <tr>
                                            <td colSpan={5}>
                                                <div className="aurora-empty-v2">
                                                    <History size={40} />
                                                    <p>Historique vierge.</p>
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>

            <style>{`
        .aurora-page-v2 { animation: fadeIn 0.8s ease-out; padding-bottom: 80px; }
        
        .aurora-page-header { margin-bottom: 35px; }
        .hero-title { font-size: 38px; font-weight: 800; margin: 0; letter-spacing: -1.5px; }
        .aurora-subtitle { color: var(--text3); font-size: 14px; font-weight: 500; margin-top: 4px; }

        .aurora-content-grid { display: flex; flex-direction: column; gap: 30px; }

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
        
        .aurora-table-v2 td { padding: 18px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
        .aurora-table-v2 tr:hover { background: rgba(99, 102, 241, 0.02); }

        .time-td-v2 { display: flex; align-items: center; gap: 8px; color: var(--text3); font-size: 13px; font-weight: 500; }
        
        .status-pill { 
          display: inline-flex; align-items: center; gap: 6px; 
          padding: 6px 12px; border-radius: 10px; font-size: 11px; font-weight: 800;
          text-transform: uppercase;
        }
        .badge-create { background: rgba(16, 185, 129, 0.08); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.15); }
        .badge-update { background: rgba(59, 130, 246, 0.08); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.15); }
        .badge-delete { background: rgba(239, 68, 68, 0.08); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.15); }
        .badge-validate { background: rgba(168, 85, 247, 0.08); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.15); }
        .badge-default { background: #f1f5f9; color: var(--text3); border: 1px solid #e2e8f0; }

        .module-tag-v2 { 
          display: inline-flex; align-items: center; gap: 6px; 
          padding: 5px 10px; background: #f8fafc; border: 1px solid #e2e8f0;
          border-radius: 8px; color: var(--text2); font-size: 12px; font-weight: 700;
        }

        .agent-box-v2 { display: flex; align-items: center; gap: 10px; }
        .agent-avatar-mini { 
          width: 28px; height: 28px; border-radius: 8px; background: #f1f5f9;
          display: flex; align-items: center; justify-content: center;
          font-weight: 800; font-size: 11px; color: var(--text2); border: 1px solid #e2e8f0;
          box-shadow: inset 0 2px 4px rgba(255,255,255,0.8);
        }
        .agent-un { font-size: 13px; font-weight: 700; color: var(--accent); }

        .details-col-v2 { 
          max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
          font-size: 13px; color: var(--text3); font-weight: 500;
        }
        .no-details { font-style: italic; opacity: 0.5; }

        .aurora-loader-inline { padding: 60px; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 15px; color: var(--text3); }
        .spinner-aurora { width: 32px; height: 32px; border: 3px solid #f1f5f9; border-top-color: var(--accent); border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        .aurora-error-v2 { padding: 60px 0; text-align: center; color: #ef4444; display: flex; flex-direction: column; align-items: center; gap: 15px; }
        .aurora-empty-v2 { padding: 60px 0; text-align: center; color: var(--text3); opacity: 0.3; }
      `}</style>
        </div>
    );
};
