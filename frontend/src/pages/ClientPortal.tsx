import React, { useState, useEffect, useRef } from 'react'
import apiService, { DocumentTransmis, UtilisateurClient } from '../api'
import { UploadCloud, CheckCircle2, Clock, AlertCircle, LogOut, Lock, User, Send, File, Trash2, Home, Activity, Building, X, FileText, History } from 'lucide-react'

const fmtDate = (d: string) => new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })

export default function ClientPortal() {
    const [token, setToken] = useState<string | null>(localStorage.getItem('client_token'))
    const [societeNom, setSocieteNom] = useState<string>(localStorage.getItem('client_societe_nom') || '')

    // Login state
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loginError, setLoginError] = useState('')
    const [loading, setLoading] = useState(false)

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
            <div style={{ minHeight: '100vh', display: 'flex', background: 'linear-gradient(135deg, #1e1e2e 0%, #11111b 100%)', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
                <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)', backdropFilter: 'blur(20px)', padding: '40px', borderRadius: '24px', width: '100%', maxWidth: '420px', boxShadow: '0 25px 50px -12px rgba(0,0,0,0.5)' }}>
                    <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                        <div style={{ width: '64px', height: '64px', background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
                            <Building size={32} color="white" />
                        </div>
                        <h1 style={{ margin: 0, fontSize: '24px', color: 'white', fontWeight: 700 }}>Espace Entreprise</h1>
                        <p style={{ margin: '8px 0 0', color: '#a1a1aa', fontSize: '14px' }}>Connectez-vous pour transmettre vos factures</p>
                    </div>

                    {loginError && <div style={{ background: 'rgba(239,68,68,0.1)', color: '#ef4444', padding: '12px', borderRadius: '8px', fontSize: '13px', marginBottom: '20px', textAlign: 'center', border: '1px solid rgba(239,68,68,0.2)' }}>{loginError}</div>}

                    <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <div>
                            <label style={{ display: 'block', color: '#a1a1aa', fontSize: '12px', marginBottom: '6px' }}>Nom d'utilisateur</label>
                            <div style={{ position: 'relative' }}>
                                <User size={18} color="#a1a1aa" style={{ position: 'absolute', top: '12px', left: '14px' }} />
                                <input value={username} onChange={e => setUsername(e.target.value)} required placeholder="Entrez votre identifiant"
                                    style={{ width: '100%', padding: '12px 14px 12px 42px', background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: 'white', outline: 'none', boxSizing: 'border-box' }} />
                            </div>
                        </div>
                        <div>
                            <label style={{ display: 'block', color: '#a1a1aa', fontSize: '12px', marginBottom: '6px' }}>Mot de passe</label>
                            <div style={{ position: 'relative' }}>
                                <Lock size={18} color="#a1a1aa" style={{ position: 'absolute', top: '12px', left: '14px' }} />
                                <input type="password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="••••••••"
                                    style={{ width: '100%', padding: '12px 14px 12px 42px', background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: 'white', outline: 'none', boxSizing: 'border-box' }} />
                            </div>
                        </div>
                        <button type="submit" disabled={loading} style={{ background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)', color: 'white', padding: '14px', borderRadius: '12px', border: 'none', fontWeight: 600, fontSize: '15px', cursor: loading ? 'not-allowed' : 'pointer', marginTop: '10px', display: 'flex', justifyContent: 'center', gap: '8px', alignItems: 'center', transition: 'all 0.2s', opacity: loading ? 0.7 : 1 }}>
                            {loading ? 'Connexion...' : <><Send size={18} /> Se Connecter</>}
                        </button>
                    </form>
                </div>
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
