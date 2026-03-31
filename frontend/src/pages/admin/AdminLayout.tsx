import React from 'react';
import { useNavigate } from 'react-router-dom';
import { getAdminUser, clearAdminSession } from '../../utils/adminTokenDecoder';
import {
  LayoutDashboard,
  Building2,
  Building,
  Users,
  Link as LinkIcon,
  History,
  User,
  LogOut,
  Zap,
  Inbox
} from 'lucide-react';

interface AdminLayoutProps {
  children: React.ReactNode;
  currentPage?: string;
}

export const AdminLayout: React.FC<AdminLayoutProps> = ({ children, currentPage = 'dashboard' }) => {
  const navigate = useNavigate();
  const adminUser = getAdminUser();
  const adminName = adminUser ? `${adminUser.prenom || adminUser.username}` : 'Admin';

  const cabinets = JSON.parse(localStorage.getItem('cabinets') || '[]');
  const currentCabinet = cabinets.find((c: any) => c.id === adminUser?.cabinet_id);
  const cabinetLabel = !adminUser?.is_super_admin && currentCabinet ? currentCabinet.nom : '';

  const handleLogout = () => {
    clearAdminSession();
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/admin/dashboard', id: 'dashboard', icon: <LayoutDashboard size={20} /> },
    { label: 'Cabinets', path: '/admin/cabinets', id: 'cabinets', icon: <Building2 size={20} />, superOnly: true },
    { label: 'Sociétés', path: '/admin/societes', id: 'societes', icon: <Building size={20} />, adminOnly: true },
    { label: 'Agents', path: '/admin/agents', id: 'agents', icon: <Users size={20} /> },
    { label: 'Liaisons', path: '/admin/associations', id: 'associations', icon: <LinkIcon size={20} />, adminOnly: true },
    { label: 'Historique', path: '/admin/history', id: 'history', icon: <History size={20} /> },
    { label: 'Performance IA', path: '/admin/ai-performance', id: 'ai-performance', icon: <Zap size={20} /> },
    { label: 'Demandes d\'accès', path: '/admin/demandes', id: 'demandes', icon: <Inbox size={20} /> },
    { label: 'Mon Profil', path: '/admin/profile', id: 'profile', icon: <User size={20} /> },
  ].filter(item => {
    if (item.superOnly && !adminUser?.is_super_admin) return false;
    if (item.adminOnly && adminUser?.is_super_admin) return false;
    return true;
  });

  return (
    <div className="admin-layout">
      {/* Background Aurora Foundation */}
      <div className="aurora-viewport">
        <div className="aurora-blob blob-1"></div>
        <div className="aurora-blob blob-2"></div>
        <div className="aurora-blob blob-3"></div>
      </div>

      <div className="aurora-sidebar-wrapper">
        <nav className="aurora-sidebar aurora-card">
          <div className="aurora-brand">
            <div className="brand-texts">
              <h2 className="glass-text">SYSTEM</h2>
              <p>Administration Professionnelle</p>
            </div>
          </div>

          <div className="admin-mini-profile">
            <div className="mini-avatar">{adminName[0].toUpperCase()}</div>
            <div className="mini-info">
              <span className="mini-name">{adminName}</span>
              <span className="mini-status">{cabinetLabel || 'Super Admin'}</span>
            </div>
          </div>

          <ul className="aurora-nav admin-scroll">
            {navItems.map((item) => (
              <li key={item.path}>
                <button
                  className={`aurora-nav-link ${currentPage === item.id ? 'active' : ''}`}
                  onClick={() => navigate(item.path)}
                >
                  <span className="nav-icon-bg">{item.icon}</span>
                  <span className="nav-text">{item.label}</span>
                </button>
              </li>
            ))}
          </ul>

          <div className="sidebar-footer">
            <button className="aurora-btn-logout" onClick={handleLogout}>
              <LogOut size={18} />
              <span>Se déconnecter</span>
            </button>
          </div>
        </nav>
      </div>

      <main className="aurora-main admin-scroll">
        <header className="aurora-header aurora-card">
          <div className="header-breadcrumbs glass-text">
            {adminUser?.is_super_admin ? 'Système Central' : (cabinetLabel || 'Cabinet')} • <span className="current-page-text">{navItems.find(i => i.id === currentPage)?.label || currentPage}</span>
          </div>
          <div className="header-actions">
            <div className="header-time glass-pill">
              {new Date().toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' })}
            </div>
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
          position: relative;
          z-index: 1;
        }

        .aurora-sidebar-wrapper {
          width: 280px;
          height: 100%;
          flex-shrink: 0;
        }

        .aurora-sidebar {
          height: 100%;
          display: flex;
          flex-direction: column;
          padding: 24px;
          border-radius: 32px !important;
        }

        .aurora-brand {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 0 0 40px 0;
        }

        .brand-icon-wrapper {
          width: 44px;
          height: 44px;
          background: var(--aurora-gradient);
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 10px 20px rgba(99, 102, 241, 0.2);
        }

        .brand-texts h2 {
          margin: 0;
          font-size: 22px;
          letter-spacing: 3px;
          font-weight: 900;
          line-height: 1;
        }

        .brand-texts p {
          margin: 4px 0 0 0;
          font-size: 10px;
          font-weight: 700;
          text-transform: uppercase;
          color: var(--text3);
          letter-spacing: 1px;
        }

        .admin-mini-profile {
          background: rgba(255, 255, 255, 0.4);
          padding: 16px;
          border-radius: 20px;
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 30px;
          border: 1px solid rgba(255, 255, 255, 0.5);
        }

        .mini-avatar {
          width: 42px;
          height: 42px;
          border-radius: 12px;
          background: var(--aurora-gradient);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 800;
          font-size: 18px;
          box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        }

        .mini-name {
          display: block;
          font-size: 14px;
          font-weight: 800;
          color: var(--text);
          font-family: 'Outfit', sans-serif;
        }

        .mini-status {
          font-size: 11px;
          color: var(--success);
          display: flex;
          align-items: center;
          gap: 6px;
          font-weight: 700;
        }

        .mini-status::before {
          content: '';
          width: 6px;
          height: 6px;
          background: var(--success);
          border-radius: 50%;
          box-shadow: 0 0 10px var(--success);
        }

        .aurora-nav {
          list-style: none;
          padding: 0;
          margin: 0;
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .aurora-nav-link {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 12px 16px;
          border: none;
          background: transparent;
          color: var(--text2);
          border-radius: 16px;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          font-family: 'Inter', sans-serif;
        }

        .aurora-nav-link:hover {
          background: rgba(99, 102, 241, 0.05);
          color: var(--accent);
          transform: translateX(4px);
        }

        .aurora-nav-link.active {
          background: white;
          color: var(--accent);
          box-shadow: 0 8px 20px rgba(99, 102, 241, 0.08);
          border: 1px solid rgba(99, 102, 241, 0.1);
        }

        .nav-icon-bg {
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 12px;
          background: rgba(255, 255, 255, 0.5);
          transition: all 0.3s;
        }

        .aurora-nav-link.active .nav-icon-bg {
          background: var(--aurora-gradient);
          color: white;
          box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
        }

        .nav-text {
          font-size: 14px;
          font-weight: 700;
        }

        .aurora-btn-logout {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
          padding: 14px;
          border-radius: 16px;
          border: 1px solid rgba(239, 68, 68, 0.1);
          background: rgba(239, 68, 68, 0.04);
          color: var(--danger);
          font-weight: 800;
          font-size: 13px;
          cursor: pointer;
          transition: all 0.3s;
          font-family: 'Outfit', sans-serif;
        }

        .aurora-btn-logout:hover {
          background: var(--danger);
          color: white;
          box-shadow: 0 10px 20px rgba(239, 68, 68, 0.2);
        }

        .aurora-main {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 24px;
          height: 100%;
          overflow: hidden;
        }

        .admin-scroll {
          overflow-y: auto;
          scrollbar-width: thin;
          scrollbar-color: rgba(99, 102, 241, 0.2) transparent;
        }

        .admin-scroll::-webkit-scrollbar { width: 6px; }
        .admin-scroll::-webkit-scrollbar-track { background: transparent; }
        .admin-scroll::-webkit-scrollbar-thumb { background: rgba(99, 102, 241, 0.2); border-radius: 10px; }
        .admin-scroll::-webkit-scrollbar-thumb:hover { background: rgba(99, 102, 241, 0.4); }

        .aurora-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 32px;
          min-height: 80px;
        }

        .header-breadcrumbs {
          font-size: 14px;
          font-weight: 700;
          font-family: 'Outfit', sans-serif;
        }

        .current-page-text {
          color: var(--text);
          font-weight: 900;
          opacity: 1;
        }

        .aurora-view-container {
          flex: 1;
        }

        @media (max-width: 1100px) {
          .admin-layout { padding: 12px; flex-direction: column; }
          .aurora-sidebar-wrapper { width: 100%; height: auto; }
          .admin-mini-profile { display: none; }
          .aurora-sidebar { border-radius: 20px !important; }
        }
      `}</style>
    </div>
  );
};
