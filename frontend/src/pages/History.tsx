import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService from '../api'

function StatusBadge({ status }: { status: string }) {
    const cls = `badge badge-${status.toLowerCase()}`
    const icons: Record<string, string> = {
        IMPORTED: '📥', EXTRACTED: '🔍', CLASSIFIED: '🧠',
        DRAFT: '📝', VALIDATED: '✅', EXPORTED: '📤', ERROR: '❌'
    }
    return <span className={cls}>{icons[status] || '•'} {status}</span>
}

export default function History() {
    const [factures, setFactures] = useState<any[]>([])
    const [filteredFactures, setFilteredFactures] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate()

    // Filtres
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

    useEffect(() => {
        load()
    }, [])

    useEffect(() => {
        let result = [...factures]

        // Recherche textuelle (Fournisseur ou N° Facture)
        if (search) {
            const s = search.toLowerCase()
            result = result.filter(f =>
                (f.supplier_name && f.supplier_name.toLowerCase().includes(s)) ||
                (f.numero_facture && f.numero_facture.toLowerCase().includes(s))
            )
        }

        // Filtre Statut
        if (statusFilter) {
            result = result.filter(f => f.status === statusFilter)
        }

        // Filtre Date
        if (dateStart) {
            result = result.filter(f => f.date_facture && f.date_facture >= dateStart)
        }
        if (dateEnd) {
            result = result.filter(f => f.date_facture && f.date_facture <= dateEnd)
        }

        // Filtre Montant
        if (amountMin) {
            result = result.filter(f => f.montant_ttc && f.montant_ttc >= parseFloat(amountMin))
        }
        if (amountMax) {
            result = result.filter(f => f.montant_ttc && f.montant_ttc <= parseFloat(amountMax))
        }

        setFilteredFactures(result)
    }, [search, statusFilter, dateStart, dateEnd, amountMin, amountMax, factures])

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">📂 Historique des Factures</h1>
                <p className="page-subtitle">Consultez et filtrez vos archives de facturation</p>
            </div>

            <div className="card" style={{ marginBottom: '24px' }}>
                <div className="aurora-form-grid" style={{ padding: '20px', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
                    <div className="aurora-input-group">
                        <label>Recherche</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="Fournisseur, N° Facture..."
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                        />
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
                        setSearch(''); setStatusFilter(''); setDateStart(''); setDateEnd(''); setAmountMin(''); setAmountMax('');
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
                                    <th>Action</th>
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
                                        <td>
                                            <button className="btn btn-ghost" style={{ padding: '6px 12px', fontSize: '12px' }}>
                                                Détails →
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
