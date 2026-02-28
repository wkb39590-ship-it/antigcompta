import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import apiService, { Facture, InvoiceLine, JournalEntry, DgiFlag } from '../api'

function StatusBadge({ status }: { status: string }) {
    return <span className={`badge badge-${status.toLowerCase()}`}>{status}</span>
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
    if (value === null) return null;
    const pct = Math.round((value || 0) * 100)
    // On ne montre que si besoin d'attention, sinon on reste discret (puissance silencieuse)
    if (pct >= 90) return null;

    const color = pct >= 80 ? 'var(--warning)' : 'var(--danger)'
    return (
        <div style={{ fontSize: '11px', color: color, fontWeight: 600 }}>
            {pct < 80 ? 'Révision conseillée' : 'À vérifier'}
        </div>
    )
}

/**
 * Page de détail d'une facture.
 * C'est le centre névralgique de l'application où l'utilisateur :
 * 1. Visualise les données extraites
 * 2. Lance les étapes du pipeline (Analyse, Qualification, Écritures)
 * 3. Corrige les erreurs potentielles
 * 4. Valide le dossier final
 */
export default function FactureDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const factureId = Number(id)

    const [facture, setFacture] = useState<Facture | null>(null)
    const [lines, setLines] = useState<InvoiceLine[]>([])
    const [editingLineId, setEditingLineId] = useState<number | null>(null)
    const [editedLine, setEditedLine] = useState<Partial<InvoiceLine> | null>(null)
    const [lineModalOpen, setLineModalOpen] = useState(false)
    const [entries, setEntries] = useState<JournalEntry[]>([])
    const [loading, setLoading] = useState(true)
    const [actionLoading, setActionLoading] = useState(false)
    const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
    const [activeTab, setActiveTab] = useState<'header' | 'lines' | 'entries'>('header')
    const [editingHeader, setEditingHeader] = useState(false)
    const [headerForm, setHeaderForm] = useState<Partial<Facture>>({})

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
            // Initialiser le formulaire avec les données chargées si on n'est pas en train d'éditer
            if (!editingHeader) {
                setHeaderForm(f)
            }
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const saveHeader = async () => {
        if (!facture) return
        setActionLoading(true)
        try {
            const updated = await apiService.updateFacture(factureId, headerForm)
            setFacture(updated)
            setEditingHeader(false)
            setMsg({ type: 'success', text: '✅ En-tête mis à jour' })
            await load() // Recharger pour être sûr de la cohérence avec les lignes/écritures
        } catch (e: any) {
            setMsg({ type: 'error', text: `Erreur: ${e.response?.data?.detail || e.message}` })
        } finally {
            setActionLoading(false)
        }
    }

    useEffect(() => { load() }, [factureId])

    /**
     * Exécute une action du pipeline et gère le retour visuel.
     * @param action Fonction asynchrone à exécuter (ex: apiService.extractFacture)
     * @param successMsg Message à afficher en cas de succès
     */
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

    // Line edit modal save
    const saveLineFromModal = async () => {
        if (!editingLineId || !editedLine) return
        setActionLoading(true)
        try {
            const payload: Partial<any> = {
                description: editedLine.description,
                quantity: editedLine.quantity,
                unit_price_ht: editedLine.unit_price_ht,
                line_amount_ht: editedLine.line_amount_ht,
                tva_rate: editedLine.tva_rate,
                pcm_account_code: editedLine.pcm_account_code,
                pcm_account_label: editedLine.pcm_account_label,
                classification_confidence: editedLine.classification_confidence,
                corrected_account_code: editedLine.pcm_account_code,
            }
            await apiService.updateInvoiceLine(editingLineId, payload)
            setMsg({ type: 'success', text: '✅ Ligne sauvegardée' })
            setLineModalOpen(false)
            setEditingLineId(null)
            setEditedLine(null)
            await load()
        } catch (e: any) {
            setMsg({ type: 'error', text: `Erreur: ${e.response?.data?.detail || e.message}` })
        } finally {
            setActionLoading(false)
        }
    }

    if (loading) return <div className="loading"><div className="spinner" /> Chargement...</div>
    if (!facture) return <div className="empty-state"><div className="empty-title">Facture introuvable</div></div>

    // basic modal styles (scoped inline for simplicity)
    const modalStyles = `
    .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center; z-index:9999 }
    .modal { background: var(--bg); padding: 18px; border-radius: 8px; width: min(900px, 95%); box-shadow: 0 10px 30px rgba(0,0,0,0.2) }
    .modal-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px }
    .modal-body textarea, .modal-body input { width:100%; padding:8px; border:1px solid var(--border); border-radius:6px; background: var(--bg2); color:var(--text) }
    .label { font-size:12px; color:var(--text3); margin-bottom:6px; display:block }
    `

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
                            onClick={() => runAction(() => apiService.extractFacture(factureId), '✅ Analyse terminée')}>
                            Lancer l'Analyse
                        </button>
                    )}
                    {facture.status === 'EXTRACTED' && (
                        <button className="btn btn-primary" disabled={actionLoading}
                            onClick={() => runAction(() => apiService.classifyFacture(factureId), '✅ Imputation terminée')}>
                            Qualifier les lignes
                        </button>
                    )}
                    {facture.status === 'CLASSIFIED' && (
                        <button className="btn btn-primary" disabled={actionLoading}
                            onClick={() => runAction(() => apiService.generateEntries(factureId), '✅ Écritures générées')}>
                            Générer les écritures
                        </button>
                    )}
                    {facture.status === 'DRAFT' && (
                        <button className="btn btn-success" disabled={actionLoading}
                            onClick={() => runAction(() => apiService.validateFacture(factureId), '✅ Facture validée!')}>
                            Valider le dossier
                        </button>
                    )}
                    {['EXTRACTED', 'CLASSIFIED', 'DRAFT'].includes(facture.status) && (
                        <button className="btn btn-danger" disabled={actionLoading}
                            onClick={() => runAction(() => apiService.rejectFacture(factureId, 'Rejeté manuellement'), '❌ Facture rejetée')}>
                            Rejeter
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
                        {tab === 'header' ? 'En-tête' : tab === 'lines' ? `Lignes (${lines.length})` : `Écritures (${entries.length})`}
                    </button>
                ))}
            </div>

            {/* Tab: Header */}
            {activeTab === 'header' && (
                <div className="two-col">
                    <div className="card">
                        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div className="card-title">Informations facture</div>
                            {editingHeader ? (
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button className="btn btn-ghost" onClick={() => { setEditingHeader(false); setHeaderForm({}) }}>Annuler</button>
                                    <button className="btn btn-primary" onClick={saveHeader} disabled={actionLoading}>Enregistrer</button>
                                </div>
                            ) : (
                                <button className="btn btn-ghost" style={{ padding: '6px 12px' }} onClick={() => { setEditingHeader(true); setHeaderForm({ ...facture }) }}>
                                    Modifier ✎
                                </button>
                            )}
                        </div>

                        <div className="three-col" style={{ gap: '12px' }}>
                            {[
                                { label: 'N° Facture', key: 'numero_facture', type: 'text' },
                                { label: 'Date', key: 'date_facture', type: 'date' },
                                { label: 'Échéance', key: 'due_date', type: 'date' },
                                { label: 'Type', key: 'invoice_type', type: 'select', options: ['ACHAT', 'VENTE', 'AVOIR', 'NOTE_FRAIS', 'IMMOBILISATION'] },
                                { label: 'Devise', key: 'devise', type: 'text' },
                                { label: 'Mode paiement', key: 'payment_mode', type: 'select', options: ['Virement', 'Chèque', 'Espèces', 'Effet', 'Autre'] },
                            ].map((field) => (
                                <div key={field.label}>
                                    <div style={{ fontSize: '11px', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>{field.label}</div>
                                    {editingHeader ? (
                                        field.type === 'select' ? (
                                            <select
                                                className="form-input"
                                                value={(headerForm as any)[field.key] || ''}
                                                onChange={e => setHeaderForm(prev => ({ ...prev, [field.key]: e.target.value }))}
                                                style={{ width: '100%', padding: '4px 8px', fontSize: '13px' }}
                                            >
                                                <option value="">—</option>
                                                {field.options?.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                                            </select>
                                        ) : (
                                            <input
                                                type={field.type}
                                                className="form-input"
                                                value={(headerForm as any)[field.key] || ''}
                                                onChange={e => setHeaderForm(prev => ({ ...prev, [field.key]: e.target.value }))}
                                                style={{ width: '100%', padding: '4px 8px', fontSize: '13px' }}
                                            />
                                        )
                                    ) : (
                                        <div style={{ fontWeight: 600 }}>{(facture as any)[field.key] || '—'}</div>
                                    )}
                                </div>
                            ))}
                        </div>

                        <div style={{ marginTop: '24px', paddingTop: '20px', borderTop: '1px solid var(--border)' }}>
                            <div className="card-title" style={{ marginBottom: '16px', fontSize: '14px' }}>Fournisseur</div>
                            <div className="three-col" style={{ gap: '12px' }}>
                                {[
                                    { label: 'Nom', key: 'supplier_name' },
                                    { label: 'ICE', key: 'supplier_ice' },
                                    { label: 'IF', key: 'supplier_if' },
                                    { label: 'RC', key: 'supplier_rc' },
                                    { label: 'Adresse', key: 'supplier_address' },
                                ].map((field) => (
                                    <div key={field.label}>
                                        <div style={{ fontSize: '11px', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>{field.label}</div>
                                        {editingHeader ? (
                                            <input
                                                className="form-input"
                                                value={(headerForm as any)[field.key] || ''}
                                                onChange={e => setHeaderForm(prev => ({ ...prev, [field.key]: e.target.value }))}
                                                style={{ width: '100%', padding: '4px 8px', fontSize: '13px' }}
                                            />
                                        ) : (
                                            <div style={{ fontWeight: 600 }}>{(facture as any)[field.key] || '—'}</div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div style={{ marginTop: '24px', paddingTop: '20px', borderTop: '1px solid var(--border)' }}>
                            <div className="card-title" style={{ marginBottom: '16px', fontSize: '14px' }}>Client</div>
                            <div className="three-col" style={{ gap: '12px' }}>
                                {[
                                    { label: 'Nom', key: 'client_name' },
                                    { label: 'ICE', key: 'client_ice' },
                                    { label: 'IF', key: 'client_if' },
                                ].map((field) => (
                                    <div key={field.label}>
                                        <div style={{ fontSize: '11px', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '4px' }}>{field.label}</div>
                                        {editingHeader ? (
                                            <input
                                                className="form-input"
                                                value={(headerForm as any)[field.key] || ''}
                                                onChange={e => setHeaderForm(prev => ({ ...prev, [field.key]: e.target.value }))}
                                                style={{ width: '100%', padding: '4px 8px', fontSize: '13px' }}
                                            />
                                        ) : (
                                            <div style={{ fontWeight: 600 }}>{(facture as any)[field.key] || '—'}</div>
                                        )}
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
                                    { label: 'Montant HT', key: 'montant_ht', color: 'var(--text)' },
                                    { label: `TVA (${facture.taux_tva || '?'}%)`, key: 'montant_tva', color: 'var(--warning)' },
                                    { label: 'Montant TTC', key: 'montant_ttc', color: 'var(--accent)' },
                                ].map((field) => (
                                    <div key={field.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <span style={{ color: 'var(--text2)', fontSize: '14px' }}>{field.label}</span>
                                        {editingHeader ? (
                                            <input
                                                type="number"
                                                className="form-input"
                                                value={(headerForm as any)[field.key] || ''}
                                                onChange={e => setHeaderForm(prev => ({ ...prev, [field.key]: e.target.value ? Number(e.target.value) : null }))}
                                                style={{ width: '120px', padding: '4px 8px', fontSize: '13px', textAlign: 'right' }}
                                            />
                                        ) : (
                                            <span style={{ fontWeight: 700, fontSize: '16px', color: field.color }}>
                                                {fmt((facture as any)[field.key])} {facture.devise || 'MAD'}
                                            </span>
                                        )}
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
                                        <th>Statut</th>
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
                                                <div>
                                                    {line.pcm_account_code ? (
                                                        <div>
                                                            <span style={{ fontFamily: 'monospace', fontWeight: 700, color: 'var(--accent)' }}>
                                                                {line.pcm_account_code}
                                                            </span>
                                                            {line.is_corrected && <span style={{ marginLeft: '6px', fontSize: '10px', color: 'var(--warning)' }}>✏️ corrigé</span>}
                                                            <div style={{ fontSize: '11px', color: 'var(--text2)' }}>{line.pcm_account_label}</div>
                                                        </div>
                                                    ) : '—'}
                                                    {line.classification_confidence != null && line.classification_confidence < 0.5 && (
                                                        <div style={{ marginTop: 6, fontSize: 12, color: 'var(--danger)' }}>⚠️ faible confiance</div>
                                                    )}
                                                </div>
                                            </td>
                                            <td style={{ minWidth: '120px' }}>
                                                <ConfidenceBar value={line.classification_confidence} />
                                            </td>
                                            <td style={{ width: 48, textAlign: 'right' }}>
                                                <button className="btn btn-icon" title="Modifier ligne" onClick={() => { setEditingLineId(line.id); setEditedLine({ ...line }); setLineModalOpen(true) }} style={{ padding: 6, minWidth: 32 }}>✎</button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}

            {/* Line Edit Modal */}
            {lineModalOpen && editedLine && (
                <div className="modal-backdrop">
                    <div className="modal">
                        <div className="modal-header">
                            <div style={{ fontWeight: 700 }}>Modifier la ligne #{editedLine.line_number}</div>
                            <button className="btn btn-ghost" onClick={() => { setLineModalOpen(false); setEditedLine(null); setEditingLineId(null) }}>✖</button>
                        </div>
                        <div className="modal-body">
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                                <div>
                                    <label className="label">Description</label>
                                    <textarea value={editedLine.description || ''} onChange={(e) => setEditedLine(prev => ({ ...(prev || {}), description: e.target.value }))} />
                                </div>
                                <div>
                                    <label className="label">Quantité</label>
                                    <input type="number" value={editedLine.quantity ?? ''} onChange={(e) => setEditedLine(prev => ({ ...(prev || {}), quantity: e.target.value ? Number(e.target.value) : null }))} />
                                    <label className="label">Unité</label>
                                    <input value={editedLine.unit || ''} onChange={(e) => setEditedLine(prev => ({ ...(prev || {}), unit: e.target.value }))} />
                                </div>
                                <div>
                                    <label className="label">PU HT</label>
                                    <input type="number" value={editedLine.unit_price_ht ?? ''} onChange={(e) => setEditedLine(prev => ({ ...(prev || {}), unit_price_ht: e.target.value ? Number(e.target.value) : null }))} />
                                </div>
                                <div>
                                    <label className="label">Montant HT</label>
                                    <input type="number" value={editedLine.line_amount_ht ?? ''} onChange={(e) => setEditedLine(prev => ({ ...(prev || {}), line_amount_ht: e.target.value ? Number(e.target.value) : null }))} />
                                </div>
                                <div>
                                    <label className="label">TVA (%)</label>
                                    <input type="number" value={editedLine.tva_rate ?? ''} onChange={(e) => setEditedLine(prev => ({ ...(prev || {}), tva_rate: e.target.value ? Number(e.target.value) : null }))} />
                                </div>
                                <div>
                                    <label className="label">Confiance</label>
                                    <input type="range" min={0} max={100} value={Math.round((editedLine.classification_confidence ?? 0) * 100)} onChange={(e) => setEditedLine(prev => ({ ...(prev || {}), classification_confidence: Number(e.target.value) / 100 }))} />
                                </div>
                                <div>
                                    <label className="label">Compte PCM</label>
                                    <input value={editedLine.pcm_account_code || ''} onChange={(e) => setEditedLine(prev => ({ ...(prev || {}), pcm_account_code: e.target.value }))} />
                                </div>
                                <div>
                                    <label className="label">Libellé compte</label>
                                    <input value={editedLine.pcm_account_label || ''} onChange={(e) => setEditedLine(prev => ({ ...(prev || {}), pcm_account_label: e.target.value }))} />
                                </div>
                            </div>
                        </div>
                        <div className="modal-footer" style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                            <button className="btn btn-ghost" onClick={() => { setLineModalOpen(false); setEditedLine(null); setEditingLineId(null) }}>Annuler</button>
                            <button className="btn btn-primary" onClick={saveLineFromModal} disabled={actionLoading}>💾 Sauver</button>
                        </div>
                    </div>
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
