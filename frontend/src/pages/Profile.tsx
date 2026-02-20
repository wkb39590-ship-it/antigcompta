import { useState, useEffect } from 'react'
import apiService from '../api'

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

    useEffect(() => {
        const loadData = async () => {
            try {
                const token = localStorage.getItem('access_token')
                if (!token) throw new Error('Non authentifié')

                const [profData, statsData] = await Promise.all([
                    apiService.getProfile(token),
                    apiService.getAgentStats(token)
                ])

                setProfile(profData)
                setStats(statsData)
            } catch (err: any) {
                console.error('[Profile] Error loading data:', err)
                setError(err.message || 'Erreur lors du chargement du profil')
            } finally {
                setLoading(false)
            }
        }

        loadData()
    }, [])

    if (loading) return <div className="loading-state">Chargement du profil...</div>
    if (error) return <div className="error-card">{error}</div>
    if (!profile) return null

    const initials = `${profile.prenom?.[0] || ''}${profile.nom?.[0] || profile.username?.[0] || ''}`.toUpperCase()

    return (
        <div className="profile-container" style={{ padding: '40px', maxWidth: '1000px', margin: '0 auto' }}>
            {/* Header Profil Premium */}
            <div className="glass-card profile-hero" style={{
                display: 'flex',
                alignItems: 'center',
                gap: '32px',
                padding: '40px',
                borderRadius: '24px',
                marginBottom: '32px',
                background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05))',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                boxShadow: '0 20px 40px rgba(0,0,0,0.1)'
            }}>
                <div className="avatar-large" style={{
                    width: '120px',
                    height: '120px',
                    borderRadius: '50%',
                    background: 'linear-gradient(45deg, var(--accent), #a78bfa)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '48px',
                    fontWeight: 'bold',
                    color: 'white',
                    boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)'
                }}>
                    {initials}
                </div>
                <div>
                    <h1 style={{ fontSize: '32px', marginBottom: '8px', color: 'var(--text1)' }}>
                        {profile.prenom} {profile.nom}
                    </h1>
                    <p style={{ color: 'var(--text3)', fontSize: '16px', marginBottom: '16px' }}>
                        @{profile.username} • {profile.is_admin ? '🏆 Administrateur' : '💼 Agent Comptable'}
                    </p>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <span className="badge" style={{ padding: '4px 12px', borderRadius: '20px', background: 'rgba(99, 102, 241, 0.1)', color: 'var(--accent)', fontSize: '12px' }}>
                            {stats?.cabinet_nom || 'Plan Comptable Marocain'}
                        </span>
                    </div>
                </div>
            </div>

            {/* Statistiques Grille */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '24px', marginBottom: '32px' }}>
                <div className="stat-card glass-card" style={{ padding: '24px', borderRadius: '20px', textAlign: 'center' }}>
                    <div style={{ fontSize: '40px', marginBottom: '8px' }}>📄</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--accent)' }}>{stats?.total_factures_validees || 0}</div>
                    <div style={{ color: 'var(--text2)', fontSize: '14px' }}>Factures Validées</div>
                </div>

                <div className="stat-card glass-card" style={{ padding: '24px', borderRadius: '20px', textAlign: 'center' }}>
                    <div style={{ fontSize: '40px', marginBottom: '8px' }}>🏢</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--success)' }}>{stats?.total_societes_gerees || 0}</div>
                    <div style={{ color: 'var(--text2)', fontSize: '14px' }}>Sociétés Gérées</div>
                </div>

                <div className="stat-card glass-card" style={{ padding: '24px', borderRadius: '20px', textAlign: 'center' }}>
                    <div style={{ fontSize: '40px', marginBottom: '8px' }}>⚡</div>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', color: 'var(--warning)' }}>98%</div>
                    <div style={{ color: 'var(--text2)', fontSize: '14px' }}>Score de Précision IA</div>
                </div>
            </div>

            {/* Informations Détaillées */}
            <div className="glass-card" style={{ padding: '32px', borderRadius: '24px' }}>
                <h3 style={{ marginBottom: '24px', borderBottom: '1px solid var(--border)', paddingBottom: '12px' }}>Informations du Compte</h3>
                <div style={{ display: 'grid', gap: '20px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: 'var(--text3)' }}>Email professionnel</span>
                        <span style={{ fontWeight: '500' }}>{profile.email}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: 'var(--text3)' }}>Nom d'utilisateur</span>
                        <span style={{ fontWeight: '500' }}>{profile.username}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ color: 'var(--text3)' }}>Compte créé le</span>
                        <span style={{ fontWeight: '500' }}>{new Date(profile.created_at).toLocaleDateString()}</span>
                    </div>
                </div>

                <div style={{ marginTop: '32px', display: 'flex', gap: '12px' }}>
                    <button className="btn-primary" style={{ padding: '10px 24px', fontSize: '14px' }}>
                        Modifier le profil
                    </button>
                    <button className="btn-secondary" style={{ padding: '10px 24px', fontSize: '14px' }}>
                        Changer le mot de passe
                    </button>
                </div>
            </div>

            <style>{`
                .glass-card {
                    background: var(--bg2);
                    border: 1px solid var(--border);
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }
                .glass-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                }
                .stat-card {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }
                .avatar-large {
                    animation: pulse 2s infinite ease-in-out;
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                    100% { transform: scale(1); }
                }
            `}</style>
        </div>
    )
}
