import React from 'react';
import { useNavigate } from 'react-router-dom';
import { getAdminUser, clearAdminSession } from '../../utils/adminTokenDecoder';

interface AdminLayoutProps {
  children: React.ReactNode;
  currentPage?: string;
}

export const AdminLayout: React.FC<AdminLayoutProps> = ({ children, currentPage = 'dashboard' }) => {
  const navigate = useNavigate();
  const adminUser = getAdminUser();
  const adminName = adminUser ? `${adminUser.prenom || adminUser.username}` : 'Admin';

  // Récupérer le nom du cabinet pour les admins simples
  const cabinets = JSON.parse(localStorage.getItem('cabinets') || '[]');
  const currentCabinet = cabinets.find((c: any) => c.id === adminUser?.cabinet_id);
  const cabinetLabel = !adminUser?.is_super_admin && currentCabinet ? currentCabinet.nom : '';

  const handleLogout = () => {
    clearAdminSession();
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/admin/dashboard', id: 'dashboard', icon: '📊' },
    { label: 'Cabinets', path: '/admin/cabinets', id: 'cabinets', icon: '🏢', superOnly: true },
    { label: 'Sociétés', path: '/admin/societes', id: 'societes', icon: '🏬', adminOnly: true },
    { label: 'Agents', path: '/admin/agents', id: 'agents', icon: '👥' },
    { label: 'Associations', path: '/admin/associations', id: 'associations', icon: '🔗', adminOnly: true },
    { label: 'Historique', path: '/admin/history', id: 'history', icon: '📜' },
    { label: 'Profil', path: '/admin/profile', id: 'profile', icon: '👤' },
  ].filter(item => {
    if (item.superOnly && !adminUser?.is_super_admin) return false;
    if (item.adminOnly && adminUser?.is_super_admin) return false;
    return true;
  });

  return (
    <div className="admin-layout aurora-bg">
      <div className="aurora-sidebar-wrapper">
        <nav className="aurora-sidebar aurora-card">
          <div className="aurora-brand">
            <div className="brand-icon-wrapper animate-float">
              <span className="brand-logo">⚡</span>
            </div>
            <div className="brand-texts">
              <h2 className="glass-text">COMPTAFACILE</h2>
              <p>Administration Système</p>
            </div>
          </div>

          <div className="admin-mini-profile">
            <div className="mini-avatar">{adminName[0].toUpperCase()}</div>
            <div className="mini-info">
              <span className="mini-name">{adminName}</span>
              <span className="mini-status">{cabinetLabel || 'En ligne'}</span>
            </div>
          </div>

          <div className="nav-divider" />

          <ul className="aurora-nav admin-scroll">
            {navItems.map((item) => (
              <li key={item.path}>
                <button
                  className={`aurora-nav-link ${currentPage === item.id ? 'active' : ''}`}
                  onClick={() => navigate(item.path)}
                >
                  <span className="nav-icon-bg">{item.icon}</span>
                  <span className="nav-text">{item.label}</span>
                  {currentPage === item.id && <div className="active-dot" />}
                </button>
              </li>
            ))}
          </ul>

          <div className="sidebar-footer">
            <button className="aurora-btn-logout" onClick={handleLogout}>
              <span className="logout-icon">🚪</span>
              <span>Quitter la session</span>
            </button>
          </div>
        </nav>
      </div>

      <main className="aurora-main admin-scroll">
        <header className="aurora-header">
          <div className="header-breadcrumbs">
            {adminUser?.is_super_admin ? 'Système' : (cabinetLabel || 'Admin')} / <span className="current-page-text">{navItems.find(i => i.id === currentPage)?.label || currentPage}</span>
          </div>
          <div className="header-actions">
            <div className="header-time">{new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}</div>
          </div>
        </header>
        <div className="aurora-view-container">
          {children}
        </div>
      </main>

      <style>{`
        .admin-layout {
          display: flex;
          height: 100vh;
          width: 100vw;
          overflow: hidden;
          padding: 24px;
          gap: 24px;
        }

        .aurora-sidebar-wrapper {
          width: 280px;
          height: 100%;
        }

        .aurora-sidebar {
          height: 100%;
          display: flex;
          flex-direction: column;
          padding: 20px;
          border-radius: 32px;
        }

        .aurora-brand {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 10px 10px 30px 10px;
        }

        .brand-icon-wrapper {
          width: 45px;
          height: 45px;
          background: var(--admin-gradient);
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
          box-shadow: 0 10px 20px var(--admin-accent-glow);
        }

        .brand-texts h2 {
          margin: 0;
          font-size: 20px;
          letter-spacing: 2px;
          font-weight: 900;
        }

        .brand-texts p {
          margin: 0;
          font-size: 10px;
          text-transform: uppercase;
          color: var(--admin-text-dim);
          letter-spacing: 1px;
        }

        .admin-mini-profile {
          background: rgba(255, 255, 255, 0.05);
          padding: 15px;
          border-radius: 20px;
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 25px;
        }

        .mini-avatar {
          width: 40px;
          height: 40px;
          border-radius: 12px;
          background: var(--admin-secondary);
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 18px;
        }

        .mini-name {
          display: block;
          font-size: 14px;
          font-weight: 700;
          color: var(--admin-text);
        }

        .mini-status {
          font-size: 10px;
          color: #10b981;
          display: flex;
          align-items: center;
          gap: 5px;
        }

        .mini-status::before {
          content: '';
          width: 6px;
          height: 6px;
          background: #10b981;
          border-radius: 50%;
          box-shadow: 0 0 10px #10b981;
        }

        .nav-divider {
          height: 1px;
          background: var(--admin-glass-border);
          margin-bottom: 20px;
        }

        .aurora-nav {
          list-style: none;
          padding: 0;
          margin: 0;
          flex: 1;
          overflow-y: auto;
        }

        .aurora-nav li {
          margin-bottom: 8px;
        }

        .aurora-nav-link {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 12px 15px;
          border: none;
          background: transparent;
          color: var(--admin-text-dim);
          border-radius: 16px;
          cursor: pointer;
          transition: all 0.3s;
          position: relative;
        }

        .aurora-nav-link:hover {
          background: rgba(255, 255, 255, 0.05);
          color: var(--admin-text);
          padding-left: 20px;
        }

        .aurora-nav-link.active {
          background: var(--admin-gradient);
          color: white;
          box-shadow: 0 10px 20px rgba(99, 102, 241, 0.2);
        }

        .nav-icon-bg {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 10px;
          background: rgba(255, 255, 255, 0.05);
          font-size: 16px;
          transition: all 0.3s;
        }

        .aurora-nav-link.active .nav-icon-bg {
          background: rgba(255, 255, 255, 0.2);
        }

        .nav-text {
          font-size: 14px;
          font-weight: 600;
        }

        .active-dot {
          width: 6px;
          height: 6px;
          background: white;
          border-radius: 50%;
          margin-left: auto;
          box-shadow: 0 0 10px white;
        }

        .sidebar-footer {
          margin-top: 20px;
          padding-top: 20px;
          border-top: 1px solid var(--admin-glass-border);
        }

        .aurora-btn-logout {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          padding: 14px;
          border-radius: 16px;
          border: 1px solid var(--admin-glass-border);
          background: rgba(239, 68, 68, 0.05);
          color: #f87171;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.3s;
        }

        .aurora-btn-logout:hover {
          background: #ef4444;
          color: white;
          box-shadow: 0 10px 20px rgba(239, 68, 68, 0.3);
        }

        .aurora-main {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 24px;
          overflow-y: auto;
          padding-right: 10px;
        }

        .aurora-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 30px;
          background: var(--admin-card);
          backdrop-filter: blur(20px);
          border: 1px solid var(--admin-glass-border);
          border-radius: 24px;
          flex-shrink: 0;
        }

        .header-breadcrumbs {
          font-size: 14px;
          color: var(--admin-text-dim);
          font-weight: 600;
        }

        .current-page-text {
          color: var(--admin-accent);
          font-weight: 800;
        }

        .header-time {
          font-size: 13px;
          color: var(--admin-text-dim);
          font-weight: 600;
          text-transform: capitalize;
        }

        .aurora-view-container {
          flex: 1;
          animation: slideUp 0.6s ease-out;
        }

        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 1024px) {
          .admin-layout { padding: 10px; flex-direction: column; }
          .aurora-sidebar-wrapper { width: 100%; height: auto; }
          .admin-mini-profile { display: none; }
          .aurora-sidebar { border-radius: 20px; }
          .aurora-nav { display: flex; gap: 10px; overflow-x: auto; padding-bottom: 10px; }
          .aurora-nav li { margin-bottom: 0; }
        }
      `}</style>
    </div>
  );
};
