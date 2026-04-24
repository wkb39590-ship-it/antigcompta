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
      const res = await apiService.listDemandesAcces();
      setDemandes(Array.isArray(res) ? res : []);
    } catch (err) {
      console.error('Erreur lors du chargement des demandes:', err);
      setDemandes([]);
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
        return <span className="tag tag-warning"><Clock size={12} /> EN ATTENTE</span>;
      case 'traitee':
        return <span className="tag tag-success"><CheckCircle size={12} /> TRAITÉE</span>;
      case 'rejetee':
        return <span className="tag tag-danger"><XCircle size={12} /> REJETÉE</span>;
      default:
        return <span className="tag">{statut.toUpperCase()}</span>;
    }
  };

  const isSuper = localStorage.getItem('is_super_admin') === 'true';

  return (
    <div className="demandes-page">
      <div className="page-header-simple">
        <h1>Demandes d'Accès</h1>
        <p>{isSuper ? "Flux centralisé des prospects et demandes d'ouverture de comptes." : "Gérez les prospects et les futures ouvertures de comptes clients."}</p>
      </div>

      <div className="view-controls pro-card">
        <div className="search-field">
          <Search size={16} />
          <input 
            type="text" 
            placeholder="Rechercher un prospect..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="filter-field">
          <Filter size={16} />
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">Tous les statuts</option>
            <option value="en_attente">En attente</option>
            <option value="traitee">Traitées</option>
            <option value="rejetee">Rejetées</option>
          </select>
        </div>
      </div>

      <div className="demandes-viewport">
        {loading ? (
          <div className="placeholder-state">
            <div className="dot-spinner"></div>
            <p>Chargement des demandes...</p>
          </div>
        ) : filteredDemandes.length === 0 ? (
          <div className="placeholder-state empty">
            <Inbox size={48} className="muted-icon" />
            <p>Aucune demande correspondante.</p>
          </div>
        ) : (
          <div className="table-wrapper pro-card" style={{ padding: 0 }}>
            <table className="pro-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Prospect</th>
                  <th>Entreprise</th>
                  <th>Contact</th>
                  <th>Statut</th>
                  {!isSuper && <th style={{ textAlign: 'right' }}>Actions</th>}
                </tr>
              </thead>
              <tbody>
                {filteredDemandes.map(demande => (
                  <tr key={demande.id}>
                    <td>
                      <span className="timestamp">{new Date(demande.created_at).toLocaleDateString('fr-FR')}</span>
                    </td>
                    <td>
                      <div className="prospect-profile-sm">
                        <div className="prospect-avatar-sm">{demande.nom_complet[0].toUpperCase()}</div>
                        <div className="prospect-info-sm">
                          <span className="prospect-name">{demande.nom_complet}</span>
                          {demande.message && <span className="prospect-msg-indicator" title={demande.message}><MessageSquare size={10} /> Message inclus</span>}
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="company-badge-sm">
                        <Building size={14} className="muted-icon" /> <span>{demande.entreprise}</span>
                      </div>
                    </td>
                    <td>
                      <div className="contact-info-sm">
                        <span><Mail size={12} /> {demande.email}</span>
                        {demande.telephone && <span><Phone size={12} /> {demande.telephone}</span>}
                      </div>
                    </td>
                    <td>{getStatusBadge(demande.statut)}</td>
                    {!isSuper && (
                      <td style={{ textAlign: 'right' }}>
                        {demande.statut === 'en_attente' && (
                          <div className="action-btn-group">
                            <button 
                              className="btn-icon btn-accept"
                              title="Accepter"
                              onClick={() => handleUpdateStatus(demande.id, 'traitee')}
                            >
                              <CheckCircle size={16} />
                            </button>
                            <button 
                              className="btn-icon btn-reject"
                              title="Rejeter"
                              onClick={() => handleUpdateStatus(demande.id, 'rejetee')}
                            >
                              <XCircle size={16} />
                            </button>
                          </div>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <style>{`
        .demandes-page { padding: 24px; animation: fadeIn 0.4s ease-out; }
        .page-header-simple h1 { font-size: 24px; font-weight: 800; color: #0f172a; margin: 0; }
        .page-header-simple p { font-size: 14px; color: #64748b; margin: 8px 0 24px; }

        .pro-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

        .view-controls { display: flex; gap: 16px; padding: 12px 16px; margin-bottom: 24px; align-items: center; }
        .search-field { flex: 1; display: flex; align-items: center; gap: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 0 12px; }
        .search-field input { width: 100%; height: 36px; border: none; background: transparent; font-size: 13px; outline: none; }
        .filter-field { display: flex; align-items: center; gap: 10px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 0 12px; }
        .filter-field select { height: 36px; border: none; background: transparent; font-size: 13px; font-weight: 600; outline: none; cursor: pointer; }

        .table-wrapper { overflow-x: auto; background: #fff; border-radius: 4px; }
        .pro-table { width: 100%; border-collapse: collapse; }
        .pro-table th { text-align: left; padding: 14px 20px; font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid #e2e8f0; background: #f8fafc; }
        .pro-table td { padding: 16px 20px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
        .pro-table tr:hover { background: #fafafa; }

        .timestamp { font-size: 13px; font-weight: 600; color: #475569; }

        .prospect-profile-sm { display: flex; align-items: center; gap: 12px; }
        .prospect-avatar-sm { width: 36px; height: 36px; background: #f1f5f9; color: #475569; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 15px; border: 1px solid #e2e8f0; flex-shrink: 0; }
        .prospect-info-sm { display: flex; flex-direction: column; gap: 4px; }
        .prospect-name { font-size: 14px; font-weight: 600; color: #1e293b; }
        .prospect-msg-indicator { font-size: 11px; color: #3b82f6; display: inline-flex; align-items: center; gap: 4px; cursor: help; font-weight: 600; }

        .company-badge-sm { display: inline-flex; align-items: center; gap: 8px; font-size: 14px; font-weight: 600; color: #334155; }

        .contact-info-sm { display: flex; flex-direction: column; gap: 6px; font-size: 13px; color: #64748b; font-weight: 500; }
        .contact-info-sm span { display: inline-flex; align-items: center; gap: 6px; }

        .action-btn-group { display: flex; gap: 8px; justify-content: flex-end; }
        .btn-icon { width: 34px; height: 34px; border: 1px solid #e2e8f0; background: #fff; border-radius: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
        .btn-icon.btn-accept { color: #16a34a; }
        .btn-icon.btn-accept:hover { background: #16a34a; color: white; border-color: #16a34a; }
        .btn-icon.btn-reject { color: #dc2626; }
        .btn-icon.btn-reject:hover { background: #dc2626; color: white; border-color: #dc2626; }

        .tag { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 800; }
        .tag-warning { background: #fffbeb; color: #d97706; border: 1px solid #fef3c7; }
        .tag-success { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; }
        .tag-danger { background: #fef2f2; color: #dc2626; border: 1px solid #fee2e2; }

        .placeholder-state { padding: 60px; text-align: center; }
        .dot-spinner { width: 24px; height: 24px; border: 3px solid #f1f5f9; border-top-color: #3b82f6; border-radius: 50%; animation: rot 0.8s linear infinite; margin: 0 auto 12px; }
        @keyframes rot { to { transform: rotate(360deg); } }
        .muted-icon { color: #94a3b8; }

        @media (max-width: 600px) { .view-controls { flex-direction: column; } .search-field { width: 100%; } }
      `}</style>
    </div>
  );
};
