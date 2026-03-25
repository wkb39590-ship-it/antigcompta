import { useState, useEffect } from 'react'
import { API_CONFIG } from '../config/apiConfig'
import {
    Calendar,
    CalendarRange,
    Layers,
    ShoppingCart,
    TrendingUp,
    FileJson,
    Banknote,
    Scale,
    AlertTriangle,
    Clock,
    CheckCircle2,
    Download,
    ChevronUp,
    ChevronDown
} from 'lucide-react'

interface EntryLine {
    id: number
    line_order: number
    account_code: string
    account_label: string
    debit: number
    credit: number
    tiers_name: string
    tiers_ice: string
}

interface Ecriture {
    id: number
    journal_code: string
    journal_label: string
    entry_date: string
    reference: string
    description: string
    is_validated: boolean
    total_debit: number
    total_credit: number
    facture_id: number
    entry_lines: EntryLine[]
}

interface JournalResponse {
    journal_code: string
    journal_label: string
    total_ecritures: number
    total_debit: number
    total_credit: number
    equilibre: boolean
    ecritures: Ecriture[]
}

interface Totaux {
    periode: string
    totaux_par_journal: Record<string, {
        journal_code: string
        journal_label: string
        nb_ecritures: number
        total_debit: number
        total_credit: number
        equilibre: boolean
    }>
}

const JOURNALS = [
    { code: '', label: 'Tous', icon: <Layers size={16} />, color: '#6366f1' },
    { code: 'ACH', label: 'Achats', icon: <ShoppingCart size={16} />, color: '#f59e0b' },
    { code: 'VTE', label: 'Ventes', icon: <TrendingUp size={16} />, color: '#10b981' },
    { code: 'IMMO', label: 'Immos', icon: <Scale size={16} />, color: '#ec4899' },
    { code: 'OD', label: 'OD', icon: <FileJson size={16} />, color: '#8b5cf6' },
    { code: 'BQ', label: 'Banque', icon: <Banknote size={16} />, color: '#3b82f6' },
]

const fmt = (n?: number) => n != null ? n.toLocaleString('fr-MA', { minimumFractionDigits: 2 }) : '0,00'

