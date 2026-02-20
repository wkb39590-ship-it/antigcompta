import { Routes, Route, NavLink, Navigate, useLocation, Outlet } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import FactureDetail from './pages/FactureDetail'
import PcmPage from './pages/PcmPage'
import Profile from './pages/Profile'
import Login from './pages/Login'

import CabinetSelector from './pages/CabinetSelector'
import { getSessionContext } from './utils/tokenDecoder'
import { isAdminLoggedIn } from './utils/adminTokenDecoder'

// Import des pages admin
import { AdminLogin } from './pages/admin/AdminLogin'
import { AdminLayout } from './pages/admin/AdminLayout'
import { AdminDashboard } from './pages/admin/AdminDashboard'
import { AdminCabinets } from './pages/admin/AdminCabinets'
import { AdminSocietes } from './pages/admin/AdminSocietes'
import { AdminAgents } from './pages/admin/AdminAgents'
import { AdminAssociations } from './pages/admin/AdminAssociations'

// Composant de protection de route pour utilisateurs normaux
function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const session = getSessionContext()
    if (!session) {
        return <Navigate to="/login" replace />
    }
    return <>{children}</>
}

// Composant de protection de route pour les administrateurs
function AdminProtectedRoute({ children }: { children: React.ReactNode }) {
    if (!isAdminLoggedIn()) {
        return <Navigate to="/admin/login" replace />
    }
    return <>{children}</>
}

function Sidebar() {
    const session = getSessionContext()
    const societeDisplay = session?.societe_raison_sociale || 'Société non sélectionnée'

    const navItems = [
        { to: '/dashboard', icon: '📊', label: 'Tableau de bord' },
        { to: '/upload', icon: '📤', label: 'Importer facture' },
        { to: '/pcm', icon: '📒', label: 'Plan Comptable' },
        { to: '/profile', icon: '👤', label: 'Mon Profil' },
    ]


    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <h1>⚡ Comptabilité<br />Zéro Saisie</h1>
                <p>PCM / CGNC Maroc</p>
            </div>
            <nav className="sidebar-nav">
                {navItems.map(item => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        {item.label}
                    </NavLink>
                ))}
            </nav>
            <div className="sidebar-footer" style={{ padding: '20px', borderTop: '1px solid var(--border)', marginTop: 'auto' }}>
                <NavLink to="/profile" className="user-profile-mini" style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px',
                    borderRadius: '12px',
                    textDecoration: 'none',
                    marginBottom: '16px',
                    transition: 'background 0.2s',
                    background: 'rgba(255,255,255,0.03)'
                }}>
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
                        color: 'white'
                    }}>
                        {session?.username?.[0].toUpperCase() || 'U'}
                    </div>
                    <div style={{ overflow: 'hidden' }}>
                        <div style={{ fontSize: '13px', fontWeight: '600', color: 'var(--text)', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                            {session?.username}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text3)', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>
                            {societeDisplay}
                        </div>
                    </div>
                </NavLink>

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
                    🚪 Déconnexion
                </button>
            </div>

        </aside>
    )
}

export default function App() {
    return (
        <Routes>
            {/* Public Auth Pages */}
            <Route path="/login" element={<Login />} />
            <Route path="/select-cabinet" element={<CabinetSelector />} />

            {/* Admin Login (public) */}
            <Route path="/admin/login" element={<AdminLogin />} />

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
                <Route path="profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            </Route>


            {/* Fallback */}
            <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
    )
}
