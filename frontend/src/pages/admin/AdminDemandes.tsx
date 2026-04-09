import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Mail, 
  Phone, 
  Building, 
  User, 
  MessageSquare,
  Search,
  Filter,
  Inbox
} from 'lucide-react';

interface Demande {
  id: number;
  nom_complet: string;
  entreprise: string;
  email: string;
  telephone?: string;
  message?: string;
  statut: string;
  created_at: string;
}

export const AdminDemandes: React.FC = () => {
  const [demandes, setDemandes] = useState<Demande[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('en_attente');
  const [search, setSearch] = useState('');

  const loadDemandes = async () => {
    setLoading(true);
    try {
      // Note: Assurez-vous d'ajouter listDemandesAcces à apiService 
      // ou utilisez un appel direct api.get('/demandes-acces/')
      const res = await apiService.listDemandesAcces();
      setDemandes(res);
    } catch (err) {
      console.error('Erreur lors du chargement des demandes:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDemandes();
  }, []);

  const handleUpdateStatus = async (id: number, statut: string) => {
    try {
      await apiService.updateStatutDemande(id, statut);
      loadDemandes();
    } catch (err) {
      console.error('Erreur lors de la mise à jour du statut:', err);
      alert('Erreur lors de la mise à jour');
    }
  };

  const filteredDemandes = demandes.filter(d => {
    const matchesFilter = filter === 'all' || d.statut === filter;
    const matchesSearch = 
      d.nom_complet.toLowerCase().includes(search.toLowerCase()) || 
      d.entreprise.toLowerCase().includes(search.toLowerCase()) ||
      d.email.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getStatusBadge = (statut: string) => {
    switch (statut) {
      case 'en_attente':
        return <span className="glass-badge badge-warning"><Clock size={12} /> En attente</span>;
      case 'traitee':
        return <span className="glass-badge badge-success"><CheckCircle size={12} /> Traitée</span>;
      case 'rejetee':
        return <span className="glass-badge badge-danger"><XCircle size={12} /> Rejetée</span>;
      default:
        return <span className="glass-badge">{statut}</span>;
    }
  };

  const isSuper = localStorage.getItem('is_super_admin') === 'true';

  return (
    <div className="admin-demandes-view">
      <div className="view-header">
        <div className="header-info">
          <h1 className="glass-text">Demandes d'accès</h1>
          <p>{isSuper ? "Vision d'ensemble de tous les prospects sur la plateforme." : "Gérez les prospects et les futures ouvertures de comptes clients."}</p>
        </div>
      </div>

      <div className="view-controls aurora-card">
        <div className="search-box">
          <Search size={18} />
          <input 
            type="text" 
            placeholder="Rechercher par nom, entreprise, email..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="filter-group">
          <Filter size={18} />
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">Tous les statuts</option>
            <option value="en_attente">En attente</option>
            <option value="traitee">Traitées</option>
            <option value="rejetee">Rejetées</option>
          </select>
        </div>
      </div>

      <div className="demandes-content">
        {loading ? (
          <div className="loading-state">Chargement des demandes...</div>
        ) : filteredDemandes.length === 0 ? (
          <div className="empty-state aurora-card">
            <Inbox size={48} />
            <p>Aucune demande d'accès trouvée.</p>
          </div>
        ) : isSuper ? (
          /* TABLE VIEW FOR SUPER ADMIN */
          <div className="aurora-card table-card animate-fadeIn">
            <div className="table-responsive">
              <table className="aurora-table-v2">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Prospect</th>
                    <th>Entreprise</th>
                    <th>Contact</th>
                    <th style={{ textAlign: 'center' }}>Statut</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredDemandes.map(d => (
                    <tr key={d.id}>
                      <td className="date-cell">{new Date(d.created_at).toLocaleDateString('fr-FR')}</td>
                      <td>
                        <div className="user-info-td">
                          <div className="mini-avatar"><User size={14} /></div>
                          <span className="name">{d.nom_complet}</span>
                        </div>
                      </td>
                      <td>
                        <div className="cabinet-tag-v2"><Building size={12} /> {d.entreprise}</div>
                      </td>
                      <td>
                        <div className="contact-td">
                          <div className="item"><Mail size={12} /> {d.email}</div>
                          {d.telephone && <div className="item"><Phone size={12} /> {d.telephone}</div>}
                        </div>
                      </td>
                      <td style={{ textAlign: 'center' }}>{getStatusBadge(d.statut)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          /* GRID VIEW FOR CABINET ADMIN */
          <div className="demandes-grid">
            {filteredDemandes.map(demande => (
              <div key={demande.id} className="demande-card aurora-card">
                <div className="card-header">
                  {getStatusBadge(demande.statut)}
                  <span className="date-text">{new Date(demande.created_at).toLocaleDateString('fr-FR')}</span>
                </div>
                
                <div className="card-body">
                  <div className="main-info">
                    <div className="avatar-placeholder">
                      <User size={24} />
                    </div>
                    <div>
                      <h3>{demande.nom_complet}</h3>
                      <p className="company-text"><Building size={14} /> {demande.entreprise}</p>
                    </div>
                  </div>

                  <div className="contact-details">
                    <div className="detail-item">
                      <Mail size={14} />
                      <span>{demande.email}</span>
                    </div>
                    {demande.telephone && (
                      <div className="detail-item">
                        <Phone size={14} />
                        <span>{demande.telephone}</span>
                      </div>
                    )}
                  </div>

                  {demande.message && (
                    <div className="message-box">
                      <MessageSquare size={14} />
                      <p>{demande.message}</p>
                    </div>
                  )}
                </div>

                {demande.statut === 'en_attente' && (
                  <div className="card-actions">
                    <button 
                      className="action-btn btn-success"
                      onClick={() => handleUpdateStatus(demande.id, 'traitee')}
                    >
                      <CheckCircle size={16} /> Accepter / Créer
                    </button>
                    <button 
                      className="action-btn btn-danger"
                      onClick={() => handleUpdateStatus(demande.id, 'rejetee')}
                    >
                      <XCircle size={16} /> Rejeter
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      <style>{`
        .admin-demandes-view {
          display: flex;
          flex-direction: column;
          gap: 24px;
          animation: fadeIn 0.4s ease-out;
        }

        .view-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-end;
        }

        .header-info h1 {
          margin: 0;
          font-size: 32px;
          font-weight: 900;
          letter-spacing: -1px;
        }

        .aurora-btn-primary { 
          background: #4f46e5 !important; 
          color: white !important; 
          box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
          display: flex; align-items: center; gap: 8px; padding: 12px 24px;
          border-radius: 14px; border: none; font-weight: 700; cursor: pointer;
          transition: all 0.3s;
        }
        .aurora-btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(79, 70, 229, 0.5); }
        
        .header-info p {
          margin: 8px 0 0 0;
          color: var(--text3);
          font-weight: 500;
        }

        .view-controls {
          display: flex;
          gap: 20px;
          padding: 16px 24px;
          background: rgba(255, 255, 255, 0.4);
          border: 1px solid rgba(255, 255, 255, 0.6);
        }

        .search-box {
          flex: 1;
          display: flex;
          align-items: center;
          gap: 12px;
          background: rgba(255, 255, 255, 0.5);
          padding: 0 16px;
          border-radius: 14px;
          border: 1px solid rgba(0, 0, 0, 0.05);
        }

        .search-box input {
          width: 100%;
          height: 44px;
          background: transparent;
          border: none;
          outline: none;
          font-size: 14px;
          color: var(--text);
          font-weight: 500;
        }

        .filter-group {
          display: flex;
          align-items: center;
          gap: 12px;
          background: rgba(255, 255, 255, 0.5);
          padding: 0 16px;
          border-radius: 14px;
          border: 1px solid rgba(0, 0, 0, 0.05);
        }

        .filter-group select {
          height: 44px;
          background: transparent;
          border: none;
          outline: none;
          font-size: 14px;
          font-weight: 700;
          color: var(--text);
          cursor: pointer;
        }

        .demandes-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
          gap: 24px;
          padding-bottom: 40px;
        }

        .demande-card {
          display: flex;
          flex-direction: column;
          padding: 24px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .demande-card:hover {
          transform: translateY(-5px);
          box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .date-text {
          font-size: 12px;
          font-weight: 700;
          color: var(--text3);
        }

        .main-info {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 20px;
        }

        .avatar-placeholder {
          width: 48px;
          height: 48px;
          background: var(--aurora-gradient);
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          box-shadow: 0 8px 16px rgba(99, 102, 241, 0.2);
        }

        .main-info h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 800;
          color: var(--text);
        }

        .company-text {
          margin: 4px 0 0 0;
          font-size: 13px;
          font-weight: 600;
          color: var(--accent);
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .contact-details {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-bottom: 20px;
        }

        .detail-item {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 13px;
          font-weight: 600;
          color: var(--text2);
        }

        .message-box {
          background: rgba(0, 0, 0, 0.03);
          padding: 12px;
          border-radius: 12px;
          font-size: 13px;
          color: var(--text2);
          display: flex;
          gap: 10px;
          margin-bottom: 24px;
        }

        .message-box p {
          margin: 0;
          line-height: 1.5;
        }

        .card-actions {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-top: auto;
        }

        .action-btn {
          height: 40px;
          border: none;
          border-radius: 10px;
          font-size: 12px;
          font-weight: 800;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 6px;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-success {
          background: rgba(34, 197, 94, 0.1);
          color: var(--success);
        }

        .btn-success:hover {
          background: var(--success);
          color: white;
        }

        .btn-danger {
          background: rgba(239, 68, 68, 0.1);
          color: var(--danger);
        }

        .btn-danger:hover {
          background: var(--danger);
          color: white;
        }

        .demandes-content {
          animation: fadeIn 0.4s ease-out;
        }

        .table-card {
          padding: 24px;
          overflow: hidden;
        }

        .table-responsive {
          overflow-x: auto;
        }

        .aurora-table-v2 {
          width: 100%;
          border-collapse: collapse;
        }

        .aurora-table-v2 th {
          text-align: left;
          padding: 16px 20px;
          font-size: 11px;
          font-weight: 800;
          color: var(--text3);
          text-transform: uppercase;
          letter-spacing: 1.5px;
          border-bottom: 1px solid var(--border);
        }

        .aurora-table-v2 td {
          padding: 16px 20px;
          border-bottom: 1px solid #f1f5f9;
          vertical-align: middle;
        }

        .date-cell {
          font-size: 13px;
          font-weight: 700;
          color: var(--text3);
        }

        .user-info-td {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .mini-avatar {
          width: 32px;
          height: 32px;
          border-radius: 8px;
          background: linear-gradient(135deg, #4f46e5, #7c3aed);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          box-shadow: 0 4px 10px rgba(99, 102, 241, 0.2);
          border: 1px solid white;
        }

        .user-info-td .name {
          font-weight: 700;
          font-size: 14px;
          color: var(--text);
        }

        .cabinet-tag-v2 {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          background: rgba(99, 102, 241, 0.05);
          border: 1px solid rgba(99, 102, 241, 0.1);
          border-radius: 8px;
          font-size: 12px;
          font-weight: 700;
          color: var(--accent);
        }

        .contact-td {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .contact-td .item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          font-weight: 600;
          color: var(--text2);
        }

        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out forwards;
        }
      `}</style>
    </div>
  );
};
