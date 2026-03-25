import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import apiService, { Facture, InvoiceLine, JournalEntry, DgiFlag } from '../api'
import {
    ArrowLeft,
    CheckCircle2,
    AlertCircle,
    AlertTriangle,
    Zap,
    Trash2,
    FileText,
    List,
    BookOpen,
    FileEdit,
    ShieldCheck,
    Box,
    Book,
    Save,
    RefreshCw,
    Scale,
    Search,
    Maximize2,
    FileSearch,
    Minus,
    Plus,
    X
} from 'lucide-react'

function StatusBadge({ status }: { status: string }) {
    return <span className={`badge badge-${status.toLowerCase()}`}>{status}</span>
}

function DgiFlagList({ flags }: { flags: DgiFlag[] }) {
    if (!flags || flags.length === 0) return (
        <div className="alert alert-success" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle2 size={16} /> Aucune anomalie DGI détectée
        </div>
    )
    return (
        <div>
            {flags.map((f, i) => (
                <div key={i} className={`dgi-flag ${f.severity.toLowerCase()}`} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px', borderRadius: '8px', marginBottom: '8px' }}>
                    <span className="dgi-flag-icon">
                        {f.severity === 'ERROR' ? <AlertCircle size={18} color="#ef4444" /> : <AlertTriangle size={18} color="#f59e0b" />}
                    </span>
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
    if (pct >= 90) return null;

    const color = pct >= 80 ? 'var(--warning)' : 'var(--danger)'
    return (
        <div style={{ fontSize: '11px', color: color, fontWeight: 600 }}>
            {pct < 80 ? 'Révision conseillée' : 'À vérifier'}
        </div>
    )
}

/**
 * Page de détail d'une facture avec prévisualisation du document original.
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
    
    // Preview states
    const [showPreview, setShowPreview] = useState(true)
    const [zoom, setZoom] = useState(100)
    const [pdfError, setPdfError] = useState(false)
    const [blobUrl, setBlobUrl] = useState<string | null>(null)

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
            if (!editingHeader) {
                setHeaderForm(f)
            }
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const loadBlob = async () => {
        try {
            const blob = await apiService.getFileBlob(factureId)
            const url = URL.createObjectURL(blob)
            setBlobUrl(url)
        } catch (err) {
            console.error('Error loading file blob:', err)
            setPdfError(true)
        }
    }

    useEffect(() => { 
        load() 
        loadBlob()
        return () => {
            if (blobUrl) URL.revokeObjectURL(blobUrl)
        }
    }, [factureId])

    const handleDelete = async () => {
        if (!window.confirm("Supprimer définitivement cette facture ? Cette opération est irréversible.")) return
        setActionLoading(true)
        try {
            await apiService.deleteFacture(factureId)
            navigate('/dashboard')
        } catch (e: any) {
            setMsg({ type: 'error', text: `Erreur suppression: ${e.response?.data?.detail || e.message}` })
        } finally {
            setActionLoading(true)
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
            await load()
        } catch (e: any) {
            setMsg({ type: 'error', text: `Erreur: ${e.response?.data?.detail || e.message}` })
        } finally {
            setActionLoading(false)
        }
    }

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

    const getStepNumber = (status: string) => {
        switch (status) {
            case 'IMPORTED': return 1;
            case 'EXTRACTED': return 2;
            case 'CLASSIFIED': return 3;
            case 'DRAFT': return 4;
            case 'VALIDATED': return 5;
            default: return 0;
        }
    }

    const currentStep = getStepNumber(facture.status)
    const getStepClass = (step: number) => {
        if (currentStep > step) return 'step done'
        if (currentStep === step) return 'step active'
        return 'step'
    }

    const fmt = (v: number | null) => v != null ? v.toLocaleString('fr-MA', { minimumFractionDigits: 2 }) : '—'

    const token = localStorage.getItem('session_token') || localStorage.getItem('access_token')
    const fileUrl = `${apiService.getFileUrl(factureId)}${token ? `?token=${token}` : ''}`
    const isImage = facture.file_path?.toLowerCase().match(/\.(jpg|jpeg|png|gif)$/)

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 100px)', overflow: 'hidden' }}>
            <style>{`
                .split-container { display: flex; flex: 1; overflow: hidden; }
                .preview-panel { flex: ${showPreview ? '1' : '0'}; display: ${showPreview ? 'flex' : 'none'}; flex-direction: column; background: #525659; border-right: 1px solid var(--border); overflow: hidden; transition: all 0.3s ease; }
                .data-panel { flex: 1; overflow-y: auto; padding: 24px; background: var(--bg); }
                .preview-toolbar { background: #323639; color: white; padding: 8px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid rgba(255,255,255,0.05); }
                .preview-viewport { flex: 1; overflow: auto; display: flex; justify-content: center; align-items: flex-start; padding: 20px; background: #4a4d50; }
                .preview-viewport iframe { width: 100%; height: 100%; border: none; background: white; border-radius: 4px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
                .preview-viewport img { max-width: 100%; box-shadow: 0 10px 30px rgba(0,0,0,0.5); transition: transform 0.2s; border-radius: 4px; }
                
                .btn-preview-tool { background: rgba(255,255,255,0.15) !important; color: white !important; border: none !important; padding: 6px !important; display: flex !important; align-items: center !important; justify-content: center !important; border-radius: 4px !important; cursor: pointer; transition: background 0.2s; }
                .btn-preview-tool:hover { background: rgba(255,255,255,0.25) !important; }

                .modal-backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.5); display:flex; align-items:center; justify-content:center; z-index:9999 }
                .modal { background: var(--bg); padding: 24px; border-radius: 12px; width: min(800px, 95%); box-shadow: 0 10px 40px rgba(0,0,0,0.2) }
                .modal-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:20px }
                .modal-body textarea, .modal-body input { width:100%; padding:10px; border:1px solid var(--border); border-radius:8px; background: var(--bg2); color:var(--text) }
                .label { font-size:12px; color:var(--text3); margin-bottom:6px; display:block; text-transform: uppercase; letter-spacing: 0.5px; }
            `}</style>

            {/* Top Toolbar */}
            <div style={{ padding: '16px 24px', borderBottom: '1px solid var(--border)', background: 'var(--bg)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <button className="btn btn-ghost" style={{ padding: '8px' }} onClick={() => navigate('/dashboard')}>
                        <ArrowLeft size={20} />
                    </button>
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>Facture #{facture.id}</h1>
                            <StatusBadge status={facture.status} />
                            <button className="btn btn-ghost btn-sm" onClick={() => setShowPreview(!showPreview)} style={{ color: showPreview ? 'var(--accent)' : 'inherit' }}>
                                <FileSearch size={16} /> {showPreview ? 'Masquer original' : 'Voir original'}
                            </button>
                        </div>
                        <div style={{ fontSize: '13px', color: 'var(--text2)', marginTop: '2px' }}>
                            {facture.numero_facture || 'N° non extrait'} • {facture.supplier_name || 'Fournisseur inconnu'}
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '8px' }}>
                    {facture.status === 'IMPORTED' && (
                        <button className="btn btn-primary" disabled={actionLoading} onClick={() => runAction(() => apiService.extractFacture(factureId), '✅ Analyse terminée')}>
                            <Zap size={16} /> Lancer l'Analyse
                        </button>
                    )}
                    {facture.status === 'EXTRACTED' && (
                        <button className="btn btn-primary" disabled={actionLoading} onClick={() => runAction(() => apiService.classifyFacture(factureId), '✅ Imputation terminée')}>
                            <RefreshCw size={16} /> Qualifier
                        </button>
                    )}
                    {facture.status === 'CLASSIFIED' && (
                        <button className="btn btn-primary" disabled={actionLoading} onClick={() => runAction(() => apiService.generateEntries(factureId), '✅ Écritures générées')}>
                            <FileText size={16} /> Générer écritures
                        </button>
                    )}
                    {facture.status === 'DRAFT' && (
                        <button className="btn btn-success" disabled={actionLoading} onClick={() => runAction(() => apiService.validateFacture(factureId), '✅ Facture validée!')}>
                            <CheckCircle2 size={16} /> Valider dossier
                        </button>
                    )}
                    {['EXTRACTED', 'CLASSIFIED', 'DRAFT'].includes(facture.status) && (
                        <button className="btn btn-warning btn-ghost" disabled={actionLoading} onClick={() => runAction(() => apiService.rejectFacture(factureId, 'Rejeté manuellement'), '❌ Facture rejetée')}>
                            <AlertTriangle size={16} /> Rejeter
                        </button>
                    )}
                    <button className="btn btn-danger" disabled={actionLoading} onClick={handleDelete} title="Suppression définitive">
                        <Trash2 size={16} /> Supprimer
                    </button>
                </div>
            </div>

            <div className="split-container">
                {/* Left: Preview */}
                <div className="preview-panel">
                    <div className="preview-toolbar">
                        <div style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, letterSpacing: '0.5px' }}>
                            <FileSearch size={14} /> APERÇU DOCUMENT
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                                <button className="btn-preview-tool" style={{ borderRadius: '0' }} onClick={() => setZoom(z => Math.max(50, z - 10))} title="Dézoomer"><Minus size={14} /></button>
                                <span style={{ fontSize: '11px', width: '40px', textAlign: 'center', fontWeight: 700 }}>{zoom}%</span>
                                <button className="btn-preview-tool" style={{ borderRadius: '0' }} onClick={() => setZoom(z => Math.min(300, z + 10))} title="Zoomer"><Plus size={14} /></button>
                            </div>
                            <button className="btn-preview-tool" onClick={() => window.open(blobUrl || fileUrl, '_blank')} title="Plein écran">
                                <Maximize2 size={14} />
                            </button>
                        </div>
                    </div>
                    <div className="preview-viewport">
                        {blobUrl ? (
                            isImage ? (
                                <img src={blobUrl} alt="Original" style={{ transform: `scale(${zoom / 100})`, transformOrigin: 'top center' }} />
                            ) : (
                                <iframe src={`${blobUrl}#toolbar=0&navpanes=0`} title="Preview" onError={() => setPdfError(true)} />
                            )
                        ) : (
                            <div style={{ color: 'white', opacity: 0.5, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px' }}>
                                <div className="spinner" style={{ borderColor: 'white', borderRightColor: 'transparent' }} />
                                Chargement du document...
                            </div>
                        )}
                        {pdfError && <div style={{ color: 'white', padding: '40px', textAlign: 'center' }}>Échec de l'aperçu. <a href={blobUrl || fileUrl} target="_blank" rel="noreferrer" style={{ color: 'var(--accent)' }}>Ouvrir manuellement</a></div>}
                    </div>
                </div>

                {/* Right: Data */}
                <div className="data-panel">
                    <div className="pipeline-steps" style={{ marginBottom: '24px', justifyContent: 'flex-start' }}>
                        <div className={getStepClass(1)}>Réception</div>
                        <span className="step-arrow">→</span>
                        <div className={getStepClass(2)}>Analyse</div>
                        <span className="step-arrow">→</span>
                        <div className={getStepClass(3)}>Imputation</div>
                        <span className="step-arrow">→</span>
                        <div className={getStepClass(4)}>Écritures</div>
                        <span className="step-arrow">→</span>
                        <div className={getStepClass(5)}>Contrôle</div>
                    </div>

                    {msg && <div className={`alert alert-${msg.type}`} style={{ marginBottom: '24px' }}>{msg.text}</div>}

                    {/* Tabs */}
                    <div style={{ display: 'flex', gap: '24px', marginBottom: '24px', borderBottom: '1px solid var(--border)' }}>
                        {(['header', 'lines', 'entries'] as const).map(tab => (
                            <button
                                key={tab}
                                onClick={() => setActiveTab(tab)}
                                style={{
                                    padding: '12px 0',
                                    background: 'none',
                                    border: 'none',
                                    cursor: 'pointer',
                                    fontSize: '14px',
                                    fontWeight: 600,
                                    color: activeTab === tab ? 'var(--accent)' : 'var(--text2)',
                                    borderBottom: activeTab === tab ? '2px solid var(--accent)' : '2px solid transparent',
                                    marginBottom: '-1px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px'
                                }}
                            >
                                {tab === 'header' && <FileText size={16} />}
                                {tab === 'lines' && <List size={16} />}
                                {tab === 'entries' && <BookOpen size={16} />}
                                {tab === 'header' ? 'En-tête' : tab === 'lines' ? `Lignes (${lines.length})` : `Écritures (${entries.length})`}
                            </button>
                        ))}
                    </div>

                    {/* Tab Content */}
                    {activeTab === 'header' && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                            <div className="card">
                                <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <div className="card-title">Données extraites</div>
                                    {editingHeader ? (
                                        <div style={{ display: 'flex', gap: '8px' }}>
                                            <button className="btn btn-ghost btn-sm" onClick={() => setEditingHeader(false)}>Annuler</button>
                                            <button className="btn btn-primary btn-sm" onClick={saveHeader} disabled={actionLoading}><Save size={14} /> Enregistrer</button>
                                        </div>
                                    ) : (
                                        <button className="btn btn-ghost btn-sm" onClick={() => { setEditingHeader(true); setHeaderForm({...facture}) }}>
                                            <FileEdit size={14} /> Modifier
                                        </button>
                                    )}
                                </div>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '20px' }}>
                                    {[
                                        { label: 'N° Facture', key: 'numero_facture', type: 'text' },
                                        { label: 'Date', key: 'date_facture', type: 'date' },
                                        { label: 'Échéance', key: 'due_date', type: 'date' },
                                        { label: 'Type', key: 'invoice_type', type: 'select', options: ['ACHAT', 'VENTE', 'AVOIR', 'NOTE_FRAIS', 'IMMOBILISATION'] },
                                        { label: 'Devise', key: 'devise', type: 'text' },
                                        { label: 'Mode paiement', key: 'payment_mode', type: 'select', options: ['Virement', 'Chèque', 'Espèces', 'Effet', 'Autre'] },
                                    ].map(field => (
                                        <div key={field.label}>
                                            <label className="label">{field.label}</label>
                                            {editingHeader ? (
                                                field.type === 'select' ? (
                                                    <select className="form-input" value={(headerForm as any)[field.key] || ''} onChange={e => setHeaderForm(p => ({...p, [field.key]: e.target.value}))} style={{ padding: '6px' }}>
                                                        <option value="">—</option>
                                                        {field.options?.map(o => <option key={o} value={o}>{o}</option>)}
                                                    </select>
                                                ) : (
                                                    <input type={field.type} className="form-input" value={(headerForm as any)[field.key] || ''} onChange={e => setHeaderForm(p => ({...p, [field.key]: e.target.value}))} style={{ padding: '6px' }} />
                                                )
                                            ) : (
                                                <div style={{ fontWeight: 600 }}>{(facture as any)[field.key] || '—'}</div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                                
                                <div style={{ marginTop: '24px', borderTop: '1px solid var(--border)', paddingTop: '20px' }}>
                                    <div className="card-title" style={{ fontSize: '14px', marginBottom: '16px' }}>Tiers (Fournisseur / Client)</div>
                                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '20px' }}>
                                        {[
                                            { label: 'Nom Fournisseur', key: 'supplier_name' },
                                            { label: 'ICE Fournisseur', key: 'supplier_ice' },
                                            { label: 'IF Fournisseur', key: 'supplier_if' },
                                            { label: 'Nom Client', key: 'client_name' },
                                            { label: 'ICE Client', key: 'client_ice' },
                                        ].map(field => (
                                            <div key={field.label}>
                                                <label className="label">{field.label}</label>
                                                {editingHeader ? (
                                                    <input className="form-input" value={(headerForm as any)[field.key] || ''} onChange={e => setHeaderForm(p => ({...p, [field.key]: e.target.value}))} style={{ padding: '6px' }} />
                                                ) : (
                                                    <div style={{ fontWeight: 600 }}>{(facture as any)[field.key] || '—'}</div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                                <div className="card">
                                    <div className="card-title" style={{ marginBottom: '16px' }}>Totaux</div>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--text2)' }}>Montant HT</span>
                                            <span style={{ fontWeight: 700 }}>{fmt(facture.montant_ht)} {facture.devise}</span>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--text2)' }}>TVA ({facture.taux_tva}%)</span>
                                            <span style={{ fontWeight: 700, color: 'var(--warning)' }}>{fmt(facture.montant_tva)} {facture.devise}</span>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border)', paddingTop: '12px' }}>
                                            <span style={{ fontWeight: 700 }}>TOTAL TTC</span>
                                            <span style={{ fontWeight: 800, color: 'var(--accent)', fontSize: '18px' }}>{fmt(facture.montant_ttc)} {facture.devise}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="card">
                                    <div className="card-title" style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <ShieldCheck size={18} color="#10b981" /> Contrôles DGI
                                    </div>
                                    <DgiFlagList flags={facture.dgi_flags} />
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'lines' && (
                        <div className="card">
                            <div className="table-wrap">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>#</th>
                                            <th>Description</th>
                                            <th>Qté</th>
                                            <th>PU HT</th>
                                            <th>Total HT</th>
                                            <th>Compte PCM</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {lines.map(line => (
                                            <tr key={line.id}>
                                                <td style={{ color: 'var(--text3)' }}>{line.line_number}</td>
                                                <td style={{ maxWidth: '300px' }}>{line.description}</td>
                                                <td>{line.quantity} {line.unit}</td>
                                                <td>{fmt(line.unit_price_ht)}</td>
                                                <td style={{ fontWeight: 600 }}>{fmt(line.line_amount_ht)}</td>
                                                <td>
                                                    <span style={{ fontWeight: 700, color: 'var(--accent)' }}>{line.pcm_account_code}</span>
                                                    <div style={{ fontSize: '11px', color: 'var(--text3)' }}>{line.pcm_account_label}</div>
                                                </td>
                                                <td style={{ textAlign: 'right' }}>
                                                    <button className="btn btn-icon" onClick={() => { setEditingLineId(line.id); setEditedLine({...line}); setLineModalOpen(true) }}>
                                                        <FileEdit size={14} />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {activeTab === 'entries' && (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            {entries.map(entry => {
                                const isBalanced = Math.abs(entry.total_debit - entry.total_credit) < 0.01;
                                return (
                                    <div key={entry.id} className="card">
                                        <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <div>
                                                <div className="card-title">{entry.journal_code} — {entry.reference}</div>
                                                <div className="card-subtitle">{entry.description}</div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ fontWeight: 700, color: isBalanced ? 'var(--success)' : 'var(--danger)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                    {isBalanced ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
                                                    {fmt(entry.total_debit)}
                                                </div>
                                                <div style={{ fontSize: '11px', color: 'var(--text3)' }}>{isBalanced ? 'Équilibré' : 'Écart détecté'}</div>
                                            </div>
                                        </div>
                                        <div className="table-wrap">
                                            <table>
                                                <thead>
                                                    <tr>
                                                        <th>Compte</th>
                                                        <th>Libellé</th>
                                                        <th style={{ textAlign: 'right' }}>Débit</th>
                                                        <th style={{ textAlign: 'right' }}>Crédit</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {entry.entry_lines.map(el => (
                                                        <tr key={el.id}>
                                                            <td style={{ fontFamily: 'monospace', fontWeight: 700 }}>{el.account_code}</td>
                                                            <td>{el.account_label}</td>
                                                            <td style={{ textAlign: 'right' }}>{el.debit > 0 ? fmt(el.debit) : '—'}</td>
                                                            <td style={{ textAlign: 'right' }}>{el.credit > 0 ? fmt(el.credit) : '—'}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </div>
            </div>

            {/* Modals */}
            {lineModalOpen && editedLine && (
                <div className="modal-backdrop">
                    <div className="modal">
                        <div className="modal-header">
                            <h3 style={{ margin: 0 }}>Modifier la ligne #{editedLine.line_number}</h3>
                            <button className="btn btn-ghost" onClick={() => setLineModalOpen(false)}><X size={20} /></button>
                        </div>
                        <div className="modal-body" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                            <div style={{ gridColumn: 'span 2' }}>
                                <label className="label">Description</label>
                                <textarea value={editedLine.description || ''} onChange={e => setEditedLine(p => ({...p!, description: e.target.value}))} rows={3} />
                            </div>
                            <div>
                                <label className="label">Quantité</label>
                                <input type="number" value={editedLine.quantity || ''} onChange={e => setEditedLine(p => ({...p!, quantity: Number(e.target.value)}))} />
                            </div>
                            <div>
                                <label className="label">PU HT</label>
                                <input type="number" value={editedLine.unit_price_ht || ''} onChange={e => setEditedLine(p => ({...p!, unit_price_ht: Number(e.target.value)}))} />
                            </div>
                            <div>
                                <label className="label">Compte PCM</label>
                                <input value={editedLine.pcm_account_code || ''} onChange={e => setEditedLine(p => ({...p!, pcm_account_code: e.target.value}))} />
                            </div>
                            <div>
                                <label className="label">Libellé compte</label>
                                <input value={editedLine.pcm_account_label || ''} onChange={e => setEditedLine(p => ({...p!, pcm_account_label: e.target.value}))} />
                            </div>
                        </div>
                        <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end', gap: '12px' }}>
                            <button className="btn btn-ghost" onClick={() => setLineModalOpen(false)}>Annuler</button>
                            <button className="btn btn-primary" onClick={saveLineFromModal} disabled={actionLoading}><Save size={16} /> Enregistrer</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
