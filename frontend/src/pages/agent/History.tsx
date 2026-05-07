import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService from '../../api'
import {
    Download,
    Search,
    Brain,
    FileEdit,
    CheckCircle2,
    ExternalLink,
    XCircle,
    Construction,
    BadgeCheck,
    Trash2,
    History as HistoryIcon,
    FileText,
    User,
    Calendar,
    Info
} from 'lucide-react'

function StatusBadge({ status }: { status: string }) {
    const cls = `badge badge-${status.toLowerCase()}`
    const icons: Record<string, any> = {
        IMPORTED: <Download size={14} />,
        EXTRACTED: <Search size={14} />,
        CLASSIFIED: <Brain size={14} />,
        DRAFT: <FileEdit size={14} />,
        VALIDATED: <CheckCircle2 size={14} />,
        EXPORTED: <ExternalLink size={14} />,
        ERROR: <XCircle size={14} />
    }
    return (
        <span className={cls} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
            {icons[status] || '•'} {status}
        </span>
    )
}

export default function History() {
    const [activeTab, setActiveTab] = useState<'factures' | 'activities'>('activities')
    const [factures, setFactures] = useState<any[]>([])
    const [filteredFactures, setFilteredFactures] = useState<any[]>([])
    const [activities, setActivities] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate()

    const [search, setSearch] = useState('')
    const [statusFilter, setStatusFilter] = useState('')
    const [dateStart, setDateStart] = useState('')
    const [dateEnd, setDateEnd] = useState('')
    const [amountMin, setAmountMin] = useState('')
    const [amountMax, setAmountMax] = useState('')

    const loadData = async () => {
        setLoading(true)
        try {
            if (activeTab === 'factures') {
                const data = await apiService.listFactures()
                setFactures(data)
                setFilteredFactures(data)
            } else {
                const data = await apiService.getActivities()
                setActivities(data)
            }
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { loadData() }, [activeTab])

    const handleDelete = async (e: React.MouseEvent, id: number) => {
        e.stopPropagation()
        if (!window.confirm("Voulez-vous vraiment supprimer définitivement cette facture ? Cette action est irréversible.")) return
        try {
            await apiService.deleteFacture(id)
            loadData()
        } catch (err: any) {
            alert("Erreur lors de la suppression: " + (err.response?.data?.detail || err.message))
        }
    }

    useEffect(() => {
        if (activeTab !== 'factures') return
        let result = [...factures]
        if (search) {
            const s = search.toLowerCase()
            result = result.filter(f =>
                (f.supplier_name && f.supplier_name.toLowerCase().includes(s)) ||
                (f.numero_facture && f.numero_facture.toLowerCase().includes(s))
            )
        }
        if (statusFilter) result = result.filter(f => f.status === statusFilter)
        if (dateStart) result = result.filter(f => f.date_facture && f.date_facture >= dateStart)
        if (dateEnd) result = result.filter(f => f.date_facture && f.date_facture <= dateEnd)
        if (amountMin) result = result.filter(f => f.montant_ttc && f.montant_ttc >= parseFloat(amountMin))
        if (amountMax) result = result.filter(f => f.montant_ttc && f.montant_ttc <= parseFloat(amountMax))
        setFilteredFactures(result)
    }, [search, statusFilter, dateStart, dateEnd, amountMin, amountMax, factures, activeTab])

    const handleCreateImmo = (e: React.MouseEvent, f: any) => {
        e.stopPropagation()
        const params = new URLSearchParams({
            designation: f.supplier_name
                ? `Acquisition - ${f.supplier_name}`
                : `Acquisition - ${f.numero_facture || 'Immobilisation'}`,
            valeur_acquisition: String(f.montant_ht ?? f.montant_ttc ?? ''),
            tva_acquisition: String(f.montant_tva ?? '0'),
            date_acquisition: f.date_facture ?? '',
            facture_id: String(f.id),
        })
        navigate(`/immobilisations?${params.toString()}`)
    }

    const immoCount = factures.filter(f => f.operation_type === 'IMMOBILISATION' && !f.has_immobilisation).length

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
            <div className="page-header">
                <h1 className="page-title">📜 Historique & Audit</h1>
                <p className="page-subtitle">Suivi complet des actions et des documents de la société</p>
            </div>

            {/* Tabs Selector */}
            <div style={{ 
                display: 'flex', 
                gap: '12px', 
                marginBottom: '24px',
                background: 'rgba(255,255,255,0.5)',
                padding: '6px',
                borderRadius: '16px',
                width: 'fit-content',
                boxShadow: 'inset 0 2px 4px rgba(0,0,0,0.05)'
            }}>
                <button 
                    onClick={() => setActiveTab('activities')}
                    style={{
                        padding: '10px 24px',
                        borderRadius: '12px',
                        border: 'none',
                        background: activeTab === 'activities' ? 'white' : 'transparent',
                        color: activeTab === 'activities' ? 'var(--accent)' : 'var(--text2)',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        boxShadow: activeTab === 'activities' ? '0 4px 12px rgba(0,0,0,0.08)' : 'none',
                        transition: 'all 0.3s'
                    }}
                >
                    <HistoryIcon size={18} /> Journal d'Audit
                </button>
                <button 
                    onClick={() => setActiveTab('factures')}
                    style={{
                        padding: '10px 24px',
                        borderRadius: '12px',
                        border: 'none',
                        background: activeTab === 'factures' ? 'white' : 'transparent',
                        color: activeTab === 'factures' ? 'var(--accent)' : 'var(--text2)',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        boxShadow: activeTab === 'factures' ? '0 4px 12px rgba(0,0,0,0.08)' : 'none',
                        transition: 'all 0.3s'
                    }}
                >
                    <FileText size={18} /> Historique Factures
                </button>
            </div>

            {activeTab === 'activities' ? (
                /* TAB ACTIVITIES (Audit Trail) */
                <div className="card">
                    {loading ? (
                        <div className="loading"><div className="spinner" /> Chargement des activités...</div>
                    ) : activities.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon">⏳</div>
                            <div className="empty-title">Aucune activité</div>
                            <div className="empty-subtitle">Les actions effectuées apparaîtront ici.</div>
                        </div>
                    ) : (
                        <div className="table-wrap">
                            <table style={{ borderCollapse: 'separate', borderSpacing: '0 8px' }}>
                                <thead style={{ background: 'transparent' }}>
                                    <tr>
                                        <th style={{ paddingLeft: '24px' }}>Action</th>
                                        <th>Entité</th>
                                        <th>Détails</th>
                                        <th>Agent</th>
                                        <th style={{ paddingRight: '24px' }}>Date & Heure</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {activities.map(act => (
                                        <tr key={act.id} style={{ background: 'white', transition: 'transform 0.2s' }}>
                                            <td style={{ padding: '16px 24px', borderRadius: '12px 0 0 12px' }}>
                                                <span style={{ 
                                                    padding: '4px 10px', 
                                                    borderRadius: '6px', 
                                                    fontSize: '11px', 
                                                    fontWeight: 800,
                                                    background: act.action_type === 'DELETE' ? '#fee2e2' : act.action_type === 'CREATE' || act.action_type.includes('VALIDATION') ? '#dcfce7' : '#e0e7ff',
                                                    color: act.action_type === 'DELETE' ? '#ef4444' : act.action_type === 'CREATE' || act.action_type.includes('VALIDATION') ? '#10b981' : '#4f46e5'
                                                }}>
                                                    {act.action_type}
                                                </span>
                                            </td>
                                            <td style={{ fontWeight: 600, color: 'var(--text)' }}>
                                                {act.entity_type} {act.entity_id && <span style={{ color: 'var(--text3)', fontSize: '12px' }}>#{act.entity_id}</span>}
                                            </td>
                                            <td style={{ color: 'var(--text2)', fontSize: '14px' }}>
                                                {act.details || '—'}
                                            </td>
                                            <td>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                    <div style={{ width: '24px', height: '24px', borderRadius: '50%', background: 'var(--accent-light)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--accent)', fontSize: '10px', fontWeight: 800 }}>
                                                        {act.agent_username?.[0]?.toUpperCase()}
                                                    </div>
                                                    <span style={{ fontSize: '14px' }}>{act.agent_username}</span>
                                                </div>
                                            </td>
                                            <td style={{ paddingRight: '24px', borderRadius: '0 12px 12px 0', color: 'var(--text3)', fontSize: '13px' }}>
                                                {new Date(act.created_at).toLocaleString('fr-FR', {
                                                    day: '2-digit', month: '2-digit', year: 'numeric',
                                                    hour: '2-digit', minute: '2-digit'
                                                })}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            ) : (
                /* TAB FACTURES (Original History) */
                <>
                    {/* Alerte immobilisations détectées */}
                    {immoCount > 0 && (
                        <div style={{
                            background: 'rgba(99, 102, 241, 0.08)',
                            border: '1px solid rgba(99, 102, 241, 0.25)',
                            borderRadius: '12px',
                            padding: '14px 20px',
                            marginBottom: '20px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            fontSize: '14px',
                            color: '#4f46e5'
                        }}>
                            <Construction size={22} />
                            <div>
                                <strong>{immoCount} facture(s) détectée(s) comme immobilisation</strong>
                                {' '}— Cliquez sur <strong>🏗️ Créer Immo</strong> pour les enregistrer directement.
                            </div>
                        </div>
                    )}

                    {/* Filtres */}
                    <div className="card" style={{ marginBottom: '24px' }}>
                        <div className="aurora-form-grid" style={{ padding: '20px', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
                            <div className="aurora-input-group">
                                <label>Recherche</label>
                                <input type="text" className="form-input" placeholder="Fournisseur, N° Facture..."
                                    value={search} onChange={e => setSearch(e.target.value)} />
                            </div>
                            <div className="aurora-input-group">
                                <label>Statut</label>
                                <select className="form-input" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
                                    <option value="">Tous les statuts</option>
                                    <option value="IMPORTED">IMPORTED</option>
                                    <option value="EXTRACTED">EXTRACTED</option>
                                    <option value="CLASSIFIED">CLASSIFIED</option>
                                    <option value="DRAFT">DRAFT</option>
                                    <option value="VALIDATED">VALIDATED</option>
                                    <option value="EXPORTED">EXPORTED</option>
                                    <option value="ERROR">ERROR</option>
                                </select>
                            </div>
                            <div className="aurora-input-group">
                                <label>Du (Date)</label>
                                <input type="date" className="form-input" value={dateStart} onChange={e => setDateStart(e.target.value)} />
                            </div>
                            <div className="aurora-input-group">
                                <label>Au (Date)</label>
                                <input type="date" className="form-input" value={dateEnd} onChange={e => setDateEnd(e.target.value)} />
                            </div>
                        </div>
                        <div style={{ padding: '0 20px 20px', display: 'flex', justifyContent: 'flex-end' }}>
                            <button className="btn btn-ghost" onClick={() => {
                                setSearch(''); setStatusFilter(''); setDateStart(''); setDateEnd(''); setAmountMin(''); setAmountMax('')
                            }}>
                                Réinitialiser les filtres
                            </button>
                        </div>
                    </div>

                    <div className="card">
                        {loading ? (
                            <div className="loading"><div className="spinner" /> Chargement...</div>
                        ) : filteredFactures.length === 0 ? (
                            <div className="empty-state">
                                <div className="empty-icon">📂</div>
                                <div className="empty-title">Aucun résultat</div>
                                <div className="empty-subtitle">Ajustez vos filtres pour trouver ce que vous cherchez</div>
                            </div>
                        ) : (
                            <div className="table-wrap">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>N° Facture</th>
                                            <th>Date</th>
                                            <th>Fournisseur</th>
                                            <th>Montant TTC</th>
                                            <th>Statut</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {filteredFactures.map(f => (
                                            <tr key={f.id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/factures/${f.id}`)}>
                                                <td style={{ color: 'var(--text3)', fontFamily: 'monospace' }}>{f.id}</td>
                                                <td style={{ fontWeight: 600 }}>{f.numero_facture || '—'}</td>
                                                <td>{f.date_facture || '—'}</td>
                                                <td>{f.supplier_name || '—'}</td>
                                                <td style={{ fontWeight: 600 }}>
                                                    {f.montant_ttc != null
                                                        ? `${f.montant_ttc.toLocaleString('fr-MA', { minimumFractionDigits: 2 })} ${f.devise || 'MAD'}`
                                                        : '—'}
                                                </td>
                                                <td><StatusBadge status={f.status} /></td>
                                                <td onClick={e => e.stopPropagation()}
                                                    style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                                                    <button className="btn btn-ghost"
                                                        style={{ padding: '6px 12px', fontSize: '12px' }}
                                                        onClick={() => navigate(`/factures/${f.id}`)}>
                                                        Détails
                                                    </button>
                                                    {f.operation_type === 'IMMOBILISATION' && !f.has_immobilisation && (
                                                        <button
                                                            onClick={(e) => handleCreateImmo(e, f)}
                                                            className="btn btn-accent"
                                                            style={{ padding: '6px 12px', fontSize: '12px' }}
                                                        >
                                                            Créer Immo
                                                        </button>
                                                    )}
                                                    <button 
                                                        className="btn btn-ghost" 
                                                        style={{ color: 'var(--danger)', padding: '6px' }}
                                                        onClick={(e) => handleDelete(e, f.id)}
                                                    >
                                                        <Trash2 size={16} />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </div>
                </>
            )}
        </div>
    )
}
