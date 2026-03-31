import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { API_CONFIG } from '../config/apiConfig'
import { CheckCircle2, X, Clock, AlertCircle, Zap, Search, ArrowLeft, FileText } from 'lucide-react'

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

interface AvoirDetail {
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
    lignes: any[]
    ecritures: Ecriture[]
}

const fmt = (n?: number) =>
    n != null ? n.toLocaleString('fr-MA', { minimumFractionDigits: 2 }) : '—'

export default function AvoirDetailView() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [selected, setSelected] = useState<AvoirDetail | null>(null)
    const [loading, setLoading] = useState(true)
    const [msg, setMsg] = useState('')

    const token = () => localStorage.getItem('session_token') || ''

    const loadDetail = async () => {
        setLoading(true)
        try {
            const r = await fetch(`${API_CONFIG.BASE_URL}/avoirs/${id}?token=${token()}`)
            if (r.ok) setSelected(await r.json())
        } finally { setLoading(false) }
    }

    useEffect(() => {
        if (id) loadDetail()
    }, [id])

    const generateEntries = async () => {
        const r = await fetch(`${API_CONFIG.BASE_URL}/avoirs/${id}/generate-entries?token=${token()}`, { method: 'POST' })
        const data = await r.json()
        if (r.ok) { setMsg('✅ Écritures générées'); loadDetail() }
        else setMsg('❌ ' + (data.detail || 'Erreur'))
    }

    const validate = async () => {
        const r = await fetch(`${API_CONFIG.BASE_URL}/avoirs/${id}/validate?token=${token()}`, { method: 'POST' })
        const data = await r.json()
        if (r.ok) { setMsg('✅ Avoir validé'); loadDetail() }
        else setMsg('❌ ' + (data.detail || 'Erreur'))
    }

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '100px', color: 'var(--text2)' }}>
                <Clock size={48} className="spin" style={{ marginBottom: '20px', opacity: 0.5 }} />
                <h2>Chargement des détails...</h2>
            </div>
        )
    }

    if (!selected) {
        return (
            <div style={{ textAlign: 'center', padding: '100px', color: 'var(--text2)' }}>
                <h2>Avoir introuvable</h2>
                <button onClick={() => navigate('/avoirs')} style={{ marginTop: '20px', padding: '10px 20px', borderRadius: '8px', border: '1px solid var(--border)', cursor: 'pointer' }}>
                    Retourner à la liste
                </button>
            </div>
        )
    }

    return (
        <div style={{ padding: '32px', maxWidth: '1000px', margin: '0 auto' }}>
            {/* Header / Bouton Retour */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '32px' }}>
                <button
                    onClick={() => navigate('/avoirs')}
                    style={{
                        background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '50%',
                        width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                        cursor: 'pointer', color: 'var(--text)'
                    }}
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text)', margin: 0, display: 'flex', alignItems: 'center', gap: '12px' }}>
                        Détail Avoir {selected.numero_avoir || `#${selected.id}`}
                    </h1>
                    <p style={{ color: 'var(--text2)', margin: '4px 0 0' }}>
                        {selected.fournisseur || selected.client} · {selected.date_avoir}
                    </p>
                </div>
            </div>

            {msg && (
                <div style={{
                    background: msg.startsWith('✅') ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                    border: `1px solid ${msg.startsWith('✅') ? '#10b981' : '#ef4444'}`,
                    borderRadius: '10px', padding: '12px 20px', marginBottom: '20px',
                    color: msg.startsWith('✅') ? '#10b981' : '#ef4444', fontSize: '14px',
                    display: 'flex', alignItems: 'center', gap: '10px'
                }}>
                    {msg.startsWith('✅') ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                    {msg.replace(/^[✅❌]\s*/, '')}
                    <button onClick={() => setMsg('')} style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}><X size={18} /></button>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '24px' }}>
                {/* Carte des Montants */}
                <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '16px', padding: '24px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
                        {[
                            { label: 'Montant HT', value: fmt(selected.montant_ht) },
                            { label: 'TVA', value: fmt(selected.montant_tva) },
                            { label: 'Montant TTC', value: fmt(selected.montant_ttc), accent: true },
                        ].map(({ label, value, accent }) => (
                            <div key={label} style={{
                                background: 'rgba(255,255,255,0.03)', borderRadius: '12px', padding: '20px', textAlign: 'center',
                                border: accent ? '1px dashed rgba(239,68,68,0.5)' : '1px solid var(--border)'
                            }}>
                                <div style={{ fontSize: '13px', color: 'var(--text2)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</div>
                                <div style={{ fontSize: '24px', fontWeight: 800, color: accent ? '#ef4444' : 'var(--text)' }}>
                                    {accent ? '-' : ''}{value} {selected.devise}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Actions principales */}
                <div style={{ display: 'flex', gap: '12px' }}>
                    {selected.status !== 'VALIDATED' && (
                        <button onClick={generateEntries} style={{
                            flex: 1, background: 'rgba(99,102,241,0.1)', color: '#818cf8',
                            border: '1px solid rgba(99,102,241,0.3)', padding: '16px', borderRadius: '12px',
                            cursor: 'pointer', fontSize: '15px', fontWeight: 600,
                            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', transition: 'all 0.2s'
                        }}>
                            <Zap size={20} /> Générer écritures
                        </button>
                    )}
                    {selected.has_draft_entries && selected.status !== 'VALIDATED' && (
                        <button onClick={validate} style={{
                            flex: 1, background: 'rgba(16,185,129,0.1)', color: '#10b981',
                            border: '1px solid rgba(16,185,129,0.3)', padding: '16px', borderRadius: '12px',
                            cursor: 'pointer', fontSize: '15px', fontWeight: 600,
                            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', transition: 'all 0.2s'
                        }}>
                            <CheckCircle2 size={20} /> Valider l'Avoir
                        </button>
                    )}
                    <button onClick={() => navigate(`/factures/${selected.id}`)} style={{
                        flex: 1, background: 'var(--card)', color: 'var(--text)',
                        border: '1px solid var(--border)', padding: '16px', borderRadius: '12px',
                        cursor: 'pointer', fontSize: '15px', fontWeight: 600,
                        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', transition: 'all 0.2s'
                    }}>
                        <FileText size={20} /> Voir le document
                    </button>
                </div>

                {/* Écritures comptables générées */}
                <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '16px', padding: '24px' }}>
                    <h3 style={{ margin: '0 0 20px', fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span>📒</span> Écritures comptables
                    </h3>
                    
                    {selected.ecritures?.length > 0 ? (
                        <div>
                            {selected.ecritures.map(e => (
                                <div key={e.id} style={{
                                    background: 'rgba(255,255,255,0.02)', borderRadius: '12px',
                                    border: '1px solid var(--border)', padding: '20px', marginBottom: '16px'
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                            <span style={{
                                                background: 'rgba(99,102,241,0.2)', color: '#818cf8',
                                                padding: '4px 12px', borderRadius: '20px', fontSize: '13px', fontWeight: 800
                                            }}>{e.journal_code}</span>
                                            <span style={{ color: 'var(--text2)', fontSize: '14px' }}>Réf: {e.reference}</span>
                                        </div>
                                        <span style={{ fontSize: '13px', color: e.is_validated ? '#10b981' : '#f59e0b', display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, background: e.is_validated ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)', padding: '4px 12px', borderRadius: '20px' }}>
                                            {e.is_validated ? <><CheckCircle2 size={16} /> Validé</> : <><Clock size={16} /> Brouillon</>}
                                        </span>
                                    </div>
                                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                                        <thead>
                                            <tr style={{ color: 'var(--text2)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                                <th style={{ textAlign: 'left', padding: '8px 0', width: '60%' }}>Compte</th>
                                                <th style={{ textAlign: 'right', padding: '8px 0', width: '20%' }}>Débit</th>
                                                <th style={{ textAlign: 'right', padding: '8px 0', width: '20%' }}>Crédit</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {e.entry_lines.map((el, i) => (
                                                <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                                                    <td style={{ padding: '12px 0', color: 'var(--text)' }}>
                                                        <span style={{ fontWeight: 700, color: '#818cf8', marginRight: '12px' }}>{el.account_code}</span>
                                                        <span style={{ color: 'var(--text)' }}>{el.account_label}</span>
                                                        {el.tiers_name && <span style={{display: 'block', fontSize: '11px', color: 'var(--text3)', marginTop: '4px'}}>{el.tiers_name}</span>}
                                                    </td>
                                                    <td style={{ textAlign: 'right', color: '#10b981', padding: '12px 0', fontWeight: 600 }}>
                                                        {el.debit > 0 ? fmt(el.debit) : ''}
                                                    </td>
                                                    <td style={{ textAlign: 'right', color: '#ef4444', padding: '12px 0', fontWeight: 600 }}>
                                                        {el.credit > 0 ? fmt(el.credit) : ''}
                                                    </td>
                                                </tr>
                                            ))}
                                            <tr style={{ borderTop: '2px solid var(--border)', background: 'rgba(0,0,0,0.1)' }}>
                                                <td style={{ padding: '12px 8px', color: 'var(--text)', fontSize: '13px', fontWeight: 800 }}>TOTAL</td>
                                                <td style={{ textAlign: 'right', color: '#10b981', padding: '12px 8px', fontWeight: 800, fontSize: '15px' }}>{fmt(e.total_debit)}</td>
                                                <td style={{ textAlign: 'right', color: '#ef4444', padding: '12px 8px', fontWeight: 800, fontSize: '15px' }}>{fmt(e.total_credit)}</td>
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div style={{
                            background: 'rgba(255,255,255,0.02)', borderRadius: '12px', padding: '40px',
                            textAlign: 'center', color: 'var(--text2)', fontSize: '15px', border: '1px dashed var(--border)'
                        }}>
                            <Zap size={32} opacity={0.5} style={{ marginBottom: '12px' }} />
                            <div>Aucune écriture comptable générée pour le moment.</div>
                            <div style={{ fontSize: '13px', marginTop: '8px', opacity: 0.7 }}>Cliquez sur le bouton "Générer écritures" ci-dessus.</div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