export default function JournalComptable() {
    const [activeJournal, setActiveJournal] = useState('')
    const [data, setData] = useState<JournalResponse | null>(null)
    const [totaux, setTotaux] = useState<Totaux | null>(null)
    const [loading, setLoading] = useState(false)
    const [expanded, setExpanded] = useState<number | null>(null)
    const [annee, setAnnee] = useState(new Date().getFullYear())
    const [mois, setMois] = useState(new Date().getMonth() + 1)
    const [filterMode, setFilterMode] = useState<'tout' | 'annee' | 'mois'>('tout')

    const token = () => localStorage.getItem('session_token') || ''

    const buildParams = () => {
        const params = new URLSearchParams({ token: token() })
        if (activeJournal) params.append('journal_code', activeJournal)
        if (filterMode === 'annee') {
            params.append('date_debut', `${annee}-01-01`)
            params.append('date_fin', `${annee}-12-31`)
        } else if (filterMode === 'mois') {
            const lastDay = new Date(annee, mois, 0).getDate()
            const mm = String(mois).padStart(2, '0')
            params.append('date_debut', `${annee}-${mm}-01`)
            params.append('date_fin', `${annee}-${mm}-${lastDay}`)
        }
        // filterMode === 'tout' => pas de filtre date => toutes les écritures
        params.append('valide_seulement', 'false')
        return params
    }

    const load = async () => {
        setLoading(true)
        try {
            const r = await fetch(`${API_CONFIG.BASE_URL}/journaux/?${buildParams()}`)
            if (r.ok) setData(await r.json())
        } finally { setLoading(false) }
    }

    const loadTotaux = async () => {
        const params = new URLSearchParams({ token: token() })
        if (filterMode === 'annee') params.append('annee', String(annee))
        else if (filterMode === 'mois') {
            params.append('annee', String(annee))
            params.append('mois', String(mois))
        }
        // filterMode === 'tout' => pas de filtre annee
        params.append('valide_seulement', 'false')
        const r = await fetch(`${API_CONFIG.BASE_URL}/journaux/totaux?${params}`)
        if (r.ok) setTotaux(await r.json())
    }

    useEffect(() => { load(); loadTotaux() }, [activeJournal, annee, mois, filterMode])

    const exportCSV = () => {
        const params = buildParams()
        window.open(`${API_CONFIG.BASE_URL}/journaux/export?${params}`, '_blank')
    }

    const MONTHS = ['', 'Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']

    return (
        <div style={{ padding: '32px', maxWidth: '1400px', margin: '0 auto' }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px' }}>
                <div>
                    <h1 style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text)', margin: 0 }}>📒 Journal Comptable</h1>
                    <p style={{ color: 'var(--text2)', margin: '4px 0 0' }}>Écritures validées par journal (PCM Maroc)</p>
                </div>
                <button onClick={exportCSV} style={{
                    background: 'rgba(16,185,129,0.15)', color: '#10b981', border: '1px solid rgba(16,185,129,0.3)',
                    padding: '10px 20px', borderRadius: '10px', cursor: 'pointer', fontSize: '14px', fontWeight: 600,
                    display: 'flex', alignItems: 'center', gap: '8px'
                }}>
                    <Download size={16} /> Export CSV
                </button>
            </div>

            {/* Filtres période */}
            <div style={{
                background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '14px',
                padding: '16px 20px', marginBottom: '20px', display: 'flex', gap: '16px', alignItems: 'center', flexWrap: 'wrap'
            }}>
                <div style={{ display: 'flex', gap: '8px' }}>
                    {(['tout', 'annee', 'mois'] as const).map(m => (
                        <button key={m} onClick={() => setFilterMode(m)} style={{
                            background: filterMode === m ? 'var(--accent)' : 'rgba(99,102,241,0.08)',
                            color: filterMode === m ? 'white' : 'var(--text2)',
                            border: 'none', padding: '7px 16px', borderRadius: '8px', cursor: 'pointer', fontSize: '13px',
                            fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px'
                        }}>
                            {m === 'tout' ? <><CalendarRange size={14} /> Tout afficher</> :
                                m === 'annee' ? <><Calendar size={14} /> Année</> :
                                    <><Clock size={14} /> Mois</>}
                        </button>
                    ))}
                </div>
                {filterMode !== 'tout' && (
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                        <label style={{ color: 'var(--text2)', fontSize: '13px' }}>Année:</label>
                        <input type="number" value={annee} onChange={e => setAnnee(Number(e.target.value))}
                            min={2020} max={2030}
                            style={{
                                background: 'rgba(99,102,241,0.08)', border: '1px solid var(--border)',
                                borderRadius: '8px', padding: '7px 12px', color: 'var(--text)', width: '90px', fontSize: '14px'
                            }} />
                        {filterMode === 'mois' && (
                            <>
                                <label style={{ color: 'var(--text2)', fontSize: '13px' }}>Mois:</label>
                                <select value={mois} onChange={e => setMois(Number(e.target.value))} style={{
                                    background: 'rgba(99,102,241,0.08)', border: '1px solid var(--border)',
                                    borderRadius: '8px', padding: '7px 12px', color: 'var(--text)', fontSize: '14px'
                                }}>
                                    {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
                                        <option key={m} value={m}>{MONTHS[m]}</option>
                                    ))}
                                </select>
                            </>
                        )}
                    </div>
                )}
            </div>

            {/* Cartes totaux par journal */}
            {totaux && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '14px', marginBottom: '24px' }}>
                    {Object.values(totaux.totaux_par_journal).map(t => {
                        const jInfo = JOURNALS.find(j => j.code === t.journal_code)
                        return (
                            <div key={t.journal_code} onClick={() => setActiveJournal(t.journal_code)}
                                style={{
                                    background: activeJournal === t.journal_code ? `${jInfo?.color}18` : 'var(--card)',
                                    border: `1px solid ${activeJournal === t.journal_code ? jInfo?.color : 'var(--border)'}`,
                                    borderRadius: '14px', padding: '16px', cursor: 'pointer', transition: 'all 0.2s'
                                }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                    <span style={{ fontWeight: 700, color: jInfo?.color || 'var(--text)', fontSize: '13px' }}>{jInfo?.label || t.journal_code}</span>
                                    <span style={{
                                        background: t.equilibre ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                                        color: t.equilibre ? '#10b981' : '#ef4444',
                                        padding: '4px 8px', borderRadius: '20px', fontSize: '10px', fontWeight: 700,
                                        display: 'flex', alignItems: 'center', gap: '4px'
                                    }}>{t.equilibre ? <><Scale size={12} /> OK</> : <><AlertTriangle size={12} /> Écart</>}</span>
                                </div>
                                <div style={{ fontSize: '11px', color: 'var(--text2)', marginBottom: '6px' }}>
                                    {t.nb_ecritures} écriture{t.nb_ecritures !== 1 ? 's' : ''}
                                </div>
                                <div style={{ fontSize: '12px' }}>
                                    <div style={{ color: '#10b981' }}>D: {fmt(t.total_debit)}</div>
                                    <div style={{ color: '#ef4444' }}>C: {fmt(t.total_credit)}</div>
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}

            {/* Onglets journaux */}
            <div style={{
                display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap',
                background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '12px', padding: '8px'
            }}>
                {JOURNALS.map(j => (
                    <button key={j.code} onClick={() => setActiveJournal(j.code)} style={{
                        background: activeJournal === j.code ? j.color : 'transparent',
                        color: activeJournal === j.code ? 'white' : 'var(--text2)',
                        border: `1px solid ${activeJournal === j.code ? j.color : 'transparent'}`,
                        padding: '7px 18px', borderRadius: '8px', cursor: 'pointer', fontSize: '13px', fontWeight: 600,
                        transition: 'all 0.15s', display: 'flex', alignItems: 'center', gap: '8px'
                    }}>{j.icon}{j.label}</button>
                ))}
            </div>

            {/* Table journal */}
            <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: '16px', overflow: 'hidden' }}>
                {loading ? (
                    <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text2)' }}>⏳ Chargement...</div>
                ) : !data || data.ecritures.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '60px' }}>
                        <div style={{ fontSize: '40px', marginBottom: '12px' }}>📭</div>
                        <div style={{ color: 'var(--text2)' }}>Aucune écriture pour cette période</div>
                    </div>
                ) : (
                    <>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                            <thead>
                                <tr style={{ background: 'rgba(255,255,255,0.03)', borderBottom: '1px solid var(--border)' }}>
                                    {['Journal', 'Date', 'N° Pièce', 'Libellé', 'Débit', 'Crédit', 'État', ''].map(h => (
                                        <th key={h} style={{ padding: '14px 16px', textAlign: h === 'Débit' || h === 'Crédit' ? 'right' : 'left', color: 'var(--text2)', fontWeight: 600, fontSize: '12px', whiteSpace: 'nowrap' }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {data.ecritures.map(e => (
                                    <>
                                        <tr key={e.id}
                                            onClick={() => setExpanded(expanded === e.id ? null : e.id)}
                                            style={{
                                                borderBottom: '1px solid var(--border)', cursor: 'pointer',
                                                background: expanded === e.id ? 'rgba(99,102,241,0.05)' : 'transparent',
                                                transition: 'background 0.15s'
                                            }}>
                                            <td style={{ padding: '12px 16px' }}>
                                                <span style={{
                                                    background: JOURNALS.find(j => j.code === e.journal_code)?.color + '22' || 'rgba(99,102,241,0.15)',
                                                    color: JOURNALS.find(j => j.code === e.journal_code)?.color || '#818cf8',
                                                    padding: '3px 10px', borderRadius: '20px', fontWeight: 700, fontSize: '11px'
                                                }}>{e.journal_code}</span>
                                            </td>
                                            <td style={{ padding: '12px 16px', color: 'var(--text2)', whiteSpace: 'nowrap' }}>{e.entry_date || '—'}</td>
                                            <td style={{ padding: '12px 16px', color: 'var(--text)', fontWeight: 600 }}>{e.reference || '—'}</td>
                                            <td style={{ padding: '12px 16px', color: 'var(--text2)', maxWidth: '280px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.description}</td>
                                            <td style={{ padding: '12px 16px', textAlign: 'right', color: '#10b981', fontWeight: 600 }}>{fmt(e.total_debit)}</td>
                                            <td style={{ padding: '12px 16px', textAlign: 'right', color: '#ef4444', fontWeight: 600 }}>{fmt(e.total_credit)}</td>
                                            <td style={{ padding: '12px 16px' }}>
                                                <span style={{
                                                    background: e.is_validated ? 'rgba(16,185,129,0.12)' : 'rgba(245,158,11,0.12)',
                                                    color: e.is_validated ? '#10b981' : '#f59e0b',
                                                    padding: '4px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 600,
                                                    display: 'inline-flex', alignItems: 'center', gap: '6px'
                                                }}>{e.is_validated ? <><CheckCircle2 size={12} /> Validé</> : <><Clock size={12} /> Brouillon</>}</span>
                                            </td>
                                            <td style={{ padding: '12px 16px', color: 'var(--text2)' }}>{expanded === e.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}</td>
                                        </tr>
                                        {expanded === e.id && (
                                            <tr key={`${e.id}-detail`}>
                                                <td colSpan={8} style={{ padding: '0 16px 16px', background: 'rgba(99,102,241,0.03)' }}>
                                                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', marginTop: '8px' }}>
                                                        <thead>
                                                            <tr style={{ color: 'var(--text2)' }}>
                                                                <th style={{ textAlign: 'left', padding: '5px 0', fontWeight: 600 }}>N°</th>
                                                                <th style={{ textAlign: 'left', padding: '5px 0', fontWeight: 600 }}>Compte</th>
                                                                <th style={{ textAlign: 'left', padding: '5px 0', fontWeight: 600 }}>Libellé compte</th>
                                                                <th style={{ textAlign: 'left', padding: '5px 0', fontWeight: 600 }}>Tiers</th>
                                                                <th style={{ textAlign: 'right', padding: '5px 0', fontWeight: 600 }}>Débit</th>
                                                                <th style={{ textAlign: 'right', padding: '5px 0', fontWeight: 600 }}>Crédit</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {e.entry_lines.map(el => (
                                                                <tr key={el.id} style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
                                                                    <td style={{ padding: '5px 0', color: 'var(--text2)' }}>{el.line_order}</td>
                                                                    <td style={{ padding: '5px 0', color: '#818cf8', fontWeight: 700 }}>{el.account_code}</td>
                                                                    <td style={{ padding: '5px 0', color: 'var(--text)' }}>{el.account_label}</td>
                                                                    <td style={{ padding: '5px 0', color: 'var(--text2)' }}>{el.tiers_name || '—'}</td>
                                                                    <td style={{ padding: '5px 0', textAlign: 'right', color: '#10b981' }}>{el.debit > 0 ? fmt(el.debit) : ''}</td>
                                                                    <td style={{ padding: '5px 0', textAlign: 'right', color: '#ef4444' }}>{el.credit > 0 ? fmt(el.credit) : ''}</td>
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                </td>
                                            </tr>
                                        )}
                                    </>
                                ))}
                            </tbody>
                        </table>

                        {/* Totaux bas de tableau */}
                        <div style={{
                            display: 'flex', justifyContent: 'flex-end', gap: '32px',
                            padding: '16px 20px', borderTop: '2px solid var(--border)',
                            background: 'rgba(255,255,255,0.02)'
                        }}>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: '11px', color: 'var(--text2)', marginBottom: '2px' }}>Total Débit</div>
                                <div style={{ fontSize: '18px', fontWeight: 700, color: '#10b981' }}>{fmt(data.total_debit)}</div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: '11px', color: 'var(--text2)', marginBottom: '2px' }}>Total Crédit</div>
                                <div style={{ fontSize: '18px', fontWeight: 700, color: '#ef4444' }}>{fmt(data.total_credit)}</div>
                            </div>
                            <div style={{ textAlign: 'right' }}>
                                <div style={{ fontSize: '11px', color: 'var(--text2)', marginBottom: '2px' }}>Équilibre</div>
                                <div style={{ fontSize: '18px', fontWeight: 700, color: data.equilibre ? '#10b981' : '#ef4444' }}>
                                    {data.equilibre ? '⚖ Équilibré' : '⚠ Écart'}
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    )
}
