import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { API_CONFIG } from '../config/apiConfig'
import {
    FileText,
    RefreshCcw,
    CheckCircle2,
    X,
    Clock,
    AlertCircle,
    Store,
    Calendar,
    Zap,
    Search,
    ChevronRight,
    ArrowLeft
} from 'lucide-react'

interface Avoir {
    id: number
    numero_avoir: string
    date_avoir: string
    type_avoir: string
    fournisseur: string
    client: string
    montant_ht: number
    montant_tva: number
    montant_ttc: number
    devise: string
    status: string
    has_entries: boolean
    has_draft_entries: boolean
    created_at: string
}

interface EntryLine {
    account_code: string
    account_label: string
    debit: number
    credit: number
    tiers_name: string
}

interface Ecriture {
    id: number
    journal_code: string
    entry_date: string
    reference: string
    description: string
    is_validated: boolean
    total_debit: number
    total_credit: number
    entry_lines: EntryLine[]
}

interface AvoirDetail extends Avoir {
    lignes: any[]
    ecritures: Ecriture[]
}

const STATUS_COLORS: Record<string, string> = {
    VALIDATED: '#10b981',
    DRAFT: '#f59e0b',
    CLASSIFIED: '#6366f1',
    EXTRACTED: '#3b82f6',
    IMPORTED: '#64748b',
    ERROR: '#ef4444',
}

const fmt = (n?: number) =>
    n != null ? n.toLocaleString('fr-MA', { minimumFractionDigits: 2 }) : '—'

