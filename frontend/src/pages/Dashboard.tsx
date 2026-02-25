import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService from '../api'

const STATUS_ORDER = ['IMPORTED', 'EXTRACTED', 'CLASSIFIED', 'DRAFT', 'VALIDATED', 'EXPORTED', 'ERROR']

function StatusBadge({ status }: { status: string }) {
    return <span className={`badge badge-${status.toLowerCase()}`}>{status}</span>
}

export default function Dashboard() {
    const [factures, setFactures] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('')
    const navigate = useNavigate()

    const load = async () => {
        setLoading(true)
        try {
            const data = await apiService.listFactures(filter || undefined)
            setFactures(data)
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { load() }, [filter])

    const stats = {
        total: factures.length,
        validated: factures.filter(f => f.status === 'VALIDATED').length,
        draft: factures.filter(f => f.status === 'DRAFT').length,
        error: factures.filter(f => f.status === 'ERROR').length,
    }

    const handleDelete = async (id: number, numero: string | null) => {
        if (!window.confirm(`Êtes-vous sûr de vouloir supprimer la facture ${numero || id} ? Cette action est irréversible.`)) {
            return
        }
        try {
            await apiService.deleteFacture(id)
            load() // Recharger la liste
        } catch (e) {
            console.error(e)
            alert("Erreur lors de la suppression")
        }
    }

    return (
        <div>
            {/* ... (previous code) */}
            <div className="page-header">
                <h1 className="page-title">Tableau de bord</h1>
                <p className="page-subtitle">Vue d'ensemble des factures et écritures comptables</p>
            </div>

            {/* Stats */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-value">{stats.total}</div>
                    <div className="stat-label">Documents en cours</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: 'var(--success)' }}>{stats.validated}</div>
                    <div className="stat-label">Dossiers validés</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: 'var(--warning)' }}>{stats.draft}</div>
                    <div className="stat-label">Travaux en attente</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: 'var(--danger)' }}>{stats.error}</div>
                    <div className="stat-label">Anomalies détectées</div>
                </div>
            </div>

            {/* Filters + Table */}
            <div className="card">
                <div className="card-header">
                    <div>
                        <div className="card-title">Factures</div>
                        <div className="card-subtitle">Cliquez sur une facture pour voir le détail</div>
                    </div>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                        <select
                            className="form-input"
                            style={{ width: 'auto' }}
                            value={filter}
                            onChange={e => setFilter(e.target.value)}
                        >
                            <option value="">Tous les statuts</option>
                            {STATUS_ORDER.map(s => <option key={s} value={s}>{s}</option>)}
                        </select>
                        <button className="btn btn-primary" onClick={() => navigate('/upload')}>
                            Transmission de documents
                        </button>
                    </div>
                </div>

                {loading ? (
                    <div className="loading"><div className="spinner" /> Chargement...</div>
                ) : factures.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">📭</div>
                        <div className="empty-title">Aucune facture</div>
                        <div className="empty-subtitle">Importez votre première facture pour commencer</div>
                    </div>
                ) : (
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>N° Facture</th>
                                    <th>Date</th>
                                    <th>Type</th>
                                    <th>Fournisseur</th>
                                    <th>Montant TTC</th>
                                    <th>Statut</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {factures.map(f => (
                                    <tr key={f.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/factures/${f.id}`)}>
                                        <td style={{ color: 'var(--text3)', fontFamily: 'monospace' }}>{f.id}</td>
                                        <td style={{ fontWeight: 600 }}>{f.numero_facture || '—'}</td>
                                        <td>{f.date_facture || '—'}</td>
                                        <td>
                                            <span style={{ fontSize: '12px', color: 'var(--text2)' }}>
                                                {f.invoice_type || '—'}
                                            </span>
                                        </td>
                                        <td>{f.supplier_name || '—'}</td>
                                        <td style={{ fontWeight: 600 }}>
                                            {f.montant_ttc != null
                                                ? `${f.montant_ttc.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} ${f.devise || 'MAD'}`
                                                : '—'}
                                        </td>
                                        <td><StatusBadge status={f.status} /></td>
                                        <td>
                                            <div style={{ display: 'flex', gap: '4px' }}>
                                                <button
                                                    className="btn btn-ghost"
                                                    style={{ padding: '6px 12px', fontSize: '12px' }}
                                                    onClick={e => { e.stopPropagation(); navigate(`/factures/${f.id}`) }}
                                                >
                                                    Voir
                                                </button>
                                                <button
                                                    className="btn btn-ghost"
                                                    style={{ padding: '6px 12px', fontSize: '12px', color: 'var(--danger)' }}
                                                    onClick={e => { e.stopPropagation(); handleDelete(f.id, f.numero_facture) }}
                                                    title="Supprimer la facture"
                                                >
                                                    Supprimer
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    )
}
