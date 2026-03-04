import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { API_CONFIG } from '../config/apiConfig'
import {
    Building2,
    Plus,
    X,
    CheckCircle2,
    AlertCircle,
    Link,
    FileText,
    Calculator,
    ChevronRight
} from 'lucide-react'

interface Immo {
    id: number
    designation: string
    categorie: string
    date_acquisition: string
    valeur_acquisition: number
    tva_acquisition: number
    duree_amortissement: number
    taux_amortissement: number
    methode: string
    compte_actif_pcm: string
    compte_amort_pcm: string
    compte_dotation_pcm: string
    statut: string
    plan_amortissement?: LigneAmort[]
}

interface LigneAmort {
    annee: number
    dotation_annuelle: number
    amortissement_cumule: number
    valeur_nette_comptable: number
    ecriture_generee: boolean
}

const METHODES = ['LINEAIRE', 'DEGRESSIF']
const CATEGORIES = ['CORPORELLE', 'INCORPORELLE', 'FINANCIERE']
const fmt = (n?: number) => n != null ? n.toLocaleString('fr-MA', { minimumFractionDigits: 2 }) : '—'

const CAT_COLOR: Record<string, string> = {
    CORPORELLE: '#6366f1', INCORPORELLE: '#f59e0b', FINANCIERE: '#10b981'
}

const DEFAULT_COMPTES: Record<string, any> = {
    CORPORELLE: { actif: '2355', amort: '2835', dot: '6193' },
    INCORPORELLE: { actif: '2220', amort: '2820', dot: '6192' },
    FINANCIERE: { actif: '2480', amort: '2880', dot: '6196' },
}

/** Détecte automatiquement la durée, catégorie et comptes PCM selon la désignation (règles PCM Maroc) */
function detectImmoDefaults(designation: string): { duree: string; categorie: string; actif: string; amort: string; dot: string } {
    const d = designation.toLowerCase()
    // Matériel informatique : PC, ordinateur, serveur, imprimante, laptop
    if (/ordinateur|laptop|pc |intel|dell|hp|lenovo|asus|serveur|imprimante|scanner|écran|moniteur|clavier|souris/.test(d)) {
        return { duree: '5', categorie: 'CORPORELLE', actif: '2355', amort: '2835', dot: '6193' }
    }
    // Logiciels / licences
    if (/logiciel|licence|license|software|erp|crm|abonnement/.test(d)) {
        return { duree: '3', categorie: 'INCORPORELLE', actif: '2220', amort: '2820', dot: '6192' }
    }
    // Véhicules
    if (/véhicule|vehicule|voiture|camion|camionette|moto|auto/.test(d)) {
        return { duree: '5', categorie: 'CORPORELLE', actif: '2340', amort: '2834', dot: '6193' }
    }
    // Mobilier / aménagement
    if (/mobilier|meuble|bureau|chaise|armoire|aménagement|décoration/.test(d)) {
        return { duree: '10', categorie: 'CORPORELLE', actif: '2350', amort: '2835', dot: '6193' }
    }
    // Matériel industriel / machines
    if (/machine|outillage|industriel|équipement|matériel|appareil|installation/.test(d)) {
        return { duree: '7', categorie: 'CORPORELLE', actif: '2350', amort: '2835', dot: '6193' }
    }
    // Construction / bâtiment
    if (/bâtiment|batiment|construction|immeuble|terrain|local/.test(d)) {
        return { duree: '20', categorie: 'CORPORELLE', actif: '2321', amort: '2832', dot: '6191' }
    }
    // Défaut : matériel corporel 5 ans
    return { duree: '5', categorie: 'CORPORELLE', actif: '2355', amort: '2835', dot: '6193' }
}

