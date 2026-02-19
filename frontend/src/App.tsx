import { Routes, Route, NavLink, Navigate, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import FactureDetail from './pages/FactureDetail'
import PcmPage from './pages/PcmPage'
import Login from './pages/Login'
import CabinetSelector from './pages/CabinetSelector'
import { getSessionContext } from './utils/tokenDecoder'

// Composant de protection de route
function ProtectedRoute({ children }: { children: React.ReactNode }) {
    const session = getSessionContext()
    if (!session) {
        return <Navigate to="/login" replace />
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
            <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border)', marginTop: 'auto' }}>
                <div style={{ fontSize: '11px', color: 'var(--text3)', marginBottom: '12px' }}>
                    🏢 {session ? `${societeDisplay}` : 'Societe non sélectionnée'}
                </div>
                <button
                    onClick={() => {
                        localStorage.clear()
                        window.location.href = '/login'
                    }}
                    style={{
                        width: '100%',
                        padding: '8px 12px',
                        background: 'var(--border)',
                        border: 'none',
                        borderRadius: '6px',
                        color: 'var(--text2)',
                        fontSize: '12px',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                    }}
                    onMouseOver={(e) => {
                        e.currentTarget.style.background = '#f44'
                        e.currentTarget.style.color = 'white'
                    }}
                    onMouseOut={(e) => {
                        e.currentTarget.style.background = 'var(--border)'
                        e.currentTarget.style.color = 'var(--text2)'
                    }}
                >
                    🚪 Déconnexion
                </button>
                <div style={{ fontSize: '11px', color: 'var(--text3)', marginTop: '12px' }}>
                    Backend: <a href="http://localhost:8090/docs" target="_blank" rel="noreferrer" style={{ color: 'var(--accent)' }}>API Docs</a>
                </div>
            </div>
        </aside>
    )
}

export default function App() {
    const location = useLocation()
    const isAuthPage = ['/login', '/select-cabinet'].includes(location.pathname)

    if (isAuthPage) {
        return (
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/select-cabinet" element={<CabinetSelector />} />
                <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
        )
    }

    return (
        <div className="app-layout">
            <Sidebar />
            <main className="main-content">
                <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/login" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/select-cabinet" element={<Navigate to="/dashboard" replace />} />
                    
                    {/* Routes protégées */}
                    <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                    <Route path="/upload" element={<ProtectedRoute><Upload /></ProtectedRoute>} />
                    <Route path="/factures/:id" element={<ProtectedRoute><FactureDetail /></ProtectedRoute>} />
                    <Route path="/pcm" element={<ProtectedRoute><PcmPage /></ProtectedRoute>} />
                </Routes>
            </main>
        </div>
    )
}
