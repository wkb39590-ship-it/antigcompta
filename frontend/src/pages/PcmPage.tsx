import { useEffect, useState } from 'react'
import apiService from '../api'

export default function PcmPage() {
    const [accounts, setAccounts] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [filterClass, setFilterClass] = useState<string>('')
    const [filterType, setFilterType] = useState<string>('')
    const [search, setSearch] = useState('')

    useEffect(() => {
        apiService.getPcmAccounts(filterClass ? Number(filterClass) : undefined)
            .then(data => setAccounts(data))
            .catch(console.error)
            .finally(() => setLoading(false))
    }, [filterClass])

    const filtered = accounts.filter(a => {
        const matchType = !filterType || a.account_type === filterType
        const matchSearch = !search || a.code.includes(search) || a.label.toLowerCase().includes(search.toLowerCase())
        return matchType && matchSearch
    })

    const CLASS_NAMES: Record<number, string> = {
        1: 'Financement permanent',
        2: 'Actif immobilisé',
        3: 'Actif circulant',
        4: 'Passif circulant',
        5: 'Trésorerie',
        6: 'Charges',
        7: 'Produits',
        8: 'Résultats',
    }

    const TYPE_COLORS: Record<string, string> = {
        CHARGE: 'var(--danger)',
        PRODUIT: 'var(--success)',
        ACTIF: 'var(--accent)',
        PASSIF: 'var(--warning)',
        TIERS: 'var(--accent2)',
    }

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Plan Comptable Marocain</h1>
                <p className="page-subtitle">Référentiel PCM/CGNC — {accounts.length} comptes chargés</p>
            </div>

            {/* Filters */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
                    <input
                        className="form-input"
                        style={{ flex: 1, minWidth: '200px' }}
                        placeholder="🔍 Rechercher par code ou libellé..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                    <select className="form-input" style={{ width: 'auto' }} value={filterClass} onChange={e => setFilterClass(e.target.value)}>
                        <option value="">Toutes les classes</option>
                        {[1, 2, 3, 4, 5, 6, 7, 8].map(c => (
                            <option key={c} value={c}>Classe {c} — {CLASS_NAMES[c]}</option>
                        ))}
                    </select>
                    <select className="form-input" style={{ width: 'auto' }} value={filterType} onChange={e => setFilterType(e.target.value)}>
                        <option value="">Tous les types</option>
                        {['CHARGE', 'PRODUIT', 'ACTIF', 'PASSIF', 'TIERS'].map(t => (
                            <option key={t} value={t}>{t}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="card">
                {loading ? (
                    <div className="loading"><div className="spinner" /> Chargement du PCM...</div>
                ) : filtered.length === 0 ? (
                    <div className="empty-state">
                        <div className="empty-icon">📒</div>
                        <div className="empty-title">Aucun compte trouvé</div>
                        <div className="empty-subtitle">Modifiez vos filtres ou lancez le seed PCM</div>
                    </div>
                ) : (
                    <div className="table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>Code</th>
                                    <th>Libellé</th>
                                    <th>Classe</th>
                                    <th>Type</th>
                                    <th>TVA</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.map(a => (
                                    <tr key={a.code}>
                                        <td>
                                            <span style={{ fontFamily: 'monospace', fontWeight: 700, color: 'var(--accent)', fontSize: '14px' }}>
                                                {a.code}
                                            </span>
                                        </td>
                                        <td style={{ fontWeight: 500 }}>{a.label}</td>
                                        <td>
                                            <span style={{ fontSize: '12px', color: 'var(--text2)' }}>
                                                {a.pcm_class} — {CLASS_NAMES[a.pcm_class] || ''}
                                            </span>
                                        </td>
                                        <td>
                                            <span style={{
                                                fontSize: '11px',
                                                fontWeight: 700,
                                                color: TYPE_COLORS[a.account_type] || 'var(--text2)',
                                                background: `${TYPE_COLORS[a.account_type] || 'var(--text2)'}20`,
                                                padding: '2px 8px',
                                                borderRadius: '4px',
                                            }}>
                                                {a.account_type}
                                            </span>
                                        </td>
                                        <td>
                                            {a.is_tva_account ? (
                                                <span style={{ fontSize: '11px', color: 'var(--warning)' }}>
                                                    🏷️ {a.tva_type}
                                                </span>
                                            ) : '—'}
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
