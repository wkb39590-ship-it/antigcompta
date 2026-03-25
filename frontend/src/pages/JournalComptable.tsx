import { useState, useEffect, Fragment } from 'react'
import { useLocation } from 'react-router-dom'
import apiService from '../api'
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
    ChevronDown,
    FileText,
    Plus,
    Trash,
    Edit,
    X
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

const DEFAULT_JOURNAL_ICONS: Record<string, { icon: any, color: string }> = {
    'ACH': { icon: <ShoppingCart size={16} />, color: '#f59e0b' },
    'VTE': { icon: <TrendingUp size={16} />, color: '#10b981' },
    'IMMO': { icon: <Scale size={16} />, color: '#ec4899' },
    'PAYE': { icon: <FileText size={16} />, color: '#f43f5e' },
    'OD': { icon: <FileJson size={16} />, color: '#8b5cf6' },
    'BANQUE': { icon: <Banknote size={16} />, color: '#3b82f6' },
    'BQ': { icon: <Banknote size={16} />, color: '#3b82f6' },
}

const fmt = (n?: number) => n != null ? n.toLocaleString('fr-MA', { minimumFractionDigits: 2 }) : '0,00'

export default function JournalComptable() {
    const [journals, setJournals] = useState<any[]>([])
    const [activeJournal, setActiveJournal] = useState('')
    const [data, setData] = useState<JournalResponse | null>(null)
    const [totaux, setTotaux] = useState<Totaux | null>(null)
    const [loading, setLoading] = useState(false)
    const [expanded, setExpanded] = useState<number | null>(null)
    const [annee, setAnnee] = useState(new Date().getFullYear())
    const [mois, setMois] = useState(new Date().getMonth() + 1)
    const [filterMode, setFilterMode] = useState<'tout' | 'annee' | 'mois'>('tout')

    // Modal nouveau journal
    const [showJournalModal, setShowJournalModal] = useState(false)
    const [newJournal, setNewJournal] = useState({ code: '', label: '', type: 'BANQUE' })

    // Saisie manuelle
    const [showManualForm, setShowManualForm] = useState(false)
    const [manualHeader, setManualHeader] = useState({
        entry_date: new Date().toISOString().split('T')[0],
        reference: '',
        description: 'Écriture de paie mensuelle'
    })
    const [manualLines, setManualLines] = useState<any[]>([
        { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
        { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
        { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
        { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
    ])

    const [employees, setEmployees] = useState<any[]>([])
    const [showQuickAdd, setShowQuickAdd] = useState(false)
    const [newEmp, setNewEmp] = useState({
        nom: '',
        prenom: '',
        salaire_base: 0,
        cin: '',
        poste: '',
        date_naissance: '',
        date_embauche: new Date().toISOString().split('T')[0],
        numero_cnss: '',
        nb_enfants: 0
    })

    const [editingId, setEditingId] = useState<number | null>(null)

    const handleEdit = (entry: any) => {
        setEditingId(entry.id)
        setManualHeader({
            entry_date: entry.entry_date,
            reference: entry.reference || '',
            description: entry.description || ''
        })
        setManualLines(entry.entry_lines.map((l: any) => ({
            account_code: l.account_code,
            account_label: l.account_label,
            debit: l.debit,
            credit: l.credit,
            tiers_name: l.tiers_name || ''
        })))
        setShowManualForm(true)
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    const handleDelete = async (id: number) => {
        if (!window.confirm("Supprimer cette écriture ?")) return
        try {
            const r = await fetch(`${API_CONFIG.BASE_URL}/journaux/${id}?token=${token()}`, { method: 'DELETE' })
            if (!r.ok) throw new Error("Erreur suppression")
            load(); loadTotaux()
        } catch (e) {
            alert("Erreur lors de la suppression")
        }
    }

    const loadEmployees = async () => {
        try {
            const data = await apiService.listEmployes()
            setEmployees(data)
        } catch (e) {
            console.error("Erreur chargement employés", e)
        }
    }

    useEffect(() => {
        loadEmployees()
    }, [])

    const handleQuickAdd = async () => {
        if (!newEmp.nom || !newEmp.prenom) return
        try {
            const payload: any = {
                ...newEmp,
                statut: 'ACTIF'
            }
            if (!payload.date_naissance) delete payload.date_naissance

            await apiService.createEmploye(payload)
            setShowQuickAdd(false)
            setNewEmp({
                nom: '',
                prenom: '',
                salaire_base: 0,
                cin: '',
                poste: '',
                date_naissance: '',
                date_embauche: new Date().toISOString().split('T')[0],
                numero_cnss: '',
                nb_enfants: 0
            })
            loadEmployees()
        } catch (e) {
            alert("Erreur lors de l'ajout rapide")
        }
    }

    const location = useLocation()

    useEffect(() => {
        const params = new URLSearchParams(location.search)
        if (params.get('showForm') === 'true') {
            setShowManualForm(true)
            if (params.get('ref')) {
                setManualHeader(h => ({ ...h, reference: params.get('ref') || '' }))
            }
        }
    }, [location.search])

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

    const fetchJournals = async () => {
        try {
            const data = await apiService.getJournalsConfig()
            if (data && data.length > 0) {
                setJournals(data)
            }
        } catch (err) {
            console.error("Erreur lors de la récupération des journaux:", err)
        }
    }

    useEffect(() => {
        fetchJournals()
    }, [])

    useEffect(() => { load(); loadTotaux() }, [activeJournal, annee, mois, filterMode])

    const handleCreateJournal = async () => {
        if (!newJournal.code || !newJournal.label) return
        try {
            await apiService.createJournalConfig(newJournal)
            setNewJournal({ code: '', label: '', type: 'BANQUE' })
            setShowJournalModal(false)
            fetchJournals()
        } catch (err) {
            alert("Erreur lors de la création du journal. Le code existe peut-être déjà.")
        }
    }

    const exportCSV = () => {
        const params = buildParams()
        window.open(`${API_CONFIG.BASE_URL}/journaux/export?${params}`, '_blank')
    }

    const handleSaveManual = async () => {
        const totalDebit = manualLines.reduce((sum, l) => sum + (parseFloat(l.debit) || 0), 0)
        const totalCredit = manualLines.reduce((sum, l) => sum + (parseFloat(l.credit) || 0), 0)

        if (Math.abs(totalDebit - totalCredit) > 0.01) {
            alert(`L'écriture n'est pas équilibrée ! Différence : ${Math.abs(totalDebit - totalCredit).toFixed(2)} MAD`)
            return
        }

        setLoading(true)
        const url = editingId
            ? `${API_CONFIG.BASE_URL}/journaux/${editingId}?token=${token()}`
            : `${API_CONFIG.BASE_URL}/journaux/manual?token=${token()}`;

        try {
            const r = await fetch(url, {
                method: editingId ? 'PUT' : 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    journal_code: activeJournal || 'PAYE',
                    ...manualHeader,
                    lines: manualLines.filter(l => l.account_code || l.debit > 0 || l.credit > 0)
                })
            })
            if (r.ok) {
                setShowManualForm(false)
                setEditingId(null)
                setManualHeader({ entry_date: new Date().toISOString().split('T')[0], reference: '', description: 'Écriture de paie mensuelle' })
                setManualLines([
                    { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
                    { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
                    { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
                    { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
                ])
                load(); loadTotaux()
            } else {
                const err = await r.json()
                alert(`Erreur: ${err.detail || 'Inconnue'}`)
            }
        } catch (e) {
            alert("Erreur réseau")
        } finally {
            setLoading(false)
        }
    }

    const handleCancelManual = () => {
        setShowManualForm(false)
        setEditingId(null)
        setManualHeader({ entry_date: new Date().toISOString().split('T')[0], reference: '', description: 'Écriture de paie mensuelle' })
        setManualLines([
            { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
            { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
            { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
            { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' },
        ])
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
                        const journal = journals.find((j) => j.code === t.journal_code)
                        const iconData = DEFAULT_JOURNAL_ICONS[t.journal_code] || (journal ? DEFAULT_JOURNAL_ICONS[journal.type] : null) || { icon: <Layers size={14} />, color: '#64748b' }
                        
                        return (
                            <div key={t.journal_code} onClick={() => setActiveJournal(t.journal_code)}
                                style={{
                                    background: activeJournal === t.journal_code ? `${iconData.color}18` : 'var(--card)',
                                    border: `1px solid ${activeJournal === t.journal_code ? iconData.color : 'var(--border)'}`,
                                    borderRadius: '14px', padding: '16px', cursor: 'pointer', transition: 'all 0.2s'
                                }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                    <span style={{ fontWeight: 700, color: iconData.color, fontSize: '13px' }}>{journal?.label || t.journal_code}</span>
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
                <button onClick={() => setActiveJournal('')} style={{
                    background: activeJournal === '' ? 'var(--accent)' : 'transparent',
                    color: activeJournal === '' ? 'white' : 'var(--text2)',
                    border: `1px solid ${activeJournal === '' ? 'var(--accent)' : 'transparent'}`,
                    padding: '7px 18px', borderRadius: '8px', cursor: 'pointer', fontSize: '13px', fontWeight: 600,
                    transition: 'all 0.15s', display: 'flex', alignItems: 'center', gap: '8px'
                }}><Layers size={16} />Tous</button>

                {journals.map(j => {
                    const iconData = DEFAULT_JOURNAL_ICONS[j.code] || DEFAULT_JOURNAL_ICONS[j.type] || { icon: <FileText size={16} />, color: '#64748b' }
                    return (
                        <button key={j.id} onClick={() => setActiveJournal(j.code)} style={{
                            background: activeJournal === j.code ? iconData.color : 'transparent',
                            color: activeJournal === j.code ? 'white' : 'var(--text2)',
                            border: `1px solid ${activeJournal === j.code ? iconData.color : 'transparent'}`,
                            padding: '7px 18px', borderRadius: '8px', cursor: 'pointer', fontSize: '13px', fontWeight: 600,
                            transition: 'all 0.15s', display: 'flex', alignItems: 'center', gap: '8px'
                        }}>{iconData.icon}{j.label}</button>
                    )
                })}

                <button
                    onClick={() => setShowJournalModal(true)}
                    style={{
                        background: 'transparent', color: 'var(--text3)', border: '1px dashed var(--border)',
                        padding: '7px 14px', borderRadius: '8px', cursor: 'pointer', fontSize: '12px',
                        display: 'flex', alignItems: 'center', gap: '6px', marginLeft: 'auto'
                    }}
                >
                    <Plus size={14} /> Nouveau Journal
                </button>
            </div>

            {/* Formulaire Saisie Manuelle (Optionnel) */}
            {activeJournal === 'PAYE' && (
                <div style={{ marginBottom: '24px' }}>
                    {!showManualForm ? (
                        <button onClick={() => setShowManualForm(true)} style={{
                            display: 'flex', alignItems: 'center', gap: '10px', padding: '12px 24px',
                            background: 'var(--accent)', color: 'white', border: 'none', borderRadius: '10px',
                            fontWeight: 600, cursor: 'pointer', boxShadow: '0 4px 6px -1px var(--accent-light)'
                        }}>
                            <Plus size={18} /> Nouvelle Écriture de Paie
                        </button>
                    ) : (
                        <div style={{ background: 'var(--card)', border: '1px solid var(--accent)', borderRadius: '16px', padding: '24px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                                <h2 style={{ margin: 0, fontSize: '18px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <div style={{ width: '8px', height: '24px', background: 'var(--accent)', borderRadius: '4px' }}></div>
                                    {editingId ? 'Modification de l\'écriture' : 'Saisie Nouvelle Écriture de Paie'}
                                </h2>
                                <button onClick={handleCancelManual} style={{ background: 'none', border: 'none', color: 'var(--text3)', cursor: 'pointer' }}>
                                    <X size={20} />
                                </button>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 2fr', gap: '16px', marginBottom: '24px' }}>
                                <div>
                                    <label style={{ display: 'block', fontSize: '12px', color: 'var(--text3)', marginBottom: '6px' }}>Date d'écriture</label>
                                    <input type="date" value={manualHeader.entry_date} onChange={e => setManualHeader({...manualHeader, entry_date: e.target.value})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '12px', color: 'var(--text3)', marginBottom: '6px' }}>Référence</label>
                                    <input type="text" placeholder="ex: PAIE/03-24" value={manualHeader.reference} onChange={e => setManualHeader({...manualHeader, reference: e.target.value})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                                <div>
                                    <label style={{ display: 'block', fontSize: '12px', color: 'var(--text3)', marginBottom: '6px' }}>Libellé de l'écriture</label>
                                    <input type="text" placeholder="Description globale..." value={manualHeader.description} onChange={e => setManualHeader({...manualHeader, description: e.target.value})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                            </div>

                            <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '20px' }}>
                                <thead>
                                    <tr style={{ background: 'var(--bg)', textAlign: 'left' }}>
                                        <th style={{ padding: '12px', fontSize: '12px', color: 'var(--text3)' }}>Compte</th>
                                        <th style={{ padding: '12px', fontSize: '12px', color: 'var(--text3)' }}>Libellé ligne</th>
                                        <th style={{ padding: '12px', fontSize: '12px', color: 'var(--text3)' }}>Salarié / Tiers</th>
                                        <th style={{ padding: '12px', fontSize: '12px', color: 'var(--text3)', textAlign: 'right', width: '130px' }}>Débit</th>
                                        <th style={{ padding: '12px', fontSize: '12px', color: 'var(--text3)', textAlign: 'right', width: '130px' }}>Crédit</th>
                                        <th style={{ width: '50px' }}></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {manualLines.map((line, idx) => (
                                        <tr key={idx} style={{ borderBottom: '1px solid var(--border)' }}>
                                            <td style={{ padding: '8px' }}>
                                                <input type="text" placeholder="6171" value={line.account_code} onChange={e => {
                                                    const nl = [...manualLines]; nl[idx].account_code = e.target.value; setManualLines(nl)
                                                }} style={{ width: '80px', padding: '8px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg)' }} />
                                            </td>
                                            <td style={{ padding: '8px' }}>
                                                <input type="text" placeholder="..." value={line.account_label} onChange={e => {
                                                    const nl = [...manualLines]; nl[idx].account_label = e.target.value; setManualLines(nl)
                                                }} style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg)' }} />
                                            </td>
                                            <td style={{ padding: '8px' }}>
                                                <select value={line.tiers_name} onChange={e => {
                                                    const val = e.target.value;
                                                    if (val === 'NEW') {
                                                        setShowQuickAdd(true)
                                                    } else {
                                                        const nl = [...manualLines];
                                                        nl[idx].tiers_name = val;
                                                        // Si c'est la première ligne, on propage aux autres
                                                        if (idx === 0) {
                                                            nl.forEach((l, i) => { if (i > 0) l.tiers_name = val; });
                                                        }
                                                        setManualLines(nl)
                                                    }
                                                }} style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }}>
                                                    <option value="">(Aucun)</option>
                                                    {employees.map(emp => (
                                                        <option key={emp.id} value={`${emp.nom} ${emp.prenom}`}>{emp.nom} {emp.prenom}</option>
                                                    ))}
                                                    <option value="NEW" style={{ color: 'var(--accent)', fontWeight: 'bold' }}>+ Nouveau Salarié...</option>
                                                </select>
                                            </td>
                                            <td style={{ padding: '8px' }}>
                                                <input type="number" step="0.01" value={line.debit} onChange={e => {
                                                    const nl = [...manualLines]; nl[idx].debit = e.target.value; setManualLines(nl)
                                                }} style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg)', textAlign: 'right' }} />
                                            </td>
                                            <td style={{ padding: '8px' }}>
                                                <input type="number" step="0.01" value={line.credit} onChange={e => {
                                                    const nl = [...manualLines]; nl[idx].credit = e.target.value; setManualLines(nl)
                                                }} style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg)', textAlign: 'right' }} />
                                            </td>
                                            <td style={{ textAlign: 'center' }}>
                                                <button onClick={() => setManualLines(manualLines.filter((_, i) => i !== idx))} style={{ color: '#ef4444', border: 'none', background: 'none', cursor: 'pointer' }}><Trash size={16} /></button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <button onClick={() => setManualLines([...manualLines, { account_code: '', account_label: '', debit: 0, credit: 0, tiers_name: '' }])}
                                    style={{ padding: '8px 16px', background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: '8px', fontSize: '13px', cursor: 'pointer' }}>
                                    + Ajouter une ligne
                                </button>

                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ display: 'flex', gap: '30px', marginBottom: '16px', fontSize: '14px', fontWeight: 600 }}>
                                        <div>Débit: <span style={{ color: 'var(--text)' }}>{fmt(manualLines.reduce((s, l) => s+parseFloat(l.debit||0), 0))}</span></div>
                                        <div>Crédit: <span style={{ color: 'var(--text)' }}>{fmt(manualLines.reduce((s, l) => s+parseFloat(l.credit||0), 0))}</span></div>
                                        <div style={{ color: Math.abs(manualLines.reduce((s,l) => s+parseFloat(l.debit||0),0) - manualLines.reduce((s,l) => s+parseFloat(l.credit||0),0)) < 0.01 ? '#10b981' : '#ef4444' }}>
                                            Écart: {fmt(Math.abs(manualLines.reduce((s,l) => s+parseFloat(l.debit||0),0) - manualLines.reduce((s,l) => s+parseFloat(l.credit||0),0)))}
                                        </div>
                                    </div>
                                    <button onClick={handleSaveManual} disabled={loading} style={{
                                        padding: '12px 30px', background: 'var(--accent)', color: 'white', border: 'none', borderRadius: '10px', fontWeight: 700, cursor: 'pointer'
                                    }}>
                                        {loading ? '⏳...' : 'Enregistrer l\'écriture'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Modal Ajout Rapide Employé */}
            {showQuickAdd && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
                }}>
                    <div style={{ background: 'var(--card)', padding: '30px', borderRadius: '16px', width: '500px', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)' }}>
                        <h3 style={{ marginTop: 0, marginBottom: '20px' }}>Nouveau Salarié (Complet)</h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                <div>
                                    <label style={{ fontSize: '11px', color: 'var(--text3)' }}>Prénom *</label>
                                    <input placeholder="Prénom" value={newEmp.prenom} onChange={e => setNewEmp({...newEmp, prenom: e.target.value})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                                <div>
                                    <label style={{ fontSize: '11px', color: 'var(--text3)' }}>Nom *</label>
                                    <input placeholder="Nom" value={newEmp.nom} onChange={e => setNewEmp({...newEmp, nom: e.target.value})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                <div>
                                    <label style={{ fontSize: '11px', color: 'var(--text3)' }}>CIN</label>
                                    <input placeholder="CIN" value={newEmp.cin} onChange={e => setNewEmp({...newEmp, cin: e.target.value})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                                <div>
                                    <label style={{ fontSize: '11px', color: 'var(--text3)' }}>Poste</label>
                                    <input placeholder="Poste" value={newEmp.poste} onChange={e => setNewEmp({...newEmp, poste: e.target.value})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                <div>
                                    <label style={{ fontSize: '11px', color: 'var(--text3)' }}>CNSS (8 chiffres)</label>
                                    <input placeholder="12345678" value={newEmp.numero_cnss} onChange={e => setNewEmp({...newEmp, numero_cnss: e.target.value})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                                <div>
                                    <label style={{ fontSize: '11px', color: 'var(--text3)' }}>Salaire Base *</label>
                                    <input type="number" placeholder="MAD" value={newEmp.salaire_base || ''} onChange={e => setNewEmp({...newEmp, salaire_base: parseFloat(e.target.value) || 0})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                            </div>
                            
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                <div>
                                    <label style={{ fontSize: '11px', color: 'var(--text3)' }}>Date de naissance</label>
                                    <input type="date" value={newEmp.date_naissance || ''} onChange={e => setNewEmp({...newEmp, date_naissance: e.target.value})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                                <div>
                                    <label style={{ fontSize: '11px', color: 'var(--text3)' }}>Date d'embauche *</label>
                                    <input type="date" value={newEmp.date_embauche || ''} onChange={e => setNewEmp({...newEmp, date_embauche: e.target.value})}
                                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)' }} />
                                </div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                            <button onClick={() => setShowQuickAdd(false)} className="btn btn-ghost">Annuler</button>
                            <button onClick={handleQuickAdd} className="btn btn-primary">Enregistrer</button>
                        </div>
                    </div>
                </div>
            )}

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
                                    <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text2)', fontWeight: 600, fontSize: '12px', whiteSpace: 'nowrap' }}>Date / Journal</th>
                                    <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text2)', fontWeight: 600, fontSize: '12px', whiteSpace: 'nowrap' }}>N° Pièce</th>
                                    <th style={{ padding: '12px 16px', textAlign: 'left', color: 'var(--text2)', fontWeight: 600, fontSize: '12px', whiteSpace: 'nowrap' }}>Libellé</th>
                                    <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--text2)', fontWeight: 600, fontSize: '12px', whiteSpace: 'nowrap' }}>Débit</th>
                                    <th style={{ padding: '12px 16px', textAlign: 'right', color: 'var(--text2)', fontWeight: 600, fontSize: '12px', whiteSpace: 'nowrap' }}>Crédit</th>
                                    <th style={{ padding: '12px 16px', textAlign: 'center', width: '100px', color: 'var(--text2)', fontWeight: 600, fontSize: '12px', whiteSpace: 'nowrap' }}>État</th>
                                    <th style={{ padding: '12px 16px', textAlign: 'center', width: '80px', color: 'var(--text2)', fontWeight: 600, fontSize: '12px', whiteSpace: 'nowrap' }}>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.ecritures.map((e) => (
                                    <Fragment key={e.id}>
                                        <tr 
                                            onClick={() => setExpanded(expanded === e.id ? null : e.id)}
                                            style={{ borderTop: '1px solid var(--border)', transition: 'background 0.2s', cursor: 'pointer', background: expanded === e.id ? 'rgba(99,102,241,0.05)' : 'transparent' }} 
                                            className="journal-row">
                                            <td style={{ padding: '16px' }}>
                                                <div style={{ fontWeight: 600 }}>{e.entry_date}</div>
                                                <div style={{ fontSize: '11px', color: 'var(--text3)' }}>{e.journal_code}</div>
                                            </td>
                                            <td style={{ padding: '16px' }}>
                                                <div style={{ fontWeight: 600, color: 'var(--accent)' }}>{e.reference || '-'}</div>
                                            </td>
                                            <td style={{ padding: '16px' }}>
                                                <div style={{ fontWeight: 500 }}>{e.description}</div>
                                            </td>
                                            <td style={{ padding: '16px', textAlign: 'right', fontWeight: 700, color: '#10b981' }}>
                                                {fmt(e.total_debit)}
                                            </td>
                                            <td style={{ padding: '16px', textAlign: 'right', fontWeight: 700, color: '#ef4444' }}>
                                                {fmt(e.total_credit)}
                                            </td>
                                            <td style={{ padding: '16px', textAlign: 'center' }}>
                                                <span style={{ 
                                                    padding: '4px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 600,
                                                    background: e.is_validated ? 'rgba(16, 185, 129, 0.1)' : 'rgba(245, 158, 11, 0.1)',
                                                    color: e.is_validated ? '#10b981' : '#f59e0b',
                                                    border: `1px solid ${e.is_validated ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)'}`
                                                }}>
                                                    {e.is_validated ? 'Validé' : 'Brouillon'}
                                                </span>
                                            </td>
                                            <td style={{ padding: '16px', textAlign: 'center' }}>
                                                <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }} onClick={ev => ev.stopPropagation()}>
                                                    <button onClick={() => handleEdit(e)} title="Modifier" style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', padding: '4px' }}>
                                                        <Edit size={16} />
                                                    </button>
                                                    <button onClick={() => handleDelete(e.id)} title="Supprimer" style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '4px' }}>
                                                        <Trash size={16} />
                                                    </button>
                                                    {e.journal_code === 'PAYE' && (
                                                        <button
                                                            title="Télécharger bulletin PDF"
                                                            style={{ background: 'none', border: 'none', color: '#10b981', cursor: 'pointer', padding: '4px' }}
                                                            onClick={async () => {
                                                                try {
                                                                    const filename = `Bulletin_Paie_${e.reference?.replace(/\//g, '-') || `Entry_${e.id}`}.pdf`
                                                                    // Si c'est un bulletin auto-généré (PAIE-X-...), on l'indique,
                                                                    // mais dans tous les cas on passe par le nouvel endpoint qui lit les lignes.
                                                                    await apiService.downloadBulletinFromEntry(e.id, filename)
                                                                } catch {
                                                                    alert('Erreur lors du téléchargement du PDF')
                                                                }
                                                            }}
                                                        >
                                                            <Download size={16} />
                                                        </button>
                                                    )}
                                                </div>
                                            </td>
                                            <td style={{ padding: '16px', color: 'var(--text2)', textAlign: 'center' }}>
                                                {expanded === e.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                            </td>
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
                                    </Fragment>
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

            {/* Modal Nouveau Journal */}
            {showJournalModal && (
                <div style={{
                    position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                    background: 'rgba(15, 23, 42, 0.6)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    zIndex: 1000, backdropFilter: 'blur(10px)'
                }}>
                    <div style={{
                        background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '20px',
                        padding: '32px', width: '450px', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                            <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>Nouveau Journal de Banque</h3>
                            <button onClick={() => setShowJournalModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text3)', cursor: 'pointer' }}>
                                <X size={20} />
                            </button>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            <div>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, color: '#1e293b', marginBottom: '8px' }}>Code (ex: BQ2, BQ_BMCE)</label>
                                <input
                                    type="text"
                                    value={newJournal.code}
                                    onChange={e => setNewJournal({ ...newJournal, code: e.target.value.toUpperCase(), type: 'BANQUE' })}
                                    style={{
                                        width: '100%', padding: '12px', borderRadius: '10px', border: '2px solid #e2e8f0',
                                        background: 'white', color: '#1e293b', fontSize: '14px'
                                    }}
                                    placeholder="BQ2"
                                />
                            </div>
                            <div>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: 600, color: '#1e293b', marginBottom: '8px' }}>Libellé (ex: Banque Populaire)</label>
                                <input
                                    type="text"
                                    value={newJournal.label}
                                    onChange={e => setNewJournal({ ...newJournal, label: e.target.value })}
                                    style={{
                                        width: '100%', padding: '12px', borderRadius: '10px', border: '2px solid #e2e8f0',
                                        background: 'white', color: '#1e293b', fontSize: '14px'
                                    }}
                                    placeholder="Banque Populaire"
                                />
                            </div>
                            {/* Le type est forcé sur BANQUE par défaut */}

                            <button
                                onClick={handleCreateJournal}
                                style={{
                                    marginTop: '8px', padding: '12px', borderRadius: '10px', background: 'var(--accent)',
                                    color: 'white', fontWeight: 600, border: 'none', cursor: 'pointer'
                                }}
                            >
                                Créer le journal
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
