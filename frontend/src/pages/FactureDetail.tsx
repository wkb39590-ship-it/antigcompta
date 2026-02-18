import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import apiService, { Facture, InvoiceLine, JournalEntry, DgiFlag } from '../api'

function StatusBadge({ status }: { status: string }) {
    const icons: Record<string, string> = {
        IMPORTED: '📥', EXTRACTED: '🔍', CLASSIFIED: '🧠',
        DRAFT: '📝', VALIDATED: '✅', EXPORTED: '📤', ERROR: '❌'
    }
    return <span className={`badge badge-${status.toLowerCase()}`}>{icons[status] || '•'} {status}</span>
}

function DgiFlagList({ flags }: { flags: DgiFlag[] }) {
    if (!flags || flags.length === 0) return (
        <div className="alert alert-success">✅ Aucune anomalie DGI détectée</div>
    )
    return (
        <div>
            {flags.map((f, i) => (
                <div key={i} className={`dgi-flag ${f.severity.toLowerCase()}`}>
                    <span className="dgi-flag-icon">{f.severity === 'ERROR' ? '🚨' : '⚠️'}</span>
                    <div>
                        <strong>{f.code}</strong>: {f.message}
                    </div>
                </div>
            ))}
        </div>
    )
}

function ConfidenceBar({ value }: { value: number | null }) {
    const pct = Math.round((value || 0) * 100)
    const color = pct >= 80 ? 'var(--success)' : pct >= 50 ? 'var(--warning)' : 'var(--danger)'
    return (
        <div className="confidence-bar">
            <div className="confidence-track">
                <div className="confidence-fill" style={{ width: `${pct}%`, background: color }} />
            </div>
            <span style={{ color, fontWeight: 600, minWidth: '36px' }}>{pct}%</span>
        </div>
    )
}

