import React, { useState, useEffect, useRef } from 'react'
import apiService, { DocumentTransmis, UtilisateurClient } from '../api'
import { UploadCloud, CheckCircle2, Clock, AlertCircle, LogOut, Lock, User, Send, File, Trash2, Home, Activity, Building, X, FileText, History, AlertTriangle, ArrowRight, Phone, Mail, MapPin } from 'lucide-react'

const fmtDate = (d: string) => new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })

export default function ClientPortal() {
    const [token, setToken] = useState<string | null>(localStorage.getItem('client_token'))
    const [societeNom, setSocieteNom] = useState<string>(localStorage.getItem('client_societe_nom') || '')
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [loginError, setLoginError] = useState<string | null>(null)
    const [showContactModal, setShowContactModal] = useState(false)

    // Access Request Form State
    const [requestForm, setRequestForm] = useState({
        nom_complet: '',
        entreprise: '',
        email: '',
        telephone: '',
        message: ''
    })
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

    const handleDelete = async (id: number) => {
        if (!window.confirm("Supprimer définitivement ce document ?")) return
        try {
            await apiService.clientDeleteTransmissionDoc(id)
            loadHistory()
        } catch (err: any) {
            alert("Erreur: " + (err.response?.data?.detail || err.message))
        }
    }

    useEffect(() => {
        if (token) loadHistory()
    }, [token])

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
            // Détection automatique du cabinet via l'URL (?cabinet=ID)
            const queryParams = new URLSearchParams(window.location.search)
            const cabinetIdParam = queryParams.get('cabinet')
            const cabinetId = cabinetIdParam ? parseInt(cabinetIdParam) : null

            await apiService.createDemandeAcces({
                ...requestForm,
                cabinet_id: cabinetId
            })
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

    const loadHistory = async () => {
        try {
            const data = await apiService.clientGetHistorique()
            setDocs(data)
        } catch (err) {
            console.error(err)
        }
    }

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true)
        else if (e.type === 'dragleave') setDragActive(false)
    }

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await uploadFile(e.dataTransfer.files[0])
        }
    }

    const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            await uploadFile(e.target.files[0])
        }
    }

    const uploadFile = async (file: File) => {
        setUploading(true)
        setUploadMsg('')
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

    if (!token) {
        return (
            <div style={{ minHeight: '100vh', display: 'flex', background: '#ffffff', fontFamily: "'Inter', sans-serif" }}>
                {/* Left: Premium Sidebar Content */}
                <div style={{ 
                    flex: '1.2', 
                    background: 'linear-gradient(rgba(30, 27, 75, 0.85), rgba(30, 27, 75, 0.85)), url("/src/assets/client-login-side.png")', 
                    backgroundSize: 'cover', 
                    backgroundPosition: 'center', 
                    padding: '80px', 
                    display: 'flex', 
                    flexDirection: 'column', 
                    justifyContent: 'space-between',
                    color: 'white'
                }}>
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '60px' }}>
                            <div style={{ width: '48px', height: '48px', background: 'white', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#4338ca' }}>
                                <Building size={24} />
                            </div>
                            <span style={{ fontSize: '24px', fontWeight: 800, letterSpacing: '-0.5px' }}>Comptafacile</span>
                        </div>
                        
                        <div style={{ maxWidth: '420px' }}>
                            <h1 style={{ fontSize: '48px', fontWeight: 800, lineHeight: '1.1', marginBottom: '32px', letterSpacing: '-1.5px' }}>
                                Simplifiez la gestion de vos factures.
                            </h1>
                            <p style={{ fontSize: '18px', color: 'rgba(255, 255, 255, 0.7)', lineHeight: '1.6', marginBottom: '48px' }}>
                                Transmettez vos documents en un clic et suivez l'état de votre comptabilité en temps réel avec notre portail sécurisé.
                            </p>
                        </div>
                    </div>
                    
                    <div style={{ fontSize: '13px', color: 'rgba(255, 255, 255, 0.4)' }}>
                        © 2026 Comptafacile — Plateforme de services comptables numériques.
                    </div>
                </div>

                {/* Right: Login Form Column */}
                <div style={{ flex: '1', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '60px', background: '#ffffff' }}>
                    <div style={{ width: '100%', maxWidth: '380px' }}>
                        <div style={{ marginBottom: '48px' }}>
                            <h2 style={{ fontSize: '32px', fontWeight: 800, color: '#0f172a', marginBottom: '12px' }}>Bienvenue</h2>
                            <p style={{ color: '#64748b', fontSize: '15px' }}>Connectez-vous à votre espace entreprise</p>
                        </div>

                        {loginError && (
                            <div style={{ 
                                background: '#fef2f2', 
                                border: '1px solid #fee2e2',
                                color: '#b91c1c', 
                                padding: '14px 16px', 
                                borderRadius: '12px', 
                                fontSize: '14px', 
                                marginBottom: '24px', 
                                display: 'flex',
                                alignItems: 'center',
                                gap: '12px',
                                fontWeight: 500
                            }}>
                                <AlertTriangle size={18} />
                                <span>{loginError}</span>
                            </div>
                        )}

                        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                <label style={{ color: '#334155', fontSize: '13px', fontWeight: 600, marginLeft: '4px' }}>Nom d'utilisateur</label>
                                <div style={{ position: 'relative' }}>
                                    <User size={18} color="#94a3b8" style={{ position: 'absolute', top: '50%', left: '16px', transform: 'translateY(-50%)' }} />
                                    <input 
                                        value={username} 
                                        onChange={e => setUsername(e.target.value)} 
                                        required 
                                        placeholder="Identifiant"
                                        style={{ 
                                            width: '100%', 
                                            padding: '16px 16px 16px 48px', 
                                            background: '#f8fafc', 
                                            border: '1px solid #e2e8f0', 
                                            borderRadius: '14px', 
                                            color: '#0f172a', 
                                            outline: 'none', 
                                            boxSizing: 'border-box',
                                            fontSize: '15px',
                                            transition: 'all 0.2s'
                                        }} 
                                        onFocus={e => { e.currentTarget.style.borderColor = '#4338ca'; e.currentTarget.style.boxShadow = '0 0 0 4px rgba(67, 56, 202, 0.1)'; }}
                                        onBlur={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.boxShadow = 'none'; }}
                                    />
                                </div>
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <label style={{ color: '#334155', fontSize: '13px', fontWeight: 600, marginLeft: '4px' }}>Mot de passe</label>
                                    <a href="#" style={{ fontSize: '13px', color: '#4338ca', fontWeight: 600, textDecoration: 'none' }}>Oublié ?</a>
                                </div>
                                <div style={{ position: 'relative' }}>
                                    <Lock size={18} color="#94a3b8" style={{ position: 'absolute', top: '50%', left: '16px', transform: 'translateY(-50%)' }} />
                                    <input 
                                        type="password" 
                                        value={password} 
                                        onChange={e => setPassword(e.target.value)} 
                                        required 
                                        placeholder="••••••••"
                                        style={{ 
                                            width: '100%', 
                                            padding: '16px 16px 16px 48px', 
                                            background: '#f8fafc', 
                                            border: '1px solid #e2e8f0', 
                                            borderRadius: '14px', 
                                            color: '#0f172a', 
                                            outline: 'none', 
                                            boxSizing: 'border-box',
                                            fontSize: '15px',
                                            transition: 'all 0.2s'
                                        }} 
                                        onFocus={e => { e.currentTarget.style.borderColor = '#4338ca'; e.currentTarget.style.boxShadow = '0 0 0 4px rgba(67, 56, 202, 0.1)'; }}
                                        onBlur={e => { e.currentTarget.style.borderColor = '#e2e8f0'; e.currentTarget.style.boxShadow = 'none'; }}
                                    />
                                </div>
                            </div>
                            <button 
                                type="submit" 
                                disabled={loading} 
                                style={{ 
                                    background: '#4338ca', 
                                    color: 'white', 
                                    padding: '18px', 
                                    borderRadius: '14px', 
                                    border: 'none', 
                                    fontWeight: 700, 
                                    fontSize: '16px', 
                                    cursor: loading ? 'not-allowed' : 'pointer', 
                                    marginTop: '8px', 
                                    display: 'flex', 
                                    justifyContent: 'center', 
                                    gap: '12px', 
                                    alignItems: 'center', 
                                    transition: 'all 0.3s', 
                                    opacity: loading ? 0.7 : 1,
                                    boxShadow: '0 4px 12px rgba(67, 56, 202, 0.25)'
                                }}
                                onMouseOver={e => { if(!loading) e.currentTarget.style.background = '#3730a3'; }}
                                onMouseOut={e => { if(!loading) e.currentTarget.style.background = '#4338ca'; }}
                            >
                                {loading ? (
                                    <div className="spinner-pro-v2"></div>
                                ) : (
                                    <>Se connecter <ArrowRight size={18} /></>
                                )}
                            </button>
                        </form>
                        
                        <div style={{ marginTop: '60px', textAlign: 'center' }}>
                            <p style={{ fontSize: '14px', color: '#64748b' }}>
                                Vous n'avez pas de compte ? <br />
                                <button 
                                    onClick={() => setShowContactModal(true)} 
                                    style={{ 
                                        background: 'none', 
                                        border: 'none', 
                                        color: '#4338ca', 
                                        fontWeight: 600, 
                                        cursor: 'pointer', 
                                        padding: 0, 
                                        textDecoration: 'underline',
                                        fontFamily: 'inherit'
                                    }}
                                >
                                    Contactez votre cabinet comptable
                                </button>
                            </p>
                        </div>
                    </div>
                </div>
                
                {/* Access Request Form Modal */}
                {showContactModal && (
                    <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.4)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
                        <div style={{ 
                            background: 'white', 
                            padding: '40px', 
                            borderRadius: '32px', 
                            width: '100%', 
                            maxWidth: '500px', 
                            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.15)',
                            position: 'relative',
                            animation: 'modalFadeIn 0.3s ease-out',
                            maxHeight: '90vh',
                            overflowY: 'auto'
                        }}>
                            {!requestSuccess ? (
                                <>
                                    <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                                        <div style={{ 
                                            width: '56px', 
                                            height: '56px', 
                                            background: '#f1f5f9', 
                                            borderRadius: '16px', 
                                            display: 'flex', 
                                            alignItems: 'center', 
                                            justifyContent: 'center', 
                                            margin: '0 auto 16px',
                                            color: '#4338ca'
                                        }}>
                                            <Building size={28} />
                                        </div>
                                        <h3 style={{ fontSize: '24px', fontWeight: 800, color: '#0f172a', margin: '0 0 8px 0' }}>Demande d'accès</h3>
                                        <p style={{ color: '#64748b', fontSize: '14px', lineHeight: '1.5' }}>
                                            Remplissez ce formulaire pour que votre cabinet comptable puisse créer votre compte.
                                        </p>
                                    </div>

                                    <form onSubmit={handleRequestAccess} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                                            <div>
                                                <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: '#475569', marginBottom: '6px', textTransform: 'uppercase' }}>Nom et Prénom *</label>
                                                <input 
                                                    required
                                                    type="text" 
                                                    value={requestForm.nom_complet}
                                                    onChange={e => setRequestForm({...requestForm, nom_complet: e.target.value})}
                                                    style={{ width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none' }}
                                                    placeholder="Votre nom et prénom"
                                                />
                                            </div>
                                            <div>
                                                <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: '#475569', marginBottom: '6px', textTransform: 'uppercase' }}>Entreprise *</label>
                                                <input 
                                                    required
                                                    type="text" 
                                                    value={requestForm.entreprise}
                                                    onChange={e => setRequestForm({...requestForm, entreprise: e.target.value})}
                                                    style={{ width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none' }}
                                                    placeholder="Ma Société SARL"
                                                />
                                            </div>
                                        </div>

                                        <div>
                                            <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: '#475569', marginBottom: '6px', textTransform: 'uppercase' }}>Email *</label>
                                            <input 
                                                required
                                                type="email" 
                                                value={requestForm.email}
                                                onChange={e => setRequestForm({...requestForm, email: e.target.value})}
                                                style={{ width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none' }}
                                                placeholder="votre-email@entreprise.ma"
                                            />
                                        </div>

                                        <div>
                                            <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: '#475569', marginBottom: '6px', textTransform: 'uppercase' }}>Téléphone</label>
                                            <input 
                                                type="tel" 
                                                value={requestForm.telephone}
                                                onChange={e => setRequestForm({...requestForm, telephone: e.target.value})}
                                                style={{ width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none' }}
                                                placeholder="+212 6XX XX XX XX"
                                            />
                                        </div>

                                        <div>
                                            <label style={{ display: 'block', fontSize: '12px', fontWeight: 700, color: '#475569', marginBottom: '6px', textTransform: 'uppercase' }}>Message (Optionnel)</label>
                                            <textarea 
                                                rows={2}
                                                value={requestForm.message}
                                                onChange={e => setRequestForm({...requestForm, message: e.target.value})}
                                                style={{ width: '100%', padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '14px', outline: 'none', resize: 'none' }}
                                                placeholder="Informations complémentaires..."
                                            />
                                        </div>

                                        <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
                                            <button 
                                                type="button"
                                                onClick={() => setShowContactModal(false)}
                                                style={{ flex: 1, padding: '14px', borderRadius: '12px', background: '#f1f5f9', color: '#475569', border: 'none', fontWeight: 700, cursor: 'pointer' }}
                                            >
                                                Annuler
                                            </button>
                                            <button 
                                                type="submit"
                                                disabled={requestSubmitting}
                                                style={{ 
                                                    flex: 2, 
                                                    padding: '14px', 
                                                    borderRadius: '12px', 
                                                    background: '#4338ca', 
                                                    color: 'white', 
                                                    border: 'none', 
                                                    fontWeight: 700, 
                                                    cursor: requestSubmitting ? 'not-allowed' : 'pointer',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    gap: '8px'
                                                }}
                                            >
                                                {requestSubmitting ? <div className="spinner-pro-v2" style={{ width: '16px', height: '16px' }}></div> : 'Envoyer la demande'}
                                            </button>
                                        </div>
                                    </form>
                                </>
                            ) : (
                                <div style={{ textAlign: 'center', padding: '20px 0' }}>
                                    <div style={{ 
                                        width: '72px', 
                                        height: '72px', 
                                        background: '#dcfce7', 
                                        borderRadius: '50%', 
                                        display: 'flex', 
                                        alignItems: 'center', 
                                        justifyContent: 'center', 
                                        margin: '0 auto 24px',
                                        color: '#16a34a'
                                    }}>
                                        <CheckCircle2 size={40} />
                                    </div>
                                    <h3 style={{ fontSize: '24px', fontWeight: 800, color: '#0f172a', margin: '0 0 12px 0' }}>Demande envoyée !</h3>
                                    <p style={{ color: '#64748b', fontSize: '16px', lineHeight: '1.6', marginBottom: '32px' }}>
                                        Votre demande a été transmise avec succès. Notre équipe reviendra vers vous très prochainement par email.
                                    </p>
                                    <button 
                                        onClick={() => {
                                            setShowContactModal(false)
                                            setRequestSuccess(false)
                                            setRequestForm({ nom_complet: '', entreprise: '', email: '', telephone: '', message: '' })
                                        }}
                                        style={{ width: '100%', padding: '16px', borderRadius: '16px', background: '#0f172a', color: 'white', border: 'none', fontWeight: 700, fontSize: '16px', cursor: 'pointer' }}
                                    >
                                        Fermer
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                )}
                
                <style>{`
                    @keyframes spin { to { transform: rotate(360deg); } }
                    @keyframes modalFadeIn { 
                        from { opacity: 0; transform: translateY(20px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    .spinner-pro-v2 {
                        width: 20px;
                        height: 20px;
                        border: 2px solid rgba(255,255,255,0.3);
                        border-top-color: white;
                        border-radius: 50%;
                        animation: spin 0.8s linear infinite;
                    }
                    @media (max-width: 1000px) {
                        div[style*="flex: 1.2"] { display: none !important; }
                    }
                `}</style>
            </div>
        )
    }

    return (
        <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
            {/* Header */}
            <header style={{ background: 'white', padding: '16px 40px', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{ width: '40px', height: '40px', background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Building size={20} color="white" />
                    </div>
                    <div>
                        <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#0f172a' }}>Portail Entreprise</h1>
                        <p style={{ margin: 0, fontSize: '13px', color: '#64748b', fontWeight: 500 }}>{societeNom}</p>
                    </div>
                </div>
                <button onClick={logout} style={{ background: 'transparent', border: '1px solid #e2e8f0', padding: '8px 16px', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px', color: '#64748b', cursor: 'pointer', fontSize: '14px', fontWeight: 600, transition: 'all 0.2s' }}>
                    <LogOut size={16} /> Déconnexion
                </button>
            </header>

            <main style={{ padding: '40px', maxWidth: '1200px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) 380px', gap: '32px' }}>
                {/* Historique */}
                <div>
                    <h2 style={{ fontSize: '20px', fontWeight: 700, color: '#0f172a', margin: '0 0 24px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <History size={20} color="#6366f1" /> Documents envoyés
                    </h2>
                    
                    {docs.length === 0 ? (
                        <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '60px 40px', textAlign: 'center' }}>
                            <div style={{ width: '64px', height: '64px', background: '#f1f5f9', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                                <FileText size={28} color="#94a3b8" />
                            </div>
                            <h3 style={{ margin: '0 0 8px', color: '#0f172a', fontSize: '18px' }}>Aucun document</h3>
                            <p style={{ margin: 0, color: '#64748b' }}>Vous n'avez pas encore envoyé de factures à votre comptable.</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {docs.map(doc => (
                                <div key={doc.id} style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                        <div style={{ width: '40px', height: '40px', background: '#e0e7ff', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            <File size={20} color="#4f46e5" />
                                        </div>
                                        <div>
                                            <div style={{ fontWeight: 600, color: '#1e293b', fontSize: '14px' }}>{doc.file_name}</div>
                                            <div style={{ fontSize: '12px', color: '#64748b', marginTop: '2px' }}>
                                                Transmis le {fmtDate(doc.date_upload)} • Type: {doc.type_document}
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            {doc.statut === 'VALIDE' && <span style={{ background: '#dcfce7', color: '#15803d', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}><CheckCircle2 size={14} /> Validé</span>}
                                            {doc.statut === 'REJETE' && <span style={{ background: '#fee2e2', color: '#b91c1c', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}><X size={14} /> Rejeté</span>}
                                            {doc.statut === 'A_TRAITER' && <span style={{ background: '#fef3c7', color: '#b45309', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '4px' }}><Clock size={14} /> En attente</span>}
                                        </div>
                                        {doc.statut === 'A_TRAITER' && (
                                            <button 
                                                onClick={() => handleDelete(doc.id)}
                                                style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '4px', display: 'flex', alignItems: 'center', transition: 'transform 0.2s' }}
                                                onMouseOver={e => e.currentTarget.style.transform = 'scale(1.2)'}
                                                onMouseOut={e => e.currentTarget.style.transform = 'scale(1)'}
                                                title="Supprimer"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Upload Zone */}
                <div>
                    <div style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '16px', padding: '24px', position: 'sticky', top: '24px' }}>
                        <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', margin: '0 0 20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <UploadCloud size={20} color="#6366f1" /> Transmettre un fichier
                        </h2>

                        <div style={{ marginBottom: '16px' }}>
                            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#334155', marginBottom: '8px' }}>Type de document</label>
                            <select value={docType} onChange={e => setDocType(e.target.value)} style={{ width: '100%', padding: '10px 12px', border: '1px solid #cbd5e1', borderRadius: '8px', outline: 'none', background: '#f8fafc', color: '#0f172a', fontWeight: 500 }}>
                                <option value="FACTURE_ACHAT">Facture d'Achat (Dépense)</option>
                                <option value="FACTURE_VENTE">Facture de Vente</option>
                                <option value="TICKET">Ticket de Caisse / Frais</option>
                                <option value="RELEVE_BANCAIRE">Relevé Bancaire</option>
                                <option value="AUTRE">Autre Document</option>
                            </select>
                        </div>

                        <div style={{ marginBottom: '20px' }}>
                            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#334155', marginBottom: '8px' }}>Notes (Optionnel)</label>
                            <textarea value={notes} onChange={e => setNotes(e.target.value)} placeholder="Précisions pour le comptable..." style={{ width: '100%', padding: '10px 12px', border: '1px solid #cbd5e1', borderRadius: '8px', outline: 'none', background: '#f8fafc', boxSizing: 'border-box', minHeight: '80px', resize: 'vertical' }} />
                        </div>

                        <div 
                            onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
                            onClick={() => fileInputRef.current?.click()}
                            style={{ 
                                background: dragActive ? '#e0e7ff' : '#f8fafc', 
                                border: `2px dashed ${dragActive ? '#6366f1' : '#cbd5e1'}`, 
                                borderRadius: '12px', padding: '32px 20px', textAlign: 'center', cursor: 'pointer', transition: 'all 0.2s',
                                opacity: uploading ? 0.5 : 1, pointerEvents: uploading ? 'none' : 'auto'
                            }}
                        >
                            <input ref={fileInputRef} type="file" style={{ display: 'none' }} onChange={handleFileChange} />
                            <UploadCloud size={32} color={dragActive ? '#4f46e5' : '#94a3b8'} style={{ margin: '0 auto 12px' }} />
                            <div style={{ fontSize: '14px', fontWeight: 600, color: '#334155', marginBottom: '4px' }}>Cliquez ou glissez un fichier ici</div>
                            <div style={{ fontSize: '12px', color: '#64748b' }}>PDF, PNG ou JPG (Max 10Mo)</div>
                        </div>

                        {uploading && <div style={{ marginTop: '16px', fontSize: '13px', color: '#4f46e5', textAlign: 'center', fontWeight: 600 }}>⏳ Envoi en cours...</div>}
                        {uploadMsg && (
                            <div style={{ marginTop: '16px', padding: '12px', borderRadius: '8px', fontSize: '13px', fontWeight: 500, background: uploadMsg.includes('✅') ? '#dcfce7' : '#fee2e2', color: uploadMsg.includes('✅') ? '#166534' : '#991b1b', border: `1px solid ${uploadMsg.includes('✅') ? '#bbf7d0' : '#fecaca'} `}}>
                                {uploadMsg}
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    )
}
