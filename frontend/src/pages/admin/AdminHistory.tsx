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
        <div className="history-page">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Historique Système</h1>
                    <p className="page-subtitle">Rapport d'audit complet des flux et opérations transverses.</p>
                </div>
            </div>

            <div className="page-content">
                <div className="data-card">
                    <div className="card-header">
                        <div className="header-title-box">
                            <History size={16} className="icon-subtle" />
                            <span>Journal d'audit</span>
                        </div>
                        <div className="system-indicator">
                            <span className="live-dot"></span>
                            Surveillance active
                        </div>
                    </div>

                    {loading ? (
                        <div className="busy-overlay">
                            <div className="standard-loader"></div>
                            <span>Chargement de la base d'audit...</span>
                        </div>
                    ) : error ? (
                        <div className="busy-overlay text-error">
                            <AlertCircle size={32} />
                            <p>{error}</p>
                        </div>
                    ) : (
                        <div className="grid-container">
                            <table className="pro-table">
                                <thead>
                                    <tr>
                                        <th>Horodatage</th>
                                        <th>Événement</th>
                                        <th>Entité</th>
                                        <th>Opérateur</th>
                                        <th>Observations</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {logs.length > 0 ? (
                                        logs.map((log) => {
                                            const action = getActionContent(log.action_type);
                                            return (
                                                <tr key={log.id}>
                                                    <td className="w-time">
                                                        <div className="inline-flex-center">
                                                            <Clock size={12} className="icon-muted" />
                                                            <span>{formatDate(log.created_at)}</span>
                                                        </div>
                                                    </td>
                                                    <td className="w-event">
                                                        <span className={`static-tag ${action.className}`}>
                                                            {action.icon}
                                                            {action.label}
                                                        </span>
                                                    </td>
                                                    <td className="w-module">
                                                        <div className="module-item">
                                                            {log.entity_type === 'DEMANDE_ACCES' ? <Zap size={10} /> : <FileText size={10} />}
                                                            {log.entity_type}
                                                        </div>
                                                    </td>
                                                    <td className="w-responsible">
                                                        <div className="agent-profile">
                                                            <div className="avatar-square">{log.agent_username?.[0]?.toUpperCase() || 'S'}</div>
                                                            <span className="username-link">@{log.agent_username || 'système'}</span>
                                                        </div>
                                                    </td>
                                                    <td className="w-details">
                                                        <div className="line-clamp" title={log.details || ''}>
                                                            {log.details || <span className="muted-italic">Détail non spécifié</span>}
                                                        </div>
                                                    </td>
                                                </tr>
                                            );
                                        })
                                    ) : (
                                        <tr>
                                            <td colSpan={5} className="empty-row">
                                                <div className="empty-hint">
                                                    <History size={48} className="icon-muted" />
                                                    <p>Aucun enregistrement d'audit trouvé.</p>
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
                .history-page { padding: 30px; background: #fafafa; min-height: 100vh; font-family: 'Inter', sans-serif; }
                .page-header { margin-bottom: 25px; }
                .page-title { font-size: 26px; font-weight: 700; color: #111827; margin: 0; letter-spacing: -0.5px; }
                .page-subtitle { color: #6b7280; font-size: 14px; margin-top: 4px; }

                .data-card { background: #fff; border: 1px solid #e5e7eb; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
                .card-header { padding: 12px 20px; border-bottom: 1px solid #e5e7eb; background: #f9fafb; display: flex; justify-content: space-between; align-items: center; }
                .header-title-box { display: flex; align-items: center; gap: 10px; font-weight: 600; color: #374151; font-size: 14px; }

                .system-indicator { display: flex; align-items: center; gap: 8px; font-size: 11px; font-weight: 700; color: #10b981; background: #f0fdf4; padding: 4px 10px; border-radius: 3px; border: 1px solid #dcfce7; }
                .live-dot { width: 6px; height: 6px; background: #10b981; border-radius: 50%; box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2); }

                .pro-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
                .pro-table th { padding: 10px 20px; text-align: left; font-size: 11px; font-weight: 700; color: #6b7280; text-transform: uppercase; letter-spacing: 0.1em; border-bottom: 1px solid #e5e7eb; background: #fff; }
                .pro-table td { padding: 10px 20px; border-bottom: 1px solid #f3f4f6; vertical-align: middle; }
                .pro-table tr:hover { background: #fcfcfc; }

                .inline-flex-center { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #4b5563; }
                .icon-muted { color: #9ca3af; }
                .icon-subtle { color: #6b7280; }

                .static-tag { display: inline-flex; align-items: center; gap: 6px; padding: 3px 8px; border-radius: 3px; font-size: 10px; font-weight: 700; text-transform: uppercase; }
                .badge-create { background: #f0fdf4; color: #166534; border: 1px solid #dcfce7; }
                .badge-update { background: #eff6ff; color: #1e40af; border: 1px solid #dbeafe; }
                .badge-delete { background: #fef2f2; color: #991b1b; border: 1px solid #fee2e2; }
                .badge-validate { background: #f5f3ff; color: #5b21b6; border: 1px solid #ede9fe; }
                .badge-default { background: #f3f4f6; color: #374151; border: 1px solid #e5e7eb; }

                .module-item { display: inline-flex; align-items: center; gap: 6px; padding: 4px 8px; border: 1px solid #e5e7eb; border-radius: 3px; color: #374151; font-size: 10px; font-weight: 700; }

                .agent-profile { display: flex; align-items: center; gap: 8px; }
                .avatar-square { width: 22px; height: 22px; background: #f3f4f6; border: 1px solid #d1d5db; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 10px; color: #4b5563; }
                .username-link { font-size: 13px; font-weight: 600; color: #4f46e5; }

                .line-clamp { margin: 0; font-size: 13px; color: #4b5563; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
                .muted-italic { color: #9ca3af; font-style: italic; font-size: 12px; }

                .busy-overlay { padding: 60px 0; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 15px; color: #6b7280; font-size: 14px; }
                .standard-loader { width: 20px; height: 20px; border: 2px solid #e5e7eb; border-top-color: #4f46e5; border-radius: 50%; animation: rot 0.8s linear infinite; }
                @keyframes rot { to { transform: rotate(360deg); } }
                .text-error { color: #dc2626; }

                .empty-hint { padding: 60px 0; text-align: center; color: #9ca3af; }
                .empty-hint p { margin-top: 10px; font-size: 14px; }
            `}</style>
        </div>
    );

};