export default function Avoirs() {
    const [avoirs, setAvoirs] = useState<Avoir[]>([])
    const [loading, setLoading] = useState(true)
    const [selected, setSelected] = useState<AvoirDetail | null>(null)
    const [detailLoading, setDetailLoading] = useState(false)
    const [msg, setMsg] = useState('')
    const navigate = useNavigate()

    const token = () => localStorage.getItem('session_token') || ''

    const load = async () => {
        setLoading(true)
        try {
            const r = await fetch(`${API_CONFIG.BASE_URL}/avoirs/?token=${token()}`)
            if (r.ok) setAvoirs(await r.json())
        } finally { setLoading(false) }
    }

    useEffect(() => { load() }, [])

    const loadDetail = async (id: number) => {
        setDetailLoading(true)
        try {
            const r = await fetch(`${API_CONFIG.BASE_URL}/avoirs/${id}?token=${token()}`)
            if (r.ok) setSelected(await r.json())
        } finally { setDetailLoading(false) }
    }

    const generateEntries = async (id: number) => {
        const r = await fetch(`${API_CONFIG.BASE_URL}/avoirs/${id}/generate-entries?token=${token()}`, { method: 'POST' })
        const data = await r.json()
        if (r.ok) { setMsg('✅ Écritures générées'); loadDetail(id); load() }
        else setMsg('❌ ' + (data.detail || 'Erreur'))
    }

    const validate = async (id: number) => {
        const r = await fetch(`${API_CONFIG.BASE_URL}/avoirs/${id}/validate?token=${token()}`, { method: 'POST' })
        const data = await r.json()
        if (r.ok) { setMsg('✅ Avoir validé'); loadDetail(id); load() }
        else setMsg('❌ ' + (data.detail || 'Erreur'))
    }

    return (
        <div style={{ padding: '32px', maxWidth: '1300px', margin: '0 auto' }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px' }}>
                <div>
                    <h1 style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text)', margin: 0, display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <FileText size={32} color="var(--accent)" /> Avoirs
                    </h1>
                    <p style={{ color: 'var(--text2)', margin: '4px 0 0 44px' }}>
                        Gestion des avoirs fournisseurs et clients
                    </p>
                </div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <span style={{
                        background: 'rgba(99,102,241,0.15)', color: '#818cf8',
                        padding: '6px 16px', borderRadius: '20px', fontSize: '13px', fontWeight: 600
                    }}>
                        {avoirs.length} avoir{avoirs.length !== 1 ? 's' : ''}
                    </span>
                    <button onClick={load} style={{
                        background: 'var(--accent)', color: 'white', border: 'none',
                        padding: '8px 18px', borderRadius: '8px', cursor: 'pointer', fontSize: '13px',
                        display: 'flex', alignItems: 'center', gap: '8px'
                    }}>
                        <RefreshCcw size={16} /> Actualiser
                    </button>
                </div>
            </div>

            {msg && (
                <div style={{
                    background: msg.startsWith('✅') ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                    border: `1px solid ${msg.startsWith('✅') ? '#10b981' : '#ef4444'}`,
                    borderRadius: '10px', padding: '12px 20px', marginBottom: '20px',
                    color: msg.startsWith('✅') ? '#10b981' : '#ef4444', fontSize: '14px',
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {msg.startsWith('✅') ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                        {msg.replace(/^[✅❌]\s*/, '')}
                    </div>
                    <button onClick={() => setMsg('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}><X size={18} /></button>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 420px' : '1fr', gap: '24px' }}>
                {/* Liste des avoirs */}
                <div>
                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text2)' }}>
                            <div style={{ fontSize: '32px', marginBottom: '12px' }}><Clock size={32} /></div>
                            Chargement...
                        </div>
                    ) : avoirs.length === 0 ? (
                        <div style={{
                            background: 'var(--card)', border: '1px solid var(--border)',
                            borderRadius: '16px', padding: '60px', textAlign: 'center'
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
                                <FileText size={48} color="var(--text3)" opacity={0.5} />
                            </div>
                            <h3 style={{ color: 'var(--text)', margin: '0 0 8px' }}>Aucun avoir</h3>
                            <p style={{ color: 'var(--text2)', margin: 0 }}>
                                Les avoirs apparaissent automatiquement lors du traitement des factures
                            </p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {avoirs.map(a => (
                                <div
                                    key={a.id}
                                    onClick={() => loadDetail(a.id)}
                                    style={{
                                        background: selected?.id === a.id ? 'rgba(99,102,241,0.08)' : 'var(--card)',
                                        border: `1px solid ${selected?.id === a.id ? 'var(--accent)' : 'var(--border)'}`,
                                        borderRadius: '14px', padding: '20px', cursor: 'pointer',
                                        transition: 'all 0.2s',
                                        display: 'grid', gridTemplateColumns: '1fr auto', gap: '12px', alignItems: 'center'
                                    }}
                                >
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                                            <span style={{ fontWeight: 700, color: 'var(--text)', fontSize: '15px' }}>
                                                {a.numero_avoir || `Avoir #${a.id}`}
                                            </span>
                                            <span style={{
                                                background: 'rgba(99,102,241,0.15)', color: '#818cf8',
                                                padding: '2px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 600
                                            }}>
                                                AVOIR
                                            </span>
                                            <span style={{
                                                background: `${STATUS_COLORS[a.status] || '#64748b'}20`,
                                                color: STATUS_COLORS[a.status] || '#64748b',
                                                padding: '2px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 600
                                            }}>
                                                {a.status}
                                            </span>
                                        </div>
                                        <div style={{ fontSize: '13px', color: 'var(--text2)', display: 'flex', gap: '16px', alignItems: 'center' }}>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Store size={14} /> {a.fournisseur || a.client || '—'}</span>
                                            <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Calendar size={14} /> {a.date_avoir || '—'}</span>
                                            {a.has_draft_entries && <span style={{ color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '4px' }}><Zap size={14} /> Écritures en attente</span>}
                                            {a.has_entries && !a.has_draft_entries && <span style={{ color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}><CheckCircle2 size={14} /> Validé</span>}
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#ef4444' }}>
                                            -{fmt(a.montant_ttc)} {a.devise}
                                        </div>
                                        <div style={{ fontSize: '12px', color: 'var(--text2)' }}>
                                            HT: {fmt(a.montant_ht)} | TVA: {fmt(a.montant_tva)}
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Panneau détail */}
                {selected && (
                    <div style={{
                        background: 'var(--card)', border: '1px solid var(--border)',
                        borderRadius: '16px', padding: '24px', height: 'fit-content',
                        position: 'sticky', top: '20px', maxHeight: '85vh', overflowY: 'auto'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                            <div>
                                <h3 style={{ margin: 0, color: 'var(--text)', fontSize: '17px' }}>
                                    {selected.numero_avoir || `Avoir #${selected.id}`}
                                </h3>
                                <p style={{ margin: '4px 0 0', color: 'var(--text2)', fontSize: '13px' }}>
                                    {selected.fournisseur || selected.client} · {selected.date_avoir}
                                </p>
                            </div>
                            <button onClick={() => setSelected(null)} style={{
                                background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text2)', fontSize: '18px',
                                display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '4px'
                            }}><X size={20} /></button>
                        </div>

                        {/* Montants */}
                        <div style={{
                            display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px', marginBottom: '20px'
                        }}>
                            {[
                                { label: 'Montant HT', value: fmt(selected.montant_ht) },
                                { label: 'TVA', value: fmt(selected.montant_tva) },
                                { label: 'TTC', value: fmt(selected.montant_ttc), accent: true },
                            ].map(({ label, value, accent }) => (
                                <div key={label} style={{
                                    background: 'rgba(255,255,255,0.03)', borderRadius: '10px',
                                    padding: '12px', textAlign: 'center',
                                    border: accent ? '1px solid rgba(239,68,68,0.3)' : '1px solid var(--border)'
                                }}>
                                    <div style={{ fontSize: '11px', color: 'var(--text2)', marginBottom: '4px' }}>{label}</div>
                                    <div style={{ fontSize: '15px', fontWeight: 700, color: accent ? '#ef4444' : 'var(--text)' }}>
                                        {value}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Actions */}
                        <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
                            {selected.status !== 'VALIDATED' && (
                                <button onClick={() => generateEntries(selected.id)} style={{
                                    flex: 1, background: 'rgba(99,102,241,0.15)', color: '#818cf8',
                                    border: '1px solid rgba(99,102,241,0.3)', padding: '9px', borderRadius: '8px',
                                    cursor: 'pointer', fontSize: '12px', fontWeight: 600,
                                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px'
                                }}><Zap size={14} /> Générer écritures</button>
                            )}
                            {selected.has_draft_entries && selected.status !== 'VALIDATED' && (
                                <button onClick={() => validate(selected.id)} style={{
                                    flex: 1, background: 'rgba(16,185,129,0.15)', color: '#10b981',
                                    border: '1px solid rgba(16,185,129,0.3)', padding: '9px', borderRadius: '8px',
                                    cursor: 'pointer', fontSize: '12px', fontWeight: 600,
                                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px'
                                }}><CheckCircle2 size={14} /> Valider</button>
                            )}
                            <button onClick={() => navigate(`/factures/${selected.id}`)} style={{
                                flex: 1, background: 'rgba(255,255,255,0.05)', color: 'var(--text2)',
                                border: '1px solid var(--border)', padding: '9px', borderRadius: '8px',
                                cursor: 'pointer', fontSize: '12px',
                                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px'
                            }}><Search size={14} /> Ouvrir facture</button>
                        </div>

                        {/* Écritures comptables */}
                        {detailLoading ? (
                            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text2)' }}>Chargement...</div>
                        ) : selected.ecritures?.length > 0 ? (
                            <div>
                                <h4 style={{ color: 'var(--text)', margin: '0 0 12px', fontSize: '14px' }}>
                                    📒 Écritures comptables
                                </h4>
                                {selected.ecritures.map(e => (
                                    <div key={e.id} style={{
                                        background: 'rgba(255,255,255,0.02)', borderRadius: '10px',
                                        border: '1px solid var(--border)', padding: '14px', marginBottom: '10px'
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                            <span style={{
                                                background: 'rgba(99,102,241,0.2)', color: '#818cf8',
                                                padding: '2px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 700
                                            }}>{e.journal_code}</span>
                                            <span style={{ fontSize: '11px', color: e.is_validated ? '#10b981' : '#f59e0b', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                {e.is_validated ? <><CheckCircle2 size={12} /> Validé</> : <><Clock size={12} /> Brouillon</>}
                                            </span>
                                        </div>
                                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                                            <thead>
                                                <tr style={{ color: 'var(--text2)' }}>
                                                    <th style={{ textAlign: 'left', padding: '4px 0' }}>Compte</th>
                                                    <th style={{ textAlign: 'right', padding: '4px 0' }}>Débit</th>
                                                    <th style={{ textAlign: 'right', padding: '4px 0' }}>Crédit</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {e.entry_lines.map((el, i) => (
                                                    <tr key={i} style={{ borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                                                        <td style={{ padding: '5px 0', color: 'var(--text)' }}>
                                                            <span style={{ fontWeight: 600, color: '#818cf8' }}>{el.account_code}</span>
                                                            <span style={{ color: 'var(--text2)', marginLeft: '8px' }}>{el.account_label}</span>
                                                        </td>
                                                        <td style={{ textAlign: 'right', color: '#10b981', padding: '5px 0' }}>
                                                            {el.debit > 0 ? fmt(el.debit) : ''}
                                                        </td>
                                                        <td style={{ textAlign: 'right', color: '#ef4444', padding: '5px 0' }}>
                                                            {el.credit > 0 ? fmt(el.credit) : ''}
                                                        </td>
                                                    </tr>
                                                ))}
                                                <tr style={{ borderTop: '2px solid var(--border)', fontWeight: 700 }}>
                                                    <td style={{ padding: '6px 0', color: 'var(--text2)', fontSize: '11px' }}>TOTAL</td>
                                                    <td style={{ textAlign: 'right', color: '#10b981' }}>{fmt(e.total_debit)}</td>
                                                    <td style={{ textAlign: 'right', color: '#ef4444' }}>{fmt(e.total_credit)}</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div style={{
                                background: 'rgba(255,255,255,0.02)', borderRadius: '10px', padding: '20px',
                                textAlign: 'center', color: 'var(--text2)', fontSize: '13px'
                            }}>
                                Aucune écriture générée — cliquez sur "Générer écritures"
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
