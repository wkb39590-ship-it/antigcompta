import React, { useState, useEffect, useRef } from 'react'
import apiService, { DocumentTransmis, UtilisateurClient } from '../api'
import {
    UploadCloud, CheckCircle2, Clock, LogOut, Lock, User, File, Trash2,
    Building, X, FileText, History, AlertTriangle, ArrowRight, Mail,
    KeyRound, Save, Eye, EyeOff, ChevronRight, LayoutDashboard, Settings
} from 'lucide-react'

const fmtDate = (d: string) => new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
const fmtDateShort = (d: string) => new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' })

type Tab = 'documents' | 'profil' | 'historique'

export default function ClientPortal() {
    const [token, setToken] = useState<string | null>(localStorage.getItem('client_token'))
    const [societeNom, setSocieteNom] = useState<string>(localStorage.getItem('client_societe_nom') || '')
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [loginError, setLoginError] = useState<string | null>(null)
    const [showContactModal, setShowContactModal] = useState(false)
    const [activeTab, setActiveTab] = useState<Tab>('documents')

    // Access Request Form State
    const [requestForm, setRequestForm] = useState({ nom_complet: '', entreprise: '', email: '', telephone: '', message: '' })
    const [requestSubmitting, setRequestSubmitting] = useState(false)
    const [requestSuccess, setRequestSuccess] = useState(false)

    // Portal state
    const [docs, setDocs] = useState<DocumentTransmis[]>([])
    const [uploading, setUploading] = useState(false)
    const [dragActive, setDragActive] = useState(false)
    const [uploadMsg, setUploadMsg] = useState('')
    const [docType, setDocType] = useState('FACTURE_ACHAT')
    const [notes, setNotes] = useState('')
    const fileInputRef = useRef<HTMLInputElement>(null)

    // Profile state
    const [profile, setProfile] = useState<any>(null)
    const [profileForm, setProfileForm] = useState({ nom: '', prenom: '', email: '' })
    const [profileSaving, setProfileSaving] = useState(false)
    const [profileMsg, setProfileMsg] = useState('')

    // Password state
    const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', confirm: '' })
    const [pwSaving, setPwSaving] = useState(false)
    const [pwMsg, setPwMsg] = useState('')
    const [showOld, setShowOld] = useState(false)
    const [showNew, setShowNew] = useState(false)

    useEffect(() => {
        if (token) {
            loadHistory()
            loadProfile()
        }
    }, [token])

    const loadProfile = async () => {
        try {
            const data = await apiService.clientGetProfile()
            setProfile(data)
            setProfileForm({ nom: data.nom || '', prenom: data.prenom || '', email: data.email || '' })
        } catch (err) { console.error(err) }
    }

    const loadHistory = async () => {
        try {
            const data = await apiService.clientGetHistorique()
            setDocs(data)
        } catch (err) { console.error(err) }
    }

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setLoginError('')
        try {
            const data = await apiService.clientLogin({ username, password })
            localStorage.setItem('client_token', data.access_token)
            localStorage.setItem('client_societe_nom', data.societe_nom)
            setToken(data.access_token)
            setSocieteNom(data.societe_nom)
        } catch (err: any) {
            setLoginError('Identifiants invalides ou compte inactif.')
        } finally {
            setLoading(false)
        }
    }

    const handleRequestAccess = async (e: React.FormEvent) => {
        e.preventDefault()
        setRequestSubmitting(true)
        try {
            const queryParams = new URLSearchParams(window.location.search)
            const cabinetIdParam = queryParams.get('cabinet')
            const cabinetId = cabinetIdParam ? parseInt(cabinetIdParam) : null
            await apiService.createDemandeAcces({ ...requestForm, cabinet_id: cabinetId })
            setRequestSuccess(true)
        } catch (err: any) {
            console.error(err)
            alert("Erreur lors de l'envoi de la demande.")
        } finally {
            setRequestSubmitting(false)
        }
    }

    const logout = () => {
        localStorage.removeItem('client_token')
        localStorage.removeItem('client_societe_nom')
        setToken(null)
    }

    const handleDelete = async (id: number) => {
        if (!window.confirm("Supprimer définitivement ce document ?")) return
        try {
            await apiService.clientDeleteTransmissionDoc(id)
            loadHistory()
        } catch (err: any) {
            alert("Erreur: " + (err.response?.data?.detail || err.message))
        }
    }

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault(); e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
        else if (e.type === 'dragleave') setDragActive(false)
    }

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault(); e.stopPropagation()
        setDragActive(false)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) await uploadFile(e.dataTransfer.files[0])
    }

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) await uploadFile(e.target.files[0])
    }

    const uploadFile = async (file: File) => {
        setUploading(true); setUploadMsg('')
        try {
            if (file.size > 10 * 1024 * 1024) throw new Error('Le fichier est trop grand (max 10MB)')
            await apiService.clientUploadDocument(file, docType, notes)
            setUploadMsg('✅ Document envoyé avec succès !')
            setNotes('')
            loadHistory()
        } catch (err: any) {
            setUploadMsg(`❌ Erreur: ${err.message || 'Impossible d\'envoyer le document'}`)
        } finally {
            setUploading(false)
            if (fileInputRef.current) fileInputRef.current.value = ''
        }
    }

    const handleSaveProfile = async () => {
        setProfileSaving(true); setProfileMsg('')
        try {
            await apiService.clientUpdateProfile(profileForm)
            setProfileMsg('✅ Profil mis à jour avec succès !')
            loadProfile()
        } catch (err: any) {
            setProfileMsg('❌ ' + (err.response?.data?.detail || 'Erreur'))
        } finally {
            setProfileSaving(false)
        }
    }

    const handleChangePassword = async () => {
        if (pwForm.new_password !== pwForm.confirm) {
            setPwMsg('❌ Les mots de passe ne correspondent pas.')
            return
        }
        setPwSaving(true); setPwMsg('')
        try {
            await apiService.clientChangePassword({ old_password: pwForm.old_password, new_password: pwForm.new_password })
            setPwMsg('✅ Mot de passe changé avec succès !')
            setPwForm({ old_password: '', new_password: '', confirm: '' })
        } catch (err: any) {
            setPwMsg('❌ ' + (err.response?.data?.detail || 'Erreur'))
        } finally {
            setPwSaving(false)
        }
    }

    const S = {
        // Base colors
        accent: '#4f46e5',
        accentLight: '#e0e7ff',
        success: '#16a34a',
        successLight: '#dcfce7',
        danger: '#dc2626',
        dangerLight: '#fee2e2',
        warning: '#b45309',
        warningLight: '#fef3c7',
        text: '#0f172a',
        text2: '#334155',
        text3: '#64748b',
        border: '#e2e8f0',
        bg: '#f8fafc',
        card: '#ffffff',
    }

    // ── LOGIN PAGE ───────────────────────────────────────────────────────
    if (!token) {
        return (
            <div style={{ minHeight: '100vh', display: 'flex', background: '#ffffff', fontFamily: "'Inter', sans-serif" }}>
                <div style={{ flex: '1.2', background: 'linear-gradient(rgba(30, 27, 75, 0.85), rgba(30, 27, 75, 0.85)), url("/src/assets/client-login-side.png")', backgroundSize: 'cover', backgroundPosition: 'center', padding: '80px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', color: 'white' }}>
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '60px' }}>
                            <div style={{ width: '48px', height: '48px', background: 'white', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4338ca' }}><Building size={24} /></div>
                            <span style={{ fontSize: '24px', fontWeight: 800 }}>Comptafacile</span>
                        </div>
                        <div style={{ maxWidth: '420px' }}>
                            <h1 style={{ fontSize: '48px', fontWeight: 800, lineHeight: '1.1', marginBottom: '32px', letterSpacing: '-1.5px' }}>Simplifiez la gestion de vos factures.</h1>
                            <p style={{ fontSize: '18px', color: 'rgba(255,255,255,0.7)', lineHeight: '1.6', marginBottom: '48px' }}>Transmettez vos documents en un clic et suivez l'état de votre comptabilité en temps réel.</p>
                        </div>
                    </div>
                    <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.4)' }}>© 2026 Comptafacile</div>
                </div>

                <div style={{ flex: '1', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '60px', background: '#ffffff' }}>
                    <div style={{ width: '100%', maxWidth: '380px' }}>
                        <div style={{ marginBottom: '48px' }}>
                            <h2 style={{ fontSize: '32px', fontWeight: 800, color: S.text, marginBottom: '12px' }}>Bienvenue</h2>
                            <p style={{ color: S.text3, fontSize: '15px' }}>Connectez-vous à votre espace entreprise</p>
                        </div>

                        {loginError && (
                            <div style={{ background: S.dangerLight, border: `1px solid #fecaca`, color: S.danger, padding: '14px 16px', borderRadius: '12px', fontSize: '14px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px', fontWeight: 500 }}>
                                <AlertTriangle size={18} /><span>{loginError}</span>
                            </div>
                        )}

                        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            {[
                                { label: "Nom d'utilisateur", icon: <User size={18} color="#94a3b8" />, value: username, onChange: (v: string) => setUsername(v), placeholder: 'Identifiant', type: 'text' },
                                { label: 'Mot de passe', icon: <Lock size={18} color="#94a3b8" />, value: password, onChange: (v: string) => setPassword(v), placeholder: '••••••••', type: 'password' }
                            ].map((f, i) => (
                                <div key={i}>
                                    <label style={{ display: 'block', color: S.text2, fontSize: '13px', fontWeight: 600, marginBottom: '8px' }}>{f.label}</label>
                                    <div style={{ position: 'relative' }}>
                                        <span style={{ position: 'absolute', top: '50%', left: '16px', transform: 'translateY(-50%)' }}>{f.icon}</span>
                                        <input type={f.type} value={f.value} onChange={e => f.onChange(e.target.value)} required placeholder={f.placeholder}
                                            style={{ width: '100%', padding: '16px 16px 16px 48px', background: S.bg, border: `1px solid ${S.border}`, borderRadius: '14px', color: S.text, outline: 'none', boxSizing: 'border-box', fontSize: '15px', transition: 'all 0.2s' }}
                                            onFocus={e => { e.currentTarget.style.borderColor = S.accent; e.currentTarget.style.boxShadow = `0 0 0 4px rgba(79,70,229,0.1)` }}
                                            onBlur={e => { e.currentTarget.style.borderColor = S.border; e.currentTarget.style.boxShadow = 'none' }}
                                        />
                                    </div>
                                </div>
                            ))}
                            <button type="submit" disabled={loading} style={{ background: S.accent, color: 'white', padding: '18px', borderRadius: '14px', border: 'none', fontWeight: 700, fontSize: '16px', cursor: loading ? 'not-allowed' : 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '12px', opacity: loading ? 0.7 : 1, boxShadow: '0 4px 12px rgba(79,70,229,0.25)' }}>
                                {loading ? <div className="spinner-pro-v2" /> : <>Se connecter <ArrowRight size={18} /></>}
                            </button>
                        </form>

                        <div style={{ marginTop: '40px', textAlign: 'center' }}>
                            <p style={{ fontSize: '14px', color: S.text3 }}>
                                Pas encore de compte ?{' '}
                                <button onClick={() => setShowContactModal(true)} style={{ background: 'none', border: 'none', color: S.accent, fontWeight: 600, cursor: 'pointer', padding: 0, textDecoration: 'underline', fontFamily: 'inherit' }}>
                                    Contactez votre cabinet
                                </button>
                            </p>
                        </div>
                    </div>
                </div>

                {/* Contact Modal */}
                {showContactModal && (
                    <div style={{ position: 'fixed', inset: 0, background: 'rgba(15,23,42,0.4)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
                        <div style={{ background: 'white', padding: '40px', borderRadius: '28px', width: '100%', maxWidth: '480px', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.15)', maxHeight: '90vh', overflowY: 'auto', animation: 'modalFadeIn 0.3s ease-out' }}>
                            {!requestSuccess ? (
                                <>
                                    <div style={{ textAlign: 'center', marginBottom: '28px' }}>
                                        <div style={{ width: '52px', height: '52px', background: S.accentLight, borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 14px', color: S.accent }}><Building size={26} /></div>
                                        <h3 style={{ fontSize: '22px', fontWeight: 800, color: S.text, margin: '0 0 8px' }}>Demande d'accès</h3>
                                        <p style={{ color: S.text3, fontSize: '14px' }}>Votre cabinet créera votre compte après réception.</p>
                                    </div>
                                    <form onSubmit={handleRequestAccess} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                            <div><label style={labelS}>Nom et Prénom *</label><input required value={requestForm.nom_complet} onChange={e => setRequestForm({ ...requestForm, nom_complet: e.target.value })} style={inputS} placeholder="Votre nom complet" /></div>
                                            <div><label style={labelS}>Entreprise *</label><input required value={requestForm.entreprise} onChange={e => setRequestForm({ ...requestForm, entreprise: e.target.value })} style={inputS} placeholder="Ma Société SARL" /></div>
                                        </div>
                                        <div><label style={labelS}>Email *</label><input required type="email" value={requestForm.email} onChange={e => setRequestForm({ ...requestForm, email: e.target.value })} style={inputS} placeholder="email@entreprise.ma" /></div>
                                        <div><label style={labelS}>Téléphone</label><input type="tel" value={requestForm.telephone} onChange={e => setRequestForm({ ...requestForm, telephone: e.target.value })} style={inputS} placeholder="+212 6XX XX XX XX" /></div>
                                        <div><label style={labelS}>Message (Optionnel)</label><textarea rows={2} value={requestForm.message} onChange={e => setRequestForm({ ...requestForm, message: e.target.value })} style={{ ...inputS, resize: 'none' }} placeholder="Informations complémentaires..." /></div>
                                        <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
                                            <button type="button" onClick={() => setShowContactModal(false)} style={{ flex: 1, padding: '13px', borderRadius: '12px', background: S.bg, color: S.text3, border: `1px solid ${S.border}`, fontWeight: 700, cursor: 'pointer' }}>Annuler</button>
                                            <button type="submit" disabled={requestSubmitting} style={{ flex: 2, padding: '13px', borderRadius: '12px', background: S.accent, color: 'white', border: 'none', fontWeight: 700, cursor: requestSubmitting ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                                                {requestSubmitting ? <div className="spinner-pro-v2" style={{ width: '16px', height: '16px' }} /> : 'Envoyer la demande'}
                                            </button>
                                        </div>
                                    </form>
                                </>
                            ) : (
                                <div style={{ textAlign: 'center', padding: '20px 0' }}>
                                    <div style={{ width: '72px', height: '72px', background: S.successLight, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px', color: S.success }}><CheckCircle2 size={40} /></div>
                                    <h3 style={{ fontSize: '22px', fontWeight: 800, color: S.text, margin: '0 0 12px' }}>Demande envoyée !</h3>
                                    <p style={{ color: S.text3, lineHeight: '1.6', marginBottom: '28px' }}>Notre équipe reviendra vers vous très prochainement.</p>
                                    <button onClick={() => { setShowContactModal(false); setRequestSuccess(false); setRequestForm({ nom_complet: '', entreprise: '', email: '', telephone: '', message: '' }) }} style={{ width: '100%', padding: '15px', borderRadius: '14px', background: S.text, color: 'white', border: 'none', fontWeight: 700, cursor: 'pointer' }}>Fermer</button>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                <style>{`
                    @keyframes spin { to { transform: rotate(360deg); } }
                    @keyframes modalFadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
                    .spinner-pro-v2 { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite; }
                    @media (max-width: 900px) { div[style*="flex: 1.2"] { display: none !important; } }
                `}</style>
            </div>
        )
    }

    // ── PORTAL AUTHENTICATED ─────────────────────────────────────────────
    const navItems: { id: Tab; label: string; icon: React.ReactNode }[] = [
        { id: 'documents', label: 'Mes Documents', icon: <LayoutDashboard size={18} /> },
        { id: 'historique', label: 'Historique', icon: <History size={18} /> },
        { id: 'profil', label: 'Mon Profil', icon: <Settings size={18} /> },
    ]

    return (
        <div style={{ minHeight: '100vh', background: S.bg, fontFamily: "'Inter', sans-serif", display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <header style={{ background: 'white', padding: '0 32px', borderBottom: `1px solid ${S.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '64px', position: 'sticky', top: 0, zIndex: 100 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                    <div style={{ width: '36px', height: '36px', background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Building size={18} color="white" /></div>
                    <div>
                        <div style={{ fontWeight: 700, fontSize: '15px', color: S.text }}>Portail Entreprise</div>
                        <div style={{ fontSize: '12px', color: S.text3 }}>{societeNom}</div>
                    </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '34px', height: '34px', background: S.accentLight, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: S.accent, fontWeight: 700, fontSize: '14px' }}>
                        {(profile?.prenom || profile?.username || 'U').charAt(0).toUpperCase()}
                    </div>
                    <button onClick={logout} style={{ background: 'transparent', border: `1px solid ${S.border}`, padding: '7px 14px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '6px', color: S.text3, cursor: 'pointer', fontSize: '13px', fontWeight: 600 }}>
                        <LogOut size={14} /> Déconnexion
                    </button>
                </div>
            </header>

            <div style={{ display: 'flex', flex: 1 }}>
                {/* Sidebar */}
                <aside style={{ width: '220px', background: 'white', borderRight: `1px solid ${S.border}`, padding: '24px 12px', flexShrink: 0 }}>
                    <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                        {navItems.map(item => (
                            <button key={item.id} onClick={() => setActiveTab(item.id)}
                                style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '10px 14px', borderRadius: '10px', border: 'none', cursor: 'pointer', fontWeight: 600, fontSize: '14px', textAlign: 'left', width: '100%', transition: 'all 0.15s', background: activeTab === item.id ? S.accentLight : 'transparent', color: activeTab === item.id ? S.accent : S.text3 }}
                                onMouseEnter={e => { if (activeTab !== item.id) e.currentTarget.style.background = S.bg }}
                                onMouseLeave={e => { if (activeTab !== item.id) e.currentTarget.style.background = 'transparent' }}
                            >
                                {item.icon}
                                {item.label}
                            </button>
                        ))}
                    </nav>
                </aside>

                {/* Main content */}
                <main style={{ flex: 1, padding: '32px', overflowY: 'auto' }}>

                    {/* ── TAB: DOCUMENTS ── */}
                    {activeTab === 'documents' && (
                        <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 360px', gap: '28px', maxWidth: '1100px' }}>
                            <div>
                                <h2 style={{ fontSize: '22px', fontWeight: 800, color: S.text, margin: '0 0 20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <FileText size={20} color={S.accent} /> Documents envoyés
                                </h2>
                                {docs.length === 0 ? (
                                    <div style={{ background: 'white', border: `1px solid ${S.border}`, borderRadius: '16px', padding: '60px 40px', textAlign: 'center' }}>
                                        <div style={{ width: '60px', height: '60px', background: S.bg, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}><FileText size={26} color="#94a3b8" /></div>
                                        <h3 style={{ margin: '0 0 8px', color: S.text }}>Aucun document</h3>
                                        <p style={{ margin: 0, color: S.text3 }}>Vous n'avez pas encore envoyé de documents.</p>
                                    </div>
                                ) : (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                                        {docs.map(doc => (
                                            <div key={doc.id} style={{ background: 'white', border: `1px solid ${S.border}`, borderRadius: '12px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                                                    <div style={{ width: '38px', height: '38px', background: S.accentLight, borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><File size={18} color={S.accent} /></div>
                                                    <div>
                                                        <div style={{ fontWeight: 600, color: S.text, fontSize: '14px' }}>{doc.file_name}</div>
                                                        <div style={{ fontSize: '12px', color: S.text3, marginTop: '2px' }}>Transmis le {fmtDate(doc.date_upload)} • {doc.type_document}</div>
                                                    </div>
                                                </div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                                    {doc.statut === 'VALIDE' && <span style={{ background: S.successLight, color: S.success, padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}><CheckCircle2 size={13} /> Validé</span>}
                                                    {doc.statut === 'REJETE' && <span style={{ background: S.dangerLight, color: S.danger, padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}><X size={13} /> Rejeté</span>}
                                                    {doc.statut === 'A_TRAITER' && <span style={{ background: S.warningLight, color: S.warning, padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}><Clock size={13} /> En attente</span>}
                                                    {doc.statut === 'A_TRAITER' && (
                                                        <button onClick={() => handleDelete(doc.id)} style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center' }} title="Supprimer"><Trash2 size={16} /></button>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {/* Upload Zone */}
                            <div>
                                <div style={{ background: 'white', border: `1px solid ${S.border}`, borderRadius: '16px', padding: '24px', position: 'sticky', top: '20px' }}>
                                    <h2 style={{ fontSize: '16px', fontWeight: 700, color: S.text, margin: '0 0 18px', display: 'flex', alignItems: 'center', gap: '8px' }}><UploadCloud size={18} color={S.accent} /> Transmettre un fichier</h2>
                                    <div style={{ marginBottom: '14px' }}>
                                        <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: S.text2, marginBottom: '6px' }}>Type de document</label>
                                        <select value={docType} onChange={e => setDocType(e.target.value)} style={{ width: '100%', padding: '10px 12px', border: `1px solid ${S.border}`, borderRadius: '8px', outline: 'none', background: S.bg, color: S.text, fontWeight: 500, fontSize: '14px' }}>
                                            <option value="FACTURE_ACHAT">Facture d'Achat (Dépense)</option>
                                            <option value="FACTURE_VENTE">Facture de Vente</option>
                                            <option value="TICKET">Ticket de Caisse / Frais</option>
                                            <option value="RELEVE_BANCAIRE">Relevé Bancaire</option>
                                            <option value="AUTRE">Autre Document</option>
                                        </select>
                                    </div>
                                    <div style={{ marginBottom: '16px' }}>
                                        <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: S.text2, marginBottom: '6px' }}>Notes (Optionnel)</label>
                                        <textarea value={notes} onChange={e => setNotes(e.target.value)} placeholder="Précisions pour le comptable..." style={{ width: '100%', padding: '10px 12px', border: `1px solid ${S.border}`, borderRadius: '8px', outline: 'none', background: S.bg, boxSizing: 'border-box', minHeight: '70px', resize: 'vertical', fontSize: '14px' }} />
                                    </div>
                                    <div onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop} onClick={() => fileInputRef.current?.click()}
                                        style={{ background: dragActive ? S.accentLight : S.bg, border: `2px dashed ${dragActive ? S.accent : '#cbd5e1'}`, borderRadius: '12px', padding: '28px 16px', textAlign: 'center', cursor: 'pointer', transition: 'all 0.2s', opacity: uploading ? 0.5 : 1, pointerEvents: uploading ? 'none' : 'auto' }}>
                                        <input ref={fileInputRef} type="file" style={{ display: 'none' }} onChange={handleFileChange} />
                                        <UploadCloud size={30} color={dragActive ? S.accent : '#94a3b8'} style={{ margin: '0 auto 10px', display: 'block' }} />
                                        <div style={{ fontSize: '13px', fontWeight: 600, color: S.text2, marginBottom: '4px' }}>Cliquez ou glissez un fichier ici</div>
                                        <div style={{ fontSize: '12px', color: S.text3 }}>PDF, PNG ou JPG (Max 10Mo)</div>
                                    </div>
                                    {uploading && <div style={{ marginTop: '12px', fontSize: '13px', color: S.accent, textAlign: 'center', fontWeight: 600 }}>⏳ Envoi en cours...</div>}
                                    {uploadMsg && <div style={{ marginTop: '12px', padding: '10px 14px', borderRadius: '8px', fontSize: '13px', fontWeight: 500, background: uploadMsg.includes('✅') ? S.successLight : S.dangerLight, color: uploadMsg.includes('✅') ? S.success : S.danger }}>{uploadMsg}</div>}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* ── TAB: HISTORIQUE ── */}
                    {activeTab === 'historique' && (
                        <div style={{ maxWidth: '800px' }}>
                            <h2 style={{ fontSize: '22px', fontWeight: 800, color: S.text, margin: '0 0 8px', display: 'flex', alignItems: 'center', gap: '8px' }}><History size={20} color={S.accent} /> Historique d'activité</h2>
                            <p style={{ color: S.text3, marginBottom: '24px', fontSize: '14px' }}>Suivi de tous vos documents transmis à votre comptable.</p>

                            {docs.length === 0 ? (
                                <div style={{ background: 'white', border: `1px solid ${S.border}`, borderRadius: '16px', padding: '60px', textAlign: 'center' }}>
                                    <History size={40} color="#94a3b8" style={{ margin: '0 auto 16px', display: 'block' }} />
                                    <p style={{ color: S.text3 }}>Aucune activité enregistrée pour le moment.</p>
                                </div>
                            ) : (
                                <div style={{ background: 'white', border: `1px solid ${S.border}`, borderRadius: '16px', overflow: 'hidden' }}>
                                    {docs.map((doc, i) => (
                                        <div key={doc.id} style={{ padding: '16px 24px', display: 'flex', alignItems: 'center', gap: '16px', borderBottom: i < docs.length - 1 ? `1px solid ${S.border}` : 'none' }}>
                                            <div style={{ position: 'relative' }}>
                                                <div style={{ width: '40px', height: '40px', background: S.accentLight, borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><File size={18} color={S.accent} /></div>
                                            </div>
                                            <div style={{ flex: 1 }}>
                                                <div style={{ fontWeight: 600, color: S.text, fontSize: '14px' }}>{doc.file_name}</div>
                                                <div style={{ fontSize: '12px', color: S.text3, marginTop: '3px' }}>
                                                    Envoyé le {fmtDate(doc.date_upload)} • Type : {doc.type_document.replace(/_/g, ' ')}
                                                    {doc.notes_client && ` • "${doc.notes_client}"`}
                                                </div>
                                            </div>
                                            <div>
                                                {doc.statut === 'VALIDE' && <span style={{ background: S.successLight, color: S.success, padding: '5px 14px', borderRadius: '20px', fontSize: '12px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '5px' }}><CheckCircle2 size={13} /> Validé</span>}
                                                {doc.statut === 'REJETE' && <span style={{ background: S.dangerLight, color: S.danger, padding: '5px 14px', borderRadius: '20px', fontSize: '12px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '5px' }}><X size={13} /> Rejeté</span>}
                                                {doc.statut === 'A_TRAITER' && <span style={{ background: S.warningLight, color: S.warning, padding: '5px 14px', borderRadius: '20px', fontSize: '12px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '5px' }}><Clock size={13} /> En attente</span>}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── TAB: PROFIL ── */}
                    {activeTab === 'profil' && (
                        <div style={{ maxWidth: '600px' }}>
                            <h2 style={{ fontSize: '22px', fontWeight: 800, color: S.text, margin: '0 0 8px', display: 'flex', alignItems: 'center', gap: '8px' }}><User size={20} color={S.accent} /> Mon Profil</h2>
                            <p style={{ color: S.text3, marginBottom: '28px', fontSize: '14px' }}>Gérez vos coordonnées et votre mot de passe.</p>

                            {/* Info Card */}
                            <div style={{ background: 'white', border: `1px solid ${S.border}`, borderRadius: '16px', padding: '28px', marginBottom: '20px' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '28px' }}>
                                    <div style={{ width: '60px', height: '60px', background: 'linear-gradient(135deg, #6366f1, #a855f7)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '22px', fontWeight: 700 }}>
                                        {(profile?.prenom || profile?.username || 'U').charAt(0).toUpperCase()}
                                    </div>
                                    <div>
                                        <div style={{ fontWeight: 700, fontSize: '18px', color: S.text }}>{profile?.prenom} {profile?.nom}</div>
                                        <div style={{ fontSize: '13px', color: S.text3 }}>@{profile?.username}</div>
                                    </div>
                                </div>

                                <h3 style={{ fontSize: '15px', fontWeight: 700, color: S.text, margin: '0 0 16px', paddingBottom: '10px', borderBottom: `1px solid ${S.border}` }}>Informations personnelles</h3>

                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px', marginBottom: '20px' }}>
                                    <div>
                                        <label style={labelS}>Prénom</label>
                                        <input value={profileForm.prenom} onChange={e => setProfileForm({ ...profileForm, prenom: e.target.value })} style={inputS} placeholder="Votre prénom" />
                                    </div>
                                    <div>
                                        <label style={labelS}>Nom</label>
                                        <input value={profileForm.nom} onChange={e => setProfileForm({ ...profileForm, nom: e.target.value })} style={inputS} placeholder="Votre nom" />
                                    </div>
                                </div>

                                <div style={{ marginBottom: '20px' }}>
                                    <label style={labelS}><Mail size={13} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '4px' }} />Email</label>
                                    <input type="email" value={profileForm.email} onChange={e => setProfileForm({ ...profileForm, email: e.target.value })} style={inputS} placeholder="votre@email.com" />
                                </div>

                                {profileMsg && <div style={{ marginBottom: '14px', padding: '10px 14px', borderRadius: '8px', fontSize: '13px', fontWeight: 500, background: profileMsg.includes('✅') ? S.successLight : S.dangerLight, color: profileMsg.includes('✅') ? S.success : S.danger }}>{profileMsg}</div>}

                                <button onClick={handleSaveProfile} disabled={profileSaving} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 24px', background: S.accent, color: 'white', border: 'none', borderRadius: '10px', fontWeight: 700, cursor: profileSaving ? 'not-allowed' : 'pointer', fontSize: '14px', opacity: profileSaving ? 0.7 : 1 }}>
                                    {profileSaving ? <div className="spinner-pro-v2" style={{ width: '16px', height: '16px' }} /> : <><Save size={15} /> Enregistrer les modifications</>}
                                </button>
                            </div>

                            {/* Password Card */}
                            <div style={{ background: 'white', border: `1px solid ${S.border}`, borderRadius: '16px', padding: '28px' }}>
                                <h3 style={{ fontSize: '15px', fontWeight: 700, color: S.text, margin: '0 0 20px', display: 'flex', alignItems: 'center', gap: '8px' }}><KeyRound size={16} color={S.accent} /> Changer le mot de passe</h3>

                                {[
                                    { label: 'Mot de passe actuel', key: 'old_password', show: showOld, toggle: () => setShowOld(!showOld) },
                                    { label: 'Nouveau mot de passe', key: 'new_password', show: showNew, toggle: () => setShowNew(!showNew) },
                                    { label: 'Confirmer le nouveau mot de passe', key: 'confirm', show: showNew, toggle: () => setShowNew(!showNew) },
                                ].map((f, i) => (
                                    <div key={i} style={{ marginBottom: '14px' }}>
                                        <label style={labelS}>{f.label}</label>
                                        <div style={{ position: 'relative' }}>
                                            <input type={f.show ? 'text' : 'password'} value={(pwForm as any)[f.key]} onChange={e => setPwForm({ ...pwForm, [f.key]: e.target.value })}
                                                style={{ ...inputS, paddingRight: '44px' }} placeholder="••••••••" />
                                            <button type="button" onClick={f.toggle} style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: S.text3, display: 'flex', alignItems: 'center' }}>
                                                {f.show ? <EyeOff size={16} /> : <Eye size={16} />}
                                            </button>
                                        </div>
                                    </div>
                                ))}

                                {pwMsg && <div style={{ marginBottom: '14px', padding: '10px 14px', borderRadius: '8px', fontSize: '13px', fontWeight: 500, background: pwMsg.includes('✅') ? S.successLight : S.dangerLight, color: pwMsg.includes('✅') ? S.success : S.danger }}>{pwMsg}</div>}

                                <button onClick={handleChangePassword} disabled={pwSaving} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 24px', background: '#0f172a', color: 'white', border: 'none', borderRadius: '10px', fontWeight: 700, cursor: pwSaving ? 'not-allowed' : 'pointer', fontSize: '14px', opacity: pwSaving ? 0.7 : 1 }}>
                                    {pwSaving ? <div className="spinner-pro-v2" style={{ width: '16px', height: '16px' }} /> : <><Lock size={15} /> Changer le mot de passe</>}
                                </button>
                            </div>
                        </div>
                    )}
                </main>
            </div>

            <style>{`
                @keyframes spin { to { transform: rotate(360deg); } }
                .spinner-pro-v2 { width: 20px; height: 20px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite; }
            `}</style>
        </div>
    )
}

// Shared styles
const labelS: React.CSSProperties = { display: 'block', fontSize: '12px', fontWeight: 700, color: '#475569', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }
const inputS: React.CSSProperties = { width: '100%', padding: '11px 14px', borderRadius: '10px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none', background: '#f8fafc', color: '#0f172a', boxSizing: 'border-box', transition: 'all 0.2s' }
