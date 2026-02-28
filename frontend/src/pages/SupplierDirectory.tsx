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

    return (
        <div className="sd-page">
            <header className="sd-header">
                <div className="sd-title-area">
                    <h1 className="sd-title">Référentiel Fournisseurs</h1>
                    <p className="sd-subtitle text-zinc-400">Automatisation des affectations comptables.</p>
                </div>
                <div className="sd-actions">
                    <button onClick={fetchMappings} className="sd-btn-icon" title="Synchroniser">
                        <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                    </button>
                    <button className="sd-btn-primary">
                        <Plus size={18} />
                        <span>Ajouter Règle</span>
                    </button>
                </div>
            </header>

            <div className="sd-search-container">
                <Search size={18} className="text-zinc-500" />
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
                                        <div className="font-mono text-white tracking-widest bg-white/5 py-1 px-3 rounded-md inline-block border border-white/5">{m.supplier_ice}</div>
                                    </td>
                                    <td>
                                        <div className="flex items-center gap-3">
                                            <span className="sd-badge font-mono">{m.pcm_account_code}</span>
                                            <span className="text-sm text-zinc-300">{m.pcm_account_label || 'Compte Fournisseur'}</span>
                                        </div>
                                    </td>
                                    <td className="text-sm text-zinc-500">
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
                    padding: 2rem 0;
                    animation: fadeUp 0.6s ease-out;
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
                    font-size: 2rem;
                    font-weight: 800;
                    color: white;
                    letter-spacing: -0.5px;
                    margin: 0 0 0.4rem 0;
                }
                
                .sd-actions {
                    display: flex;
                    gap: 1rem;
                }

                .sd-btn-icon {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 42px;
                    height: 42px;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    color: white;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                .sd-btn-icon:hover {
                    background: rgba(255, 255, 255, 0.08);
                }

                .sd-btn-primary {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0 1.5rem;
                    height: 42px;
                    border-radius: 12px;
                    background: linear-gradient(135deg, #3b82f6, #6366f1);
                    border: none;
                    color: white;
                    font-weight: 600;
                    font-size: 0.875rem;
                    cursor: pointer;
                    transition: all 0.3s;
                    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
                }
                .sd-btn-primary:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
                }

                .sd-search-container {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                    background: rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    padding: 0 1.25rem;
                    border-radius: 16px;
                    margin-bottom: 1.5rem;
                    backdrop-filter: blur(10px);
                }

                .sd-search-input {
                    flex: 1;
                    background: transparent;
                    border: none;
                    color: white;
                    height: 54px;
                    font-size: 0.95rem;
                    outline: none;
                }
                .sd-search-input::placeholder {
                    color: rgba(255, 255, 255, 0.3);
                }

                .sd-glass-card {
                    background: rgba(15, 15, 20, 0.6);
                    border: 1px solid rgba(255, 255, 255, 0.05);
                    border-radius: 20px;
                    overflow: hidden;
                    backdrop-filter: blur(12px);
                }

                .sd-table {
                    width: 100%;
                    border-collapse: collapse;
                }

                .sd-table th {
                    text-align: left;
                    padding: 1.25rem 1.5rem;
                    font-size: 0.65rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1.5px;
                    color: rgba(255, 255, 255, 0.4);
                    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                }

                .sd-tr {
                    transition: all 0.2s;
                }
                .sd-tr:hover {
                    background: rgba(255, 255, 255, 0.02);
                }
                
                .sd-tr td {
                    padding: 1.25rem 1.5rem;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
                }

                .sd-badge {
                    background: rgba(59, 130, 246, 0.15);
                    color: #60a5fa;
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    padding: 0.25rem 0.75rem;
                    border-radius: 8px;
                    font-size: 0.85rem;
                }

                .sd-btn-delete {
                    background: transparent;
                    border: none;
                    color: rgba(244, 63, 94, 0.5);
                    padding: 0.5rem;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s;
                }
                .sd-btn-delete:hover {
                    background: rgba(244, 63, 94, 0.1);
                    color: #f43f5e;
                }

                .sd-empty {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 4rem 2rem;
                    text-align: center;
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
