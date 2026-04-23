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
          <div className="demandes-grid">
            {filteredDemandes.map(demande => (
              <div key={demande.id} className="pro-card demande-item">
                <div className="item-header">
                  {getStatusBadge(demande.statut)}
                  <span className="timestamp">{new Date(demande.created_at).toLocaleDateString('fr-FR')}</span>
                </div>
                
                <div className="item-body">
                  <div className="prospect-profile">
                    <div className="prospect-avatar">{demande.nom_complet[0]}</div>
                    <div className="prospect-info">
                      <h3>{demande.nom_complet}</h3>
                      <span className="prospect-company"><Building size={12} /> {demande.entreprise}</span>
                    </div>
                  </div>

                  <div className="prospect-contacts">
                    <div className="contact-row">
                      <Mail size={12} />
                      <span>{demande.email}</span>
                    </div>
                    {demande.telephone && (
                      <div className="contact-row">
                        <Phone size={12} />
                        <span>{demande.telephone}</span>
                      </div>
                    )}
                  </div>

                  {demande.message && (
                    <div className="prospect-message">
                      <MessageSquare size={12} className="muted-icon" />
                      <p>{demande.message}</p>
                    </div>
                  )}
                </div>

                {demande.statut === 'en_attente' && (
                  <div className="item-actions">
                    <button 
                      className="btn-action-sm btn-accept"
                      onClick={() => handleUpdateStatus(demande.id, 'traitee')}
                    >
                      <CheckCircle size={14} /> Accepter
                    </button>
                    <button 
                      className="btn-action-sm btn-reject"
                      onClick={() => handleUpdateStatus(demande.id, 'rejetee')}
                    >
                      <XCircle size={14} /> Rejeter
                    </button>
                  </div>
                )}
              </div>
            ))}
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

        .demandes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
        .demande-item { display: flex; flex-direction: column; padding: 20px; transition: transform 0.2s; }
        .demande-item:hover { transform: translateY(-2px); border-color: #3b82f6; }

        .item-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .timestamp { font-size: 11px; font-weight: 700; color: #94a3b8; }

        .prospect-profile { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
        .prospect-avatar { width: 40px; height: 40px; background: #f1f5f9; color: #475569; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 16px; border: 1px solid #e2e8f0; }
        .prospect-info h3 { margin: 0; font-size: 15px; font-weight: 700; color: #1e293b; }
        .prospect-company { font-size: 12px; color: #3b82f6; font-weight: 600; display: flex; align-items: center; gap: 4px; }

        .prospect-contacts { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
        .contact-row { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; color: #64748b; }

        .prospect-message { background: #f8fafc; padding: 10px; border-radius: 4px; border: 1px solid #f1f5f9; margin-bottom: 20px; }
        .prospect-message p { margin: 0; font-size: 12px; color: #475569; line-height: 1.5; font-style: italic; }

        .item-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: auto; }
        .btn-action-sm { border: none; padding: 10px; border-radius: 4px; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s; }
        .btn-accept { background: #3b82f6; color: white; }
        .btn-accept:hover { background: #2563eb; }
        .btn-reject { background: #f1f5f9; color: #ef4444; border: 1px solid #fee2e2; }
        .btn-reject:hover { background: #fee2e2; }

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
