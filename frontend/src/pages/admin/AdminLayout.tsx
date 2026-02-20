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
  const adminName = adminUser ? `${adminUser.username}` : 'Admin';

  const handleLogout = () => {
    clearAdminSession();
    navigate('/admin/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/admin/dashboard', id: 'dashboard' },
    { label: 'Cabinets', path: '/admin/cabinets', id: 'cabinets' },
    { label: 'Sociétés', path: '/admin/societes', id: 'societes' },
    { label: 'Agents', path: '/admin/agents', id: 'agents' },
    { label: 'Associations', path: '/admin/associations', id: 'associations' },
  ];

  return (
    <div className="admin-layout">
      <nav className="admin-sidebar">
        <div className="admin-header">
          <h2>🔐 Admin Panel</h2>
          <p className="admin-user">👤 {adminName}</p>
        </div>

        <ul className="nav-menu">
          {navItems.map((item) => (
            <li key={item.path}>
              <button
                className={`nav-link ${currentPage === item.id ? 'active' : ''}`}
                onClick={() => navigate(item.path)}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>

        <button className="btn-logout" onClick={handleLogout}>
          🚪 Déconnexion
        </button>
      </nav>

      <main className="admin-content">
        {children}
      </main>

      <style>{`
        .admin-layout {
          display: flex;
          height: 100vh;
          background: #f5f5f5;
        }

        .admin-sidebar {
          width: 280px;
          background: #2c3e50;
          color: white;
          padding: 20px 0;
          box-shadow: 2px 0 8px rgba(0,0,0,0.1);
          overflow-y: auto;
        }

        .admin-header {
          padding: 20px;
          border-bottom: 1px solid rgba(255,255,255,0.1);
          margin-bottom: 20px;
        }

        .admin-header h2 {
          margin: 0 0 10px 0;
          font-size: 20px;
        }

        .admin-user {
          margin: 0;
          font-size: 12px;
          opacity: 0.8;
        }

        .nav-menu {
          list-style: none;
          margin: 0;
          padding: 0;
        }

        .nav-menu li {
          margin: 0;
        }

        .nav-link {
          display: block;
          width: 100%;
          padding: 15px 20px;
          background: none;
          border: none;
          color: inherit;
          text-align: left;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }

        .nav-link:hover {
          background: rgba(255,255,255,0.1);
          padding-left: 25px;
        }

        .nav-link.active {
          background: rgba(52, 152, 219, 0.3);
          border-left: 4px solid #3498db;
          padding-left: 20px;
          font-weight: 600;
        }

        .btn-logout {
          position: absolute;
          bottom: 20px;
          left: 20px;
          right: 20px;
          padding: 10px;
          background: #e74c3c;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: background 0.2s;
        }

        .btn-logout:hover {
          background: #c0392b;
        }

        .admin-sidebar {
          position: relative;
        }

        .admin-content {
          flex: 1;
          padding: 40px;
          overflow-y: auto;
        }

        @media (max-width: 768px) {
          .admin-layout {
            flex-direction: column;
          }

          .admin-sidebar {
            width: 100%;
            display: flex;
            height: auto;
          }

          .admin-content {
            padding: 20px;
          }
        }
      `}</style>
    </div>
  );
};