export default function FactureDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const factureId = Number(id)

    const [facture, setFacture] = useState<Facture | null>(null)
    const [lines, setLines] = useState<InvoiceLine[]>([])
    const [entries, setEntries] = useState<JournalEntry[]>([])
    const [loading, setLoading] = useState(true)
    const [actionLoading, setActionLoading] = useState(false)
    const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
    const [activeTab, setActiveTab] = useState<'header' | 'lines' | 'entries'>('header')

    const load = async () => {
        setLoading(true)
        try {
            const [f, l, e] = await Promise.all([
                apiService.getFacture(factureId),
                apiService.getFactureLines(factureId),
                apiService.getFactureEntries(factureId),
            ])
            setFacture(f)
            setLines(l)
            setEntries(e.journal_entries || [])
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { load() }, [factureId])

    const runAction = async (action: () => Promise<any>, successMsg: string) => {
        setActionLoading(true)
        setMsg(null)
        try {
            await action()
            setMsg({ type: 'success', text: successMsg })
            await load()
        } catch (e: any) {
            const detail = e.response?.data?.detail || e.message
            setMsg({ type: 'error', text: `Erreur: ${typeof detail === 'string' ? detail : JSON.stringify(detail)}` })
        } finally {
            setActionLoading(false)
        }
    }

    if (loading) return <div className="loading"><div className="spinner" /> Chargement...</div>
    if (!facture) return <div className="empty-state"><div className="empty-title">Facture introuvable</div></div>

    const fmt = (v: number | null) => v != null ? v.toLocaleString('fr-MA', { minimumFractionDigits: 2 }) : '—'

    return (
        <div>
            {/* Header */}
            <div className="page-header" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
                <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                        <button className="btn btn-ghost" style={{ padding: '6px 12px' }} onClick={() => navigate('/dashboard')}>
                            ← Retour
                        </button>
                        <h1 className="page-title">Facture #{facture.id}</h1>
                        <StatusBadge status={facture.status} />
                    </div>
                    <p className="page-subtitle">{facture.numero_facture || 'N° non extrait'} — {facture.supplier_name || 'Fournisseur inconnu'}</p>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {facture.status === 'IMPORTED' && (
                        <button className="btn btn-primary" disabled={actionLoading}
                            onClick={() => runAction(() => apiService.extractFacture(factureId), '✅ Extraction terminée')}>
                            🔍 Extraire
                        </button>
                    )}
                    {facture.status === 'EXTRACTED' && (
                        <button className="btn btn-primary" disabled={actionLoading}
                            onClick={() => runAction(() => apiService.classifyFacture(factureId), '✅ Classification terminée')}>
                            🧠 Classifier
                        </button>
                    )}
                    {facture.status === 'CLASSIFIED' && (
                        <button className="btn btn-primary" disabled={actionLoading}
                            onClick={() => runAction(() => apiService.generateEntries(factureId), '✅ Écritures générées')}>
                            📝 Générer écritures
                        </button>
                    )}
                    {facture.status === 'DRAFT' && (
                        <button className="btn btn-success" disabled={actionLoading}
                            onClick={() => runAction(() => apiService.validateFacture(factureId), '✅ Facture validée!')}>
                            ✅ Valider
                        </button>
                    )}
                    {['EXTRACTED', 'CLASSIFIED', 'DRAFT'].includes(facture.status) && (
                        <button className="btn btn-danger" disabled={actionLoading}
                            onClick={() => runAction(() => apiService.rejectFacture(factureId, 'Rejeté manuellement'), '❌ Facture rejetée')}>
                            ❌ Rejeter
                        </button>
                    )}
                </div>
            </div>

            {msg && (
                <div className={`alert alert-${msg.type}`} style={{ marginBottom: '24px' }}>
                    {msg.text}
                </div>
            )}

            {/* Tabs */}
            <div style={{ display: 'flex', gap: '4px', marginBottom: '24px', borderBottom: '1px solid var(--border)', paddingBottom: '0' }}>
                {(['header', 'lines', 'entries'] as const).map(tab => (
                    <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        style={{
                            padding: '10px 20px',
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontWeight: 600,
                            color: activeTab === tab ? 'var(--accent)' : 'var(--text2)',
                            borderBottom: activeTab === tab ? '2px solid var(--accent)' : '2px solid transparent',
                            marginBottom: '-1px',
                            transition: 'all 0.2s',
                        }}
                    >
                        {tab === 'header' ? '📋 En-tête' : tab === 'lines' ? `📦 Lignes (${lines.length})` : `📒 Écritures (${entries.length})`}
                    </button>
                ))}
            </div>

            {/* Tab: Header */}
            {activeTab === 'header' && (
                <div className="two-col">
                    <div className="card">
                        <div className="card-header"><div className="card-title">Informations facture</div></div>
                        <div className="three-col" style={{ gap: '12px' }}>
                            {[
                                ['N° Facture', facture.numero_facture],
                                ['Date', facture.date_facture],
                                ['Échéance', facture.due_date],
                                ['Type', facture.invoice_type],
                                ['Devise', facture.devise],
                                ['Mode paiement', facture.payment_mode],
                            ].map(([label, value]) => (
                                <div key={label as string}>
                                    <div style={{ fontSize: '11px', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>{label}</div>
                                    <div style={{ fontWeight: 600 }}>{value || '—'}</div>
                                </div>
                            ))}
                        </div>

                        <div style={{ marginTop: '24px', paddingTop: '20px', borderTop: '1px solid var(--border)' }}>
                            <div className="card-title" style={{ marginBottom: '16px', fontSize: '14px' }}>Fournisseur</div>
                            <div className="three-col" style={{ gap: '12px' }}>
                                {[
                                    ['Nom', facture.supplier_name],
                                    ['ICE', facture.supplier_ice],
                                    ['IF', facture.supplier_if],
                                    ['RC', facture.supplier_rc],
                                    ['Adresse', facture.supplier_address],
                                ].map(([label, value]) => (
                                    <div key={label as string}>
                                        <div style={{ fontSize: '11px', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>{label}</div>
                                        <div style={{ fontWeight: 600 }}>{value || '—'}</div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div style={{ marginTop: '24px', paddingTop: '20px', borderTop: '1px solid var(--border)' }}>
                            <div className="card-title" style={{ marginBottom: '16px', fontSize: '14px' }}>Client</div>
                            <div className="three-col" style={{ gap: '12px' }}>
                                {[
                                    ['Nom', facture.client_name],
                                    ['ICE', facture.client_ice],
                                    ['IF', facture.client_if],
                                ].map(([label, value]) => (
                                    <div key={label as string}>
                                        <div style={{ fontSize: '11px', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>{label}</div>
                                        <div style={{ fontWeight: 600 }}>{value || '—'}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {/* Montants */}
                        <div className="card">
                            <div className="card-title" style={{ marginBottom: '16px' }}>Montants</div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                {[
                                    ['Montant HT', facture.montant_ht, 'var(--text)'],
                                    [`TVA (${facture.taux_tva || '?'}%)`, facture.montant_tva, 'var(--warning)'],
                                    ['Montant TTC', facture.montant_ttc, 'var(--accent)'],
                                ].map(([label, value, color]) => (
                                    <div key={label as string} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <span style={{ color: 'var(--text2)', fontSize: '14px' }}>{label as string}</span>
                                        <span style={{ fontWeight: 700, fontSize: '16px', color: color as string }}>
                                            {fmt(value as number | null)} {facture.devise || 'MAD'}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* DGI Flags */}
                        <div className="card">
                            <div className="card-title" style={{ marginBottom: '16px' }}>🛡️ Contrôles DGI</div>
                            <DgiFlagList flags={facture.dgi_flags || []} />
                        </div>
                    </div>
                </div>
            )}

            {/* Tab: Lines */}
            {activeTab === 'lines' && (
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">Lignes produits / services</div>
                        <div className="card-subtitle">Classification Plan Comptable Marocain</div>
                    </div>
                    {lines.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon">📦</div>
                            <div className="empty-title">Aucune ligne extraite</div>
                            <div className="empty-subtitle">Lancez l'extraction pour obtenir les lignes</div>
                        </div>
                    ) : (
                        <div className="table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>Description</th>
                                        <th>Qté</th>
                                        <th>PU HT</th>
                                        <th>Montant HT</th>
                                        <th>TVA</th>
                                        <th>Compte PCM</th>
                                        <th>Confiance</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {lines.map(line => (
                                        <tr key={line.id}>
                                            <td style={{ color: 'var(--text3)' }}>{line.line_number}</td>
                                            <td style={{ maxWidth: '200px' }}>
                                                <div style={{ fontWeight: 500 }}>{line.description || '—'}</div>
                                                {line.classification_reason && (
                                                    <div style={{ fontSize: '11px', color: 'var(--text3)', marginTop: '2px' }}>
                                                        {line.classification_reason}
                                                    </div>
                                                )}
                                            </td>
                                            <td>{line.quantity ?? '—'} {line.unit || ''}</td>
                                            <td>{fmt(line.unit_price_ht)}</td>
                                            <td style={{ fontWeight: 600 }}>{fmt(line.line_amount_ht)}</td>
                                            <td>{line.tva_rate != null ? `${line.tva_rate}%` : '—'}</td>
                                            <td>
                                                {line.pcm_account_code ? (
                                                    <div>
                                                        <span style={{ fontFamily: 'monospace', fontWeight: 700, color: 'var(--accent)' }}>
                                                            {line.pcm_account_code}
                                                        </span>
                                                        {line.is_corrected && <span style={{ marginLeft: '6px', fontSize: '10px', color: 'var(--warning)' }}>✏️ corrigé</span>}
                                                        <div style={{ fontSize: '11px', color: 'var(--text2)' }}>{line.pcm_account_label}</div>
                                                    </div>
                                                ) : '—'}
                                            </td>
                                            <td style={{ minWidth: '120px' }}>
                                                <ConfidenceBar value={line.classification_confidence} />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {/* Tab: Entries */}
            {activeTab === 'entries' && (
                <div>
                    {entries.length === 0 ? (
                        <div className="card">
                            <div className="empty-state">
                                <div className="empty-icon">📒</div>
                                <div className="empty-title">Aucune écriture générée</div>
                                <div className="empty-subtitle">Classifiez les lignes puis générez les écritures</div>
                            </div>
                        </div>
                    ) : entries.map(entry => {
                        const isBalanced = Math.abs(entry.total_debit - entry.total_credit) <= 0.01
                        return (
                            <div key={entry.id} className="card" style={{ marginBottom: '16px' }}>
                                <div className="card-header">
                                    <div>
                                        <div className="card-title">
                                            Journal {entry.journal_code} — {entry.reference || 'Sans référence'}
                                            {entry.is_validated && <span className="badge badge-validated" style={{ marginLeft: '12px' }}>✅ Validée</span>}
                                        </div>
                                        <div className="card-subtitle">{entry.description}</div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: '12px', color: 'var(--text3)' }}>Équilibre</div>
                                        <div style={{ fontWeight: 700, color: isBalanced ? 'var(--success)' : 'var(--danger)' }}>
                                            {isBalanced ? '✅ Équilibré' : `⚠️ Écart: ${Math.abs(entry.total_debit - entry.total_credit).toFixed(2)}`}
                                        </div>
                                    </div>
                                </div>

                                <div className="table-wrap">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>N°</th>
                                                <th>Compte</th>
                                                <th>Libellé</th>
                                                <th>Tiers</th>
                                                <th style={{ textAlign: 'right' }}>Débit</th>
                                                <th style={{ textAlign: 'right' }}>Crédit</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {entry.entry_lines.map(el => (
                                                <tr key={el.id}>
                                                    <td style={{ color: 'var(--text3)' }}>{el.line_order}</td>
                                                    <td>
                                                        <span style={{ fontFamily: 'monospace', fontWeight: 700, color: 'var(--accent)' }}>
                                                            {el.account_code}
                                                        </span>
                                                    </td>
                                                    <td>{el.account_label || '—'}</td>
                                                    <td style={{ fontSize: '12px', color: 'var(--text2)' }}>{el.tiers_name || '—'}</td>
                                                    <td style={{ textAlign: 'right', fontWeight: el.debit > 0 ? 700 : 400, color: el.debit > 0 ? 'var(--text)' : 'var(--text3)' }}>
                                                        {el.debit > 0 ? fmt(el.debit) : '—'}
                                                    </td>
                                                    <td style={{ textAlign: 'right', fontWeight: el.credit > 0 ? 700 : 400, color: el.credit > 0 ? 'var(--text)' : 'var(--text3)' }}>
                                                        {el.credit > 0 ? fmt(el.credit) : '—'}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                        <tfoot>
                                            <tr style={{ background: 'var(--bg3)' }}>
                                                <td colSpan={4} style={{ fontWeight: 700, padding: '10px 14px' }}>TOTAUX</td>
                                                <td style={{ textAlign: 'right', fontWeight: 700, padding: '10px 14px', color: 'var(--accent)' }}>
                                                    {fmt(entry.total_debit)}
                                                </td>
                                                <td style={{ textAlign: 'right', fontWeight: 700, padding: '10px 14px', color: 'var(--accent)' }}>
                                                    {fmt(entry.total_credit)}
                                                </td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}
        </div>
    )
}
