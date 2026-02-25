import React, { useState, useEffect } from 'react'
import apiService from '../api'
import { Edit2, Zap } from 'lucide-react'

interface AgentProfile {
    id: number
    username: string
    email: string
    nom: string
    prenom: string
    is_admin: boolean
    created_at: string
}

interface AgentStats {
    total_factures_validees: number
    total_societes_gerees: number
    cabinet_nom: string
}

export default function Profile() {
    const [profile, setProfile] = useState<AgentProfile | null>(null)
    const [stats, setStats] = useState<AgentStats | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [message, setMessage] = useState<string | null>(null)

    // Editing states
    const [isEditing, setIsEditing] = useState(false)
    const [isChangingPassword, setIsChangingPassword] = useState(false)
    const [formData, setFormData] = useState({
        nom: '',
        prenom: '',
        email: '',
        password: '',
        confirmPassword: ''
    })

    const loadData = async () => {
        setLoading(true)
        try {
            const token = localStorage.getItem('access_token') || localStorage.getItem('session_token')
            if (!token) throw new Error('Non authentifié')

            const [profData, statsData] = await Promise.all([
                apiService.getProfile(token),
                apiService.getAgentStats(token)
            ])

            setProfile(profData)
            setStats(statsData)
            setFormData({
                nom: profData.nom || '',
                prenom: profData.prenom || '',
                email: profData.email || '',
                password: '',
                confirmPassword: ''
            })
        } catch (err: any) {
            console.error('[Profile] Error loading data:', err)
            setError(err.message || 'Erreur lors du chargement du profil')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        loadData()
    }, [])

    const handleUpdateProfile = async (e: React.FormEvent) => {
        e.preventDefault()
        setError(null)
        setMessage(null)
        try {
            await apiService.updateProfile({
                nom: formData.nom,
                prenom: formData.prenom,
                email: formData.email
            })
            setMessage('Profil mis à jour avec succès')
            setIsEditing(false)
            loadData() // Reload profile
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Erreur lors de la mise à jour')
        }
    }

    const handleUpdatePassword = async (e: React.FormEvent) => {
        e.preventDefault()
        setError(null)
        setMessage(null)

        if (formData.password !== formData.confirmPassword) {
            setError('Les mots de passe ne correspondent pas')
            return
        }

        try {
            await apiService.updateProfile({
                password: formData.password
            })
            setMessage('Mot de passe changé avec succès')
            setIsChangingPassword(false)
            setFormData(prev => ({ ...prev, password: '', confirmPassword: '' }))
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Erreur lors du changement de mot de passe')
        }
    }

    if (loading) return (
        <div className="loading" style={{ height: '80vh', color: 'var(--text2)' }}>
            <div className="spinner" />
            Chargement du profil...
        </div>
    )

    if (!profile) return (
        <div className="container-pro" style={{ padding: '40px' }}>
            <div className="alert alert-error">{error || 'Profil introuvable'}</div>
        </div>
    )

    const initials = `${profile.prenom?.[0] || ''}${profile.nom?.[0] || profile.username?.[0] || ''}`.toUpperCase()

    return (
        <div className="profile-container container-pro animate-in fade-in duration-500 pb-20">
            {/* Header Profil Premium */}
            <div className="glass-card profile-hero" style={{
                display: 'flex',
                alignItems: 'center',
                gap: '32px',
                padding: '40px',
                borderRadius: '24px',
                marginBottom: '32px',
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02))',
                backdropFilter: 'blur(10px)',
                border: '1px solid var(--border)',
                boxShadow: 'var(--shadow-lg)'
            }}>
                <div className="avatar-large" style={{
                    width: '120px',
                    height: '120px',
                    borderRadius: '30px',
                    background: 'linear-gradient(45deg, var(--accent), var(--accent2))',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '48px',
                    fontWeight: '900',
                    color: 'white',
                    boxShadow: '0 0 30px rgba(59, 130, 246, 0.3)'
                }}>
                    {initials}
                </div>
                <div>
                    <h1 style={{ fontSize: '32px', marginBottom: '8px', fontWeight: '800', color: 'white' }}>
                        {profile.prenom} {profile.nom}
                    </h1>
                    <p style={{ color: 'var(--text2)', fontSize: '16px', marginBottom: '16px', fontWeight: '500' }}>
                        @{profile.username} • <span style={{ color: profile.is_admin ? 'var(--warning)' : 'var(--accent)' }}>{profile.is_admin ? 'Super Administrateur' : 'Agent Comptable'}</span>
                    </p>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <span className="badge" style={{ padding: '6px 16px', borderRadius: '12px', background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent)', fontWeight: '700', fontSize: '11px', letterSpacing: '0.05em' }}>
                            {stats?.cabinet_nom || 'SANS CABINET'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Statistiques Grille */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginBottom: '32px' }}>
                <div className="card" style={{ textAlign: 'center', padding: '32px' }}>
                    <div style={{ fontSize: '32px', marginBottom: '12px' }}>📄</div>
                    <div className="stat-value" style={{ color: 'var(--accent)' }}>{stats?.total_factures_validees || 0}</div>
                    <div className="stat-label">Pièces Comptables Validées</div>
                </div>

                <div className="card" style={{ textAlign: 'center', padding: '32px' }}>
                    <div style={{ fontSize: '32px', marginBottom: '12px' }}>🏢</div>
                    <div className="stat-value" style={{ color: 'var(--success)' }}>{stats?.total_societes_gerees || 0}</div>
                    <div className="stat-label">Dossiers Clientèle</div>
                </div>

                <div className="card" style={{ textAlign: 'center', padding: '32px' }}>
                    <div style={{ fontSize: '32px', marginBottom: '12px' }}>⚡</div>
                    <div className="stat-value" style={{ color: 'var(--warning)' }}>98.4%</div>
                    <div className="stat-label">Efficacité Systémique</div>
                </div>
            </div>

            {/* Notifications */}
            {error && <div className="alert alert-error animate-in slide-in-from-top-4 duration-300 mb-6">{error}</div>}
            {message && <div className="alert alert-success animate-in slide-in-from-top-4 duration-300 mb-6">{message}</div>}

            {/* Informations Détaillées / Formulaire */}
            <div className="card" style={{ padding: '40px' }}>
                <div className="card-header" style={{ marginBottom: '32px' }}>
                    <div>
                        <h2 className="card-title">Paramètres du Compte</h2>
                        <p className="card-subtitle">Gérez vos informations personnelles et votre sécurité.</p>
                    </div>
                </div>

                {isEditing ? (
                    <form onSubmit={handleUpdateProfile} className="space-y-6">
                        <div className="two-col">
                            <div className="form-group">
                                <label className="form-label">Prénom</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={formData.prenom}
                                    onChange={e => setFormData({ ...formData, prenom: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Nom</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    value={formData.nom}
                                    onChange={e => setFormData({ ...formData, nom: e.target.value })}
                                    required
                                />
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Email Professionnel</label>
                            <input
                                type="email"
                                className="form-input"
                                value={formData.email}
                                onChange={e => setFormData({ ...formData, email: e.target.value })}
                                required
                            />
                        </div>
                        <div style={{ display: 'flex', gap: '12px', marginTop: '32px' }}>
                            <button type="submit" className="btn btn-primary">Enregistrer les modifications</button>
                            <button type="button" className="btn btn-ghost" onClick={() => setIsEditing(false)}>Annuler</button>
                        </div>
                    </form>
                ) : isChangingPassword ? (
                    <form onSubmit={handleUpdatePassword} className="space-y-6">
                        <div className="form-group">
                            <label className="form-label">Nouveau mot de passe</label>
                            <input
                                type="password"
                                className="form-input"
                                placeholder="8 caractères minimum"
                                value={formData.password}
                                onChange={e => setFormData({ ...formData, password: e.target.value })}
                                required
                                minLength={8}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Confirmer le mot de passe</label>
                            <input
                                type="password"
                                className="form-input"
                                placeholder="Répétez le mot de passe"
                                value={formData.confirmPassword}
                                onChange={e => setFormData({ ...formData, confirmPassword: e.target.value })}
                                required
                                minLength={8}
                            />
                        </div>
                        <div style={{ display: 'flex', gap: '12px', marginTop: '32px' }}>
                            <button type="submit" className="btn btn-primary">Mettre à jour la clé d'accès</button>
                            <button type="button" className="btn btn-ghost" onClick={() => setIsChangingPassword(false)}>Annuler</button>
                        </div>
                    </form>
                ) : (
                    <div className="space-y-6">
                        <div style={{ display: 'grid', gap: '24px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                <span className="form-label" style={{ margin: 0 }}>Nom complet</span>
                                <span style={{ fontWeight: '700', color: 'white' }}>{profile.prenom} {profile.nom}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                <span className="form-label" style={{ margin: 0 }}>Identifiant</span>
                                <span style={{ fontWeight: '700', color: 'var(--text2)' }}>@{profile.username}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                <span className="form-label" style={{ margin: 0 }}>Email</span>
                                <span style={{ fontWeight: '700', color: 'white' }}>{profile.email}</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                <span className="form-label" style={{ margin: 0 }}>Date d'ancrage</span>
                                <span style={{ fontWeight: '700', color: 'var(--text3)' }}>{new Date(profile.created_at).toLocaleDateString()}</span>
                            </div>
                        </div>

                        <div style={{ marginTop: '40px', display: 'flex', gap: '16px' }}>
                            <button className="btn btn-primary" onClick={() => setIsEditing(true)}>
                                <Edit2 size={16} />
                                Modifier le profil
                            </button>
                            <button className="btn btn-ghost" onClick={() => setIsChangingPassword(true)}>
                                <Zap size={16} />
                                Changer le mot de passe
                            </button>
                        </div>
                    </div>
                )}
            </div>

            <style>{`
                .profile-hero {
                    animation: float-profile 6s ease-in-out infinite;
                }
                .avatar-large {
                    transition: transform 0.3s ease;
                }
                .avatar-large:hover {
                    transform: scale(1.05) rotate(5deg);
                }
                @keyframes float-profile {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-10px); }
                }
            `}</style>
        </div>
    )
}
