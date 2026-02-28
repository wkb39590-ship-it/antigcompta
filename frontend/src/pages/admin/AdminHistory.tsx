import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { getAdminUser } from '../../utils/adminTokenDecoder';

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

    const getActionBadgeClass = (type: string) => {
        switch (type) {
            case 'CREATE': return 'badge-create';
            case 'UPDATE': return 'badge-update';
            case 'DELETE': return 'badge-delete';
            case 'VALIDATE': return 'badge-validate';
            default: return 'badge-default';
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
        <div className="admin-history-page">
            <div className="admin-page-header">
                <h1 className="glass-text">Historique des Actions</h1>
                <p>Suivez toutes les interventions effectuées sur le système.</p>
            </div>

            <div className="aurora-wide-card aurora-card">
                {loading ? (
                    <div className="aurora-loader">
                        <div className="loader-spinner"></div>
                        <span>Chargement des logs...</span>
                    </div>
                ) : error ? (
                    <div className="aurora-error-state">{error}</div>
                ) : (
                    <div className="aurora-table-wrapper">
                        <table className="aurora-table">
                            <thead>
                                <tr>
                                    <th>DATE & HEURE</th>
                                    <th>ACTION</th>
                                    <th>ENTITÉ</th>
                                    <th>AGENT</th>
                                    <th>DÉTAILS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {logs.length > 0 ? (
                                    logs.map((log) => (
                                        <tr key={log.id}>
                                            <td className="time-cell">{formatDate(log.created_at)}</td>
                                            <td>
                                                <span className={`action-badge ${getActionBadgeClass(log.action_type)}`}>
                                                    {log.action_type}
                                                </span>
                                            </td>
                                            <td className="entity-cell">{log.entity_type}</td>
                                            <td className="agent-cell">
                                                <div className="agent-info">
                                                    <span className="agent-username">@{log.agent_username || 'Système'}</span>
                                                </div>
                                            </td>
                                            <td className="details-cell">{log.details}</td>
                                        </tr>
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan={5} className="empty-state">Aucune action enregistrée pour le moment.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <style>{`
        .admin-history-page {
          animation: fadeIn 0.8s ease-out;
        }

        .action-badge {
          padding: 4px 10px;
          border-radius: 8px;
          font-size: 11px;
          font-weight: 800;
          text-transform: uppercase;
        }

        .badge-create { background: rgba(16, 185, 129, 0.1); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.2); }
        .badge-update { background: rgba(59, 130, 246, 0.1); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.2); }
        .badge-delete { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
        .badge-validate { background: rgba(168, 85, 247, 0.1); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.2); }
        .badge-default { background: rgba(148, 163, 184, 0.1); color: #94a1b8; border: 1px solid rgba(148, 163, 184, 0.2); }

        .time-cell { font-family: monospace; color: var(--admin-text-dim); }
        .entity-cell { font-weight: 700; color: var(--admin-text); }
        .agent-username { color: var(--admin-accent); font-weight: 600; }
        .details-cell { color: var(--admin-text-dim); max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        .aurora-table-wrapper {
          margin-top: 10px;
          overflow-x: auto;
        }
      `}</style>
        </div>
    );
};
