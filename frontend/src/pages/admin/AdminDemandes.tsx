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
  Inbox,
  Trash2
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
  const [selectedDemande, setSelectedDemande] = useState<Demande | null>(null);
  const [showProvisioning, setShowProvisioning] = useState(false);
  const [provUsername, setProvUsername] = useState('');
  const [provPassword, setProvPassword] = useState('');
  const [provError, setProvError] = useState('');
  const [provLoading, setProvLoading] = useState(false);
  const [createdCredentials, setCreatedCredentials] = useState<{username: string; password: string} | null>(null);
  // Delete state
  const [deleteTarget, setDeleteTarget] = useState<Demande | null>(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

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

  const handleReject = async (id: number) => {
    try {
      await apiService.updateStatutDemande(id, 'rejetee');
      setSelectedDemande(null);
      loadDemandes();
    } catch (err) {
      alert('Erreur lors du rejet');
    }
  };

  const handleAccept = async () => {
    if (!selectedDemande) return;
    if (!provUsername.trim() || !provPassword.trim()) {
      setProvError('Veuillez renseigner le nom d\'utilisateur et le mot de passe.');
      return;
    }
    setProvLoading(true);
    setProvError('');
    try {
      const res = await apiService.updateStatutDemande(selectedDemande.id, 'traitee', provUsername.trim(), provPassword.trim());
      setSelectedDemande(null);
      setShowProvisioning(false);
      setProvUsername('');
      setProvPassword('');
      if (res.generated_username) {
        setCreatedCredentials({ username: res.generated_username, password: res.generated_password });
      }
      loadDemandes();
    } catch (err: any) {
      setProvError(err?.response?.data?.detail || 'Erreur lors de la création du compte.');
    } finally {
      setProvLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleteLoading(true);
    try {
      await apiService.deleteDemandeAcces(deleteTarget.id);
      setDeleteTarget(null);
      loadDemandes();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Erreur lors de la suppression.');
    } finally {
      setDeleteLoading(false);
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
                  <tr key={demande.id} onClick={() => setSelectedDemande(demande)} style={{ cursor: 'pointer' }} className="clickable-row">
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
                        <div className="action-btn-group">
                          {demande.statut === 'en_attente' && (
                            <button 
                              className="btn-icon btn-accept"
                              title="Accepter et ouvrir compte"
                              onClick={(e) => { 
                                e.stopPropagation(); 
                                setSelectedDemande(demande);
                                setShowProvisioning(true);
                                setProvUsername(demande.email);
                                setProvPassword('');
                                setProvError('');
                              }}
                            >
                              <CheckCircle size={16} />
                            </button>
                          )}
                          {demande.statut === 'en_attente' && (
                            <button 
                              className="btn-icon btn-reject"
                              title="Rejeter"
                              onClick={(e) => { e.stopPropagation(); handleReject(demande.id); }}
                            >
                              <XCircle size={16} />
                            </button>
                          )}
                          <button
                            className="btn-icon btn-delete"
                            title="Supprimer"
                            onClick={(e) => { e.stopPropagation(); setDeleteTarget(demande); }}
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedDemande && (
        <div className="modal-overlay" onClick={() => setSelectedDemande(null)}>
          <div className="pro-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Détails de la demande</h2>
              <button className="close-btn" onClick={() => setSelectedDemande(null)}>
                <XCircle size={20} />
              </button>
            </div>
            
            <div className="modal-content">
              <div className="preview-profile">
                <div className="modal-avatar">{selectedDemande.nom_complet[0].toUpperCase()}</div>
                <div>
                  <h3>{selectedDemande.nom_complet}</h3>
                  <p><Building size={14} /> {selectedDemande.entreprise}</p>
                </div>
                <div style={{ marginLeft: 'auto' }}>
                  {getStatusBadge(selectedDemande.statut)}
                </div>
              </div>

              <div className="modal-grid">
                <div className="info-block">
                  <label>Email</label>
                  <div>{selectedDemande.email}</div>
                </div>
                <div className="info-block">
                  <label>Téléphone</label>
                  <div>{selectedDemande.telephone || 'Non renseigné'}</div>
                </div>
                <div className="info-block msg-block">
                  <label>Date de la demande</label>
                  <div>{new Date(selectedDemande.created_at).toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</div>
                </div>
              </div>

              <div className="info-block msg-block">
                <label>Message du prospect</label>
                <div className="msg-box">
                  {selectedDemande.message ? selectedDemande.message : <em>Aucun message fourni.</em>}
                </div>
              </div>
            </div>

            {!isSuper && selectedDemande.statut === 'en_attente' && (
              <div className="modal-footer" style={{ flexDirection: 'column', alignItems: 'stretch', gap: 0 }}>
                {!showProvisioning ? (
                  <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', padding: '16px 24px' }}>
                    <button
                      className="btn-modal btn-modal-reject"
                      onClick={() => handleReject(selectedDemande.id)}
                    >
                      <XCircle size={18} /> Rejeter la demande
                    </button>
                    <button
                      className="btn-modal btn-modal-accept"
                      onClick={() => { setShowProvisioning(true); setProvUsername(selectedDemande.email); setProvPassword(''); setProvError(''); }}
                    >
                      <CheckCircle size={18} /> Accepter et Ouvrir compte
                    </button>
                  </div>
                ) : (
                  <div style={{ padding: '16px 24px', display: 'flex', flexDirection: 'column', gap: 12 }}>
                    <p style={{ margin: 0, fontWeight: 700, color: '#0f172a', fontSize: 14 }}>Définir les identifiants de connexion du client</p>
                    {provError && <div style={{ color: '#dc2626', background: '#fef2f2', border: '1px solid #fee2e2', borderRadius: 6, padding: '8px 12px', fontSize: 13 }}>{provError}</div>}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                      <div>
                        <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: 4 }}>Nom d'utilisateur</label>
                        <input
                          value={provUsername}
                          onChange={e => setProvUsername(e.target.value)}
                          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: 6, fontSize: 14, boxSizing: 'border-box' }}
                          placeholder="ex: client@acme.ma"
                        />
                      </div>
                      <div>
                        <label style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: 4 }}>Mot de passe</label>
                        <input
                          type="text"
                          value={provPassword}
                          onChange={e => setProvPassword(e.target.value)}
                          style={{ width: '100%', padding: '8px 12px', border: '1px solid #e2e8f0', borderRadius: 6, fontSize: 14, boxSizing: 'border-box' }}
                          placeholder="ex: Azerty2024!"
                        />
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
                      <button className="btn-modal" style={{ background: '#f1f5f9', color: '#475569', border: '1px solid #e2e8f0' }} onClick={() => setShowProvisioning(false)}>Annuler</button>
                      <button className="btn-modal btn-modal-accept" onClick={handleAccept} disabled={provLoading}>
                        {provLoading ? 'Création...' : <><CheckCircle size={16}/> Confirmer l'ouverture</>}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {createdCredentials && (
        <div className="modal-overlay" onClick={() => setCreatedCredentials(null)}>
          <div className="pro-modal" style={{ maxWidth: 440 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header" style={{ borderBottom: '2px solid #dcfce7' }}>
              <h2 style={{ color: '#16a34a', display: 'flex', alignItems: 'center', gap: 10 }}>
                <CheckCircle size={20} /> Compte créé avec succès
              </h2>
              <button className="close-btn" onClick={() => setCreatedCredentials(null)}><XCircle size={20} /></button>
            </div>
            <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: 16 }}>
              <p style={{ margin: 0, fontSize: 14, color: '#475569' }}>Transmettez ces identifiants au client pour qu'il puisse se connecter au portail.</p>
              <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 8, padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
                <div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: '#16a34a', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>Nom d'utilisateur</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', fontFamily: 'monospace', background: 'white', padding: '8px 12px', borderRadius: 6, border: '1px solid #dcfce7', userSelect: 'all' }}>{createdCredentials.username}</div>
                </div>
                <div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: '#16a34a', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>Mot de passe</div>
                  <div style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', fontFamily: 'monospace', background: 'white', padding: '8px 12px', borderRadius: 6, border: '1px solid #dcfce7', userSelect: 'all' }}>{createdCredentials.password}</div>
                </div>
              </div>
              <p style={{ margin: 0, fontSize: 12, color: '#94a3b8', textAlign: 'center' }}>⚠️ Notez ces informations, le mot de passe ne sera plus affiché.</p>
            </div>
            <div style={{ padding: '16px 24px', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn-modal btn-modal-accept" onClick={() => setCreatedCredentials(null)}>Compris, fermer</button>
            </div>
          </div>
        </div>
      )}

      {/* ── MODALE SUPPRESSION ──────────────────────── */}
      {deleteTarget && (
        <div className="modal-overlay" onClick={() => setDeleteTarget(null)}>
          <div className="pro-modal" style={{ maxWidth: 420 }} onClick={e => e.stopPropagation()}>
            <div className="modal-header" style={{ borderBottom: '2px solid #fee2e2' }}>
              <h2 style={{ color: '#dc2626', display: 'flex', alignItems: 'center', gap: 10 }}>
                <Trash2 size={18} /> Confirmer la suppression
              </h2>
              <button className="close-btn" onClick={() => setDeleteTarget(null)}><XCircle size={20} /></button>
            </div>
            <div style={{ padding: '24px' }}>
              <p style={{ margin: 0, fontSize: 14, color: '#475569', lineHeight: 1.6 }}>
                Êtes-vous sûr de vouloir supprimer définitivement la demande de
                <strong style={{ color: '#0f172a' }}> {deleteTarget.nom_complet}</strong>
                <span style={{ color: '#64748b' }}> ({deleteTarget.entreprise})</span> ?
              </p>
              <p style={{ margin: '12px 0 0', fontSize: 13, color: '#dc2626', background: '#fef2f2', border: '1px solid #fee2e2', borderRadius: 6, padding: '8px 12px' }}>
                ⚠️ Cette action est irréversible.
              </p>
            </div>
            <div className="modal-footer" style={{ borderTop: '1px solid #fee2e2' }}>
              <button className="btn-modal" style={{ background: '#f1f5f9', color: '#475569', border: '1px solid #e2e8f0' }} onClick={() => setDeleteTarget(null)}>Annuler</button>
              <button
                className="btn-modal"
                style={{ background: '#dc2626', color: 'white' }}
                onClick={handleDelete}
                disabled={deleteLoading}
              >
                {deleteLoading ? 'Suppression...' : <><Trash2 size={16} /> Supprimer</>}
              </button>
            </div>
          </div>
        </div>
      )}

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

        .action-btn-group { display: flex; gap: 8px; justify-content: flex-end; align-items: center; }
        .btn-icon { width: 34px; height: 34px; border: 1px solid #e2e8f0; background: #fff; border-radius: 4px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
        .btn-icon.btn-accept { color: #16a34a; }
        .btn-icon.btn-accept:hover { background: #16a34a; color: white; border-color: #16a34a; }
        .btn-icon.btn-reject { color: #dc2626; }
        .btn-icon.btn-reject:hover { background: #dc2626; color: white; border-color: #dc2626; }
        .btn-icon.btn-edit { color: #3b82f6; }
        .btn-icon.btn-edit:hover { background: #3b82f6; color: white; border-color: #3b82f6; }
        .btn-icon.btn-delete { color: #f59e0b; }
        .btn-icon.btn-delete:hover { background: #dc2626; color: white; border-color: #dc2626; }
        .edit-field { display: flex; flex-direction: column; gap: 4px; }
        .edit-field label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
        .edit-field input, .edit-field textarea { width: 100%; padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 14px; color: #0f172a; outline: none; transition: border-color 0.2s; box-sizing: border-box; font-family: inherit; }
        .edit-field input:focus, .edit-field textarea:focus { border-color: #4f46e5; box-shadow: 0 0 0 3px rgba(79,70,229,0.1); }

        .tag { display: inline-flex; align-items: center; gap: 4px; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 800; }
        .tag-warning { background: #fffbeb; color: #d97706; border: 1px solid #fef3c7; }
        .tag-success { background: #f0fdf4; color: #16a34a; border: 1px solid #dcfce7; }
        .tag-danger { background: #fef2f2; color: #dc2626; border: 1px solid #fee2e2; }

        .placeholder-state { padding: 60px; text-align: center; }
        .dot-spinner { width: 24px; height: 24px; border: 3px solid #f1f5f9; border-top-color: #3b82f6; border-radius: 50%; animation: rot 0.8s linear infinite; margin: 0 auto 12px; }
        @keyframes rot { to { transform: rotate(360deg); } }
        .muted-icon { color: #94a3b8; }
        
        .clickable-row:hover { background-color: #f1f5f9 !important; }

        .modal-overlay { position: fixed; inset: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 20px; animation: fadeIn 0.2s; }
        .pro-modal { width: 100%; max-width: 600px; background: white; border-radius: 12px; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); display: flex; flex-direction: column; overflow: hidden; animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
        .modal-header { padding: 20px 24px; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between; }
        .modal-header h2 { margin: 0; font-size: 18px; font-weight: 700; color: #0f172a; }
        .close-btn { background: none; border: none; color: #94a3b8; cursor: pointer; transition: color 0.2s; display: flex; }
        .close-btn:hover { color: #0f172a; }
        .modal-content { padding: 24px; display: flex; flex-direction: column; gap: 24px; background: #fafafa; }
        .preview-profile { display: flex; gap: 16px; align-items: center; background: white; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; }
        .modal-avatar { width: 48px; height: 48px; border-radius: 8px; background: #e0e7ff; color: #4338ca; font-size: 20px; font-weight: 800; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .preview-profile h3 { margin: 0 0 4px; font-size: 16px; font-weight: 700; color: #1e293b; }
        .preview-profile p { margin: 0; font-size: 13px; color: #64748b; font-weight: 600; display: flex; align-items: center; gap: 6px; }
        .modal-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .info-block label { display: block; font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px; }
        .info-block div { font-size: 14px; font-weight: 500; color: #0f172a; }
        .msg-block { grid-column: 1 / -1; }
        .msg-box { background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 8px; font-size: 14px; color: #334155; line-height: 1.6; min-height: 80px; }
        .modal-footer { padding: 16px 24px; border-top: 1px solid #e2e8f0; display: flex; justify-content: flex-end; gap: 12px; background: white; }
        .btn-modal { padding: 10px 16px; border-radius: 6px; font-size: 14px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: all 0.2s; border: none; }
        .btn-modal-reject { background: #fef2f2; color: #dc2626; border: 1px solid #fee2e2; }
        .btn-modal-reject:hover { background: #dc2626; color: white; }
        .btn-modal-accept { background: #4f46e5; color: white; box-shadow: 0 4px 12px rgba(79,70,229,0.2); }
        .btn-modal-accept:hover { background: #4338ca; transform: translateY(-1px); }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        @media (max-width: 600px) { .view-controls { flex-direction: column; } .search-field { width: 100%; } }
      `}</style>
    </div>
  );
};
