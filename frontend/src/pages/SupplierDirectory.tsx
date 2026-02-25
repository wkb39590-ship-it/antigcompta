import React, { useState, useEffect } from 'react';
import apiService from '../api';
import {
    Users,
    Trash2,
    Search,
    RefreshCw,
    ShieldCheck,
    Database,
    Plus,
    Zap,
    Download,
    ChevronDown,
    MoreHorizontal,
    Edit2,
    Pause,
    Play
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
    const [lastSync] = useState<string>('2 min');

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
        if (!window.confirm('Voulez-vous vraiment supprimer cette règle ?')) return;
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
        <div className="container-pro animate-in fade-in duration-500 space-y-8 pb-12">

            {/* --- HEADER --- */}
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-1">
                    <h1 className="text-3xl font-bold tracking-tight text-white">Référentiel Fournisseurs</h1>
                    <p className="text-zinc-500 text-sm">Gestion des schémas d'imputation automatique et des mappings tiers.</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={fetchMappings}
                        className="btn btn-ghost"
                        title="Actualiser les données"
                    >
                        <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                        <span>Synchroniser</span>
                    </button>
                    <button className="btn btn-primary">
                        <Plus size={18} />
                        <span>Nouvelle règle</span>
                    </button>
                </div>
            </header>

            {/* --- KPI GRID --- */}
            <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                    { label: 'Tiers Référencés', value: mappings.length, diff: '+12%', icon: Users },
                    { label: 'Règles Actives', value: mappings.length + 8, diff: '+2.4%', icon: Zap },
                    { label: 'Taux Auto', value: '88.4%', diff: '+5.7%', icon: ShieldCheck },
                    { label: 'État Système', value: 'OK', diff: 'Optimal', icon: Database }
                ].map((stat, i) => (
                    <div key={i} className="card p-6 flex flex-col justify-between hover:border-blue-500/30 transition-all group">
                        <div className="flex items-center justify-between mb-4">
                            <span className="stat-label text-[10px] font-bold tracking-widest">{stat.label}</span>
                            <stat.icon size={18} className="text-zinc-700 group-hover:text-blue-500/50 transition-colors" />
                        </div>
                        <div className="flex items-baseline justify-between">
                            <div className="stat-value text-3xl font-bold text-white tracking-tight">{stat.value}</div>
                            <span className={`text-[10px] font-bold ${stat.diff.includes('+') ? 'text-emerald-500' : 'text-zinc-500'}`}>
                                {stat.diff}
                            </span>
                        </div>
                    </div>
                ))}
            </section>

            {/* --- TOOLBAR CARD --- */}
            <div className="card p-4">
                <div className="flex flex-col md:flex-row items-center gap-4">
                    <div className="relative flex-[6] w-full">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
                        <input
                            type="text"
                            placeholder="Rechercher par ICE, libellé ou compte..."
                            className="form-input pl-10 h-11"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div className="flex flex-[4] items-center gap-2 w-full">
                        <select className="form-input h-11 flex-1">
                            <option>Tous les statuts</option>
                            <option>Actif</option>
                            <option>Pause</option>
                        </select>
                        <select className="form-input h-11 flex-1">
                            <option>Tous les types</option>
                            <option>Automatique</option>
                            <option>Manuel</option>
                        </select>
                        <button className="btn btn-ghost h-11 px-4" title="Exporter en Excel">
                            <Download size={18} />
                        </button>
                    </div>
                </div>
            </div>

            {/* --- TABLE CARD --- */}
            <div className="card p-0 overflow-hidden">
                <div className="table-wrap">
                    <table className="w-full text-sm text-left border-collapse">
                        <thead>
                            <tr className="bg-zinc-900/50 border-b border-zinc-800">
                                <th className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-zinc-500">Fournisseur & ICE</th>
                                <th className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-zinc-500">Mapping PCM</th>
                                <th className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-zinc-500">Statut</th>
                                <th className="px-6 py-4 font-bold text-[10px] uppercase tracking-widest text-zinc-500 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-zinc-800">
                            {loading ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-24 text-center">
                                        <div className="loading"><div className="spinner" /> Synchronisation...</div>
                                    </td>
                                </tr>
                            ) : filteredMappings.length === 0 ? (
                                <tr>
                                    <td colSpan={4} className="px-6 py-24 text-center text-zinc-600 italic">
                                        Aucun résultat pour cette recherche.
                                    </td>
                                </tr>
                            ) : (
                                filteredMappings.map((m, idx) => (
                                    <tr key={m.id} className="group hover:bg-white/[0.02] transition-colors">
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col">
                                                <span className="font-bold text-white group-hover:text-blue-400 transition-colors">Fournisseur {idx + 1}</span>
                                                <span className="text-[10px] font-mono text-zinc-600 mt-0.5">{m.supplier_ice}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-col gap-1">
                                                <div className="flex items-center gap-2">
                                                    <span className="px-2 py-0.5 bg-zinc-800 text-blue-400 rounded text-xs font-mono font-bold">
                                                        {m.pcm_account_code}
                                                    </span>
                                                    <span className="text-xs text-zinc-400">{m.pcm_account_label || '—'}</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-sm">
                                            {idx % 3 === 0 ? (
                                                <span className="badge badge-validated">Actif</span>
                                            ) : idx % 3 === 1 ? (
                                                <span className="badge badge-draft" style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#fbbf24' }}>Pause</span>
                                            ) : (
                                                <span className="badge badge-imported">Inactif</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-5 text-right">
                                            <div className="flex items-center justify-end gap-1 opacity-10 md:opacity-0 group-hover:opacity-100 transition-opacity">
                                                <button className="btn btn-ghost p-2 rounded-lg hover:text-white" title="Modifier">
                                                    <Edit2 size={16} />
                                                </button>
                                                <button className="btn btn-ghost p-2 rounded-lg hover:text-white" title="Mettre en pause">
                                                    {idx % 3 === 1 ? <Play size={16} /> : <Pause size={16} />}
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(m.id)}
                                                    className="btn btn-ghost p-2 rounded-lg hover:text-danger"
                                                    title="Supprimer la règle"
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            </div>
                                            <div className="group-hover:hidden transition-all text-zinc-700">
                                                <MoreHorizontal size={18} />
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* --- DISCRETE SYNC STATE (REPLACED TECHNICAL FOOTER) --- */}
            <div className="flex items-center justify-center gap-4 text-[10px] font-bold uppercase tracking-widest text-zinc-700">
                <span className="flex items-center gap-1.5"><div className="w-1 h-1 rounded-full bg-blue-500 animate-pulse"></div> Flux Sécurisé</span>
                <div className="h-1 w-1 bg-zinc-800 rounded-full"></div>
                <span>Sync v2.4-stable</span>
            </div>
        </div>
    );
};

export default SupplierDirectory;
