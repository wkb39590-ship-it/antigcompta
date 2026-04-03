import React, { useState, useEffect } from 'react';
import apiService from '../api';
import { Search, Plus, Trash2, RefreshCw, AlertCircle } from 'lucide-react';

interface Mapping {
    id: number;
    supplier_ice: string;
    pcm_account_code: string;
    pcm_account_label: string;
    updated_at: string;
}

const SupplierDirectory: React.FC = () => {
    const [mappings, setMappings] = useState<Mapping[]>([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newMapping, setNewMapping] = useState({ supplier_ice: '', pcm_account_code: '' });
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchMappings();
    }, []);

    const fetchMappings = async () => {
        setLoading(true);
        try {
            const data = await apiService.listMappings();
            setMappings(data);
        } catch (err) {
            console.error('Error fetching mappings:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: number) => {
        if (!window.confirm('Voulez-vous vraiment supprimer cette correspondance ?')) return;
        try {
            await apiService.deleteMapping(id);
            setMappings(mappings.filter(m => m.id !== id));
        } catch (err) {
            alert('Erreur lors de la suppression');
        }
    };

    const filteredMappings = mappings.filter(m =>
        m.supplier_ice.toLowerCase().includes(searchTerm.toLowerCase()) ||
        m.pcm_account_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (m.pcm_account_label && m.pcm_account_label.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    const handleCreateMapping = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newMapping.supplier_ice || !newMapping.pcm_account_code) {
            alert('Veuillez remplir tous les champs');
            return;
        }
        setSubmitting(true);
        try {
            await apiService.createMapping(newMapping);
            await fetchMappings();
            setIsModalOpen(false);
            setNewMapping({ supplier_ice: '', pcm_account_code: '' });
        } catch (err) {
            alert('Erreur lors de la création de la règle. Vérifiez les informations.');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="sd-page">
            <header className="sd-header">
                <div className="sd-title-area">
                    <h1 className="sd-title">Référentiel Fournisseurs</h1>
                    <p className="sd-subtitle">Automatisation des affectations comptables.</p>
                </div>
                <div className="sd-actions">
                    <button onClick={fetchMappings} className="sd-btn-icon" title="Synchroniser">
                        <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                    </button>
                     <button onClick={() => setIsModalOpen(true)} className="sd-btn-primary">
                        <Plus size={18} />
                        <span>Ajouter Règle</span>
                    </button>
                </div>
            </header>

            <div className="sd-search-container">
                <Search size={18} className="sd-search-icon" />
                <input
                    type="text"
                    placeholder="Rechercher par ICE ou compte (ex: 6111)..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="sd-search-input"
                />
            </div>

            <div className="sd-glass-card">
                {loading ? (
                    <div className="sd-empty">
                        <RefreshCw className="animate-spin text-blue-500 mb-2" size={24} />
                        <p className="text-zinc-400">Chargement du référentiel...</p>
                    </div>
                ) : filteredMappings.length === 0 ? (
                    <div className="sd-empty text-zinc-500">
                        <AlertCircle size={32} className="mb-3 opacity-50" />
                        <p>Aucun mapping fournisseur trouvé.</p>
                        <span className="text-xs opacity-50 block mt-1">L'IA créera des règles automatiquement lors de la validation des factures.</span>
                    </div>
                ) : (
                    <table className="sd-table">
                        <thead>
                            <tr>
                                <th>Identifiant (ICE)</th>
                                <th>Imputation (PCM)</th>
                                <th>Dernière Maj.</th>
                                <th className="text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredMappings.map((m) => (
                                <tr key={m.id} className="sd-tr">
                                    <td>
                                        <div className="sd-ice-badge">{m.supplier_ice}</div>
                                    </td>
                                    <td>
                                        <div className="flex items-center gap-3">
                                            <span className="sd-badge font-mono">{m.pcm_account_code}</span>
                                            <span className="text-sm text-slate-600">{m.pcm_account_label || 'Compte Fournisseur'}</span>
                                        </div>
                                    </td>
                                    <td className="text-sm text-slate-400">
                                        {m.updated_at ? new Date(m.updated_at).toLocaleDateString('fr-FR') : 'Récent'}
                                    </td>
                                    <td className="text-right">
                                        <button
                                            onClick={() => handleDelete(m.id)}
                                            className="sd-btn-delete"
                                            title="Supprimer la règle"
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>

            {/* MODAL AJOUT REGLE */}
            {isModalOpen && (
                <div className="sd-modal-overlay">
                    <div className="sd-modal-content">
                        <div className="sd-modal-header">
                            <h2 className="sd-modal-title">Nouvelle Règle Fournisseur</h2>
                            <button onClick={() => setIsModalOpen(false)} className="sd-modal-close">&times;</button>
                        </div>
                        <form onSubmit={handleCreateMapping} className="sd-modal-form">
                            <div className="sd-form-group">
                                <label>Identifiant (ICE) du Fournisseur</label>
                                <input 
                                    type="text" 
                                    placeholder="Ex: 000086358..." 
                                    value={newMapping.supplier_ice}
                                    onChange={e => setNewMapping({...newMapping, supplier_ice: e.target.value})}
                                    required
                                />
                            </div>
                            <div className="sd-form-group">
                                <label>Compte PCM (6111, 2355...)</label>
                                <input 
                                    type="text" 
                                    placeholder="Ex: 6111" 
                                    value={newMapping.pcm_account_code}
                                    onChange={e => setNewMapping({...newMapping, pcm_account_code: e.target.value})}
                                    required
                                />
                            </div>
                            <div className="sd-modal-actions">
                                <button type="button" onClick={() => setIsModalOpen(false)} className="sd-btn-secondary">Annuler</button>
                                <button type="submit" disabled={submitting} className="sd-btn-primary">
                                    {submitting ? 'Enregistrement...' : 'Enregistrer la Règle'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* SYNC DISCRETE */}
            <div className="mt-8 flex justify-center">
                <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 text-emerald-500 text-[10px] font-bold uppercase tracking-widest border border-emerald-500/20">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    Synchronisation active
                </div>
            </div>

            <style>{`
                .sd-page {
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 2.5rem 1rem;
                    animation: fadeUp 0.6s ease-out;
                    background: transparent;
                }
                
                @keyframes fadeUp {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                .sd-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                    margin-bottom: 2.5rem;
                }

                .sd-title {
                    font-size: 2.25rem;
                    font-weight: 800;
                    color: #1e293b;
                    letter-spacing: -0.025em;
                    margin: 0 0 0.5rem 0;
                }

                .sd-subtitle {
                    color: #64748b;
                    font-size: 0.95rem;
                }
                
                .sd-actions {
                    display: flex;
                    gap: 0.75rem;
                }

                .sd-btn-icon {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 44px;
                    height: 44px;
                    border-radius: 12px;
                    background: #fff;
                    border: 1px solid #e2e8f0;
                    color: #64748b;
                    cursor: pointer;
                    transition: all 0.2s;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
                }
                .sd-btn-icon:hover {
                    background: #f8fafc;
                    border-color: #cbd5e1;
                    color: #1e293b;
                }

                .sd-btn-primary {
                    display: flex;
                    align-items: center;
                    gap: 0.6rem;
                    padding: 0 1.5rem;
                    height: 44px;
                    border-radius: 12px;
                    background: #2563eb;
                    border: none;
                    color: white;
                    font-weight: 600;
                    font-size: 0.9rem;
                    cursor: pointer;
                    transition: all 0.2s;
                    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
                }
                .sd-btn-primary:hover {
                    background: #1d4ed8;
                    transform: translateY(-1px);
                    box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
                }

                .sd-search-container {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    background: #fff;
                    border: 1px solid #e2e8f0;
                    padding: 0 1.25rem;
                    border-radius: 14px;
                    margin-bottom: 2rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                    transition: all 0.2s;
                }
                .sd-search-container:focus-within {
                    border-color: #3b82f6;
                    box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
                }

                .sd-search-icon {
                    color: #94a3b8;
                }

                .sd-search-input {
                    flex: 1;
                    background: transparent;
                    border: none;
                    color: #1e293b;
                    height: 52px;
                    font-size: 0.95rem;
                    outline: none;
                }
                .sd-search-input::placeholder {
                    color: #94a3b8;
                }

                .sd-glass-card {
                    background: #ffffff;
                    border: 1px solid #e2e8f0;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                }

                .sd-table {
                    width: 100%;
                    border-collapse: collapse;
                }

                .sd-table thead {
                    background: #f8fafc;
                }

                .sd-table th {
                    text-align: left;
                    padding: 1rem 1.5rem;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    color: #64748b;
                    border-bottom: 1px solid #e2e8f0;
                }

                .sd-tr {
                    transition: all 0.2s;
                }
                .sd-tr:hover {
                    background: #f1f5f9;
                }
                
                .sd-tr td {
                    padding: 1.25rem 1.5rem;
                    border-bottom: 1px solid #f1f5f9;
                    color: #334155;
                }

                .sd-ice-badge {
                    font-family: 'JetBrains Mono', 'Fira Code', monospace;
                    color: #475569;
                    letter-spacing: 0.02em;
                    background: #f1f5f9;
                    padding: 0.35rem 0.75rem;
                    border-radius: 6px;
                    display: inline-block;
                    border: 1px solid #e2e8f0;
                    font-size: 0.85rem;
                    font-weight: 500;
                }

                .sd-badge {
                    background: #eff6ff;
                    color: #1d4ed8;
                    border: 1px solid #dbeafe;
                    padding: 0.25rem 0.6rem;
                    border-radius: 6px;
                    font-size: 0.8rem;
                    font-weight: 600;
                }

                .sd-btn-delete {
                    background: transparent;
                    border: none;
                    color: #ef4444;
                    padding: 0.5rem;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s;
                    opacity: 0.6;
                }
                .sd-btn-delete:hover {
                    background: #fef2f2;
                    opacity: 1;
                    transform: scale(1.1);
                }

                .sd-empty {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 5rem 2rem;
                    text-align: center;
                    color: #94a3b8;
                }

                /* MODAL STYLES */
                .sd-modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.4);
                    backdrop-filter: blur(4px);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                    animation: fadeIn 0.2s ease-out;
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }

                .sd-modal-content {
                    background: #fff;
                    width: 100%;
                    max-width: 450px;
                    border-radius: 20px;
                    padding: 2rem;
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
                    animation: scaleIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
                }
                @keyframes scaleIn {
                    from { transform: scale(0.9); opacity: 0; }
                    to { transform: scale(1); opacity: 1; }
                }

                .sd-modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 2rem;
                }
                .sd-modal-title {
                    font-size: 1.25rem;
                    font-weight: 700;
                    color: #1e293b;
                }
                .sd-modal-close {
                    background: none;
                    border: none;
                    font-size: 1.5rem;
                    color: #94a3b8;
                    cursor: pointer;
                    transition: color 0.2s;
                }
                .sd-modal-close:hover { color: #1e293b; }

                .sd-modal-form {
                    display: flex;
                    flex-direction: column;
                    gap: 1.5rem;
                }
                .sd-form-group {
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                }
                .sd-form-group label {
                    font-size: 0.85rem;
                    font-weight: 600;
                    color: #64748b;
                }
                .sd-form-group input {
                    height: 48px;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 0 1rem;
                    font-size: 0.95rem;
                    color: #1e293b;
                    outline: none;
                    transition: all 0.2s;
                }
                .sd-form-group input:focus {
                    border-color: #3b82f6;
                    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
                }

                .sd-modal-actions {
                    display: flex;
                    justify-content: flex-end;
                    gap: 1rem;
                    margin-top: 1rem;
                }

                .sd-btn-secondary {
                    padding: 0 1.5rem;
                    height: 44px;
                    border-radius: 12px;
                    background: #f8fafc;
                    border: 1px solid #e2e8f0;
                    color: #64748b;
                    font-weight: 600;
                    font-size: 0.9rem;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                .sd-btn-secondary:hover {
                    background: #f1f5f9;
                    color: #1e293b;
                }

                @media (max-width: 768px) {
                    .sd-header { flex-direction: column; align-items: flex-start; gap: 1.5rem; }
                    .sd-actions { width: 100%; justify-content: space-between; }
                }
            `}</style>
        </div>
    );
};

export default SupplierDirectory;