export default function Immobilisations() {
    const [immos, setImmos] = useState<Immo[]>([])
    const [loading, setLoading] = useState(true)
    const [selected, setSelected] = useState<Immo | null>(null)
    const [showForm, setShowForm] = useState(false)
    const [msg, setMsg] = useState('')
    const [form, setForm] = useState({
        designation: '', categorie: 'CORPORELLE', date_acquisition: '',
        valeur_acquisition: '', tva_acquisition: '0', duree_amortissement: '5',
        methode: 'LINEAIRE', compte_actif_pcm: '2355', compte_amort_pcm: '2835', compte_dotation_pcm: '6193'
    })

    const token = () => localStorage.getItem('session_token') || ''
    const location = useLocation()
    const [fromFacture, setFromFacture] = useState<string | null>(null)

    const load = async () => {
        setLoading(true)
        try {
            const r = await fetch(`${API_CONFIG.BASE_URL} /immobilisations/ ? token = ${token()} `)
            if (r.ok) setImmos(await r.json())
        } finally { setLoading(false) }
    }

    const loadDetail = async (id: number) => {
        const r = await fetch(`${API_CONFIG.BASE_URL} /immobilisations/${id}?token = ${token()} `)
        if (r.ok) setSelected(await r.json())
    }

    useEffect(() => { load() }, [])

    // Pré-remplissage depuis l'historique factures (Option B)
    useEffect(() => {
        const params = new URLSearchParams(location.search)
        const designation = params.get('designation')
        if (designation) {
            // Détection intelligente durée + comptes selon la désignation
            const defaults = detectImmoDefaults(designation)
            setForm({
                designation,
                categorie: defaults.categorie,
                date_acquisition: params.get('date_acquisition') || '',
                valeur_acquisition: params.get('valeur_acquisition') || '',
                tva_acquisition: params.get('tva_acquisition') || '0',
                duree_amortissement: defaults.duree,
                methode: 'LINEAIRE',
                compte_actif_pcm: defaults.actif,
                compte_amort_pcm: defaults.amort,
                compte_dotation_pcm: defaults.dot,
            })
            setFromFacture(params.get('facture_id'))
            setShowForm(true)
            window.history.replaceState({}, '', '/immobilisations')
        }
    }, [location.search])

    const handleCategorie = (cat: string) => {
        const c = DEFAULT_COMPTES[cat] || DEFAULT_COMPTES['CORPORELLE']
        setForm(f => ({ ...f, categorie: cat, compte_actif_pcm: c.actif, compte_amort_pcm: c.amort, compte_dotation_pcm: c.dot }))
    }

    const submit = async (e: React.FormEvent) => {
        e.preventDefault()
        const payload = {
            ...form,
            valeur_acquisition: parseFloat(form.valeur_acquisition),
            tva_acquisition: parseFloat(form.tva_acquisition),
            duree_amortissement: parseInt(form.duree_amortissement),
            facture_id: fromFacture ? parseInt(fromFacture) : null,
        }
        const r = await fetch(`${API_CONFIG.BASE_URL} /immobilisations/ ? token = ${token()} `, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        const data = await r.json()
        if (r.ok) {
            setMsg('✅ Immobilisation créée')
            setShowForm(false)
            load()
            setSelected(data)
        } else {
            setMsg('❌ ' + (data.detail || 'Erreur'))
        }
    }

    const genDotation = async (immoId: number, annee: number) => {
        const r = await fetch(`${API_CONFIG.BASE_URL} /immobilisations/${immoId} /dotation/${annee}?token = ${token()} `, { method: 'POST' })
        const data = await r.json()
        if (r.ok) { setMsg(`✅ Dotation ${annee} générée`); loadDetail(immoId) }
        else setMsg('❌ ' + (data.detail || 'Erreur'))
    }

    const currentYear = new Date().getFullYear()

    return (
        <div style={{ padding: '32px', maxWidth: '1300px', margin: '0 auto' }}>
            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '32px' }}>
                <div>
                    <h1 style={{ fontSize: '28px', fontWeight: 700, color: 'var(--text)', margin: 0, display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <Building2 size={32} color="var(--accent)" /> Immobilisations
                    </h1>
                    <p style={{ color: 'var(--text2)', margin: '4px 0 0 44px' }}>Gestion des actifs et plans d'amortissement</p>
                </div>
                <button onClick={() => setShowForm(!showForm)} style={{
                    background: showForm ? 'rgba(239,68,68,0.1)' : 'var(--accent)',
                    color: showForm ? '#ef4444' : 'white',
                    border: showForm ? '1px solid #ef4444' : 'none',
                    padding: '10px 22px', borderRadius: '10px', cursor: 'pointer', fontSize: '14px', fontWeight: 600,
                    display: 'flex', alignItems: 'center', gap: '8px'
                }}>
                    {showForm ? <><X size={18} /> Annuler</> : <><Plus size={18} /> Nouvelle immobilisation</>}
                </button>
            </div>

            {msg && (
                <div style={{
                    background: msg.startsWith('✅') ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                    border: `1px solid ${msg.startsWith('✅') ? '#10b981' : '#ef4444'} `,
                    borderRadius: '10px', padding: '12px 20px', marginBottom: '20px',
                    color: msg.startsWith('✅') ? '#10b981' : '#ef4444',
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {msg.startsWith('✅') ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                        {msg.replace(/^[✅❌]\s*/, '')}
                    </div>
                    <button onClick={() => setMsg('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}><X size={18} /></button>
                </div>
            )}

            {/* Formulaire de création */}
            {showForm && (
                <form onSubmit={submit} style={{
                    background: 'var(--card)', border: '1px solid var(--border)',
                    borderRadius: '16px', padding: '28px', marginBottom: '28px'
                }}>
                    <h3 style={{ color: 'var(--text)', margin: '0 0 20px', fontSize: '17px' }}>📋 Nouvelle immobilisation</h3>
                    {fromFacture && (
                        <div style={{
                            background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.25)',
                            borderRadius: '10px', padding: '12px 16px', marginBottom: '20px',
                            color: '#4f46e5', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '10px'
                        }}>
                            <Link size={16} />
                            <div>
                                <strong>Données pré-remplies depuis la Facture #{fromFacture}</strong>
                                <span style={{ color: 'var(--text2)', marginLeft: '8px' }}>— Vérifiez la catégorie et la durée avant de valider.</span>
                            </div>
                        </div>
                    )}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                        <div style={{ gridColumn: '1 / -1' }}>
                            <label style={{ color: 'var(--text2)', fontSize: '12px', display: 'block', marginBottom: '6px' }}>Désignation *</label>
                            <input value={form.designation} onChange={e => setForm(f => ({ ...f, designation: e.target.value }))} required
                                placeholder="ex: Ordinateur portable HP" style={{
                                    width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)',
                                    borderRadius: '8px', padding: '10px 14px', color: 'var(--text)', fontSize: '14px', boxSizing: 'border-box'
                                }} />
                        </div>
                        {[
                            { label: 'Catégorie *', field: 'categorie', type: 'select', options: CATEGORIES },
                            { label: 'Méthode *', field: 'methode', type: 'select', options: METHODES },
                            { label: 'Date acquisition *', field: 'date_acquisition', type: 'date' },
                            { label: 'Valeur HT (MAD) *', field: 'valeur_acquisition', type: 'number', placeholder: '50000' },
                            { label: 'TVA (MAD)', field: 'tva_acquisition', type: 'number', placeholder: '10000' },
                            { label: "Durée (années) *", field: 'duree_amortissement', type: 'number', placeholder: '5' },
                            { label: 'Compte actif (PCM)', field: 'compte_actif_pcm', type: 'text', placeholder: '2355' },
                            { label: "Compte amort. (PCM)", field: 'compte_amort_pcm', type: 'text', placeholder: '2835' },
                            { label: "Compte dotation (PCM)", field: 'compte_dotation_pcm', type: 'text', placeholder: '6193' },
                        ].map(({ label, field, type, options, placeholder }: any) => (
                            <div key={field}>
                                <label style={{ color: 'var(--text2)', fontSize: '12px', display: 'block', marginBottom: '6px' }}>{label}</label>
                                {type === 'select' ? (
                                    <select
                                        value={(form as any)[field]}
                                        onChange={e => field === 'categorie' ? handleCategorie(e.target.value) : setForm(f => ({ ...f, [field]: e.target.value }))}
                                        style={{
                                            width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)',
                                            borderRadius: '8px', padding: '10px 14px', color: 'var(--text)', fontSize: '14px'
                                        }}>
                                        {options.map((o: string) => <option key={o} value={o}>{o}</option>)}
                                    </select>
                                ) : (
                                    <input type={type} value={(form as any)[field]} placeholder={placeholder} required={label.includes('*')}
                                        onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))}
                                        style={{
                                            width: '100%', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--border)',
                                            borderRadius: '8px', padding: '10px 14px', color: 'var(--text)', fontSize: '14px', boxSizing: 'border-box'
                                        }} />
                                )}
                            </div>
                        ))}
                    </div>
                    <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
                        <button type="submit" style={{
                            background: 'var(--accent)', color: 'white', border: 'none',
                            padding: '11px 28px', borderRadius: '9px', cursor: 'pointer', fontSize: '14px', fontWeight: 600
                        }}>Créer & calculer plan d'amortissement</button>
                    </div>
                </form>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 500px' : '1fr', gap: '24px' }}>
                {/* Liste */}
                <div>
                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text2)' }}>⏳ Chargement...</div>
                    ) : immos.length === 0 ? (
                        <div style={{
                            background: 'var(--card)', border: '1px solid var(--border)',
                            borderRadius: '16px', padding: '60px', textAlign: 'center'
                        }}>
                            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🏗️</div>
                            <h3 style={{ color: 'var(--text)', margin: '0 0 8px' }}>Aucune immobilisation</h3>
                            <p style={{ color: 'var(--text2)', margin: 0 }}>Créez votre première immobilisation avec le bouton ci-dessus</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {immos.map(im => (
                                <div key={im.id} onClick={() => loadDetail(im.id)}
                                    style={{
                                        background: selected?.id === im.id ? 'rgba(99,102,241,0.08)' : 'var(--card)',
                                        border: `1px solid ${selected?.id === im.id ? 'var(--accent)' : 'var(--border)'} `,
                                        borderRadius: '14px', padding: '20px', cursor: 'pointer', transition: 'all 0.2s',
                                        display: 'grid', gridTemplateColumns: '1fr auto', alignItems: 'center', gap: '16px'
                                    }}>
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                                            <span style={{ fontWeight: 700, color: 'var(--text)', fontSize: '15px' }}>{im.designation}</span>
                                            <span style={{
                                                background: `${CAT_COLOR[im.categorie]} 22`, color: CAT_COLOR[im.categorie],
                                                padding: '2px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 600
                                            }}>{im.categorie}</span>
                                            <span style={{
                                                background: im.statut === 'ACTIF' ? 'rgba(16,185,129,0.15)' : 'rgba(100,116,139,0.15)',
                                                color: im.statut === 'ACTIF' ? '#10b981' : '#64748b',
                                                padding: '2px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: 600
                                            }}>{im.statut}</span>
                                        </div>
                                        <div style={{ fontSize: '12px', color: 'var(--text2)', display: 'flex', gap: '16px' }}>
                                            <span>📅 {im.date_acquisition}</span>
                                            <span>⏳ {im.duree_amortissement} ans · {im.methode}</span>
                                            <span>📋 {im.compte_actif_pcm}</span>
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#6366f1' }}>
                                            {fmt(im.valeur_acquisition)} MAD
                                        </div>
                                        <div style={{ fontSize: '11px', color: 'var(--text2)' }}>
                                            Taux: {((im.taux_amortissement || 0) * 100).toFixed(2)}%
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Panneau plan d'amortissement */}
                {selected && (
                    <div style={{
                        background: 'var(--card)', border: '1px solid var(--border)',
                        borderRadius: '16px', padding: '24px', height: 'fit-content',
                        position: 'sticky', top: '20px', maxHeight: '85vh', overflowY: 'auto'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                            <div>
                                <h3 style={{ margin: 0, color: 'var(--text)', fontSize: '16px' }}>{selected.designation}</h3>
                                <p style={{ margin: '4px 0 0', color: 'var(--text2)', fontSize: '12px' }}>
                                    {selected.categorie} · {selected.methode} · {selected.duree_amortissement} ans
                                </p>
                            </div>
                            <button onClick={() => setSelected(null)} style={{
                                background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text2)', fontSize: '18px'
                            }}>✕</button>
                        </div>

                        {/* Résumé */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' }}>
                            {[
                                { label: 'Valeur HT', value: `${fmt(selected.valeur_acquisition)} MAD` },
                                { label: 'TVA', value: `${fmt(selected.tva_acquisition)} MAD` },
                                { label: 'Durée', value: `${selected.duree_amortissement} ans` },
                                { label: 'Taux', value: `${((selected.taux_amortissement || 0) * 100).toFixed(2)}% ` },
                            ].map(({ label, value }) => (
                                <div key={label} style={{
                                    background: 'rgba(255,255,255,0.03)', borderRadius: '10px',
                                    padding: '12px', border: '1px solid var(--border)'
                                }}>
                                    <div style={{ fontSize: '11px', color: 'var(--text2)', marginBottom: '4px' }}>{label}</div>
                                    <div style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text)' }}>{value}</div>
                                </div>
                            ))}
                        </div>

                        {/* Comptes PCM */}
                        <div style={{ marginBottom: '20px', fontSize: '12px', color: 'var(--text2)', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                            {[
                                { label: 'Actif', code: selected.compte_actif_pcm },
                                { label: 'Amort.', code: selected.compte_amort_pcm },
                                { label: 'Dotation', code: selected.compte_dotation_pcm },
                            ].map(({ label, code }) => (
                                <span key={label} style={{
                                    background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.2)',
                                    padding: '3px 10px', borderRadius: '6px', color: '#818cf8', fontSize: '11px'
                                }}>
                                    {label}: <strong>{code}</strong>
                                </span>
                            ))}
                        </div>

                        {/* Plan d'amortissement */}
                        <h4 style={{ color: 'var(--text)', margin: '0 0 12px', fontSize: '14px' }}>
                            📊 Plan d'amortissement
                        </h4>
                        {selected.plan_amortissement && selected.plan_amortissement.length > 0 ? (
                            <div style={{ overflowX: 'auto' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                                    <thead>
                                        <tr style={{ borderBottom: '1px solid var(--border)' }}>
                                            {['Année', 'Dotation', 'Cumul', 'VNC', 'Action'].map(h => (
                                                <th key={h} style={{ padding: '8px 4px', textAlign: h === 'Action' ? 'center' : 'right', color: 'var(--text2)', fontWeight: 600, whiteSpace: 'nowrap' }}>
                                                    {h === 'Année' ? <span style={{ textAlign: 'left', display: 'block' }}>{h}</span> : h}
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {selected.plan_amortissement.map((l, i) => (
                                            <tr key={l.annee} style={{
                                                borderBottom: '1px solid rgba(255,255,255,0.04)',
                                                background: l.annee === currentYear ? 'rgba(99,102,241,0.06)' : 'transparent'
                                            }}>
                                                <td style={{ padding: '8px 4px', color: l.annee === currentYear ? '#818cf8' : 'var(--text)', fontWeight: l.annee === currentYear ? 700 : 400 }}>
                                                    {l.annee}{l.annee === currentYear && <span style={{ fontSize: '10px', color: '#818cf8', marginLeft: '4px' }}>◀</span>}
                                                </td>
                                                <td style={{ textAlign: 'right', padding: '8px 4px', color: '#f59e0b' }}>{fmt(l.dotation_annuelle)}</td>
                                                <td style={{ textAlign: 'right', padding: '8px 4px', color: 'var(--text2)' }}>{fmt(l.amortissement_cumule)}</td>
                                                <td style={{ textAlign: 'right', padding: '8px 4px', color: '#10b981' }}>{fmt(l.valeur_nette_comptable)}</td>
                                                <td style={{ textAlign: 'center', padding: '8px 4px' }}>
                                                    {!l.ecriture_generee ? (
                                                        <button onClick={(e) => { e.stopPropagation(); genDotation(selected.id, l.annee) }}
                                                            title="Générer écriture dotation"
                                                            style={{
                                                                background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.2)',
                                                                color: '#818cf8', borderRadius: '6px', padding: '3px 8px',
                                                                cursor: 'pointer', fontSize: '11px'
                                                            }}>⚡</button>
                                                    ) : (
                                                        <span title="Écriture générée" style={{ color: '#10b981', fontSize: '14px' }}>✅</span>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div style={{ color: 'var(--text2)', fontSize: '13px', textAlign: 'center', padding: '20px' }}>
                                Aucun plan calculé
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    )
}
