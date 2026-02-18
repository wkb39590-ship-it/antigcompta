import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import FactureDetail from './pages/FactureDetail'
import PcmPage from './pages/PcmPage'

function Sidebar() {
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
            <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border)' }}>
                <div style={{ fontSize: '11px', color: 'var(--text3)' }}>
                    Backend: <a href="http://localhost:8090/docs" target="_blank" rel="noreferrer" style={{ color: 'var(--accent)' }}>API Docs</a>
                </div>
            </div>
        </aside>
    )
}

export default function App() {
    return (
        <BrowserRouter>
            <div className="app-layout">
                <Sidebar />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Navigate to="/dashboard" replace />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/upload" element={<Upload />} />
                        <Route path="/factures/:id" element={<FactureDetail />} />
                        <Route path="/pcm" element={<PcmPage />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    )
}
