import React, { useState, useEffect } from 'react';
import apiService from '../api';
import {
    Users,
    Trash2,
    Search,
    RefreshCw,
    ShieldCheck,
    AlertCircle,
    Database,
    ArrowRight
} from 'lucide-react';

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
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchMappings();
    }, []);

    const fetchMappings = async () => {
        setLoading(true);
        try {
            const data = await apiService.listMappings();
            setMappings(data);
            setError(null);
        } catch (err) {
            console.error('Error fetching mappings:', err);
            setError('Impossible de charger le répertoire des fournisseurs.');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (id: number) => {
        if (!window.confirm('Voulez-vous vraiment supprimer cet apprentissage ? Le système devra ré-apprendre ce fournisseur.')) return;
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
        m.pcm_account_label.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="p-6 space-y-6 animate-in fade-in duration-700">
            {/* Header section with Aurora accent */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
                        Répertoire Fournisseurs
                    </h1>
                    <p className="text-gray-400 mt-1 flex items-center gap-2">
                        <Users size={16} className="text-emerald-400" />
                        Gestion des mappings intelligents et de l'IA apprenante
                    </p>
                </div>

                <button
                    onClick={fetchMappings}
                    className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-all"
                >
                    <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                    <span>Actualiser</span>
                </button>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white/5 border border-white/10 p-4 rounded-2xl flex items-center gap-4">
                    <div className="p-3 bg-blue-500/20 text-blue-400 rounded-xl">
                        <Database size={24} />
                    </div>
                    <div>
                        <div className="text-2xl font-bold">{mappings.length}</div>
                        <div className="text-xs text-gray-500 uppercase tracking-wider">Fournisseurs appris</div>
                    </div>
                </div>

                <div className="bg-white/5 border border-white/10 p-4 rounded-2xl flex items-center gap-4">
                    <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-xl">
                        <ShieldCheck size={24} />
                    </div>
                    <div>
                        <div className="text-2xl font-bold">100%</div>
                        <div className="text-xs text-gray-500 uppercase tracking-wider">Précision mémorisée</div>
                    </div>
                </div>

                <div className="bg-white/5 border border-white/10 p-4 rounded-2xl flex items-center gap-4">
                    <div className="p-3 bg-purple-500/20 text-purple-400 rounded-xl">
                        <RefreshCw size={24} />
                    </div>
                    <div>
                        <div className="text-2xl font-bold">Feedback Loop</div>
                        <div className="text-xs text-gray-500 uppercase tracking-wider">IA en auto-apprentissage</div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="bg-white/5 border border-white/10 rounded-3xl overflow-hidden backdrop-blur-xl">
                <div className="p-6 border-b border-white/10 flex flex-col md:flex-row gap-4 justify-between items-center">
                    <div className="relative w-full md:w-96">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={18} />
                        <input
                            type="text"
                            placeholder="Rechercher par ICE ou Code PCM..."
                            className="w-full bg-white/10 border border-white/10 rounded-xl py-2 pl-10 pr-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-400 bg-blue-500/10 px-3 py-1.5 rounded-lg border border-blue-500/20">
                        <AlertCircle size={16} className="text-blue-400" />
                        <span>Le système utilise l'ICE pour identifier les fournisseurs de façon unique.</span>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-white/5 text-gray-400 text-sm uppercase tracking-wider">
                                <th className="px-6 py-4 font-medium">ICE Fournisseur</th>
                                <th className="px-6 py-4 font-medium">Action Apprise</th>
                                <th className="px-6 py-4 font-medium">Compte PCM</th>
                                <th className="px-6 py-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {loading ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-12 text-center text-gray-500 italic">
                                        <RefreshCw className="animate-spin inline-block mr-2" /> Chargement...
                                    </td>
                                </tr>
                            ) : filteredMappings.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-12 text-center text-gray-500 italic">
                                        {searchTerm ? "Aucun mapping ne correspond à votre recherche." : "Le système n'a pas encore appris de mappings. Validez des factures pour commencer !"}
                                    </td>
                                </tr>
                            ) : (
                                filteredMappings.map((m) => (
                                    <tr key={m.id} className="hover:bg-white/5 transition-colors group">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <span className="font-mono bg-white/5 px-2 py-1 rounded text-blue-400">{m.supplier_ice}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2 text-emerald-400">
                                                <ArrowRight size={16} />
                                                <span className="text-sm font-medium">Automatisme</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col">
                                                <span className="font-bold text-gray-200">{m.pcm_account_code}</span>
                                                <span className="text-xs text-gray-500">{m.pcm_account_label}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => handleDelete(m.id)}
                                                className="p-2 text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-all opacity-0 group-hover:opacity-100"
                                                title="Oublier ce mapping"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                <div className="p-4 bg-white/5 text-xs text-gray-500 text-center border-t border-white/10">
                    Les mappings sont spécifiques à votre cabinet et garantissent une automatisation sans erreur pour les factures récurrentes.
                </div>
            </div>
        </div>
    );
};

export default SupplierDirectory;
