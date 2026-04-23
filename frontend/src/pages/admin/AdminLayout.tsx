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
    { label: 'Tableau de bord', path: '/admin/dashboard', id: 'dashboard', icon: <LayoutDashboard size={18} /> },
    { label: 'Cabinets', path: '/admin/cabinets', id: 'cabinets', icon: <Building2 size={18} />, superOnly: true },
    { label: 'Sociétés', path: '/admin/societes', id: 'societes', icon: <Building size={18} />, adminOnly: true },
    { label: 'Agents', path: '/admin/agents', id: 'agents', icon: <Users size={18} /> },
    { label: 'Liaisons', path: '/admin/associations', id: 'associations', icon: <LinkIcon size={18} />, adminOnly: true },
    { label: 'Historique', path: '/admin/history', id: 'history', icon: <History size={18} /> },
    { label: 'Performance IA', path: '/admin/ai-performance', id: 'ai-performance', icon: <Zap size={18} /> },
    { label: 'Demandes d\'accès', path: '/admin/demandes', id: 'demandes', icon: <Inbox size={18} /> },
    { label: 'Mon Profil', path: '/admin/profile', id: 'profile', icon: <User size={18} /> },
  ].filter(item => {
    if (item.superOnly && !adminUser?.is_super_admin) return false;
    if (item.adminOnly && adminUser?.is_super_admin) return false;
    return true;
  });

  return (
    <div className="admin-app-host">
      <aside className="admin-sidebar">
        <div className="sidebar-brand">
          <h1 className="brand-name">SYSTEM</h1>
          <span className="brand-sub">Administration Professionnelle</span>
        </div>

        <div className="agent-profile-section">
          <div className="profile-badge">
            <div className="avatar-letter">{adminName[0].toUpperCase()}</div>
            <div className="profile-text">
              <span className="user-displayName">{adminName}</span>
              <span className="user-entity">{cabinetLabel || 'Super Admin'}</span>
            </div>
          </div>
        </div>

        <nav className="sidebar-links">
          {navItems.map((item) => (
            <button
              key={item.path}
              className={`nav-link ${currentPage === item.id ? 'link-active' : ''}`}
              onClick={() => navigate(item.path)}
            >
              <span className="link-icon">{item.icon}</span>
              <span className="link-text">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-termination">
          <button onClick={handleLogout} className="btn-logout">
            <LogOut size={16} />
            <span>Se déconnecter</span>
          </button>
        </div>
      </aside>

      <main className="admin-viewport">
        <header className="viewport-header">
          <div className="breadcrumb">
            <span className="crumb-primary">{navItems.find(i => i.id === currentPage)?.label || currentPage}</span>
            <span className="crumb-divider">/</span>
            <span className="crumb-secondary">{cabinetLabel || 'Système Central'}</span>
          </div>
          <div className="viewport-time">
            {new Date().toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' }).toUpperCase()}
          </div>
        </header>
        
        <div className="viewport-content">
          {children}
        </div>
      </main>

      <style>{`
        .admin-app-host { display: flex; height: 100vh; background: #f8fafc; font-family: 'Inter', sans-serif; color: #1e293b; }

        /* Sidebar Styling */
        .admin-sidebar { width: 260px; background: #fff; border-right: 1px solid #e2e8f0; display: flex; flex-direction: column; }
        
        .sidebar-brand { padding: 24px; border-bottom: 1px solid #f1f5f9; }
        .brand-name { margin: 0; font-size: 20px; font-weight: 800; color: #0f172a; letter-spacing: 0.05em; }
        .brand-sub { font-size: 10px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.1em; display: block; margin-top: 2px; }

        .agent-profile-section { padding: 20px 24px; }
        .profile-badge { display: flex; align-items: center; gap: 12px; padding: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; }
        .avatar-letter { width: 32px; height: 32px; background: #3b82f6; color: #fff; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px; flex-shrink: 0; }
        .profile-text { display: flex; flex-direction: column; overflow: hidden; }
        .user-displayName { font-size: 13px; font-weight: 700; color: #1e293b; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; }
        .user-entity { font-size: 10px; font-weight: 600; color: #10b981; white-space: nowrap; text-overflow: ellipsis; overflow: hidden; }

        .sidebar-links { flex: 1; padding: 16px; display: flex; flex-direction: column; gap: 4px; }
        .nav-link { 
          display: flex; align-items: center; gap: 12px; padding: 10px 12px;
          border: none; background: transparent; border-radius: 4px;
          color: #64748b; font-size: 14px; font-weight: 500; text-align: left;
          cursor: pointer; transition: all 0.2s;
        }
        .nav-link:hover { background: #f1f5f9; color: #1e293b; }
        .nav-link.link-active { background: #eff6ff; color: #3b82f6; font-weight: 700; }
        .link-icon { display: flex; align-items: center; opacity: 0.7; }
        .link-active .link-icon { opacity: 1; }

        .sidebar-termination { padding: 16px 24px; border-top: 1px solid #f1f5f9; }
        .btn-logout { 
          width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;
          padding: 10px; background: transparent; border: 1px solid #e2e8f0;
          border-radius: 4px; font-size: 13px; font-weight: 600; color: #64748b;
          cursor: pointer; transition: all 0.2s;
        }
        .btn-logout:hover { background: #fef2f2; color: #dc2626; border-color: #fecaca; }

        /* Main Viewport Styling */
        .admin-viewport { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        
        .viewport-header { 
          height: 64px; min-height: 64px; background: #fff; border-bottom: 1px solid #e2e8f0;
          display: flex; justify-content: space-between; align-items: center; padding: 0 32px;
        }
        .breadcrumb { display: flex; align-items: center; gap: 8px; }
        .crumb-primary { font-size: 16px; font-weight: 700; color: #0f172a; }
        .crumb-divider { color: #cbd5e1; font-size: 14px; }
        .crumb-secondary { font-size: 13px; font-weight: 600; color: #64748b; }
        .viewport-time { font-size: 11px; font-weight: 700; color: #94a3b8; letter-spacing: 0.1em; }

        .viewport-content { flex: 1; overflow-y: auto; }
      `}</style>
    </div>
  );
};
