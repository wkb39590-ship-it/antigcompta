import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import apiService, { Immo } from '../api'
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

// ... (interfaces LigneAmort etc are now in api.ts)

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
    const [showForm, setShowForm] = useState(false)
    const [msg, setMsg] = useState('')
    const navigate = useNavigate()
    const [form, setForm] = useState({
        designation: '', categorie: 'CORPORELLE', date_acquisition: '',
        valeur_acquisition: '', tva_acquisition: '0', duree_amortissement: '5',
        methode: 'LINEAIRE', compte_actif_pcm: '2355', compte_amort_pcm: '2835', compte_dotation_pcm: '6193'
    })

    const location = useLocation()
    const [fromFacture, setFromFacture] = useState<string | null>(null)

    const load = async () => {
        setLoading(true)
        try {
            const data = await apiService.listImmobilisations()
            setImmos(data)
        } catch (err: any) {
            console.error(err)
            setMsg('❌ Erreur lors du chargement')
        } finally { setLoading(false) }
    }

    const loadDetail = (id: number) => {
        navigate(`/immobilisations/${id}`)
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
        try {
            const data = await apiService.createImmobilisation(payload)
            setMsg('✅ Immobilisation créée')
            setShowForm(false)
            load()
            navigate(`/immobilisations/${data.id}`)
        } catch (err: any) {
            setMsg('❌ ' + (err.response?.data?.detail || 'Erreur'))
        }
    }

    const genDotation = async (immoId: number, annee: number) => {
        try {
            await apiService.generateDotation(immoId, annee)
            setMsg(`✅ Dotation ${annee} générée`)
            load()
        } catch (err: any) {
            setMsg('❌ ' + (err.response?.data?.detail || 'Erreur'))
        }
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

            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '24px' }}>
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
                                        background: 'var(--card)',
                                        border: '1px solid var(--border)',
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

            </div>
        </div>
    )
}
