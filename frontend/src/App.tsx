import { useState, useEffect } from 'react'
import { Routes, Route, NavLink, Navigate, useLocation, Outlet } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import FactureDetail from './pages/FactureDetail'
import PcmPage from './pages/PcmPage'
import Profile from './pages/Profile'
import History from './pages/History'
import SupplierDirectory from './pages/SupplierDirectory'
import Login from './pages/Login'

import CabinetSelector from './pages/CabinetSelector'
import { getSessionContext } from './utils/tokenDecoder'
import { isAdminLoggedIn } from './utils/adminTokenDecoder'
import { API_CONFIG } from './config/apiConfig'

// Import des pages admin
// AdminLogin supprimé car unifié dans Login.tsx
import { AdminLayout } from './pages/admin/AdminLayout'
import { AdminDashboard } from './pages/admin/AdminDashboard'
import { AdminCabinets } from './pages/admin/AdminCabinets'
import { AdminSocietes } from './pages/admin/AdminSocietes'
import { AdminAgents } from './pages/admin/AdminAgents'
import { AdminAssociations } from './pages/admin/AdminAssociations'
import { AdminProfile } from './pages/admin/AdminProfile'
import { AdminHistory } from './pages/admin/AdminHistory'

// ──────────────────────────────────────────────────────────────────────────
// COMPOSANTS DE PROTECTION (Security Guards)
// ──────────────────────────────────────────────────────────────────────────

/**
 * Empêche l'accès aux pages si l'agent n'est pas connecté.
 */
function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const session = getSessionContext()
    if (!session) {
        return <Navigate to="/login" replace />
    }
    return <>{children}</>
}

/**
 * Empêche l'accès aux pages d'administration si l'utilisateur n'est pas admin.
 */
function AdminProtectedRoute({ children }: { children: React.ReactNode }) {
    if (!isAdminLoggedIn()) {
        return <Navigate to="/login" replace />
    }
    return <>{children}</>
}

