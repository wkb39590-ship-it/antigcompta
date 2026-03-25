import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService from '../api'
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
    ArrowRight,
    Trash2
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
    const [factures, setFactures] = useState<any[]>([])
    const [filteredFactures, setFilteredFactures] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate()

    const [search, setSearch] = useState('')
    const [statusFilter, setStatusFilter] = useState('')
    const [dateStart, setDateStart] = useState('')
    const [dateEnd, setDateEnd] = useState('')
    const [amountMin, setAmountMin] = useState('')
    const [amountMax, setAmountMax] = useState('')

    const load = async () => {
        setLoading(true)
        try {
            const data = await apiService.listFactures()
            setFactures(data)
            setFilteredFactures(data)
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { load() }, [])

    const handleDelete = async (e: React.MouseEvent, id: number) => {
        e.stopPropagation()
        if (!window.confirm("Voulez-vous vraiment supprimer définitivement cette facture ? Cette action est irréversible.")) return
        try {
            await apiService.deleteFacture(id)
            load()
        } catch (err: any) {
            alert("Erreur lors de la suppression: " + (err.response?.data?.detail || err.message))
        }
    }

    useEffect(() => {
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
    }, [search, statusFilter, dateStart, dateEnd, amountMin, amountMax, factures])

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
        <div>
            <div className="page-header">
                <h1 className="page-title">📂 Historique des Factures</h1>
                <p className="page-subtitle">Consultez et filtrez vos archives de facturation</p>
            </div>

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
                    <div className="aurora-input-group">
                        <label>Montant Min</label>
                        <input type="number" className="form-input" placeholder="0.00" value={amountMin} onChange={e => setAmountMin(e.target.value)} />
                    </div>
                    <div className="aurora-input-group">
                        <label>Montant Max</label>
                        <input type="number" className="form-input" placeholder="99999" value={amountMax} onChange={e => setAmountMax(e.target.value)} />
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

            {/* Tableau */}
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
                                    <th>Type IA</th>
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
                                        <td>
                                            {f.operation_type === 'IMMOBILISATION' ? (
                                                <span style={{
                                                    display: 'inline-flex', alignItems: 'center', gap: '4px',
                                                    padding: '3px 8px', borderRadius: '20px', fontSize: '11px', fontWeight: 700,
                                                    background: 'rgba(99,102,241,0.12)', color: '#4f46e5'
                                                }}><Construction size={12} /> IMMO</span>
                                            ) : (
                                                <span style={{ color: 'var(--text3)', fontSize: '12px' }}>
                                                    {f.operation_type || '—'}
                                                </span>
                                            )}
                                        </td>
                                        <td><StatusBadge status={f.status} /></td>
                                        <td onClick={e => e.stopPropagation()}
                                            style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                                            <button className="btn btn-ghost"
                                                style={{ padding: '6px 12px', fontSize: '12px' }}
                                                onClick={() => navigate(`/factures/${f.id}`)}>
                                                Détails →
                                            </button>
                                            {f.operation_type === 'IMMOBILISATION' && !f.has_immobilisation && (
                                                <button
                                                    onClick={(e) => handleCreateImmo(e, f)}
                                                    style={{
                                                        padding: '6px 12px', fontSize: '12px', fontWeight: 700,
                                                        background: 'rgba(99,102,241,0.12)', color: '#4f46e5',
                                                        border: '1px solid rgba(99,102,241,0.3)', borderRadius: '8px',
                                                        cursor: 'pointer', display: 'inline-flex', alignItems: 'center',
                                                        gap: '4px', whiteSpace: 'nowrap', transition: 'all 0.2s'
                                                    }}
                                                    onMouseOver={e => (e.currentTarget.style.background = 'rgba(99,102,241,0.2)')}
                                                    onMouseOut={e => (e.currentTarget.style.background = 'rgba(99,102,241,0.12)')}
                                                >
                                                    <Construction size={12} /> Créer Immo
                                                </button>
                                            )}
                                            {f.has_immobilisation && (
                                                <span style={{
                                                    padding: '6px 12px', fontSize: '11px', fontWeight: 700,
                                                    color: '#10b981', display: 'inline-flex', alignItems: 'center', gap: '4px'
                                                }}>
                                                    <BadgeCheck size={14} /> Immobilisé
                                                </span>
                                            )}
                                            <button 
                                                className="btn btn-ghost" 
                                                style={{ color: 'var(--danger)', padding: '6px' }}
                                                onClick={(e) => handleDelete(e, f.id)}
                                                title="Supprimer la facture"
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
        </div>
    )
}