function Sidebar() {
    const session = getSessionContext()
    const [showSocMenu, setShowSocMenu] = useState(false)
    const [societes, setSocietes] = useState<any[]>([])
    const [loadingSoc, setLoadingSoc] = useState(false)

    const societeDisplay = session?.societe_raison_sociale || 'Société non sélectionnée'

    const navItems = [
        { to: '/dashboard', label: 'Tableau de bord' },
        { to: '/upload', label: 'Transmission' },
        { to: '/pcm', label: 'Plan Comptable' },
        { to: '/history', label: 'Historique' },
        { to: '/mappings', label: 'Répertoire' },
        { to: '/profile', label: 'Mon Profil' },
    ]

    useEffect(() => {
        if (showSocMenu && session?.cabinet_id) {
            loadSocietes()
        }
    }, [showSocMenu])

    const loadSocietes = async () => {
        setLoadingSoc(true)
        try {
            const token = localStorage.getItem('access_token')
            const response = await fetch(`${API_CONFIG.AUTH.SOCIETES_AUTH}?token=${token}&cabinet_id=${session?.cabinet_id}`)
            if (response.ok) {
                const data = await response.json()
                setSocietes(data)
            }
        } catch (err) {
            console.error('Error loading societes:', err)
        } finally {
            setLoadingSoc(false)
        }
    }

    const handleSwitchSociete = async (socId: number) => {
        const token = localStorage.getItem('access_token')
        if (!token || !session?.cabinet_id) return

        try {
            const response = await fetch(`${API_CONFIG.AUTH.SELECT_SOCIETE}?token=${token}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cabinet_id: session.cabinet_id,
                    societe_id: socId
                })
            })

            if (response.ok) {
                const data = await response.json()
                localStorage.setItem('session_token', data.session_token)
                localStorage.setItem('current_societe_id', String(socId))
                window.location.reload()
            }
        } catch (err) {
            console.error('Switch failed:', err)
        }
    }

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <h1>comptafacile</h1>
                <p>Gestion Comptable Intégrale</p>
            </div>
            <nav className="sidebar-nav">
                {navItems.map(item => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
                    >
                        {item.label}
                    </NavLink>
                ))}
            </nav>
            <div className="sidebar-footer" style={{ padding: '20px', borderTop: '1px solid var(--border)', marginTop: 'auto', position: 'relative' }}>

                {showSocMenu && (
                    <div className="soc-switcher-menu" style={{
                        position: 'absolute',
                        bottom: '100%',
                        left: '10px',
                        right: '10px',
                        background: '#1e293b',
                        borderRadius: '12px',
                        border: '1px solid var(--border)',
                        padding: '8px',
                        marginBottom: '10px',
                        boxShadow: '0 10px 25px rgba(0,0,0,0.3)',
                        zIndex: 100,
                        maxHeight: '300px',
                        overflowY: 'auto'
                    }}>
                        <div style={{ fontSize: '10px', fontWeight: 'bold', color: 'var(--text3)', padding: '8px', textTransform: 'uppercase' }}>
                            Changer de société
                        </div>
                        {loadingSoc ? (
                            <div style={{ padding: '10px', fontSize: '12px' }}>Chargement...</div>
                        ) : (
                            societes.map(s => (
                                <button
                                    key={s.id}
                                    onClick={() => handleSwitchSociete(s.id)}
                                    style={{
                                        width: '100%',
                                        padding: '10px',
                                        textAlign: 'left',
                                        background: s.id === session?.societe_id ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: s.id === session?.societe_id ? 'var(--accent)' : 'white',
                                        fontSize: '13px',
                                        cursor: 'pointer',
                                        display: 'block',
                                        transition: 'background 0.2s',
                                        fontWeight: s.id === session?.societe_id ? 'bold' : 'normal'
                                    }}
                                    onMouseOver={(e) => (e.currentTarget.style.background = 'rgba(255,255,255,0.05)')}
                                    onMouseOut={(e) => (e.currentTarget.style.background = s.id === session?.societe_id ? 'rgba(99, 102, 241, 0.2)' : 'transparent')}
                                >
                                    {s.raison_sociale}
                                </button>
                            ))
                        )}
                    </div>
                )}

                <div
                    className="user-profile-mini"
                    onClick={() => setShowSocMenu(!showSocMenu)}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '12px',
                        borderRadius: '12px',
                        textDecoration: 'none',
                        marginBottom: '16px',
                        transition: 'background 0.2s',
                        background: showSocMenu ? 'rgba(99, 102, 241, 0.1)' : 'rgba(255,255,255,0.03)',
                        cursor: 'pointer',
                        border: showSocMenu ? '1px solid var(--accent)' : '1px solid transparent'
                    }}
                >
                    <div style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: '50%',
                        background: 'var(--accent)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '14px',
                        fontWeight: 'bold',
                        color: 'white',
                        flexShrink: 0
                    }}>
                        {session?.username?.[0].toUpperCase() || 'U'}
                    </div>
                    <div style={{ overflow: 'hidden', flexGrow: 1 }}>
                        <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text)', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                            {session?.username}
                        </div>
                        <div style={{ fontSize: '11px', color: showSocMenu ? 'var(--accent)' : 'var(--text3)', whiteSpace: 'nowrap', textOverflow: 'ellipsis', display: 'flex', alignItems: 'center', gap: '4px' }}>
                            {societeDisplay} <span>{showSocMenu ? '▲' : '▼'}</span>
                        </div>
                    </div>
                </div>

                <button
                    onClick={() => {
                        localStorage.clear()
                        window.location.href = '/login'
                    }}
                    className="logout-btn"
                    style={{
                        width: '100%',
                        padding: '10px',
                        background: 'transparent',
                        border: '1px solid var(--border)',
                        borderRadius: '8px',
                        color: 'var(--text2)',
                        fontSize: '12px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        gap: '8px',
                        transition: 'all 0.2s'
                    }}
                >
                    Déconnexion
                </button>
            </div>

        </aside>
    )
}

/**
 * Composant racine de l'application.
 * Définit la structure des routes et les dépendances globales.
 */
export default function App() {
    return (
        <Routes>
            {/* Public Auth Pages */}
            <Route path="/login" element={<Login />} />
            <Route path="/select-cabinet" element={<CabinetSelector />} />

            {/* Admin Protected Routes */}
            <Route
                path="/admin/dashboard"
                element={
                    <AdminProtectedRoute>
                        <AdminLayout currentPage="dashboard">
                            <AdminDashboard />
                        </AdminLayout>
                    </AdminProtectedRoute>
                }
            />
            <Route
                path="/admin/cabinets"
                element={
                    <AdminProtectedRoute>
                        <AdminLayout currentPage="cabinets">
                            <AdminCabinets />
                        </AdminLayout>
                    </AdminProtectedRoute>
                }
            />
            <Route
                path="/admin/societes"
                element={
                    <AdminProtectedRoute>
                        <AdminLayout currentPage="societes">
                            <AdminSocietes />
                        </AdminLayout>
                    </AdminProtectedRoute>
                }
            />
            <Route
                path="/admin/agents"
                element={
                    <AdminProtectedRoute>
                        <AdminLayout currentPage="agents">
                            <AdminAgents />
                        </AdminLayout>
                    </AdminProtectedRoute>
                }
            />
            <Route
                path="/admin/associations"
                element={
                    <AdminProtectedRoute>
                        <AdminLayout currentPage="associations">
                            <AdminAssociations />
                        </AdminLayout>
                    </AdminProtectedRoute>
                }
            />
            <Route
                path="/admin/history"
                element={
                    <AdminProtectedRoute>
                        <AdminLayout currentPage="history">
                            <AdminHistory />
                        </AdminLayout>
                    </AdminProtectedRoute>
                }
            />
            <Route
                path="/admin/profile"
                element={
                    <AdminProtectedRoute>
                        <AdminLayout currentPage="profile">
                            <AdminProfile />
                        </AdminLayout>
                    </AdminProtectedRoute>
                }
            />

            {/* User Routes with Sidebar Layout */}
            <Route
                path="/"
                element={
                    <div className="app-layout">
                        <Sidebar />
                        <main className="main-content">
                            <Outlet />
                        </main>
                    </div>
                }
            >
                <Route index element={<Navigate to="/dashboard" replace />} />
                <Route path="dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                <Route path="upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
                <Route path="factures/:id" element={<ProtectedRoute><FactureDetail /></ProtectedRoute>} />
                <Route path="pcm" element={<ProtectedRoute><PcmPage /></ProtectedRoute>} />
                <Route path="history" element={<ProtectedRoute><History /></ProtectedRoute>} />
                <Route path="mappings" element={<ProtectedRoute><SupplierDirectory /></ProtectedRoute>} />
                <Route path="profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            </Route>


            {/* Fallback */}
            <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
    )
}
